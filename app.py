from flask import Flask, request, render_template
from pprint import pprint
from leap import Leap, ApiException
import asyncio
import aiohttp
import os
import requests
from PIL import Image
import constants
from datetime import datetime
import io

app = Flask(__name__)
model_id = constants.modelId
leap = Leap(
    access_token=constants.key
)

path = os.path.dirname('GeneratedImages')
image_file = f"{datetime.now().strftime('%m_%d_%Y_%H_%M_%S')}.png"

@app.route('/')
async def index():
    return render_template('index.html')

@app.route('/generateimage', methods=['GET', 'POST'])
def generate():
    try:
        if request.method == 'GET':
            return render_template('generateImage.html')
        elif request.method == 'POST':
            # Generate an Image
            generate_response = leap.images.generate(
                prompt= request.form.get('floating_prompt'),  # required
                model_id=model_id,  # required
                negative_prompt=request.form.get("floating_negative_prompt"),  # optional
                steps=int(request.form.get('floating_steps')),  # optional
                width=int(request.form.get('floating_width')),  # optional
                height=int(request.form.get('floating_height')),  # optional
                number_of_images=int(request.form.get('floating_number_of_images')),  # optional
                prompt_strength=7,  # optional
                seed=4523184,  # optional
            )
            #pprint(generate_response.body)
            return render_template('generateImage.html', image=generate_response.status)
        else:
            print(request.method)
    except ApiException as e:
        print("Exception when calling ImagesApi.generate: %s\n" % e)
        pprint(e.body)


@app.route('/listImages')
def listImages():
    if request.method == 'GET':
        image_folder = 'static/GeneratedImages'
        image_files = [f for f in os.listdir(image_folder) if f.endswith(('.jpg', '.png', '.jpeg'))]

        return render_template('listImages.html', image_files=image_files)
    elif request.method == 'POST':
        list_all_response = leap.images.list_all( 
            model_id=model_id,  # required
            only_finished=True,  # optional
            page=3,  # optional
            page_size=3,  # optional
        )
        images = list_all_response.body
        async def fetch_image(session, url, path, name):
            try:
                async with session.get(url) as response:
                    if response.status == 200:
                        image_data = await response.read()
                        image = Image.open(io.BytesIO(image_data))
                        image.thumbnail((512,512))
                        #image_file = os.path.basename(url)
                        #print(image_file)
                        image.save(os.path.join(path, './GeneratedImages', name[:15] + '.png'))
                    else:
                        return f"Failed to retrieve URL. Status code: {response.status}"
            except Exception as e:
                return f"Error: {str(e)}"
            
        async def download_images(images, path):
            async with aiohttp.ClientSession() as session:
                tasks = []
                links = {}
                for i in images:
                    p = ['prompt', 'images']
                    keys = dict((key, i[key]) for key in p)
                    prompts, image_url = keys.values()
                    links.update({prompts: image_url[0]['uri'] })
                for link in links:
                    task = fetch_image(session, links[link], path, link)
                    #print(link)
                    tasks.append(task)
                
                results = await asyncio.gather(*tasks)
                #print(results)
            return results
        
        result = asyncio.run(download_images(images, path))
        return render_template('listImages.html', images=result)
    else:
        return 'There was an error'



if __name__ == '__main__':
    app.run(debug=True, host='localhost')
    #loop = asyncio.get_event_loop()
    #results = loop.run_until_complete(download_images(images, path))
    

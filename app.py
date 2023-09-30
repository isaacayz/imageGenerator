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






"""async def load_url(uri):
            links = []
            for i in images:
                p = ['prompt', 'images']
                keys = dict((key, i[key]) for key in p)
                image_url = keys['images'][0]['uri']
                links.append(image_url)
            for x in links:
                async with aiohttp.ClientSession() as session:
                    async with session.get(x, timeout=10) as response:
                        print("i am inside a random session")
                        response = requests.get(x, stream=True)
                        if response.status_code == 200:
                            img = Image.open((response).raw)
                            img.save(os.path.join(path,'./GeneratedImages', image_file))
                            return 'content'
                        else:
                            return f"Failed to retrieve URL. Status code: {response.status_code}" """
        

# List All Image Jobs
"""list_all_response = leap.images.list_all(
    model_id=model_id,  # required
    only_finished=True,  # optional
    page=1,  # optional
    page_size=5,  # optional
)
images = list_all_response.body

async def fetch_image(session, url, path):
    try:
        async with session.get(url, timeout=10) as response:
            if response.status == 200:
                print("I am in the response")
                image_data = await response.read()
                image = Image.open(io.BytesIO(image_data))
                image_file = os.path.basename(url)
                image.save(os.path.join(path, './GeneratedImages', image_file))
                return 'content'
            else:
                return f"Failed to retrieve URL. Status code: {response.status}"
    except Exception as e:
        return f"Error: {str(e)}"

async def download_images(images, path):
    async with aiohttp.ClientSession() as session:
        tasks = []
        for i in images:
            p = ['prompt', 'images']
            keys = dict((key, i[key]) for key in p)
            image_url = keys['images'][0]['uri']
            task = fetch_image(session, image_url, path)
            tasks.append(task)
        print("Just inside the second try catch declaration")
        results = await asyncio.gather(*tasks)
        return results
"""



"""    async def fetch_and_save_image(session, image_url, path, image_file):
        async with session.get(image_url) as response:
            if response.status == 200:
                img_data = await response.read()
                with open(os.path.join(path, './GeneratedImages', image_file), 'wb') as img_file:
                    img_file.write(img_data)
                return 'content'
            else:
                return f"Failed to retrieve URL. Status code: {response.status}"

    async def load_url(uri, images, path):
        links = [image['uri'] for image in images]
        
        async with aiohttp.ClientSession() as session:
            tasks = []
            for link in links:
                tasks.append(fetch_and_save_image(session, link, path, image_file))
            
            results = await asyncio.gather(*tasks)
        
        return results


"""

    
""" async def load_url(uri):
            links = []
            for i in images:
                p = ['prompt', 'images']
                keys = dict((key, i[key]) for key in p)
                image_url = keys['images'][0]['uri']
                links.append(image_url)
            for x in links:
                response = requests.get(x, stream=True)
                if response.status_code == 200:
                    img = Image.open((response).raw)
                    img.save(os.path.join(path,'./GeneratedImages', image_file))
                    return 'content'
                else:
                    return f"Failed to retrieve URL. Status code: {response.status_code}"
            else:
                return "URL key not found in the dictionary."
"""







if __name__ == '__main__':
    app.run(debug=True, host='localhost')
    #loop = asyncio.get_event_loop()
    #results = loop.run_until_complete(download_images(images, path))
    

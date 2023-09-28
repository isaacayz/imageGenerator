from flask import Flask, request, render_template
from pprint import pprint
from leap import Leap, ApiException
import asyncio
import json
import os
import requests
from PIL import Image
import constants
from datetime import datetime

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
    try:
        # List All Image Jobs
        list_all_response = leap.images.list_all(
            model_id=model_id,  # required
            only_finished=True,  # optional
            page=1,  # optional
            page_size=5,  # optional
        )
        image = dict(list_all_response.body[0]['images'][0])
        
        def load_url(uri):
            #to_dict = dict(image['images'])
            if 'uri' in image:
                url = image[uri]
                response = requests.get(url, stream=True)
                if response.status_code == 200:
                    # If the request is successful (status code 200), you can access the content
                    img = Image.open((response).raw)
                    img.save(os.path.join(path,'./GeneratedImages', image_file))
                    #fp = open('test_image.png', 'wb')
                    #fp.write(response.content)
                    #content = 
                    return 'content'
                else:
                    return f"Failed to retrieve URL. Status code: {response.status_code}"
            else:
                return "URL key not found in the dictionary."
        #print(type(image['images'][0]))

    except ApiException as e:
        print("Exception when calling ImagesApi.list_all: %s\n" % e)
        pprint(e.body)

    
    return load_url('uri') #render_template('listImages.html', image=image)






if __name__ == '__main__':
    app.run(debug=True, host='localhost')

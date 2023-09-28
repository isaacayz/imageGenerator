from flask import Flask, request, render_template
from pprint import pprint
from leap import Leap, ApiException
import asyncio
from flask_bootstrap import Bootstrap
import constants

app = Flask(__name__)

leap = Leap(
    access_token=constants.key
)

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
                model_id="26a1a203-3a46-42cb-8cfa-f4de075907d8",  # required
                negative_prompt=request.form.get("floating_negative_prompt"),  # optional
                steps=int(request.form.get('floating_steps')),  # optional
                width=int(request.form.get('floating_width')),  # optional
                height=int(request.form.get('floating_height')),  # optional
                number_of_images=int(request.form.get('floating_number_of_images')),  # optional
                prompt_strength=7,  # optional
                seed=4523184,  # optional
            )
            pprint(generate_response.body)
            return render_template('generateImage.html', image=generate_response.status)
        else:
            print(request.method)
    except ApiException as e:
        print("Exception when calling ImagesApi.generate: %s\n" % e)
        pprint(e.body)


@app.route('/listImages')
def listImages():
    return render_template('listImages.html')


if __name__ == '__main__':
    app.run(debug=True, host='localhost')

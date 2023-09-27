from flask import Flask, request, render_template
from pprint import pprint
from leap import Leap, ApiException
import asyncio
from flask_bootstrap import Bootstrap
import constants

app = Flask(__name__)
Bootstrap(app)

leap = Leap(
    access_token=constants.key
)


@app.route('/')
async def index():
    try:
        # Generate an Image
        generate_response = await leap.images.generate(
            prompt="A cat drinking hot coffee",  # required
            model_id="26a1a203-3a46-42cb-8cfa-f4de075907d8",  # required
            negative_prompt="asymmetric, bad hands, bad hair",  # optional
            steps=50,  # optional
            width=1024,  # optional
            height=1024,  # optional
            number_of_images=1,  # optional
            prompt_strength=7,  # optional
            seed=4523184,  # optional
            #webhook_url="string_example",  # optional
        )
        pprint(generate_response.body)
    except ApiException as e:
        print("Exception when calling ImagesApi.generate: %s\n" % e)
        pprint(e.body)
        pprint(e.headers)
        pprint(e.status)
        pprint(e.reason)
        pprint(e.round_trip_time)



if __name__ == '__main__':
    app.run(host='localhost')

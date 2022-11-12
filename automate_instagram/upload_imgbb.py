import requests
import json


def upload2imgbb(url, imgbb_cred, output_image_path):

    with open(imgbb_cred, "r") as reader:
        params = json.load(reader)
    files = {
        'image': open(output_image_path, 'rb'),
    }

    response = requests.post(url=url, params=params, files=files)
    uploaded_url = response.json()["data"]["url"]
    return uploaded_url

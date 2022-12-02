import requests
import pandas as pd
import os
import json
from datetime import datetime

## Get authantication  ## Parts of the code has been taken from https://towardsdatascience.com/how-to-use-the-reddit-api-in-python-5e05ddfd1e5c
def get_auth(auth_dict_loc, header_file_loc):
    with open(auth_dict_loc, 'r') as reader:
        auth_val = json.load(reader)

    CLIENT_ID = auth_val["CLIENT_ID"]
    SECRET_KEY = auth_val["SECRET_KEY"]
    username = auth_val["username"]
    pwd = auth_val["password"]
    user_agent = auth_val["user_agent"]

    # note that CLIENT_ID refers to 'personal use script' and SECRET_TOKEN to 'token'
    auth = requests.auth.HTTPBasicAuth(CLIENT_ID, SECRET_KEY)

    # here we pass our login method (password), username, and password
    data = {'grant_type': 'password',
            'username': username,
            'password': pwd}

    # setup our header info, which gives reddit a brief description of our app
    headers = {'User-Agent': user_agent}

    # send our request for an OAuth token
    res = requests.post('https://www.reddit.com/api/v1/access_token',
                    auth=auth, data=data, headers=headers)

    if not res.status_code==200:
        return "check username and password"

    # convert response to JSON and pull access_token value
    TOKEN = res.json()['access_token']

    # add authorization to our headers dictionary
    headers["Authorization"] = f"bearer {TOKEN}"

    # while the token is valid (~2 hours) we just add headers=headers to our requests
    auth_status = requests.get('https://oauth.reddit.com/api/v1/me', headers=headers)
    if not auth_status.status_code==200:
        return "Token not generated"

    with open(header_file_loc, "w") as writer:
        json.dump(headers, writer, ensure_ascii=False)

    return "Successfully Created header"


def get_stories(header_file_loc, subreddit, output_filename, top_n, filter_type, filter_by, after_loc):
    with open(header_file_loc, 'r') as reader:
        headers = json.load(reader)

    params={"limit":top_n, "t":filter_by}

    if os.path.exists(after_loc):
        with open(after_loc, "r") as reader:
            params["after"] = reader.readline().split("\n")[0]
    res = requests.get(f"https://oauth.reddit.com/r/{subreddit}/{filter_type}",
            headers=headers, params=params)
    return res

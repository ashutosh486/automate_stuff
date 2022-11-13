
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
    if os.path.exists(output_filename):
        df = pd.read_excel(output_filename)
        old_count = len(df)
    else:
        df = pd.DataFrame()

    for story in res.json()["data"]["children"]:
        df = df.append({
                'subreddit': story['data']['subreddit'],
                'author':story['data']['author'],
                'title': story['data']['title'],
                'selftext': story['data']['selftext'],
                'upvote_ratio': story['data']['upvote_ratio'],
                'ups': story['data']['ups'],
                'created_utc': story['data']['created_utc'],
        }, ignore_index=True)
    if len(res.json()["data"]["children"])>0:
        fullname = story['kind'] + '_' + story['data']['id']
        with open(after_loc, "w") as writer:
            writer.write(fullname+"\n"+datetime.fromtimestamp(story['data']['created_utc']).strftime('%Y-%m-%dT%H:%M:%SZ'))
    df.drop_duplicates(subset=["title", "selftext"], inplace=True, keep='last')
    df = df.sort_values(by=['ups'], ascending=False)
    df = df[df["ups"]>20]
    new_count = len(df)
    print("New Items Added {} for {} by {}".format(new_count-old_count, filter_type, filter_by))
    df.to_excel(output_filename, index=False)
    return new_count-old_count
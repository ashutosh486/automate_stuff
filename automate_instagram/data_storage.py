import pandas as pd
import os
import json
from datetime import datetime

def store_data(res, output_filename, after_loc, filter_type, filter_by):
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


import pandas as pd
import os
import random
import json
from upload_imgbb import upload2imgbb
from create_post import create_post
from reddit_api import get_auth, get_stories
from post_on_insta import upload2instagram 
import re

def main(cfg):
    
    reddit_auth_file = cfg["reddit_auth_file"]
    reddit_headers = cfg["reddit_headers"]
    imgbb_cred = cfg["imgbb_cred"]
    cred_loc = cfg["cred_loc"]

    input_story_loc = cfg["input_story_loc"]
    posted_story_loc = cfg["posted_story_loc"]
    file_num_loc = cfg["file_num_loc"]
    output_image_path = cfg["output_image_path"]

    template_image_path =cfg["template_image_path"] 
    regular_font_path = cfg["regular_font_path"]
    url = cfg["url"]

    n_results = cfg["n_results"]


    print("Number of stories to be posted:", n_results)
    ## Get Authorisation
    auth_status = get_auth(reddit_auth_file, reddit_headers)
    print("Authentication Granted")

    ## Get top 100 stories every day
    story_status = get_stories(header_file_loc = reddit_headers, output_filename = input_story_loc, subreddit="TwoSentenceHorror",
                                top_n = 100, filter_type = "top", filter_by = "day")
    print("Status of Stories:", story_status)

    ## Select Random n_results stories from input_story_loc
    all_stories = pd.read_excel(input_story_loc)
    if os.path.exists(posted_story_loc):
        stories_posted = pd.read_excel(posted_story_loc)
        all_stories = all_stories[(~all_stories.title.isin(stories_posted.title))&(~all_stories.selftext.isin(stories_posted.selftext))]

    else:
        stories_posted = pd.DataFrame()
    print(all_stories.shape, stories_posted.shape)

    if len(all_stories[all_stories["ups"]>1500])>=n_results:
        to_be_uploaded = all_stories[all_stories["ups"]>3000].sample(n=n_results)
        stories_posted = pd.concat([stories_posted, to_be_uploaded])
        stories_posted.to_excel(posted_story_loc, index=False)


        with open(file_num_loc, 'r') as reader:
            out_file_num = int(reader.readline())

        for index, row in to_be_uploaded.iterrows():
            with open(file_num_loc, 'r') as reader:
                out_file_num = int(reader.readline())
            setup_line = row["title"].replace("*", "")
            if len(row["selftext"])>0:
                punchline = row["selftext"].replace("*", "")
            else:
                punchline=""
            setup_line = re.sub("(\[[A-Z0-9]+\])", "", setup_line, 1).strip()

            if row["author"]=="[deleted]":
                author_credit = ""
            else:
                author_credit = f'Credit: u/{row["author"]}'
                
            print(f"--------------------STORY NUMBER:{str(out_file_num)}--------------------")
            print("SETUP:", setup_line)
            print("PUNCHLINE:", punchline)
            print("AUTHOR:", author_credit)

            if "reddit" in setup_line.lower() or "reddit" in punchline.lower() or "r/" in setup_line.lower() or  "r/" in punchline.lower() :
                continue

            create_post(template_image_path, output_image_path, regular_font_path, setup_line, punchline, author_credit)

            media_url = upload2imgbb(url, imgbb_cred, output_image_path)
            upload_status = upload2instagram(cred_loc, media_url, out_file_num)
            if upload_status=="FAILED":
                stories_posted = stories_posted.drop(stories_posted[(stories_posted["title"]==row["title"]) &
                                                                    (stories_posted["selftext"]==row["selftext"])].index)
                stories_posted.to_excel(posted_story_loc, index=False)
                continue
            out_file_num+=1
            with open(file_num_loc, 'w') as writer:
                writer.write(str(out_file_num))

    else:
        print("No more stories left")

if __name__=="__main__":
    ## Read the config File
    with open("config.json", "r") as reader:
        cfg = json.load(reader)

    main(cfg)
## Credit for this code goes to : Justin Stolpe (https://github.com/jstolpe/blog_code/tree/master/instagram_graph_api/python)

import requests
import pandas as pd
import os
import json
from datetime import datetime, timezone
import random
import time

def getCreds(cred_loc):
    """ Get creds required for use in the applications

    Returns:
        dictonary: credentials needed globally
    """
    with open(cred_loc, "r") as reader:
        insta_cred = json.load(reader)
    return insta_cred

def makeApiCall( url, endpointParams, type ) :
    """ Request data from endpoint with params

    Args:
        url: string of the url endpoint to make request from
        endpointParams: dictionary keyed by the names of the url parameters
    Returns:
        object: data from the endpoint
    """

    if type == 'POST' : # post request
        data = requests.post( url, endpointParams )
    else : # get request
        data = requests.get( url, endpointParams )

    response = dict() # hold response info
    response['url'] = url # url we are hitting
    response['endpoint_params'] = endpointParams #parameters for the endpoint
    response['endpoint_params_pretty'] = json.dumps( endpointParams, indent = 4 ) # pretty print for cli
    response['json_data'] = json.loads( data.content ) # response data from the api
    response['json_data_pretty'] = json.dumps( response['json_data'], indent = 4 ) # pretty print for cli

    return response # get and return content

def createMediaObject( params ) :
	""" Create media object
	Args:
		params: dictionary of params

	API Endpoint:
		https://graph.facebook.com/v5.0/{ig-user-id}/media?image_url={image-url}&caption={caption}&access_token={access-token}
		https://graph.facebook.com/v5.0/{ig-user-id}/media?video_url={video-url}&caption={caption}&access_token={access-token}
	Returns:
		object: data from the endpoint
	"""

	url = params['endpoint_base'] + params['instagram_account_id'] + '/media' # endpoint url

	endpointParams = dict() # parameter to send to the endpoint
	endpointParams['caption'] = params['caption']  # caption for the post
	endpointParams['access_token'] = params['access_token'] # access token

	if 'IMAGE' == params['media_type'] : # posting image
		endpointParams['image_url'] = params['media_url']  # url to the asset
	else : # posting video
		endpointParams['media_type'] = params['media_type']  # specify media type
		endpointParams['video_url'] = params['media_url']  # url to the asset

	return makeApiCall( url, endpointParams, 'POST' ) # make the api call

def getMediaObjectStatus( mediaObjectId, params ) :
	""" Check the status of a media object
	Args:
		mediaObjectId: id of the media object
		params: dictionary of params

	API Endpoint:
		https://graph.facebook.com/v5.0/{ig-container-id}?fields=status_code
	Returns:
		object: data from the endpoint
	"""

	url = params['endpoint_base'] + '/' + mediaObjectId # endpoint url

	endpointParams = dict() # parameter to send to the endpoint
	endpointParams['fields'] = 'status_code' # fields to get back
	endpointParams['access_token'] = params['access_token'] # access token

	return makeApiCall( url, endpointParams, 'GET' ) # make the api call

def publishMedia( mediaObjectId, params ) :
	""" Publish content
	Args:
		mediaObjectId: id of the media object
		params: dictionary of params

	API Endpoint:
		https://graph.facebook.com/v5.0/{ig-user-id}/media_publish?creation_id={creation-id}&access_token={access-token}
	Returns:
		object: data from the endpoint
	"""

	url = params['endpoint_base'] + params['instagram_account_id'] + '/media_publish' # endpoint url

	endpointParams = dict() # parameter to send to the endpoint
	endpointParams['creation_id'] = mediaObjectId # fields to get back
	endpointParams['access_token'] = params['access_token'] # access token

	return makeApiCall( url, endpointParams, 'POST' ) # make the api call

def getContentPublishingLimit( params ) :
	""" Get the api limit for the user
	Args:
		params: dictionary of params

	API Endpoint:
		https://graph.facebook.com/v5.0/{ig-user-id}/content_publishing_limit?fields=config,quota_usage
	Returns:
		object: data from the endpoint
	"""

	url = params['endpoint_base'] + params['instagram_account_id'] + '/content_publishing_limit' # endpoint url

	endpointParams = dict() # parameter to send to the endpoint
	endpointParams['fields'] = 'config,quota_usage' # fields to get back
	endpointParams['access_token'] = params['access_token'] # access token

	return makeApiCall( url, endpointParams, 'GET' ) # make the api callz

def upload2instagram(cred_loc, media_url, post_num):
    params = getCreds(cred_loc) # get creds from defines
    params['media_type'] = 'IMAGE' # type of asset
    params['media_url'] = media_url # url on public server for the post
    params['caption'] = f'''Story No: {str(post_num)}
    Follow @2senthorror for more 2 sentence horror stories
    .
    .
    .
    .
    .
    #horror #halloween #horrormovies #art #horrorfan #scary #creepy #horrormovie #horrorart #movie #spooky #film #horrorcommunity #horrorfilm #movies #horroraddict #terror #dark #s #goth #thriller #gore #cosplay #horrorcollector #cinema #gothic #horrorjunkie #slasher #instahorror''' # Caption
    for i in range(3):
        imageMediaObjectResponse = createMediaObject( params ) # create a media object through the api
        if "error" not in imageMediaObjectResponse['json_data']:
            break

    try:
        imageMediaObjectId = imageMediaObjectResponse['json_data']['id'] # id of the media object that was created
        imageMediaStatusCode = 'IN_PROGRESS'
        print(f"IMAGE MEDIA OBJECT: ID = {imageMediaObjectId}")

        while imageMediaStatusCode != 'FINISHED' : # keep checking until the object status is finished
            imageMediaObjectStatusResponse = getMediaObjectStatus( imageMediaObjectId, params ) # check the status on the object
            imageMediaStatusCode = imageMediaObjectStatusResponse['json_data']['status_code'] # update status code

            print(f"IMAGE MEDIA OBJECT STATUS: Status Code = {imageMediaStatusCode}")
            time.sleep( 5 ) # wait 5 seconds if the media object is still being processed

        publishImageResponse = publishMedia( imageMediaObjectId, params ) # publish the post to instagram

        print(f"PUBLISHED IMAGE RESPONSE: tResponse = {publishImageResponse['json_data_pretty']}")

        contentPublishingApiLimit = getContentPublishingLimit( params ) # get the users api limit
        print(f"CONTENT PUBLISHING USER API LIMIT: Response = {contentPublishingApiLimit['json_data_pretty']}")
        return "SUCCESS"
    except :
        print("Failed to upload")
        print("STATUS RETURNED:", imageMediaObjectResponse["json_data_pretty"])
        return "FAILED"


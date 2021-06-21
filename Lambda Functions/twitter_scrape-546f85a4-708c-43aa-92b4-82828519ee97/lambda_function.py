import requests
import json
from datetime import datetime, timedelta
import boto3
from time import sleep


s3 = boto3.client("s3")
dynamodb = boto3.client("dynamodb")
#table = dynamodb.Table('tweets_raw')

TWEETS_RAW = 'tweets_table' #update here
Twitter_credentials = 'aml-twitter-creds'
TWITTER_SCRAPER_TRIGGER_BUCKET = 'aml-twitter-scraper-trigger'

def read_secret(filepath):
    resp = s3.get_object(Bucket=Twitter_credentials, Key=filepath)
    s = resp['Body'].read().decode('utf-8')
    return s

def create_url():
    daysago = str((datetime.utcnow() - timedelta(days = 7)).isoformat()+"Z")
    query = "vaccine context:123.1220701888179359745 -is:retweet lang:en"
    max_results = 'max_results=100'
    end_time = "end_time="+daysago
    tweet_fields = "tweet.fields=author_id,geo,created_at,public_metrics"
    place_fields = "place.fields=full_name,country,geo"
    url = "https://api.twitter.com/2/tweets/search/recent?query={}&{}&{}&{}&{}".format(
        query, tweet_fields, max_results, place_fields, end_time
    )
    return url

def create_headers(bearer_token):
    headers = {"Authorization": "Bearer {}".format(bearer_token)}
    return headers

def connect_to_endpoint(url, headers):
    response = requests.request("GET", url, headers=headers)
    print(response.status_code)
    if response.status_code != 200:
        raise Exception(response.status_code, response.text)
    return  response.json()

def lambda_handler(event, context):
    bearer_token = read_secret('twitter_bearer.txt')
    url = create_url()
    headers = create_headers(bearer_token)
    count = 0
    json_response = connect_to_endpoint(url, headers)
    for tweet in json_response['data']:
        id = tweet['id'],
        text = tweet['text'],
        created_at = tweet['created_at'],
        #"geo" : tweet['geo'],
        retweet_count = tweet['public_metrics']['retweet_count'],
        reply_count = tweet['public_metrics']['reply_count'],
        like_count = tweet['public_metrics']['like_count'],
        quote_count = tweet['public_metrics']['quote_count']
        # sentiment = 0
        put_response = dynamodb.put_item(
            TableName = TWEETS_RAW,
            Item = {
                "id": {
                    "N": id[0]
                },
                "text" : {
                    "S": text[0]
                },
                "created_at" : {
                    "S" : created_at[0]
                },
                "retweet_count": {
                    "N": str(retweet_count[0])
                },
                "like_count" : {
                    "N": str(like_count[0])
                },
                "reply_count": {
                    "N": str(reply_count[0])
                },
                "sentiment":{
                    "S": ''
                }
            })
        count += 1
    print(count, "tweets added to dynamodb")
    
    sleep(120)
    s3.put_object(Bucket=TWITTER_SCRAPER_TRIGGER_BUCKET, Key='trigger.txt', Body='')
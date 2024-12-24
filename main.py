import tweepy
import os
from google.cloud import storage
from dotenv import load_dotenv
import json

load_dotenv()

def twitter_data(request):
    API_KEY = os.getenv("API_KEY")
    API_SECRET_KEY = os.getenv("API_SECRET_KEY")
    ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
    ACCESS_TOKEN_SECRET = os.getenv("ACCESS_TOKEN_SECRET")

    auth = tweepy.OAuthHandler(API_KEY, API_SECRET_KEY)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
    api = tweepy.API(auth)

    hashtag = "#Python"
    tweets = api.search_tweets(q=hashtag, count=100, lang="pl")

    tweet_data = []
    for tweet in tweets:
        tweet_info = {
            "user": tweet.user.screen_name,
            "tweet": tweet.text,
            "date": str(tweet.created_at)
        }
        tweet_data.append(tweet_info)

    storage_client = storage.Client()
    bucket = storage_client.get_bucket("your-bucket-name")
    blob = bucket.blob("tweets_data.json")
    blob.upload_from_string(json.dumps(tweet_data))

    return "Dane zapisane"
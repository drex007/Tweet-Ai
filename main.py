import tweepy
import time
import random
import logging
import os
from datetime import datetime, timedelta
import schedule
from dotenv import load_dotenv
from openai import OpenAI
load_dotenv()

CONSUMER_API_KEY = os.getenv("CONSUMER_API_KEY")
CONSUMER_API_KEY_SECRET = os.getenv("CONSUMER_API_KEY_SECRET")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
ACCESS_TOKEN_SECRET = os.getenv("ACCESS_TOKEN_SECRET")
OPEN_AI_SECRET_KEY= os.getenv("OPEN_AI_SECRET_KEY")


open_ai_client = OpenAI(
    api_key =OPEN_AI_SECRET_KEY
)

PROMPT = """
You have a knack at generating distinct engaging crypto,web3 and recent economic news twitter threads. You are to generate a humanized thread of not more than 500 words from any of this spaces.
Ensure to use emojis where neccessary,make the tweet lively !!!!!!!!
"""

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("twitter_bot.log"),
        logging.StreamHandler()
    ]
)

class TwitterBot:
    def __init__(self, consumer_key, consumer_secret, access_token, access_token_secret):
        """Initialize the Twitter bot with API credentials."""
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initializing Twitter Bot")
        
        self.client = tweepy.Client(
            consumer_key=consumer_key, consumer_secret =consumer_secret, access_token = access_token, access_token_secret = access_token_secret
        )
        
        
    def _generate_tweet_from_ai(self, prompt):
        try:
            completion = open_ai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                        {"role": "user", "content": prompt}]
            )


            print(completion.choices[0].message.content.strip(), "completion")
            return {
                "state":1,
                "text":completion.choices[0].message.content.strip()
            }

        except Exception as e:
            print(e, "OPEN AI ERROR")
            return {"state":0,"text":""}

    def post_tweet(self):
        
        try:
            #Generate tweet from ai
            tweet = self._generate_tweet_from_ai(PROMPT)
            # Post the tweet
            if tweet.get("state") == 1:
                self.client.create_tweet(text=tweet.get("text"))
                self.logger.info(f"Posted tweet")
                return True
            
            return False
        except Exception as e:
            self.logger.error(f"Error posting tweet: {e}")
            return False

def main():
    # Create bot instance
    try:
        bot = TwitterBot(CONSUMER_API_KEY, CONSUMER_API_KEY_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
        # Schedule tweet posting every 1:30min hours
        schedule.every(90).minutes.do(bot.post_tweet)
        
        # Post one tweet immediately when starting
        bot.post_tweet()
        
        logging.info("Bot started successfully. Tweets will be posted every 1hr:30min.")
    
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
            
    except KeyboardInterrupt:
        logging.info("Bot stopped by user.")
    except Exception as e:
        logging.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
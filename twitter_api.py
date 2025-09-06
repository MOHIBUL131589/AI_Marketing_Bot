import os
import tweepy
import time
from typing import Dict, List, Optional
from datetime import datetime

class TwitterAPI:
    """
    A wrapper class for Twitter API operations using both OAuth 1.0a and OAuth 2.0.
    """
    
    def __init__(self, max_retries: int = 3, retry_delay: int = 5):
        """
        Initialize Twitter API client with both OAuth 1.0a and OAuth 2.0 authentication.
        
        Args:
            max_retries (int): Maximum number of retries for rate-limited requests
            retry_delay (int): Initial delay between retries in seconds (doubles with each retry)
        """
        try:
            # Get OAuth 1.0a credentials for posting
            consumer_key = os.getenv('TWITTER_API_KEY')
            consumer_secret = os.getenv('TWITTER_API_SECRET')
            access_token = os.getenv('TWITTER_ACCESS_TOKEN')
            access_token_secret = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
            
            # Get OAuth 2.0 Bearer Token for reading
            bearer_token = os.getenv('TWITTER_BEARER_TOKEN')
            
            if not all([consumer_key, consumer_secret, access_token, access_token_secret]):
                raise ValueError("Missing OAuth 1.0a credentials - required for posting tweets")
            
            if not bearer_token:
                raise ValueError("Missing Bearer Token - required for reading tweets")
            
            print("\nInitializing Twitter client...")
            
            # Initialize client with both OAuth 1.0a and OAuth 2.0
            self.client = tweepy.Client(
                consumer_key=consumer_key,
                consumer_secret=consumer_secret,
                access_token=access_token,
                access_token_secret=access_token_secret,
                bearer_token=bearer_token,
                return_type=dict,
                wait_on_rate_limit=True
            )
            
            self.max_retries = max_retries
            self.retry_delay = retry_delay
            print("✓ Twitter client initialized successfully")
            
        except Exception as e:
            print(f"\nError initializing Twitter client: {str(e)}")
            raise

    def _handle_rate_limit(self, operation: str, retry_count: int) -> bool:
        """
        Handle rate limit with exponential backoff.
        
        Args:
            operation (str): Description of the operation being performed
            retry_count (int): Current retry attempt number
            
        Returns:
            bool: True if should retry, False if max retries exceeded
        """
        if retry_count >= self.max_retries:
            print(f"\n❌ Max retries ({self.max_retries}) exceeded for {operation}")
            return False
            
        wait_time = self.retry_delay * (2 ** retry_count)
        print(f"\n⏳ Rate limit hit for {operation}. Waiting {wait_time} seconds...")
        
        # Show a waiting animation
        for i in range(wait_time):
            remaining = wait_time - i
            print(f"\rWaiting... {remaining} seconds remaining {'.' * (i % 4)}", end='', flush=True)
            time.sleep(1)
        print("\r", end='', flush=True)  # Clear the last waiting message
        
        return True

    def post_tweet(self, content: str) -> Optional[Dict]:
        """
        Post a tweet using Twitter API v2 with retry logic.
        """
        if not content or len(content) > 280:
            print(f"Invalid tweet length: {len(content)} characters")
            return None
            
        retry_count = 0
        while True:
            try:
                print(f"\nPosting tweet ({len(content)} chars)...")
                response = self.client.create_tweet(text=content)
                
                if response and 'data' in response:
                    tweet_data = response['data']
                    print(f"✓ Tweet posted successfully (ID: {tweet_data['id']})")
                    return {
                        'id': tweet_data['id'],
                        'text': content,
                        'created_at': datetime.now().isoformat()
                    }
                else:
                    print("⚠ No response data received")
                    return None
                    
            except tweepy.TooManyRequests:
                if not self._handle_rate_limit("posting tweet", retry_count):
                    return None
                retry_count += 1
                
            except Exception as e:
                print(f"\nError posting tweet: {str(e)}")
                if hasattr(e, 'response') and e.response is not None:
                    print(f"Response Status: {e.response.status_code}")
                    print(f"Response Text: {e.response.text}")
                return None

    def post_thread(self, tweets: List[str]) -> List[Dict]:
        """
        Post a thread of tweets using Twitter API v2 with retry logic.
        """
        if not tweets:
            return []
            
        thread_metadata = []
        previous_tweet_id = None

        for index, tweet in enumerate(tweets, 1):
            if len(tweet) > 280:
                print(f"Skipping tweet {index} - exceeds 280 characters: {len(tweet)}")
                continue
                
            retry_count = 0
            while True:
                try:
                    print(f"\nPosting tweet {index}/{len(tweets)}...")
                    
                    if previous_tweet_id:
                        response = self.client.create_tweet(
                            text=tweet,
                            in_reply_to_tweet_id=previous_tweet_id
                        )
                    else:
                        response = self.client.create_tweet(text=tweet)

                    if response and 'data' in response:
                        tweet_data = response['data']
                        metadata = {
                            'id': tweet_data['id'],
                            'text': tweet,
                            'created_at': datetime.now().isoformat()
                        }
                        thread_metadata.append(metadata)
                        previous_tweet_id = tweet_data['id']
                        print(f"✓ Thread tweet {index}/{len(tweets)} posted")
                        break  # Success, move to next tweet
                    
                except tweepy.TooManyRequests:
                    if not self._handle_rate_limit(f"posting tweet {index}/{len(tweets)}", retry_count):
                        return thread_metadata
                    retry_count += 1
                    
                except Exception as e:
                    print(f"Error in thread at tweet {index}: {str(e)}")
                    if hasattr(e, 'response') and e.response is not None:
                        print(f"Response Status: {e.response.status_code}")
                        print(f"Response Text: {e.response.text}")
                    return thread_metadata

        return thread_metadata

    def get_tweet_metrics(self, tweet_id: str) -> Optional[Dict]:
        """
        Get engagement metrics for a tweet using Twitter API v2 with retry logic.
        """
        retry_count = 0
        while True:
            try:
                response = self.client.get_tweet(
                    tweet_id,
                    tweet_fields=['public_metrics']
                )
                
                if response and 'data' in response:
                    metrics = response['data']['public_metrics']
                    return {
                        'likes': metrics['like_count'],
                        'retweets': metrics['retweet_count'],
                        'replies': metrics['reply_count'],
                        'quotes': metrics['quote_count'],
                        'collected_at': datetime.now().isoformat()
                    }
                return None
                
            except tweepy.TooManyRequests:
                if not self._handle_rate_limit(f"fetching metrics for tweet {tweet_id}", retry_count):
                    return None
                retry_count += 1
                
            except Exception as e:
                print(f"Error fetching metrics for tweet {tweet_id}: {str(e)}")
                if hasattr(e, 'response') and e.response is not None:
                    print(f"Response Status: {e.response.status_code}")
                    print(f"Response Text: {e.response.text}")
                return None

    def get_trending_topics(self, woeid: int = 1) -> List[str]:
        """
        Get current trending topics/hashtags with retry logic.
        Note: This still uses API v1.1 as v2 doesn't have a direct trending topics endpoint.
        
        Args:
            woeid (int): Where On Earth ID for location-based trends (default: 1 for global)
            
        Returns:
            List[str]: List of trending topics/hashtags
        """
        retry_count = 0
        while True:
            try:
                # Initialize v1.1 API for trends
                auth = tweepy.OAuthHandler(
                    os.getenv('TWITTER_API_KEY'),
                    os.getenv('TWITTER_API_SECRET')
                )
                auth.set_access_token(
                    os.getenv('TWITTER_ACCESS_TOKEN'),
                    os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
                )
                api = tweepy.API(auth)
                
                trends = api.get_place_trends(woeid)
                return [trend['name'] for trend in trends[0]['trends']]
                
            except tweepy.TooManyRequests:
                if not self._handle_rate_limit("fetching trending topics", retry_count):
                    return []
                retry_count += 1
                
            except tweepy.TweepyException as e:
                print(f"Error fetching trending topics: {str(e)}")
                return [] 
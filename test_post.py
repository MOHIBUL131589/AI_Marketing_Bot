import os
from dotenv import load_dotenv
from content_generator import ContentGenerator
from twitter_api import TwitterAPI

def verify_environment():
    """Verify all required environment variables are present."""
    required_vars = [
        'OPENAI_API_KEY',
        'TWITTER_API_KEY',
        'TWITTER_API_SECRET',
        'TWITTER_ACCESS_TOKEN',
        'TWITTER_ACCESS_TOKEN_SECRET',
        'TWITTER_BEARER_TOKEN'
    ]
    
    missing = [var for var in required_vars if not os.getenv(var)]
    
    if missing:
        print("\nMissing required environment variables:")
        for var in missing:
            print(f"❌ {var}")
        return False
        
    print("\nEnvironment variables check:")
    for var in required_vars:
        print(f"✓ {var} is set")
    return True

def test_single_post():
    """Test posting a single tweet about AI technology."""
    print("\nInitializing test...")
    
    # Load environment variables
    load_dotenv()
    
    # Verify environment
    if not verify_environment():
        print("\nTest aborted: Missing environment variables")
        return False
    
    try:
        print("\nInitializing services...")
        content_generator = ContentGenerator()
        twitter_api = TwitterAPI()
        
        print("\nGenerating tweet content...")
        content = content_generator.generate_tweet(
            "The rapid advancement of AI technology and its impact on our future",
            tone="insightful",
            include_hashtags=True
        )
        
        if not content:
            print("❌ Failed to generate tweet content")
            return False
            
        print(f"\nGenerated content [{len(content)} chars]:")
        print(f"{content}")
        
        print("\nAttempting to post tweet...")
        tweet_data = twitter_api.post_tweet(content)
        
        if tweet_data:
            print("\n✓ Tweet posted successfully!")
            print(f"Tweet ID: {tweet_data['id']}")
            return True
        else:
            print("\n❌ Failed to post tweet")
            return False
            
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_single_post()
    print("\nTest completed:", "✓ Success" if success else "❌ Failed") 
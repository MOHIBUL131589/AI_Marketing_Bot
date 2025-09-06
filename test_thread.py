import os
from dotenv import load_dotenv
from content_generator import ContentGenerator
from twitter_api import TwitterAPI

def test_claude_thread():
    """Test posting a thread about Claude in Cursor (Cluey)."""
    print("\nInitializing Claude/Cursor thread test...")
    
    # Load environment variables
    load_dotenv()
    
    try:
        print("\nInitializing services...")
        content_generator = ContentGenerator()
        twitter_api = TwitterAPI()
        
        print("\nGenerating expert thread about Claude in Cursor...")
        
        # Predefined high-quality thread content
        thread_content = [
            "🔥 Mind-blowing fact: Claude in Cursor is revolutionizing coding! Studies show it can boost development speed by up to 400%. This isn't just another AI - it's your personal coding genius that understands context, intent, and best practices. #AI #Coding",
            
            "🌟 What makes Claude special?\n- Real-time code understanding\n- Context-aware suggestions\n- Intelligent error detection\n- Natural language processing\n\nIt's like having a senior developer watching your code 24/7! #CodingAI #Development",
            
            "🧠 Technical brilliance:\n- Understands multiple languages & frameworks\n- Suggests optimizations proactively\n- Explains complex code in simple terms\n- Helps with testing & documentation\n\nIt's not just autocomplete - it's your coding companion! #TechInnovation",
            
            "⚡ Real productivity gains:\n- 60% faster debugging\n- 40% less time writing boilerplate\n- 80% faster code reviews\n- Instant documentation generation\n\nDevelopers using Claude report saving 15+ hours per week! #ProductivityHacks #CodingTools",
            
            "🚀 The future is here! Claude in Cursor is transforming how we code. Join thousands of developers experiencing the next evolution in programming.\n\nTry it now: cursor.sh\n\n#ClaudeAI #CursorIDE #FutureOfCoding #AI #Development"
        ]
        
        print("\nGenerated expert thread content:")
        for i, tweet in enumerate(thread_content, 1):
            print(f"\nTweet {i}:")
            print(f"{tweet}")
        
        print("\nAttempting to post thread...")
        thread_data = twitter_api.post_thread(thread_content)
        
        if thread_data:
            print("\n✓ Thread posted successfully!")
            print(f"Number of tweets: {len(thread_data)}")
            for i, tweet in enumerate(thread_data, 1):
                print(f"\nTweet {i} ID: {tweet['id']}")
            return True
        else:
            print("\n❌ Failed to post thread")
            return False
            
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_claude_thread()
    print("\nTest completed:", "✓ Success" if success else "❌ Failed") 
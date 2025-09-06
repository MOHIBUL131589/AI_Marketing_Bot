import os
from dotenv import load_dotenv
from scheduler import MarketingScheduler
import signal
import sys

def signal_handler(sig, frame):
    """Handle graceful shutdown on CTRL+C"""
    print('\nShutting down gracefully...')
    sys.exit(0)

def main():
    # Load environment variables
    load_dotenv()
    
    # Verify required environment variables
    required_vars = [
        'OPENAI_API_KEY',
        'TWITTER_API_KEY',
        'TWITTER_API_SECRET',
        'TWITTER_ACCESS_TOKEN',
        'TWITTER_ACCESS_TOKEN_SECRET',
        'TWITTER_BEARER_TOKEN'
    ]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        print("Error: Missing required environment variables:")
        for var in missing_vars:
            print(f"- {var}")
        sys.exit(1)
    
    # Create data directory if it doesn't exist
    os.makedirs('data', exist_ok=True)
    
    # Initialize and run the scheduler
    scheduler = MarketingScheduler()
    
    # Register signal handler for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        scheduler.run()
        print("AI Marketing Bot is running. Press CTRL+C to exit.")
        
        # Keep the main thread alive
        while True:
            signal.pause()
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 
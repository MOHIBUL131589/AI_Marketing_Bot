import os
import schedule
import time
from datetime import datetime
from typing import Dict, List, Optional
import threading

from content_generator import ContentGenerator
from twitter_api import TwitterAPI
from engagement_tracker import EngagementTracker

class MarketingScheduler:
    def __init__(self):
        """Initialize the marketing scheduler with necessary components."""
        self.content_generator = ContentGenerator()
        self.twitter_api = TwitterAPI()
        self.engagement_tracker = EngagementTracker()
        
        # Parse posting times from environment variable
        self.posting_times = os.getenv('POSTING_TIMES', '09:00,15:00').split(',')
        
        # Define AI focus areas by category for more organized content rotation
        self.ai_focus_areas = {
            "AI Development": [
                "How GPT-4 is revolutionizing code generation and pair programming",
                "The rise of AI-powered IDEs and developer productivity tools",
                "Automated code review and quality assurance with AI",
                "AI-driven debugging and error prediction systems",
                "Neural architecture search and AutoML in development"
            ],
            "Enterprise AI": [
                "AI-powered microservices and API design patterns",
                "Scalable MLOps practices for enterprise applications",
                "AI in legacy system modernization and migration",
                "Real-time AI processing in enterprise systems",
                "AI governance and compliance in enterprise software"
            ],
            "AI Security": [
                "AI-powered threat detection and response systems",
                "LLM security vulnerabilities and mitigation strategies",
                "Privacy-preserving AI development techniques",
                "AI in code security analysis and vulnerability detection",
                "Zero-trust architecture with AI components"
            ],
            "AI Innovation": [
                "Multimodal AI models in software development",
                "AI agents and autonomous system design",
                "Quantum computing integration with AI systems",
                "Edge AI deployment strategies and patterns",
                "AI-driven requirements analysis and specification"
            ],
            "AI Ethics & Future": [
                "Responsible AI development practices and guidelines",
                "AI bias detection and mitigation in development",
                "The future of human-AI collaboration in coding",
                "Sustainable and green AI development practices",
                "AI transparency and explainability in systems"
            ]
        }
        
        # Initialize category rotation
        self.categories = list(self.ai_focus_areas.keys())
        self.current_category_index = 0
        self.topic_indices = {category: 0 for category in self.categories}

    def get_next_focus_area(self) -> str:
        """Get the next focus area using category rotation."""
        # Get current category
        current_category = self.categories[self.current_category_index]
        
        # Get next topic from current category
        topics = self.ai_focus_areas[current_category]
        current_topic_index = self.topic_indices[current_category]
        focus_area = topics[current_topic_index]
        
        # Update indices
        self.topic_indices[current_category] = (current_topic_index + 1) % len(topics)
        self.current_category_index = (self.current_category_index + 1) % len(self.categories)
        
        return focus_area

    def schedule_daily_posts(self):
        """Schedule all daily posting jobs."""
        # Morning expert thread
        schedule.every().day.at("09:00").do(self.post_morning_expert_thread)
        
        # Afternoon expert thread
        schedule.every().day.at("15:00").do(self.post_afternoon_expert_thread)
        
        # Schedule metrics collection every 2 hours
        schedule.every(2).hours.do(self.collect_metrics)

    def post_morning_expert_thread(self):
        """Post a morning expert thread about AI technology."""
        try:
            focus_area = self.get_next_focus_area()
            print(f"\nGenerating morning expert thread about: {focus_area}")
            
            tweets = self.content_generator.generate_ai_expert_thread(focus_area)
            
            # Add category context to first tweet
            category = self.categories[(self.current_category_index - 1) % len(self.categories)]
            tweets[0] = f"🎯 {category} Insights:\n{tweets[0]}"
            
            thread_data = self.twitter_api.post_thread(tweets)
            
            if thread_data:
                for tweet_data in thread_data:
                    self.engagement_tracker.store_tweet(tweet_data, f"expert_thread_morning_{category.lower()}")
                print(f"Posted morning expert thread ({category}) with {len(thread_data)} tweets")
                
        except Exception as e:
            print(f"Error in morning expert thread: {str(e)}")

    def post_afternoon_expert_thread(self):
        """Post an afternoon expert thread about AI technology."""
        try:
            focus_area = self.get_next_focus_area()
            print(f"\nGenerating afternoon expert thread about: {focus_area}")
            
            tweets = self.content_generator.generate_ai_expert_thread(focus_area)
            
            # Add category context to first tweet
            category = self.categories[(self.current_category_index - 1) % len(self.categories)]
            tweets[0] = f"💡 {category} Deep Dive:\n{tweets[0]}"
            
            thread_data = self.twitter_api.post_thread(tweets)
            
            if thread_data:
                for tweet_data in thread_data:
                    self.engagement_tracker.store_tweet(tweet_data, f"expert_thread_afternoon_{category.lower()}")
                print(f"Posted afternoon expert thread ({category}) with {len(thread_data)} tweets")
                
        except Exception as e:
            print(f"Error in afternoon expert thread: {str(e)}")

    def collect_metrics(self):
        """Collect and store engagement metrics for recent tweets."""
        try:
            # Get recent tweets from database
            recent_tweets = self.engagement_tracker.get_best_performing_tweets(limit=50)
            
            for tweet in recent_tweets:
                metrics = self.twitter_api.get_tweet_metrics(tweet['id'])
                if metrics:
                    self.engagement_tracker.store_metrics(tweet['id'], metrics)
            
            print(f"Collected metrics for {len(recent_tweets)} tweets")
        except Exception as e:
            print(f"Error collecting metrics: {str(e)}")

    def run(self):
        """Run the scheduler in a separate thread."""
        self.schedule_daily_posts()
        
        def run_scheduler():
            while True:
                schedule.run_pending()
                time.sleep(60)
        
        scheduler_thread = threading.Thread(target=run_scheduler)
        scheduler_thread.daemon = True
        scheduler_thread.start()
        
        print("Marketing scheduler is running...")
        
        # Keep the main thread alive
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nShutting down gracefully...") 
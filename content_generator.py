import os
from openai import OpenAI
from typing import Dict, List, Optional

class ContentGenerator:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

    def generate_tweet(self, prompt: str, tone: str = "professional", include_hashtags: bool = True) -> str:
        """
        Generate a tweet using OpenAI's GPT model.
        
        Args:
            prompt (str): The main topic or product to tweet about
            tone (str): The desired tone of the tweet
            include_hashtags (bool): Whether to include relevant hashtags
        
        Returns:
            str: The generated tweet
        """
        system_prompt = f"""You are a social media marketing expert. Create an engaging tweet that is:
        - Attention-grabbing and memorable
        - Written in a {tone} tone
        - Under 280 characters
        - Natural and authentic sounding
        {"- Include 2-3 relevant hashtags at the end" if include_hashtags else ""}
        """

        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Create a tweet about: {prompt}"}
            ],
            max_tokens=150,
            temperature=0.7
        )
        
        return response.choices[0].message.content.strip()

    def generate_value_thread(self, topic: str, num_tweets: int = 5) -> List[str]:
        """
        Generate a thread of valuable tips or insights.
        
        Args:
            topic (str): The main topic for the thread
            num_tweets (int): Number of tweets in the thread
        
        Returns:
            List[str]: List of tweets forming a thread
        """
        system_prompt = f"""Create a thread of {num_tweets} tweets about {topic}. Each tweet should:
        - Provide valuable, actionable insights
        - Be engaging and informative
        - Be under 280 characters
        - Flow naturally from one tweet to the next
        """

        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Create a thread about: {topic}"}
            ],
            max_tokens=500,
            temperature=0.7
        )

        # Split the response into individual tweets
        tweets = [tweet.strip() for tweet in response.choices[0].message.content.split('\n') if tweet.strip()]
        return tweets

    def generate_trending_response(self, trend: str, product_context: str) -> str:
        """
        Generate a response to a trending topic that naturally incorporates product promotion.
        
        Args:
            trend (str): The trending topic or hashtag
            product_context (str): Information about the product to promote
        
        Returns:
            str: A contextual tweet relating the trend to the product
        """
        system_prompt = """Create a tweet that naturally connects a trending topic with our product/service.
        The connection should feel organic and not forced. The tweet should be engaging and under 280 characters."""

        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Trending topic: {trend}\nProduct context: {product_context}"}
            ],
            max_tokens=150,
            temperature=0.7
        )

        return response.choices[0].message.content.strip()

    def generate_ai_expert_thread(self, focus_area: str) -> List[str]:
        """
        Generate an expert-level thread about AI technology with deep insights.
        
        Args:
            focus_area (str): Specific area of AI to focus on (e.g., 'LLMs', 'Computer Vision', etc.)
        
        Returns:
            List[str]: List of tweets forming a high-quality thread
        """
        system_prompt = f"""You are a leading AI researcher and industry expert. Create a thread of 5 tweets about {focus_area} that follows this specific structure:

        Tweet 1 (Hook): 
        - Start with a powerful statistic, surprising fact, or thought-provoking question
        - Create immediate interest in the topic
        - Use 🔥 or 💡 to grab attention

        Tweet 2 (Context & Problem):
        - Explain why this topic matters NOW
        - Highlight current challenges or pain points
        - Include specific industry examples
        - Use 🎯 or 🌟 for key points

        Tweet 3 (Technical Insight):
        - Share deep technical knowledge that's not commonly known
        - Include specific implementation details or architectural insights
        - Cite recent research or developments
        - Use 🔧 or 🧠 for technical concepts

        Tweet 4 (Practical Application):
        - Provide 2-3 actionable takeaways
        - Include code examples or specific tools when relevant
        - Focus on immediate implementation
        - Use ⚡ or 💻 for practical tips

        Tweet 5 (Future Impact & CTA):
        - Predict future developments
        - Include a clear call-to-action
        - Add 3-4 relevant hashtags
        - Use 🚀 or 🔮 for future predictions

        Requirements for ALL tweets:
        1. Each must be under 280 characters
        2. Use data points and specific examples
        3. Maintain a balance between technical depth and accessibility
        4. Include relevant links to tools/research when applicable
        5. Use consistent narrative threading
        """

        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Create an expert thread about {focus_area} in AI technology"}
            ],
            max_tokens=1000,
            temperature=0.8  # Slightly increased for more creative variations
        )

        # Split and clean the tweets
        tweets = [tweet.strip() for tweet in response.choices[0].message.content.split('\n') if tweet.strip()]
        return tweets 
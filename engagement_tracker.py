import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Optional

class EngagementTracker:
    def __init__(self, db_path: str = "data/engagement.db"):
        """
        Initialize the engagement tracker with a SQLite database.
        
        Args:
            db_path (str): Path to the SQLite database file
        """
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Initialize the database with required tables."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Create tweets table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS tweets (
            id TEXT PRIMARY KEY,
            content TEXT NOT NULL,
            type TEXT NOT NULL,
            created_at TEXT NOT NULL,
            metadata TEXT
        )
        """)

        # Create engagement metrics table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS engagement_metrics (
            tweet_id TEXT,
            likes INTEGER,
            retweets INTEGER,
            replies INTEGER,
            impressions INTEGER,
            collected_at TEXT NOT NULL,
            FOREIGN KEY (tweet_id) REFERENCES tweets(id)
        )
        """)

        conn.commit()
        conn.close()

    def store_tweet(self, tweet_data: Dict, tweet_type: str = "regular"):
        """
        Store a new tweet in the database.
        
        Args:
            tweet_data (Dict): Tweet metadata including id, content, and creation time
            tweet_type (str): Type of tweet (regular, thread, response, etc.)
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO tweets (id, content, type, created_at, metadata)
        VALUES (?, ?, ?, ?, ?)
        """, (
            tweet_data['id'],
            tweet_data['text'],
            tweet_type,
            tweet_data['created_at'],
            json.dumps(tweet_data)
        ))

        conn.commit()
        conn.close()

    def store_metrics(self, tweet_id: str, metrics: Dict):
        """
        Store engagement metrics for a tweet.
        
        Args:
            tweet_id (str): The ID of the tweet
            metrics (Dict): Engagement metrics data
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO engagement_metrics 
        (tweet_id, likes, retweets, replies, impressions, collected_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (
            tweet_id,
            metrics['likes'],
            metrics['retweets'],
            metrics['replies'],
            metrics['impressions'],
            metrics['collected_at']
        ))

        conn.commit()
        conn.close()

    def get_best_performing_tweets(self, limit: int = 5) -> List[Dict]:
        """
        Get the best performing tweets based on engagement metrics.
        
        Args:
            limit (int): Number of tweets to return
            
        Returns:
            List[Dict]: List of tweet data with their metrics
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
        SELECT 
            t.id,
            t.content,
            t.type,
            t.created_at,
            MAX(m.likes) as likes,
            MAX(m.retweets) as retweets,
            MAX(m.replies) as replies,
            MAX(m.impressions) as impressions
        FROM tweets t
        JOIN engagement_metrics m ON t.id = m.tweet_id
        GROUP BY t.id
        ORDER BY (likes + retweets * 2 + replies * 3) DESC
        LIMIT ?
        """, (limit,))

        results = cursor.fetchall()
        conn.close()

        return [{
            'id': row[0],
            'content': row[1],
            'type': row[2],
            'created_at': row[3],
            'metrics': {
                'likes': row[4],
                'retweets': row[5],
                'replies': row[6],
                'impressions': row[7]
            }
        } for row in results]

    def get_performance_stats(self, days: int = 30) -> Dict:
        """
        Get performance statistics for a specific time period.
        
        Args:
            days (int): Number of days to analyze
            
        Returns:
            Dict: Performance statistics
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
        SELECT 
            t.type,
            AVG(m.likes) as avg_likes,
            AVG(m.retweets) as avg_retweets,
            AVG(m.replies) as avg_replies,
            AVG(m.impressions) as avg_impressions,
            COUNT(*) as total_posts
        FROM tweets t
        JOIN engagement_metrics m ON t.id = m.tweet_id
        WHERE datetime(t.created_at) >= datetime('now', ?)
        GROUP BY t.type
        """, (f'-{days} days',))

        results = cursor.fetchall()
        conn.close()

        return {row[0]: {
            'avg_likes': row[1],
            'avg_retweets': row[2],
            'avg_replies': row[3],
            'avg_impressions': row[4],
            'total_posts': row[5]
        } for row in results} 
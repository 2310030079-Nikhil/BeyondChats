#!/usr/bin/env python3
"""
Reddit Persona Generator

A Python script that analyzes Reddit users' posts and comments to generate
detailed personality profiles using AI language models.

Usage:
    python persona_generator.py <reddit_profile_url>

Example:
    python persona_generator.py https://www.reddit.com/user/kojied/
"""

import sys
import os
import json
import re
import argparse
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

try:
    import praw
    PRAW_AVAILABLE = True
except ImportError:
    PRAW_AVAILABLE = False
    logger.warning("PRAW not available. Install with: pip install praw")

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning("OpenAI not available. Install with: pip install openai")

try:
    from dotenv import load_dotenv
    load_dotenv()
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False
    logger.warning("python-dotenv not available. Install with: pip install python-dotenv")

from utils import clean_text, extract_username_from_url, create_output_directory


class RedditScraper:
    """Handles Reddit data scraping using PRAW."""
    
    def __init__(self):
        """Initialize Reddit API client."""
        if not PRAW_AVAILABLE:
            raise ImportError("PRAW is required for Reddit scraping. Install with: pip install praw")
        
        # Get credentials from environment variables
        client_id = os.getenv('REDDIT_CLIENT_ID')
        client_secret = os.getenv('REDDIT_CLIENT_SECRET')
        user_agent = os.getenv('REDDIT_USER_AGENT', 'PersonaGenerator/1.0')
        
        if not client_id or not client_secret:
            raise ValueError(
                "Reddit API credentials not found. Please set REDDIT_CLIENT_ID and "
                "REDDIT_CLIENT_SECRET in your .env file or environment variables."
            )
        
        self.reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent
        )
        
        logger.info("Reddit API client initialized successfully")
    
    def scrape_user_data(self, username: str, post_limit: int = 10, comment_limit: int = 10) -> Dict:
        """
        Scrape user's posts and comments from Reddit.
        
        Args:
            username: Reddit username (without u/ prefix)
            post_limit: Maximum number of posts to fetch
            comment_limit: Maximum number of comments to fetch
            
        Returns:
            Dictionary containing user data
        """
        try:
            user = self.reddit.redditor(username)
            
            # Check if user exists
            try:
                user.id  # This will raise an exception if user doesn't exist
            except Exception:
                raise ValueError(f"Reddit user '{username}' not found or account is suspended")
            
            logger.info(f"Scraping data for user: {username}")
            
            # Fetch posts
            posts = []
            try:
                for submission in user.submissions.new(limit=post_limit):
                    posts.append({
                        'id': submission.id,
                        'title': submission.title,
                        'selftext': submission.selftext,
                        'subreddit': str(submission.subreddit),
                        'score': submission.score,
                        'created_utc': submission.created_utc,
                        'url': submission.url,
                        'num_comments': submission.num_comments
                    })
            except Exception as e:
                logger.warning(f"Error fetching posts: {e}")
            
            # Fetch comments
            comments = []
            try:
                for comment in user.comments.new(limit=comment_limit):
                    comments.append({
                        'id': comment.id,
                        'body': comment.body,
                        'subreddit': str(comment.subreddit),
                        'score': comment.score,
                        'created_utc': comment.created_utc,
                        'parent_id': comment.parent_id
                    })
            except Exception as e:
                logger.warning(f"Error fetching comments: {e}")
            
            logger.info(f"Successfully scraped {len(posts)} posts and {len(comments)} comments")
            
            return {
                'username': username,
                'posts': posts,
                'comments': comments,
                'total_posts': len(posts),
                'total_comments': len(comments),
                'scraped_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error scraping user data: {e}")
            raise


class PersonaGenerator:
    """Generates user personas using AI language models."""
    
    def __init__(self):
        """Initialize the persona generator."""
        self.openai_available = OPENAI_AVAILABLE
        
        if self.openai_available:
            api_key = os.getenv('OPENAI_API_KEY')
            if api_key:
                openai.api_key = api_key
                logger.info("OpenAI API initialized")
            else:
                logger.warning("OpenAI API key not found. Using mock generation.")
                self.openai_available = False
    
    def generate_persona_with_ai(self, user_data: Dict) -> str:
        """
        Generate persona using OpenAI GPT-4.
        
        Args:
            user_data: Dictionary containing scraped Reddit data
            
        Returns:
            Generated persona as string
        """
        if not self.openai_available:
            return self._generate_mock_persona(user_data)
        
        try:
            # Prepare content for analysis
            content_summary = self._prepare_content_for_analysis(user_data)
            
            prompt = f"""
            Analyze the following Reddit user data and create a comprehensive persona profile:

            {content_summary}

            Please generate a detailed persona that includes:

            1. **Name/Handle**: {user_data['username']}
            2. **Demographics**: Inferred age range, gender (if determinable), location hints
            3. **Interests**: Primary topics and hobbies based on subreddit activity
            4. **Communication Style**: Tone, formality, humor, etc.
            5. **Top Subreddits**: Most active communities
            6. **Posting Behavior**: Frequency, engagement patterns, preferred content types
            7. **Standout Traits**: Unique characteristics or notable patterns

            For each trait or characteristic, cite specific posts or comments that support your inference.
            Use the format: [Evidence: Post/Comment ID - "excerpt"]

            Make the analysis insightful but respectful, focusing on public behavior patterns.
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert in digital psychology and social media analysis. Provide thoughtful, evidence-based personality insights while being respectful and ethical."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000,
                temperature=0.7
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error generating AI persona: {e}")
            return self._generate_mock_persona(user_data)
    
    def _prepare_content_for_analysis(self, user_data: Dict) -> str:
        """Prepare user content for AI analysis."""
        content = f"Reddit User: {user_data['username']}\n"
        content += f"Total Posts: {user_data['total_posts']}\n"
        content += f"Total Comments: {user_data['total_comments']}\n\n"
        
        # Add recent posts
        content += "RECENT POSTS:\n"
        for i, post in enumerate(user_data['posts'][:5], 1):
            content += f"{i}. [r/{post['subreddit']}] {post['title']}\n"
            if post['selftext']:
                content += f"   Content: {clean_text(post['selftext'])[:200]}...\n"
            content += f"   Score: {post['score']}, Comments: {post['num_comments']}\n\n"
        
        # Add recent comments
        content += "RECENT COMMENTS:\n"
        for i, comment in enumerate(user_data['comments'][:5], 1):
            content += f"{i}. [r/{comment['subreddit']}] {clean_text(comment['body'])[:200]}...\n"
            content += f"   Score: {comment['score']}\n\n"
        
        return content
    
    def _generate_mock_persona(self, user_data: Dict) -> str:
        """Generate a mock persona when AI is not available."""
        username = user_data['username']
        posts = user_data['posts']
        comments = user_data['comments']
        
        # Analyze subreddits
        subreddit_counts = {}
        for post in posts:
            subreddit_counts[post['subreddit']] = subreddit_counts.get(post['subreddit'], 0) + 1
        for comment in comments:
            subreddit_counts[comment['subreddit']] = subreddit_counts.get(comment['subreddit'], 0) + 1
        
        top_subreddits = sorted(subreddit_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # Calculate average scores
        post_scores = [p['score'] for p in posts if p['score'] > 0]
        comment_scores = [c['score'] for c in comments if c['score'] > 0]
        avg_post_score = sum(post_scores) / len(post_scores) if post_scores else 0
        avg_comment_score = sum(comment_scores) / len(comment_scores) if comment_scores else 0
        
        persona = f"""
REDDIT USER PERSONA ANALYSIS
{'=' * 50}

**Name/Handle**: u/{username}

**Demographics**: 
- Age Range: Unable to determine from available data
- Gender: Not specified
- Location: Not determinable from public posts

**Primary Interests**:
Based on subreddit activity, this user shows interest in:
"""
        
        for subreddit, count in top_subreddits:
            persona += f"- r/{subreddit} ({count} posts/comments)\n"
        
        persona += f"""
**Communication Style**:
- Posts {len(posts)} submissions and {len(comments)} comments in recent activity
- Average post score: {avg_post_score:.1f}
- Average comment score: {avg_comment_score:.1f}
- Engagement level: {'High' if len(posts) + len(comments) > 15 else 'Moderate' if len(posts) + len(comments) > 5 else 'Low'}

**Top Subreddits**:
"""
        
        for i, (subreddit, count) in enumerate(top_subreddits, 1):
            persona += f"{i}. r/{subreddit} - {count} interactions\n"
        
        persona += f"""
**Posting Behavior**:
- Content creation: {len(posts)} original posts
- Community engagement: {len(comments)} comments
- Preferred interaction: {'Comments' if len(comments) > len(posts) else 'Posts' if len(posts) > len(comments) else 'Balanced'}

**Standout Traits**:
"""
        
        # Analyze content for traits
        if any('help' in (p.get('title', '') + p.get('selftext', '')).lower() for p in posts):
            persona += "- Helpful nature: Shows willingness to assist others\n"
            
        if any(len(c['body']) > 500 for c in comments):
            persona += "- Detailed communicator: Writes comprehensive responses\n"
            
        if len(set(p['subreddit'] for p in posts + comments)) > 5:
            persona += "- Diverse interests: Active across multiple communities\n"
        
        persona += f"""
**Evidence Citations**:
"""
        
        # Add evidence from recent posts/comments
        if posts:
            persona += f"- Recent post in r/{posts[0]['subreddit']}: \"{posts[0]['title'][:100]}...\"\n"
        if comments:
            persona += f"- Recent comment in r/{comments[0]['subreddit']}: \"{clean_text(comments[0]['body'])[:100]}...\"\n"
        
        persona += f"""
---
Analysis generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Note: This is a basic analysis. For more detailed insights, configure OpenAI API access.
"""
        
        return persona


def save_persona_to_file(persona: str, username: str, output_dir: str = "output") -> str:
    """
    Save persona to a text file.
    
    Args:
        persona: Generated persona text
        username: Reddit username
        output_dir: Output directory
        
    Returns:
        Path to saved file
    """
    create_output_directory(output_dir)
    
    filename = f"persona_{username}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    filepath = os.path.join(output_dir, filename)
    
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(persona)
        
        logger.info(f"Persona saved to: {filepath}")
        return filepath
        
    except Exception as e:
        logger.error(f"Error saving persona to file: {e}")
        raise


def main():
    """Main function to run the persona generator."""
    parser = argparse.ArgumentParser(
        description="Generate a personality profile from Reddit user data",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python persona_generator.py https://www.reddit.com/user/kojied/
  python persona_generator.py https://www.reddit.com/u/Hungry-Move-6603/
  python persona_generator.py kojied
        """
    )
    
    parser.add_argument(
        'reddit_url',
        help='Reddit user profile URL or username'
    )
    
    parser.add_argument(
        '--posts',
        type=int,
        default=10,
        help='Number of posts to analyze (default: 10)'
    )
    
    parser.add_argument(
        '--comments',
        type=int,
        default=10,
        help='Number of comments to analyze (default: 10)'
    )
    
    parser.add_argument(
        '--output-dir',
        default='output',
        help='Output directory for persona files (default: output)'
    )
    
    args = parser.parse_args()
    
    try:
        # Extract username from URL or use as-is
        username = extract_username_from_url(args.reddit_url)
        if not username:
            logger.error("Invalid Reddit URL or username provided")
            sys.exit(1)
        
        logger.info(f"Starting persona generation for user: {username}")
        
        # Initialize scraper and generator
        if not PRAW_AVAILABLE:
            logger.error("PRAW is not available. Please install it with: pip install praw")
            sys.exit(1)
        
        scraper = RedditScraper()
        generator = PersonaGenerator()
        
        # Scrape user data
        user_data = scraper.scrape_user_data(username, args.posts, args.comments)
        
        if user_data['total_posts'] == 0 and user_data['total_comments'] == 0:
            logger.warning("No posts or comments found for this user")
            print("Warning: No public posts or comments found for analysis")
        
        # Generate persona
        logger.info("Generating persona...")
        persona = generator.generate_persona_with_ai(user_data)
        
        # Save to file
        filepath = save_persona_to_file(persona, username, args.output_dir)
        
        print(f"\n✅ Persona generation completed!")
        print(f"📁 Saved to: {filepath}")
        print(f"👤 User: u/{username}")
        print(f"📊 Analyzed: {user_data['total_posts']} posts, {user_data['total_comments']} comments")
        
        # Display preview
        print(f"\n📋 Preview:")
        print("-" * 50)
        print(persona[:500] + "..." if len(persona) > 500 else persona)
        
    except KeyboardInterrupt:
        logger.info("Process interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
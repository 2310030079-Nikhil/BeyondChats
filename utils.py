"""
Utility functions for the Reddit Persona Generator.

This module contains helper functions for text processing, URL parsing,
and file operations.
"""

import re
import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)


def clean_text(text: str) -> str:
    """
    Clean and normalize text content.
    
    Args:
        text: Raw text to clean
        
    Returns:
        Cleaned text
    """
    if not text:
        return ""
    
    # Remove Reddit markdown
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)  # Bold
    text = re.sub(r'\*(.*?)\*', r'\1', text)      # Italic
    text = re.sub(r'~~(.*?)~~', r'\1', text)      # Strikethrough
    text = re.sub(r'\^(.*?)\^', r'\1', text)      # Superscript
    
    # Remove URLs
    text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
    
    # Remove Reddit-specific formatting
    text = re.sub(r'/u/\w+', '', text)            # User mentions
    text = re.sub(r'/r/\w+', '', text)            # Subreddit mentions
    text = re.sub(r'&gt;.*?\n', '', text)         # Quotes
    
    # Clean up whitespace
    text = re.sub(r'\n+', ' ', text)              # Multiple newlines
    text = re.sub(r'\s+', ' ', text)              # Multiple spaces
    text = text.strip()
    
    return text


def extract_username_from_url(url_or_username: str) -> Optional[str]:
    """
    Extract Reddit username from URL or return username if already clean.
    
    Args:
        url_or_username: Reddit URL or username
        
    Returns:
        Clean username or None if invalid
    """
    if not url_or_username:
        return None
    
    # Remove leading/trailing whitespace
    url_or_username = url_or_username.strip()
    
    # If it's already just a username (no URL), return it
    if not url_or_username.startswith('http'):
        # Remove u/ prefix if present
        if url_or_username.startswith('u/'):
            return url_or_username[2:]
        return url_or_username
    
    # Extract from URL patterns
    patterns = [
        r'reddit\.com/u/([^/\?#]+)',
        r'reddit\.com/user/([^/\?#]+)',
        r'reddit\.com/users/([^/\?#]+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url_or_username, re.IGNORECASE)
        if match:
            return match.group(1)
    
    logger.warning(f"Could not extract username from: {url_or_username}")
    return None


def create_output_directory(directory: str) -> None:
    """
    Create output directory if it doesn't exist.
    
    Args:
        directory: Directory path to create
    """
    try:
        os.makedirs(directory, exist_ok=True)
        logger.debug(f"Output directory ready: {directory}")
    except Exception as e:
        logger.error(f"Failed to create output directory {directory}: {e}")
        raise


def validate_reddit_credentials() -> bool:
    """
    Validate that required Reddit API credentials are available.
    
    Returns:
        True if credentials are available, False otherwise
    """
    required_vars = ['REDDIT_CLIENT_ID', 'REDDIT_CLIENT_SECRET']
    
    for var in required_vars:
        if not os.getenv(var):
            logger.error(f"Missing required environment variable: {var}")
            return False
    
    return True


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format.
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Formatted size string
    """
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename by removing invalid characters.
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
    # Remove invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # Remove leading/trailing dots and spaces
    filename = filename.strip('. ')
    
    # Ensure it's not empty
    if not filename:
        filename = "unnamed"
    
    return filename


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate text to specified length with suffix.
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated
        
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def count_words(text: str) -> int:
    """
    Count words in text.
    
    Args:
        text: Text to count words in
        
    Returns:
        Word count
    """
    if not text:
        return 0
    
    # Split on whitespace and filter empty strings
    words = [word for word in text.split() if word.strip()]
    return len(words)


def extract_subreddits_from_text(text: str) -> list:
    """
    Extract subreddit mentions from text.
    
    Args:
        text: Text to search
        
    Returns:
        List of subreddit names
    """
    if not text:
        return []
    
    # Find r/subreddit patterns
    pattern = r'r/([a-zA-Z0-9_]+)'
    matches = re.findall(pattern, text, re.IGNORECASE)
    
    # Remove duplicates and return
    return list(set(matches))


def calculate_engagement_score(posts: list, comments: list) -> float:
    """
    Calculate a simple engagement score based on activity.
    
    Args:
        posts: List of posts
        comments: List of comments
        
    Returns:
        Engagement score (0-100)
    """
    if not posts and not comments:
        return 0.0
    
    # Simple scoring: posts worth more than comments
    post_score = len(posts) * 2
    comment_score = len(comments) * 1
    
    total_score = post_score + comment_score
    
    # Normalize to 0-100 scale (arbitrary max of 50 for scaling)
    max_possible = 50 * 2 + 50 * 1  # 50 posts + 50 comments
    normalized_score = min(100, (total_score / max_possible) * 100)
    
    return round(normalized_score, 1)
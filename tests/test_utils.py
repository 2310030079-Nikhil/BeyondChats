"""
Unit tests for utility functions.

Run with: python -m pytest tests/test_utils.py
"""

import pytest
import os
import tempfile
from utils import (
    clean_text,
    extract_username_from_url,
    create_output_directory,
    validate_reddit_credentials,
    format_file_size,
    sanitize_filename,
    truncate_text,
    count_words,
    extract_subreddits_from_text,
    calculate_engagement_score
)


class TestCleanText:
    """Test text cleaning functionality."""
    
    def test_clean_basic_text(self):
        """Test basic text cleaning."""
        text = "This is a simple text."
        result = clean_text(text)
        assert result == "This is a simple text."
    
    def test_clean_markdown(self):
        """Test markdown removal."""
        text = "This is **bold** and *italic* text."
        result = clean_text(text)
        assert result == "This is bold and italic text."
    
    def test_clean_urls(self):
        """Test URL removal."""
        text = "Check out https://www.example.com for more info."
        result = clean_text(text)
        assert "https://www.example.com" not in result
        assert "Check out  for more info." in result
    
    def test_clean_reddit_mentions(self):
        """Test Reddit mention removal."""
        text = "Ask /u/username about /r/subreddit"
        result = clean_text(text)
        assert "/u/username" not in result
        assert "/r/subreddit" not in result
    
    def test_clean_empty_text(self):
        """Test empty text handling."""
        assert clean_text("") == ""
        assert clean_text(None) == ""
    
    def test_clean_whitespace(self):
        """Test whitespace normalization."""
        text = "Too    many   spaces\n\nand\n\nnewlines"
        result = clean_text(text)
        assert "  " not in result
        assert "\n" not in result


class TestExtractUsername:
    """Test username extraction functionality."""
    
    def test_extract_from_user_url(self):
        """Test extraction from /user/ URL."""
        url = "https://www.reddit.com/user/testuser/"
        result = extract_username_from_url(url)
        assert result == "testuser"
    
    def test_extract_from_u_url(self):
        """Test extraction from /u/ URL."""
        url = "https://www.reddit.com/u/testuser"
        result = extract_username_from_url(url)
        assert result == "testuser"
    
    def test_extract_from_username_only(self):
        """Test handling of plain username."""
        username = "testuser"
        result = extract_username_from_url(username)
        assert result == "testuser"
    
    def test_extract_from_u_prefix(self):
        """Test handling of u/ prefixed username."""
        username = "u/testuser"
        result = extract_username_from_url(username)
        assert result == "testuser"
    
    def test_extract_invalid_url(self):
        """Test handling of invalid URL."""
        url = "https://www.example.com/invalid"
        result = extract_username_from_url(url)
        assert result is None
    
    def test_extract_empty_input(self):
        """Test handling of empty input."""
        assert extract_username_from_url("") is None
        assert extract_username_from_url(None) is None


class TestFileOperations:
    """Test file operation utilities."""
    
    def test_create_output_directory(self):
        """Test directory creation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_dir = os.path.join(temp_dir, "test_output")
            create_output_directory(test_dir)
            assert os.path.exists(test_dir)
            assert os.path.isdir(test_dir)
    
    def test_format_file_size(self):
        """Test file size formatting."""
        assert format_file_size(0) == "0 B"
        assert format_file_size(1024) == "1.0 KB"
        assert format_file_size(1024 * 1024) == "1.0 MB"
        assert format_file_size(1024 * 1024 * 1024) == "1.0 GB"
    
    def test_sanitize_filename(self):
        """Test filename sanitization."""
        assert sanitize_filename("normal_file.txt") == "normal_file.txt"
        assert sanitize_filename("file<>with|bad*chars") == "file__with_bad_chars"
        assert sanitize_filename("") == "unnamed"
        assert sanitize_filename("   ") == "unnamed"


class TestTextUtilities:
    """Test text utility functions."""
    
    def test_truncate_text(self):
        """Test text truncation."""
        text = "This is a long text that should be truncated"
        result = truncate_text(text, 20)
        assert len(result) <= 20
        assert result.endswith("...")
    
    def test_truncate_short_text(self):
        """Test truncation of short text."""
        text = "Short text"
        result = truncate_text(text, 20)
        assert result == text
    
    def test_count_words(self):
        """Test word counting."""
        assert count_words("") == 0
        assert count_words("one") == 1
        assert count_words("one two three") == 3
        assert count_words("  spaced   words  ") == 2
        assert count_words(None) == 0
    
    def test_extract_subreddits(self):
        """Test subreddit extraction."""
        text = "I love r/programming and r/python communities"
        result = extract_subreddits_from_text(text)
        assert "programming" in result
        assert "python" in result
        assert len(result) == 2
    
    def test_extract_subreddits_empty(self):
        """Test subreddit extraction from empty text."""
        assert extract_subreddits_from_text("") == []
        assert extract_subreddits_from_text("No subreddits here") == []


class TestEngagementScore:
    """Test engagement score calculation."""
    
    def test_calculate_engagement_empty(self):
        """Test engagement score with no data."""
        score = calculate_engagement_score([], [])
        assert score == 0.0
    
    def test_calculate_engagement_posts_only(self):
        """Test engagement score with posts only."""
        posts = [{"id": 1}, {"id": 2}]
        score = calculate_engagement_score(posts, [])
        assert score > 0
    
    def test_calculate_engagement_comments_only(self):
        """Test engagement score with comments only."""
        comments = [{"id": 1}, {"id": 2}]
        score = calculate_engagement_score([], comments)
        assert score > 0
    
    def test_calculate_engagement_mixed(self):
        """Test engagement score with mixed content."""
        posts = [{"id": 1}]
        comments = [{"id": 1}, {"id": 2}]
        score = calculate_engagement_score(posts, comments)
        assert 0 < score <= 100


# Mock environment for testing credentials
class TestCredentials:
    """Test credential validation."""
    
    def test_validate_credentials_missing(self, monkeypatch):
        """Test validation with missing credentials."""
        monkeypatch.delenv("REDDIT_CLIENT_ID", raising=False)
        monkeypatch.delenv("REDDIT_CLIENT_SECRET", raising=False)
        assert not validate_reddit_credentials()
    
    def test_validate_credentials_present(self, monkeypatch):
        """Test validation with present credentials."""
        monkeypatch.setenv("REDDIT_CLIENT_ID", "test_id")
        monkeypatch.setenv("REDDIT_CLIENT_SECRET", "test_secret")
        assert validate_reddit_credentials()


if __name__ == "__main__":
    pytest.main([__file__])
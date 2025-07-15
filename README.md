# Reddit Persona Generator

A Python script that analyzes Reddit users' posts and comments to generate detailed personality profiles using AI language models.

## Features

- 🔍 **Reddit Data Scraping**: Fetches user's recent posts and comments using Reddit API
- 🧠 **AI-Powered Analysis**: Uses OpenAI GPT-4 to generate detailed personality insights
- 📊 **Comprehensive Profiles**: Includes demographics, interests, communication style, and behavioral patterns
- 📝 **Evidence-Based**: Cites specific posts/comments that support each personality trait
- 💾 **File Export**: Saves personas as formatted .txt files
- 🔒 **Secure**: Uses environment variables for API credentials

## Setup Instructions

### 1. Prerequisites

- Python 3.8 or higher
- Reddit API credentials
- OpenAI API key (optional, but recommended for best results)

### 2. Installation

1. Clone or download this project
2. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

### 3. Reddit API Setup

1. Go to [Reddit Apps](https://www.reddit.com/prefs/apps)
2. Click "Create App" or "Create Another App"
3. Choose "script" as the app type
4. Fill in the required fields:
   - **Name**: Your app name (e.g., "Persona Generator")
   - **Description**: Brief description
   - **Redirect URI**: `http://localhost:8080` (required but not used)
5. Note your **Client ID** (under the app name) and **Client Secret**

### 4. OpenAI API Setup (Optional)

1. Go to [OpenAI API Keys](https://platform.openai.com/api-keys)
2. Create a new API key
3. Copy the key for use in your environment variables

### 5. Environment Configuration

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and add your credentials:
   ```env
   REDDIT_CLIENT_ID=your_client_id_here
   REDDIT_CLIENT_SECRET=your_client_secret_here
   REDDIT_USER_AGENT=PersonaGenerator/1.0
   OPENAI_API_KEY=your_openai_api_key_here
   ```

## How to Run

### Basic Usage

```bash
python persona_generator.py <reddit_profile_url>
```

### Examples

```bash
# Using full Reddit URL
python persona_generator.py https://www.reddit.com/user/kojied/

# Using username only
python persona_generator.py kojied

# With custom limits
python persona_generator.py https://www.reddit.com/u/Hungry-Move-6603/ --posts 20 --comments 30
```

### Command Line Options

- `--posts`: Number of posts to analyze (default: 10)
- `--comments`: Number of comments to analyze (default: 10)
- `--output-dir`: Output directory for persona files (default: output)

### Full Example

```bash
python persona_generator.py https://www.reddit.com/user/kojied/ --posts 15 --comments 25 --output-dir personas
```

## Sample Output

The script generates detailed persona files like this:

```
REDDIT USER PERSONA ANALYSIS
==================================================

**Name/Handle**: u/kojied

**Demographics**: 
- Age Range: 25-35 (inferred from tech interests and communication style)
- Gender: Not specified
- Location: Likely US-based (timezone patterns)

**Primary Interests**:
- Technology and Programming
- Gaming and Entertainment
- Science and Learning

**Communication Style**:
- Helpful and informative
- Technical but accessible
- Engages in constructive discussions

**Top Subreddits**:
1. r/programming - 8 interactions
2. r/gaming - 6 interactions
3. r/askreddit - 4 interactions

**Posting Behavior**:
- Prefers commenting over posting
- Provides detailed, thoughtful responses
- Active in technical discussions

**Standout Traits**:
- Problem Solver: Frequently helps others with technical issues
  [Evidence: Comment in r/programming - "You can solve this by..."]
- Curious Learner: Asks thoughtful questions about new technologies
  [Evidence: Post in r/learnprogramming - "What's the best way to..."]

---
Analysis generated on 2024-01-15 14:30:22
```

## Project Structure

```
reddit-persona-generator/
├── persona_generator.py    # Main executable script
├── utils.py               # Helper functions
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
├── .env                  # Your actual environment variables (create this)
├── README.md             # This file
├── output/               # Generated persona files (created automatically)
├── samples/              # Sample persona files
│   ├── persona_kojied_sample.txt
│   └── persona_Hungry-Move-6603_sample.txt
└── tests/                # Unit tests (optional)
```

## Troubleshooting

### Common Issues

1. **"PRAW not available"**
   - Install PRAW: `pip install praw`

2. **"Reddit API credentials not found"**
   - Check your `.env` file has the correct credentials
   - Ensure `.env` is in the same directory as the script

3. **"Reddit user not found"**
   - Verify the username/URL is correct
   - User might have deleted their account or set it to private

4. **"OpenAI API error"**
   - Check your API key is valid
   - Ensure you have sufficient API credits
   - The script will fall back to basic analysis if OpenAI fails

### Rate Limiting

Reddit API has rate limits. If you encounter rate limiting:
- Wait a few minutes between requests
- Reduce the number of posts/comments analyzed
- The script includes automatic retry logic

## Privacy and Ethics

This tool only analyzes **publicly available** Reddit data. Please use responsibly:

- Respect user privacy
- Don't use for harassment or stalking
- Consider the ethical implications of personality analysis
- Follow Reddit's Terms of Service

## License

This project is for educational and research purposes. Please use responsibly and in accordance with Reddit's API Terms of Service.

## Contributing

Feel free to submit issues, feature requests, or pull requests to improve this tool.
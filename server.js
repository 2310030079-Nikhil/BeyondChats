import express from 'express';
import cors from 'cors';
import axios from 'axios';
import fs from 'fs/promises';
import path from 'path';

const app = express();
const PORT = 3001;

app.use(cors());
app.use(express.json());
app.use(express.static('dist'));

// Helper function to extract username from Reddit URL
function extractUsername(url) {
  const match = url.match(/reddit\.com\/(?:u|user)\/([^\/\?#]+)/i);
  return match ? match[1] : null;
}

// Helper function to fetch Reddit data
async function fetchRedditData(username) {
  try {
    // Fetch user's posts
    const postsResponse = await axios.get(`https://www.reddit.com/user/${username}/submitted.json?limit=50`, {
      headers: {
        'User-Agent': 'PersonaAnalyzer/1.0'
      }
    });

    // Fetch user's comments
    const commentsResponse = await axios.get(`https://www.reddit.com/user/${username}/comments.json?limit=50`, {
      headers: {
        'User-Agent': 'PersonaAnalyzer/1.0'
      }
    });

    return {
      posts: postsResponse.data.data.children.map(child => child.data),
      comments: commentsResponse.data.data.children.map(child => child.data)
    };
  } catch (error) {
    throw new Error(`Failed to fetch Reddit data: ${error.message}`);
  }
}

// Helper function to analyze content and generate persona
function generatePersona(username, data) {
  const { posts, comments } = data;
  const allContent = [...posts, ...comments];
  
  if (allContent.length === 0) {
    return {
      username,
      summary: "No public posts or comments found for analysis.",
      traits: [],
      engagement: {
        totalPosts: 0,
        totalComments: 0,
        avgScore: 0
      }
    };
  }

  // Analyze interests based on subreddits
  const subredditCounts = {};
  allContent.forEach(item => {
    const subreddit = item.subreddit;
    subredditCounts[subreddit] = (subredditCounts[subreddit] || 0) + 1;
  });

  const topSubreddits = Object.entries(subredditCounts)
    .sort(([,a], [,b]) => b - a)
    .slice(0, 5);

  // Analyze personality traits from content
  const traits = [];
  
  // Check for helpful behavior
  const helpfulKeywords = ['help', 'advice', 'suggestion', 'recommend', 'try this', 'solution'];
  const helpfulContent = allContent.filter(item => 
    helpfulKeywords.some(keyword => 
      (item.title || item.body || '').toLowerCase().includes(keyword)
    )
  );
  
  if (helpfulContent.length > 3) {
    traits.push({
      trait: "Helpful and Supportive",
      evidence: helpfulContent.slice(0, 2).map(item => ({
        type: item.title ? 'post' : 'comment',
        content: (item.title || item.body || '').substring(0, 100) + '...',
        subreddit: item.subreddit
      })),
      confidence: Math.min(helpfulContent.length * 10, 100)
    });
  }

  // Check for technical interests
  const techKeywords = ['code', 'programming', 'software', 'tech', 'development', 'algorithm'];
  const techContent = allContent.filter(item => 
    techKeywords.some(keyword => 
      (item.title || item.body || '').toLowerCase().includes(keyword)
    )
  );
  
  if (techContent.length > 2) {
    traits.push({
      trait: "Technology Enthusiast",
      evidence: techContent.slice(0, 2).map(item => ({
        type: item.title ? 'post' : 'comment',
        content: (item.title || item.body || '').substring(0, 100) + '...',
        subreddit: item.subreddit
      })),
      confidence: Math.min(techContent.length * 15, 100)
    });
  }

  // Check for creative interests
  const creativeSubreddits = ['art', 'music', 'writing', 'photography', 'design', 'creative'];
  const creativeContent = allContent.filter(item => 
    creativeSubreddits.some(sub => item.subreddit.toLowerCase().includes(sub))
  );
  
  if (creativeContent.length > 1) {
    traits.push({
      trait: "Creative and Artistic",
      evidence: creativeContent.slice(0, 2).map(item => ({
        type: item.title ? 'post' : 'comment',
        content: (item.title || item.body || '').substring(0, 100) + '...',
        subreddit: item.subreddit
      })),
      confidence: Math.min(creativeContent.length * 20, 100)
    });
  }

  // Analyze engagement patterns
  const totalScore = allContent.reduce((sum, item) => sum + (item.score || 0), 0);
  const avgScore = totalScore / allContent.length;
  
  // Check for active discussion participation
  const longComments = comments.filter(comment => (comment.body || '').length > 200);
  if (longComments.length > 5) {
    traits.push({
      trait: "Thoughtful Communicator",
      evidence: longComments.slice(0, 2).map(item => ({
        type: 'comment',
        content: (item.body || '').substring(0, 150) + '...',
        subreddit: item.subreddit
      })),
      confidence: Math.min(longComments.length * 8, 100)
    });
  }

  return {
    username,
    summary: `Active Reddit user with ${posts.length} posts and ${comments.length} comments. Primary interests include ${topSubreddits.slice(0, 3).map(([sub]) => sub).join(', ')}.`,
    interests: topSubreddits.map(([subreddit, count]) => ({ subreddit, count })),
    traits,
    engagement: {
      totalPosts: posts.length,
      totalComments: comments.length,
      avgScore: Math.round(avgScore * 100) / 100,
      mostActiveSubreddits: topSubreddits.slice(0, 3)
    }
  };
}

// Helper function to format persona as text
function formatPersonaAsText(persona) {
  let text = `REDDIT USER PERSONA ANALYSIS\n`;
  text += `${'='.repeat(50)}\n\n`;
  text += `Username: u/${persona.username}\n`;
  text += `Generated: ${new Date().toISOString()}\n\n`;
  
  text += `SUMMARY\n`;
  text += `${'-'.repeat(20)}\n`;
  text += `${persona.summary}\n\n`;
  
  if (persona.interests && persona.interests.length > 0) {
    text += `TOP INTERESTS (by activity)\n`;
    text += `${'-'.repeat(30)}\n`;
    persona.interests.forEach((interest, index) => {
      text += `${index + 1}. r/${interest.subreddit} (${interest.count} posts/comments)\n`;
    });
    text += `\n`;
  }
  
  if (persona.traits && persona.traits.length > 0) {
    text += `PERSONALITY TRAITS\n`;
    text += `${'-'.repeat(25)}\n`;
    persona.traits.forEach((trait, index) => {
      text += `${index + 1}. ${trait.trait} (${trait.confidence}% confidence)\n`;
      text += `   Evidence:\n`;
      trait.evidence.forEach(evidence => {
        text += `   - [${evidence.type} in r/${evidence.subreddit}] ${evidence.content}\n`;
      });
      text += `\n`;
    });
  }
  
  text += `ENGAGEMENT STATISTICS\n`;
  text += `${'-'.repeat(30)}\n`;
  text += `Total Posts: ${persona.engagement.totalPosts}\n`;
  text += `Total Comments: ${persona.engagement.totalComments}\n`;
  text += `Average Score: ${persona.engagement.avgScore}\n`;
  
  if (persona.engagement.mostActiveSubreddits) {
    text += `Most Active Subreddits: ${persona.engagement.mostActiveSubreddits.map(([sub]) => `r/${sub}`).join(', ')}\n`;
  }
  
  text += `\n${'-'.repeat(50)}\n`;
  text += `Analysis generated by Reddit Persona Analyzer\n`;
  
  return text;
}

// API endpoint to generate persona
app.post('/api/persona', async (req, res) => {
  try {
    const { redditUrl } = req.body;
    
    if (!redditUrl) {
      return res.status(400).json({ error: 'Reddit URL is required' });
    }
    
    const username = extractUsername(redditUrl);
    if (!username) {
      return res.status(400).json({ error: 'Invalid Reddit user URL' });
    }
    
    // Fetch Reddit data
    const redditData = await fetchRedditData(username);
    
    // Generate persona
    const persona = generatePersona(username, redditData);
    
    // Format as text
    const personaText = formatPersonaAsText(persona);
    
    // Save to file
    const filename = `persona_${username}_${Date.now()}.txt`;
    const filepath = path.join(process.cwd(), 'generated', filename);
    
    // Ensure directory exists
    await fs.mkdir(path.dirname(filepath), { recursive: true });
    await fs.writeFile(filepath, personaText);
    
    res.json({
      success: true,
      persona,
      filename,
      downloadUrl: `/api/download/${filename}`
    });
    
  } catch (error) {
    console.error('Error generating persona:', error);
    res.status(500).json({ error: error.message });
  }
});

// Download endpoint
app.get('/api/download/:filename', async (req, res) => {
  try {
    const filename = req.params.filename;
    const filepath = path.join(process.cwd(), 'generated', filename);
    
    const fileContent = await fs.readFile(filepath, 'utf8');
    
    res.setHeader('Content-Disposition', `attachment; filename="${filename}"`);
    res.setHeader('Content-Type', 'text/plain');
    res.send(fileContent);
    
  } catch (error) {
    res.status(404).json({ error: 'File not found' });
  }
});

app.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
});
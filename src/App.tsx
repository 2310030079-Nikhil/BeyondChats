import React, { useState } from 'react';
import { Download, Users, Brain, TrendingUp, AlertCircle, CheckCircle } from 'lucide-react';

interface PersonaTrait {
  trait: string;
  evidence: {
    type: string;
    content: string;
    subreddit: string;
  }[];
  confidence: number;
}

interface PersonaResult {
  username: string;
  summary: string;
  interests: { subreddit: string; count: number; }[];
  traits: PersonaTrait[];
  engagement: {
    totalPosts: number;
    totalComments: number;
    avgScore: number;
    mostActiveSubreddits: [string, number][];
  };
}

interface ApiResponse {
  success: boolean;
  persona: PersonaResult;
  filename: string;
  downloadUrl: string;
}

function App() {
  const [redditUrl, setRedditUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<ApiResponse | null>(null);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!redditUrl.trim()) return;

    setLoading(true);
    setError('');
    setResult(null);

    try {
      const response = await fetch('http://localhost:3001/api/persona', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ redditUrl: redditUrl.trim() }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Failed to generate persona');
      }

      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = () => {
    if (result) {
      window.open(`http://localhost:3001${result.downloadUrl}`, '_blank');
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-orange-50 to-red-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-orange-200">
        <div className="max-w-4xl mx-auto px-4 py-6">
          <div className="flex items-center space-x-3">
            <div className="bg-orange-500 rounded-full p-2">
              <Brain className="h-6 w-6 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Reddit Persona Analyzer</h1>
              <p className="text-gray-600">Discover personality insights from Reddit activity</p>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-4 py-8">
        {/* Input Form */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-8">
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label htmlFor="reddit-url" className="block text-sm font-medium text-gray-700 mb-2">
                Reddit User Profile URL
              </label>
              <input
                type="url"
                id="reddit-url"
                value={redditUrl}
                onChange={(e) => setRedditUrl(e.target.value)}
                placeholder="https://www.reddit.com/u/username"
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
                required
              />
              <p className="text-sm text-gray-500 mt-1">
                Enter a Reddit user profile URL (e.g., https://www.reddit.com/u/username)
              </p>
            </div>
            
            <button
              type="submit"
              disabled={loading}
              className="w-full bg-orange-500 hover:bg-orange-600 disabled:opacity-50 text-white font-medium py-3 px-6 rounded-lg transition-colors duration-200 flex items-center justify-center space-x-2"
            >
              {loading ? (
                <>
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                  <span>Analyzing Profile...</span>
                </>
              ) : (
                <>
                  <Users className="h-5 w-5" />
                  <span>Generate Persona</span>
                </>
              )}
            </button>
          </form>
        </div>

        {/* Error Message */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-8 flex items-center space-x-3">
            <AlertCircle className="h-5 w-5 text-red-500 flex-shrink-0" />
            <div>
              <h3 className="text-red-800 font-medium">Error</h3>
              <p className="text-red-700">{error}</p>
            </div>
          </div>
        )}

        {/* Results */}
        {result && (
          <div className="space-y-6">
            {/* Success Message with Download */}
            <div className="bg-green-50 border border-green-200 rounded-lg p-4 flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <CheckCircle className="h-5 w-5 text-green-500" />
                <div>
                  <h3 className="text-green-800 font-medium">Persona Generated Successfully</h3>
                  <p className="text-green-700">Analysis complete for u/{result.persona.username}</p>
                </div>
              </div>
              <button
                onClick={handleDownload}
                className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg flex items-center space-x-2 transition-colors duration-200"
              >
                <Download className="h-4 w-4" />
                <span>Download .txt</span>
              </button>
            </div>

            {/* Summary */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <h2 className="text-xl font-bold text-gray-900 mb-4">Summary</h2>
              <p className="text-gray-700">{result.persona.summary}</p>
            </div>

            {/* Interests */}
            {result.persona.interests.length > 0 && (
              <div className="bg-white rounded-lg shadow-md p-6">
                <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center space-x-2">
                  <TrendingUp className="h-5 w-5 text-orange-500" />
                  <span>Top Interests</span>
                </h2>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {result.persona.interests.slice(0, 6).map((interest, index) => (
                    <div key={interest.subreddit} className="bg-orange-50 rounded-lg p-4">
                      <div className="flex items-center justify-between">
                        <span className="font-medium text-gray-900">r/{interest.subreddit}</span>
                        <span className="text-sm bg-orange-200 text-orange-800 px-2 py-1 rounded-full">
                          {interest.count} posts
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Personality Traits */}
            {result.persona.traits.length > 0 && (
              <div className="bg-white rounded-lg shadow-md p-6">
                <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center space-x-2">
                  <Brain className="h-5 w-5 text-purple-500" />
                  <span>Personality Traits</span>
                </h2>
                <div className="space-y-6">
                  {result.persona.traits.map((trait, index) => (
                    <div key={index} className="border border-gray-200 rounded-lg p-4">
                      <div className="flex items-center justify-between mb-3">
                        <h3 className="font-semibold text-gray-900">{trait.trait}</h3>
                        <span className="text-sm bg-purple-100 text-purple-800 px-2 py-1 rounded-full">
                          {trait.confidence}% confidence
                        </span>
                      </div>
                      <div className="space-y-2">
                        <p className="text-sm font-medium text-gray-700">Evidence:</p>
                        {trait.evidence.map((evidence, evidenceIndex) => (
                          <div key={evidenceIndex} className="bg-gray-50 rounded p-3">
                            <div className="flex items-center space-x-2 mb-1">
                              <span className="text-xs bg-gray-200 text-gray-700 px-2 py-1 rounded">
                                {evidence.type}
                              </span>
                              <span className="text-xs text-gray-600">r/{evidence.subreddit}</span>
                            </div>
                            <p className="text-sm text-gray-700">{evidence.content}</p>
                          </div>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Engagement Stats */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <h2 className="text-xl font-bold text-gray-900 mb-4">Engagement Statistics</h2>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="text-center">
                  <div className="text-3xl font-bold text-blue-600">{result.persona.engagement.totalPosts}</div>
                  <div className="text-gray-600">Total Posts</div>
                </div>
                <div className="text-center">
                  <div className="text-3xl font-bold text-green-600">{result.persona.engagement.totalComments}</div>
                  <div className="text-gray-600">Total Comments</div>
                </div>
                <div className="text-center">
                  <div className="text-3xl font-bold text-orange-600">{result.persona.engagement.avgScore}</div>
                  <div className="text-gray-600">Average Score</div>
                </div>
              </div>
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-12">
        <div className="max-w-4xl mx-auto px-4 py-6">
          <p className="text-center text-gray-600 text-sm">
            Reddit Persona Analyzer - Analyzing public Reddit data to generate personality insights
          </p>
        </div>
      </footer>
    </div>
  );
}

export default App;
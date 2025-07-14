/**
 * 🌐 EXTERNAL INTELLIGENCE MONITOR
 * Real-time monitoring of external signals and market intelligence
 * 
 * Features:
 * - Social media tracking (LinkedIn, Twitter, executive content)
 * - Competitor intelligence (website changes, pricing, product launches)
 * - Market intelligence (industry news, funding, regulatory changes)
 * - Customer intelligence (website monitoring, social presence, expansion signals)
 */

import React, { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { 
  Globe, 
  TrendingUp, 
  AlertCircle, 
  Eye, 
  DollarSign,
  Users,
  Building,
  Newspaper,
  Twitter,
  Linkedin,
  ExternalLink,
  Clock,
  ArrowUp,
  ArrowDown,
  Target,
  Zap
} from 'lucide-react';

// Types
interface SocialMediaPost {
  id: string;
  platform: 'linkedin' | 'twitter' | 'executive';
  author: string;
  content: string;
  engagement: number;
  timestamp: string;
  relevance: number;
  sentiment: 'positive' | 'neutral' | 'negative';
  tags: string[];
}

interface CompetitorAlert {
  id: string;
  company: string;
  type: 'website_change' | 'pricing_update' | 'product_launch' | 'hiring_trend';
  title: string;
  description: string;
  impact: 'low' | 'medium' | 'high' | 'critical';
  timestamp: string;
  url?: string;
  change_percentage?: number;
}

interface MarketIntelligence {
  id: string;
  type: 'industry_news' | 'funding' | 'regulatory' | 'economic';
  title: string;
  description: string;
  source: string;
  impact_score: number;
  timestamp: string;
  url: string;
  tags: string[];
}

interface CustomerSignal {
  id: string;
  customer: string;
  type: 'website_activity' | 'social_mention' | 'news_coverage' | 'expansion_signal';
  title: string;
  description: string;
  opportunity_score: number;
  timestamp: string;
  actionable: boolean;
}

const ExternalIntelligenceMonitor: React.FC = () => {
  const [activeFilter, setActiveFilter] = useState<string>('all');
  const [timeRange, setTimeRange] = useState<string>('24h');

  // Mock data - in production, would come from external APIs
  const socialMediaPosts: SocialMediaPost[] = [
    {
      id: '1',
      platform: 'linkedin',
      author: 'TechCorp CEO',
      content: 'Excited to announce our Q3 results showing 340% growth in enterprise adoption...',
      engagement: 1250,
      timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
      relevance: 0.95,
      sentiment: 'positive',
      tags: ['enterprise', 'growth', 'Q3']
    },
    {
      id: '2',
      platform: 'twitter',
      author: 'Industry Analyst',
      content: 'The AI automation market is experiencing unprecedented consolidation. Key players to watch...',
      engagement: 890,
      timestamp: new Date(Date.now() - 4 * 60 * 60 * 1000).toISOString(),
      relevance: 0.88,
      sentiment: 'neutral',
      tags: ['AI', 'automation', 'market']
    },
    {
      id: '3',
      platform: 'executive',
      author: 'MegaCorp CTO',
      content: 'Our infrastructure modernization initiative is ahead of schedule. Looking for AI partners...',
      engagement: 450,
      timestamp: new Date(Date.now() - 6 * 60 * 60 * 1000).toISOString(),
      relevance: 0.92,
      sentiment: 'positive',
      tags: ['infrastructure', 'AI', 'partnerships']
    }
  ];

  const competitorAlerts: CompetitorAlert[] = [
    {
      id: '1',
      company: 'CompetitorX',
      type: 'pricing_update',
      title: 'Enterprise pricing increased by 25%',
      description: 'CompetitorX raised their enterprise tier pricing from $199/month to $249/month',
      impact: 'high',
      timestamp: new Date(Date.now() - 3 * 60 * 60 * 1000).toISOString(),
      url: 'https://competitorx.com/pricing',
      change_percentage: 25
    },
    {
      id: '2',
      company: 'RivalCorp',
      type: 'product_launch',
      title: 'New AI automation suite launched',
      description: 'RivalCorp announced their new AI automation suite targeting mid-market customers',
      impact: 'medium',
      timestamp: new Date(Date.now() - 8 * 60 * 60 * 1000).toISOString(),
      url: 'https://rivalcorp.com/products/ai-suite'
    },
    {
      id: '3',
      company: 'StartupY',
      type: 'hiring_trend',
      title: 'Aggressive hiring in sales team',
      description: 'StartupY posted 15 new sales positions in the last 2 weeks, indicating expansion',
      impact: 'medium',
      timestamp: new Date(Date.now() - 12 * 60 * 60 * 1000).toISOString()
    }
  ];

  const marketIntelligence: MarketIntelligence[] = [
    {
      id: '1',
      type: 'funding',
      title: 'AI Automation sector sees $2.3B in funding',
      description: 'Q3 funding in AI automation reached record highs with 47 deals totaling $2.3B',
      source: 'TechCrunch',
      impact_score: 0.89,
      timestamp: new Date(Date.now() - 5 * 60 * 60 * 1000).toISOString(),
      url: 'https://techcrunch.com/ai-funding-q3',
      tags: ['funding', 'AI', 'automation']
    },
    {
      id: '2',
      type: 'regulatory',
      title: 'New AI governance framework proposed',
      description: 'EU proposes new framework for AI governance affecting enterprise deployments',
      source: 'Reuters',
      impact_score: 0.76,
      timestamp: new Date(Date.now() - 7 * 60 * 60 * 1000).toISOString(),
      url: 'https://reuters.com/ai-governance',
      tags: ['regulatory', 'EU', 'governance']
    },
    {
      id: '3',
      type: 'industry_news',
      title: 'Enterprise AI adoption accelerates',
      description: 'Gartner reports 65% of enterprises now have AI initiatives in production',
      source: 'Gartner',
      impact_score: 0.82,
      timestamp: new Date(Date.now() - 10 * 60 * 60 * 1000).toISOString(),
      url: 'https://gartner.com/ai-adoption',
      tags: ['enterprise', 'adoption', 'AI']
    }
  ];

  const customerSignals: CustomerSignal[] = [
    {
      id: '1',
      customer: 'TechCorp',
      type: 'website_activity',
      title: 'Website activity increased 340%',
      description: 'TechCorp website traffic to pricing and enterprise pages spiked significantly',
      opportunity_score: 0.94,
      timestamp: new Date(Date.now() - 1 * 60 * 60 * 1000).toISOString(),
      actionable: true
    },
    {
      id: '2',
      customer: 'MegaCorp',
      type: 'expansion_signal',
      title: 'Infrastructure modernization mentioned',
      description: 'CTO mentioned infrastructure modernization and looking for AI partners',
      opportunity_score: 0.87,
      timestamp: new Date(Date.now() - 6 * 60 * 60 * 1000).toISOString(),
      actionable: true
    },
    {
      id: '3',
      customer: 'GrowthCo',
      type: 'social_mention',
      title: 'Positive mention in industry forum',
      description: 'CEO mentioned challenges with current automation tools in LinkedIn post',
      opportunity_score: 0.73,
      timestamp: new Date(Date.now() - 14 * 60 * 60 * 1000).toISOString(),
      actionable: true
    }
  ];

  // Helper functions
  const getImpactColor = (impact: string) => {
    switch (impact) {
      case 'critical': return 'text-red-400 bg-red-900/20';
      case 'high': return 'text-orange-400 bg-orange-900/20';
      case 'medium': return 'text-yellow-400 bg-yellow-900/20';
      case 'low': return 'text-green-400 bg-green-900/20';
      default: return 'text-gray-400 bg-gray-900/20';
    }
  };

  const getSentimentColor = (sentiment: string) => {
    switch (sentiment) {
      case 'positive': return 'text-green-400';
      case 'negative': return 'text-red-400';
      case 'neutral': return 'text-gray-400';
      default: return 'text-gray-400';
    }
  };

  const getPlatformIcon = (platform: string) => {
    switch (platform) {
      case 'linkedin': return <Linkedin className="h-4 w-4" />;
      case 'twitter': return <Twitter className="h-4 w-4" />;
      case 'executive': return <Users className="h-4 w-4" />;
      default: return <Globe className="h-4 w-4" />;
    }
  };

  const formatTimeAgo = (timestamp: string) => {
    const now = new Date();
    const time = new Date(timestamp);
    const diffHours = Math.floor((now.getTime() - time.getTime()) / (1000 * 60 * 60));
    
    if (diffHours < 1) return 'Just now';
    if (diffHours < 24) return `${diffHours}h ago`;
    return `${Math.floor(diffHours / 24)}d ago`;
  };

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-white">External Intelligence Monitor</h2>
          <p className="text-gray-400">Real-time monitoring of market signals and competitive intelligence</p>
        </div>
        <div className="flex items-center space-x-4">
          <select 
            value={timeRange} 
            onChange={(e) => setTimeRange(e.target.value)}
            className="bg-gray-800 text-white border border-gray-600 rounded-lg px-3 py-2 text-sm"
          >
            <option value="1h">Last Hour</option>
            <option value="24h">Last 24 Hours</option>
            <option value="7d">Last 7 Days</option>
            <option value="30d">Last 30 Days</option>
          </select>
          <div className="flex items-center space-x-2">
            <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
            <span className="text-sm text-gray-400">Live monitoring</span>
          </div>
        </div>
      </div>

      {/* Filter tabs */}
      <div className="flex space-x-1 bg-gray-800 p-1 rounded-lg">
        {[
          { key: 'all', label: 'All Signals', icon: Globe },
          { key: 'social', label: 'Social Media', icon: Users },
          { key: 'competitors', label: 'Competitors', icon: Target },
          { key: 'market', label: 'Market Intel', icon: TrendingUp },
          { key: 'customers', label: 'Customer Signals', icon: Building }
        ].map(({ key, label, icon: Icon }) => (
          <button
            key={key}
            onClick={() => setActiveFilter(key)}
            className={`flex items-center space-x-2 px-4 py-2 rounded-md transition-all ${
              activeFilter === key
                ? 'bg-blue-600 text-white'
                : 'text-gray-400 hover:text-white hover:bg-gray-700'
            }`}
          >
            <Icon className="h-4 w-4" />
            <span className="text-sm">{label}</span>
          </button>
        ))}
      </div>

      {/* Content grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Social Media Tracking */}
        {(activeFilter === 'all' || activeFilter === 'social') && (
          <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-semibold text-white flex items-center space-x-2">
                <Users className="h-5 w-5" />
                <span>Social Media Tracking</span>
              </h3>
              <span className="text-xs text-gray-400">{socialMediaPosts.length} posts</span>
            </div>
            
            <div className="space-y-3">
              {socialMediaPosts.map((post) => (
                <div key={post.id} className="bg-gray-700 rounded-lg p-3">
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center space-x-2">
                      {getPlatformIcon(post.platform)}
                      <span className="text-sm font-medium text-white">{post.author}</span>
                      <span className={`text-xs px-2 py-1 rounded ${getSentimentColor(post.sentiment)}`}>
                        {post.sentiment}
                      </span>
                    </div>
                    <span className="text-xs text-gray-400">{formatTimeAgo(post.timestamp)}</span>
                  </div>
                  
                  <p className="text-sm text-gray-300 mb-2">{post.content}</p>
                  
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-4 text-xs text-gray-400">
                      <span>Engagement: {post.engagement.toLocaleString()}</span>
                      <span>Relevance: {Math.round(post.relevance * 100)}%</span>
                    </div>
                    <div className="flex flex-wrap gap-1">
                      {post.tags.map((tag, idx) => (
                        <span key={idx} className="text-xs bg-gray-600 text-gray-300 px-2 py-1 rounded">
                          {tag}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Competitor Intelligence */}
        {(activeFilter === 'all' || activeFilter === 'competitors') && (
          <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-semibold text-white flex items-center space-x-2">
                <Target className="h-5 w-5" />
                <span>Competitor Intelligence</span>
              </h3>
              <span className="text-xs text-gray-400">{competitorAlerts.length} alerts</span>
            </div>
            
            <div className="space-y-3">
              {competitorAlerts.map((alert) => (
                <div key={alert.id} className="bg-gray-700 rounded-lg p-3">
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center space-x-2">
                      <span className="text-sm font-medium text-white">{alert.company}</span>
                      <span className={`text-xs px-2 py-1 rounded ${getImpactColor(alert.impact)}`}>
                        {alert.impact}
                      </span>
                    </div>
                    <span className="text-xs text-gray-400">{formatTimeAgo(alert.timestamp)}</span>
                  </div>
                  
                  <h4 className="text-sm font-medium text-white mb-1">{alert.title}</h4>
                  <p className="text-sm text-gray-300 mb-2">{alert.description}</p>
                  
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      {alert.change_percentage && (
                        <span className="text-xs text-orange-400">
                          {alert.change_percentage > 0 ? '+' : ''}{alert.change_percentage}%
                        </span>
                      )}
                      <span className="text-xs text-gray-400 capitalize">
                        {alert.type.replace('_', ' ')}
                      </span>
                    </div>
                    {alert.url && (
                      <a 
                        href={alert.url} 
                        target="_blank" 
                        rel="noopener noreferrer"
                        className="text-xs text-blue-400 hover:text-blue-300 flex items-center space-x-1"
                      >
                        <ExternalLink className="h-3 w-3" />
                        <span>View</span>
                      </a>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Market Intelligence */}
        {(activeFilter === 'all' || activeFilter === 'market') && (
          <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-semibold text-white flex items-center space-x-2">
                <TrendingUp className="h-5 w-5" />
                <span>Market Intelligence</span>
              </h3>
              <span className="text-xs text-gray-400">{marketIntelligence.length} updates</span>
            </div>
            
            <div className="space-y-3">
              {marketIntelligence.map((intel) => (
                <div key={intel.id} className="bg-gray-700 rounded-lg p-3">
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center space-x-2">
                      <Newspaper className="h-4 w-4 text-gray-400" />
                      <span className="text-sm font-medium text-white">{intel.source}</span>
                      <span className="text-xs text-gray-400 capitalize">
                        {intel.type.replace('_', ' ')}
                      </span>
                    </div>
                    <span className="text-xs text-gray-400">{formatTimeAgo(intel.timestamp)}</span>
                  </div>
                  
                  <h4 className="text-sm font-medium text-white mb-1">{intel.title}</h4>
                  <p className="text-sm text-gray-300 mb-2">{intel.description}</p>
                  
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <span className="text-xs text-blue-400">
                        Impact: {Math.round(intel.impact_score * 100)}%
                      </span>
                      <div className="flex flex-wrap gap-1">
                        {intel.tags.map((tag, idx) => (
                          <span key={idx} className="text-xs bg-gray-600 text-gray-300 px-2 py-1 rounded">
                            {tag}
                          </span>
                        ))}
                      </div>
                    </div>
                    <a 
                      href={intel.url} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="text-xs text-blue-400 hover:text-blue-300 flex items-center space-x-1"
                    >
                      <ExternalLink className="h-3 w-3" />
                      <span>Read</span>
                    </a>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Customer Intelligence */}
        {(activeFilter === 'all' || activeFilter === 'customers') && (
          <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-semibold text-white flex items-center space-x-2">
                <Building className="h-5 w-5" />
                <span>Customer Intelligence</span>
              </h3>
              <span className="text-xs text-gray-400">{customerSignals.length} signals</span>
            </div>
            
            <div className="space-y-3">
              {customerSignals.map((signal) => (
                <div key={signal.id} className="bg-gray-700 rounded-lg p-3">
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center space-x-2">
                      <span className="text-sm font-medium text-white">{signal.customer}</span>
                      {signal.actionable && (
                        <span className="text-xs bg-green-600 text-white px-2 py-1 rounded">
                          Actionable
                        </span>
                      )}
                    </div>
                    <span className="text-xs text-gray-400">{formatTimeAgo(signal.timestamp)}</span>
                  </div>
                  
                  <h4 className="text-sm font-medium text-white mb-1">{signal.title}</h4>
                  <p className="text-sm text-gray-300 mb-2">{signal.description}</p>
                  
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <span className="text-xs text-green-400">
                        Opportunity: {Math.round(signal.opportunity_score * 100)}%
                      </span>
                      <span className="text-xs text-gray-400 capitalize">
                        {signal.type.replace('_', ' ')}
                      </span>
                    </div>
                    {signal.actionable && (
                      <button className="text-xs bg-blue-600 text-white px-3 py-1 rounded hover:bg-blue-700">
                        Take Action
                      </button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Summary stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-400">Social Mentions</p>
              <p className="text-2xl font-bold text-white">{socialMediaPosts.length}</p>
            </div>
            <Users className="h-8 w-8 text-blue-400" />
          </div>
          <p className="text-xs text-green-400 mt-1">+15% from yesterday</p>
        </div>
        
        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-400">Competitor Alerts</p>
              <p className="text-2xl font-bold text-white">{competitorAlerts.length}</p>
            </div>
            <Target className="h-8 w-8 text-orange-400" />
          </div>
          <p className="text-xs text-yellow-400 mt-1">2 high impact</p>
        </div>
        
        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-400">Market Updates</p>
              <p className="text-2xl font-bold text-white">{marketIntelligence.length}</p>
            </div>
            <TrendingUp className="h-8 w-8 text-green-400" />
          </div>
          <p className="text-xs text-blue-400 mt-1">Avg impact: 82%</p>
        </div>
        
        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-400">Customer Signals</p>
              <p className="text-2xl font-bold text-white">{customerSignals.length}</p>
            </div>
            <Building className="h-8 w-8 text-purple-400" />
          </div>
          <p className="text-xs text-green-400 mt-1">3 actionable</p>
        </div>
      </div>
    </div>
  );
};

export default ExternalIntelligenceMonitor; 
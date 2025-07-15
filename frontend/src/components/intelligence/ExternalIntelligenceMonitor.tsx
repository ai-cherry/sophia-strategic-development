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
  Zap,
  Shield,
  Activity,
  BarChart3
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

interface CompetitorProfile {
  id: string;
  name: string;
  category: string;
  description: string;
  website: string;
  threat_level: number;
  market_share: number;
  growth_rate: number;
  key_products: string[];
  strengths: string[];
  weaknesses: string[];
  similarity_score?: number;
}

interface CompetitorIntelligence {
  id: string;
  competitor_id: string;
  intelligence_type: string;
  title: string;
  description: string;
  source: string;
  impact_score: number;
  confidence_score: number;
  timestamp: string;
  tags: string[];
  similarity_score?: number;
}

interface CompetitorAlert {
  id: string;
  company: string;
  type: 'website_change' | 'pricing_update' | 'product_launch' | 'hiring_trend';
  title: string;
  description: string;
  impact: 'high' | 'medium' | 'low';
  timestamp: string;
  source: string;
  confidence: number;
}

interface ThreatAnalysis {
  total_competitors: number;
  threat_distribution: {
    critical: number;
    high: number;
    medium: number;
    low: number;
  };
  category_distribution: {
    direct: number;
    indirect: number;
    emerging: number;
    substitute: number;
  };
  top_threats: Array<{
    name: string;
    threat_level: number;
    category: string;
    key_products: string[];
  }>;
  emerging_threats: Array<{
    name: string;
    threat_level: number;
    growth_rate: number;
  }>;
  market_insights: {
    total_market_share: number;
    average_growth_rate: number;
  };
}

interface IntelligenceSummary {
  total_items: number;
  period_days: number;
  type_distribution: Record<string, number>;
  impact_analysis: {
    high_impact: number;
    medium_impact: number;
    low_impact: number;
  };
  top_intelligence: Array<{
    title: string;
    competitor_id: string;
    impact_score: number;
    intelligence_type: string;
    timestamp: string;
  }>;
}

// API Functions
const fetchCompetitorProfiles = async (query: string = 'property management', limit: number = 10): Promise<CompetitorProfile[]> => {
  const response = await fetch(`/api/v1/competitors/profiles?query=${encodeURIComponent(query)}&limit=${limit}`);
  if (!response.ok) throw new Error('Failed to fetch competitor profiles');
  const data = await response.json();
  return data.results || [];
};

const fetchCompetitorIntelligence = async (query: string = 'AI', limit: number = 20): Promise<CompetitorIntelligence[]> => {
  const response = await fetch(`/api/v1/competitors/intelligence/search?query=${encodeURIComponent(query)}&limit=${limit}&days_back=30`);
  if (!response.ok) throw new Error('Failed to fetch competitor intelligence');
  const data = await response.json();
  return data.results || [];
};

const fetchThreatAnalysis = async (): Promise<ThreatAnalysis> => {
  const response = await fetch('/api/v1/competitors/analytics/threat-analysis');
  if (!response.ok) throw new Error('Failed to fetch threat analysis');
  const data = await response.json();
  return data.analysis || {};
};

const fetchIntelligenceSummary = async (days_back: number = 7): Promise<IntelligenceSummary> => {
  const response = await fetch(`/api/v1/competitors/analytics/intelligence-summary?days_back=${days_back}`);
  if (!response.ok) throw new Error('Failed to fetch intelligence summary');
  const data = await response.json();
  return data.summary || {};
};

const fetchDashboardData = async () => {
  const response = await fetch('/api/v1/competitors/analytics/dashboard');
  if (!response.ok) throw new Error('Failed to fetch dashboard data');
  const data = await response.json();
  return data.dashboard || {};
};

const ExternalIntelligenceMonitor: React.FC = () => {
  const [activeFilter, setActiveFilter] = useState<string>('all');
  const [timeRange, setTimeRange] = useState<string>('24h');
  const [searchQuery, setSearchQuery] = useState<string>('');

  // React Query hooks for real-time data
  const { data: competitorProfiles, isLoading: profilesLoading, error: profilesError } = useQuery({
    queryKey: ['competitor-profiles', searchQuery],
    queryFn: () => fetchCompetitorProfiles(searchQuery || 'property management', 10),
    refetchInterval: 5 * 60 * 1000, // Refetch every 5 minutes
  });

  const { data: competitorIntelligence, isLoading: intelligenceLoading, error: intelligenceError } = useQuery({
    queryKey: ['competitor-intelligence', searchQuery],
    queryFn: () => fetchCompetitorIntelligence(searchQuery || 'AI', 20),
    refetchInterval: 5 * 60 * 1000,
  });

  const { data: threatAnalysis, isLoading: threatLoading, error: threatError } = useQuery({
    queryKey: ['threat-analysis'],
    queryFn: fetchThreatAnalysis,
    refetchInterval: 10 * 60 * 1000, // Refetch every 10 minutes
  });

  const { data: intelligenceSummary, isLoading: summaryLoading, error: summaryError } = useQuery({
    queryKey: ['intelligence-summary', timeRange],
    queryFn: () => fetchIntelligenceSummary(timeRange === '24h' ? 1 : timeRange === '7d' ? 7 : 30),
    refetchInterval: 5 * 60 * 1000,
  });

  const { data: dashboardData, isLoading: dashboardLoading, error: dashboardError } = useQuery({
    queryKey: ['competitor-dashboard'],
    queryFn: fetchDashboardData,
    refetchInterval: 5 * 60 * 1000,
  });

  // Mock data for social media (would be replaced with real API in production)
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
    }
  ];

  // Convert competitor intelligence to alerts format
  const competitorAlerts: CompetitorAlert[] = (competitorIntelligence || []).map(intel => ({
    id: intel.id,
    company: intel.competitor_id, // This would be resolved to company name in production
    type: intel.intelligence_type as any,
    title: intel.title,
    description: intel.description,
    impact: intel.impact_score >= 8 ? 'high' : intel.impact_score >= 5 ? 'medium' : 'low',
    timestamp: intel.timestamp,
    source: intel.source,
    confidence: intel.confidence_score
  }));

  // Filter logic
  const filteredAlerts = competitorAlerts.filter(alert => {
    if (activeFilter === 'all') return true;
    return alert.type === activeFilter;
  });

  const filteredPosts = socialMediaPosts.filter(post => {
    if (activeFilter === 'all') return true;
    return post.platform === activeFilter;
  });

  // Time range filtering
  const getTimeRangeFilter = () => {
    const now = new Date();
    switch (timeRange) {
      case '24h': return new Date(now.getTime() - 24 * 60 * 60 * 1000);
      case '7d': return new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
      case '30d': return new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000);
      default: return new Date(now.getTime() - 24 * 60 * 60 * 1000);
    }
  };

  const timeFilter = getTimeRangeFilter();
  const filteredByTime = filteredAlerts.filter(alert => 
    new Date(alert.timestamp) >= timeFilter
  );

  // Loading and error states
  const isLoading = profilesLoading || intelligenceLoading || threatLoading || summaryLoading || dashboardLoading;
  const hasError = profilesError || intelligenceError || threatError || summaryError || dashboardError;

  if (hasError) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <div className="flex items-center">
          <AlertCircle className="h-5 w-5 text-red-600 mr-2" />
          <span className="text-red-800">Error loading competitor intelligence data</span>
        </div>
      </div>
    );
  }

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
                      <span className="text-xs text-gray-400 capitalize">
                        {alert.type.replace('_', ' ')}
                      </span>
                    </div>
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
              <span className="text-xs text-gray-400">{intelligenceSummary?.total_items || 0} updates</span>
            </div>
            
            <div className="space-y-3">
              {intelligenceSummary?.top_intelligence.map((intel) => (
                <div key={intel.title} className="bg-gray-700 rounded-lg p-3">
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center space-x-2">
                      <Newspaper className="h-4 w-4 text-gray-400" />
                      <span className="text-sm font-medium text-white">{intel.title}</span>
                      <span className="text-xs text-gray-400 capitalize">
                        {intel.intelligence_type.replace('_', ' ')}
                      </span>
                    </div>
                    <span className="text-xs text-gray-400">{formatTimeAgo(intel.timestamp)}</span>
                  </div>
                  
                  <p className="text-sm text-gray-300 mb-2">{intel.description}</p>
                  
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <span className="text-xs text-blue-400">
                        Impact: {Math.round(intel.impact_score * 100)}%
                      </span>
                    </div>
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
              <span className="text-xs text-gray-400">{intelligenceSummary?.total_items || 0} signals</span>
            </div>
            
            <div className="space-y-3">
              {intelligenceSummary?.top_intelligence.map((signal) => (
                <div key={signal.title} className="bg-gray-700 rounded-lg p-3">
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center space-x-2">
                      <span className="text-sm font-medium text-white">{signal.title}</span>
                    </div>
                    <span className="text-xs text-gray-400">{formatTimeAgo(signal.timestamp)}</span>
                  </div>
                  
                  <p className="text-sm text-gray-300 mb-2">{signal.description}</p>
                  
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <span className="text-xs text-green-400">
                        Opportunity: {Math.round(signal.impact_score * 100)}%
                      </span>
                      <span className="text-xs text-gray-400 capitalize">
                        {signal.intelligence_type.replace('_', ' ')}
                      </span>
                    </div>
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
              <p className="text-2xl font-bold text-white">{intelligenceSummary?.total_items || 0}</p>
            </div>
            <TrendingUp className="h-8 w-8 text-green-400" />
          </div>
          <p className="text-xs text-blue-400 mt-1">Avg impact: 82%</p>
        </div>
        
        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-400">Customer Signals</p>
              <p className="text-2xl font-bold text-white">{intelligenceSummary?.total_items || 0}</p>
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
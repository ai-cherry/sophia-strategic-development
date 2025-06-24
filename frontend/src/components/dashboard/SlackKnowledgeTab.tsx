import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../ui/card';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Badge } from '../ui/badge';
import { Alert, AlertDescription } from '../ui/alert';
import { Progress } from '../ui/progress';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '../ui/table';
import {
  MessageSquare,
  Hash,
  Users,
  TrendingUp,
  Brain,
  CheckCircle,
  XCircle,
  Clock,
  AlertCircle,
  Search,
  Filter,
  Calendar,
  BarChart3,
  MessageCircle,
  Lightbulb,
  Target,
  Loader2
} from 'lucide-react';

interface SlackStats {
  total_conversations: number;
  total_messages: number;
  active_channels: number;
  insights_extracted: number;
  knowledge_value_conversations: number;
  avg_business_value_score: number;
}

interface SlackChannel {
  channel_id: string;
  channel_name: string;
  business_function: string;
  conversation_count: number;
  message_count: number;
  unique_participants: number;
  avg_business_value: number;
  insights_extracted: number;
  knowledge_value_score: number;
  last_activity: string;
}

interface SlackConversation {
  conversation_id: string;
  conversation_title: string;
  channel_name: string;
  participant_count: number;
  message_count: number;
  business_value_score: number;
  sentiment_score: number;
  contains_decisions: boolean;
  contains_action_items: boolean;
  start_time: string;
  duration_minutes: number;
  conversation_summary: string;
  key_topics: string[];
}

interface SlackInsight {
  insight_id: string;
  insight_type: string;
  insight_category: string;
  insight_title: string;
  insight_description: string;
  confidence_score: number;
  business_impact: string;
  is_actionable: boolean;
  human_validated: boolean;
  extracted_at: string;
  conversation_title: string;
  channel_name: string;
}

export const SlackKnowledgeTab: React.FC = () => {
  const [stats, setStats] = useState<SlackStats | null>(null);
  const [channels, setChannels] = useState<SlackChannel[]>([]);
  const [conversations, setConversations] = useState<SlackConversation[]>([]);
  const [insights, setInsights] = useState<SlackInsight[]>([]);
  const [activeView, setActiveView] = useState<'overview' | 'conversations' | 'insights'>('overview');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedChannel, setSelectedChannel] = useState<string>('all');
  const [businessValueFilter, setBusinessValueFilter] = useState<number>(0.5);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Load Slack data on component mount
  useEffect(() => {
    loadSlackData();
  }, []);

  const loadSlackData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Load all Slack data in parallel
      const [statsResponse, channelsResponse, conversationsResponse, insightsResponse] = await Promise.all([
        fetch('/api/v1/knowledge/slack/stats'),
        fetch('/api/v1/knowledge/slack/channels'),
        fetch('/api/v1/knowledge/slack/conversations?limit=50'),
        fetch('/api/v1/knowledge/slack/insights?limit=20')
      ]);

      if (statsResponse.ok) {
        setStats(await statsResponse.json());
      }

      if (channelsResponse.ok) {
        setChannels(await channelsResponse.json());
      }

      if (conversationsResponse.ok) {
        const conversationsData = await conversationsResponse.json();
        setConversations(conversationsData.conversations || []);
      }

      if (insightsResponse.ok) {
        const insightsData = await insightsResponse.json();
        setInsights(insightsData.insights || []);
      }

    } catch (error) {
      console.error('Failed to load Slack data:', error);
      setError('Failed to load Slack knowledge data');
    } finally {
      setLoading(false);
    }
  };

  const handleSearchConversations = async () => {
    if (!searchQuery.trim()) {
      loadSlackData();
      return;
    }

    try {
      setLoading(true);
      const params = new URLSearchParams({
        query: searchQuery,
        limit: '50'
      });

      if (selectedChannel !== 'all') {
        params.append('channel_id', selectedChannel);
      }

      const response = await fetch(`/api/v1/knowledge/slack/search?${params}`);
      
      if (response.ok) {
        const data = await response.json();
        setConversations(data.conversations || []);
      }

    } catch (error) {
      console.error('Search failed:', error);
      setError('Failed to search Slack conversations');
    } finally {
      setLoading(false);
    }
  };

  const validateInsight = async (insightId: string, isValid: boolean) => {
    try {
      const response = await fetch(`/api/v1/knowledge/slack/insights/${insightId}/validate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ is_valid: isValid })
      });

      if (response.ok) {
        // Update local state
        setInsights(prev => 
          prev.map(insight => 
            insight.insight_id === insightId 
              ? { ...insight, human_validated: true }
              : insight
          )
        );
      }

    } catch (error) {
      console.error('Failed to validate insight:', error);
    }
  };

  const getBusinessValueColor = (score: number) => {
    if (score >= 0.8) return 'text-green-600 bg-green-100';
    if (score >= 0.6) return 'text-yellow-600 bg-yellow-100';
    return 'text-red-600 bg-red-100';
  };

  const getSentimentColor = (score: number) => {
    if (score > 0.3) return 'text-green-600';
    if (score > -0.3) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getInsightTypeIcon = (type: string) => {
    switch (type) {
      case 'customer_feedback': return <MessageCircle className="h-4 w-4" />;
      case 'product_insight': return <Lightbulb className="h-4 w-4" />;
      case 'competitive_intel': return <Target className="h-4 w-4" />;
      case 'process_improvement': return <TrendingUp className="h-4 w-4" />;
      default: return <Brain className="h-4 w-4" />;
    }
  };

  const formatDuration = (minutes: number) => {
    if (minutes < 60) return `${minutes}m`;
    const hours = Math.floor(minutes / 60);
    const remainingMinutes = minutes % 60;
    return `${hours}h ${remainingMinutes}m`;
  };

  const formatNumber = (num: number) => {
    if (num >= 1000) return `${(num / 1000).toFixed(1)}K`;
    return num.toString();
  };

  // Mock data for demo (replace with actual API calls)
  const mockStats: SlackStats = {
    total_conversations: 2847,
    total_messages: 15623,
    active_channels: 24,
    insights_extracted: 156,
    knowledge_value_conversations: 423,
    avg_business_value_score: 0.73
  };

  const mockChannels: SlackChannel[] = [
    {
      channel_id: 'C123',
      channel_name: 'sales-team',
      business_function: 'Sales',
      conversation_count: 145,
      message_count: 892,
      unique_participants: 12,
      avg_business_value: 0.85,
      insights_extracted: 23,
      knowledge_value_score: 0.9,
      last_activity: '2024-01-21'
    },
    {
      channel_id: 'C456',
      channel_name: 'product-discussions',
      business_function: 'Product',
      conversation_count: 98,
      message_count: 567,
      unique_participants: 8,
      avg_business_value: 0.78,
      insights_extracted: 18,
      knowledge_value_score: 0.82,
      last_activity: '2024-01-21'
    },
    {
      channel_id: 'C789',
      channel_name: 'customer-feedback',
      business_function: 'Customer Success',
      conversation_count: 67,
      message_count: 423,
      unique_participants: 15,
      avg_business_value: 0.92,
      insights_extracted: 31,
      knowledge_value_score: 0.95,
      last_activity: '2024-01-20'
    }
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h3 className="text-lg font-semibold">Slack Knowledge Extraction</h3>
        <p className="text-sm text-gray-600">
          AI-powered insights from team conversations and institutional knowledge
        </p>
      </div>

      {/* Error Alert */}
      {error && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* Stats Overview */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-gray-600 flex items-center gap-2">
              <MessageSquare className="h-4 w-4" />
              Conversations
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{formatNumber(mockStats.total_conversations)}</div>
            <p className="text-xs text-gray-500">Total processed</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-gray-600 flex items-center gap-2">
              <Hash className="h-4 w-4" />
              Active Channels
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{mockStats.active_channels}</div>
            <p className="text-xs text-gray-500">Being monitored</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-gray-600 flex items-center gap-2">
              <Brain className="h-4 w-4" />
              Insights Extracted
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{mockStats.insights_extracted}</div>
            <p className="text-xs text-gray-500">AI-generated insights</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-gray-600 flex items-center gap-2">
              <TrendingUp className="h-4 w-4" />
              Business Value
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {(mockStats.avg_business_value_score * 100).toFixed(0)}%
            </div>
            <p className="text-xs text-gray-500">Average value score</p>
          </CardContent>
        </Card>
      </div>

      {/* View Selector */}
      <div className="flex gap-2">
        <Button
          variant={activeView === 'overview' ? 'default' : 'outline'}
          onClick={() => setActiveView('overview')}
        >
          <BarChart3 className="h-4 w-4 mr-2" />
          Overview
        </Button>
        <Button
          variant={activeView === 'conversations' ? 'default' : 'outline'}
          onClick={() => setActiveView('conversations')}
        >
          <MessageSquare className="h-4 w-4 mr-2" />
          Conversations
        </Button>
        <Button
          variant={activeView === 'insights' ? 'default' : 'outline'}
          onClick={() => setActiveView('insights')}
        >
          <Brain className="h-4 w-4 mr-2" />
          Insights
        </Button>
      </div>

      {/* Overview Tab */}
      {activeView === 'overview' && (
        <div className="space-y-6">
          {/* Channel Analytics */}
          <Card>
            <CardHeader>
              <CardTitle>Channel Knowledge Value</CardTitle>
              <CardDescription>
                Channels ranked by knowledge extraction potential and business value
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Channel</TableHead>
                    <TableHead>Function</TableHead>
                    <TableHead>Conversations</TableHead>
                    <TableHead>Participants</TableHead>
                    <TableHead>Business Value</TableHead>
                    <TableHead>Insights</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {mockChannels.map((channel) => (
                    <TableRow key={channel.channel_id}>
                      <TableCell className="font-medium">
                        #{channel.channel_name}
                      </TableCell>
                      <TableCell>
                        <Badge variant="outline">{channel.business_function}</Badge>
                      </TableCell>
                      <TableCell>{channel.conversation_count}</TableCell>
                      <TableCell>{channel.unique_participants}</TableCell>
                      <TableCell>
                        <div className="flex items-center gap-2">
                          <div className={`px-2 py-1 rounded text-xs ${getBusinessValueColor(channel.avg_business_value)}`}>
                            {(channel.avg_business_value * 100).toFixed(0)}%
                          </div>
                        </div>
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center gap-1">
                          <Brain className="h-3 w-3" />
                          {channel.insights_extracted}
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Conversations Tab */}
      {activeView === 'conversations' && (
        <div className="space-y-4">
          {/* Search and Filters */}
          <Card>
            <CardContent className="pt-6">
              <div className="flex gap-2 mb-4">
                <Input
                  placeholder="Search conversations..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleSearchConversations()}
                  className="flex-1"
                />
                <Button onClick={handleSearchConversations} disabled={loading}>
                  {loading ? (
                    <Loader2 className="h-4 w-4 animate-spin" />
                  ) : (
                    <Search className="h-4 w-4" />
                  )}
                </Button>
              </div>
              
              <div className="flex gap-4 items-center">
                <div className="flex items-center gap-2">
                  <Filter className="h-4 w-4" />
                  <span className="text-sm">Business Value:</span>
                  <input
                    type="range"
                    min="0"
                    max="1"
                    step="0.1"
                    value={businessValueFilter}
                    onChange={(e) => setBusinessValueFilter(parseFloat(e.target.value))}
                    className="w-20"
                  />
                  <span className="text-sm">{(businessValueFilter * 100).toFixed(0)}%+</span>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Conversations List */}
          <div className="space-y-3">
            {/* Mock conversations for demo */}
            {[
              {
                conversation_id: 'conv_1',
                conversation_title: 'Q4 Sales Strategy Discussion',
                channel_name: 'sales-team',
                participant_count: 8,
                message_count: 23,
                business_value_score: 0.92,
                sentiment_score: 0.65,
                contains_decisions: true,
                contains_action_items: true,
                start_time: '2024-01-21T14:30:00Z',
                duration_minutes: 45,
                conversation_summary: 'Discussion about Q4 sales targets, new customer acquisition strategies, and territory planning.',
                key_topics: ['sales targets', 'customer acquisition', 'territory planning']
              },
              {
                conversation_id: 'conv_2',
                conversation_title: 'Product Feature Feedback from Enterprise Client',
                channel_name: 'product-discussions',
                participant_count: 5,
                message_count: 18,
                business_value_score: 0.88,
                sentiment_score: 0.2,
                contains_decisions: false,
                contains_action_items: true,
                start_time: '2024-01-21T11:15:00Z',
                duration_minutes: 32,
                conversation_summary: 'Customer feedback on new dashboard features, reported usability issues, and requested improvements.',
                key_topics: ['customer feedback', 'dashboard features', 'usability']
              }
            ].map((conversation) => (
              <Card key={conversation.conversation_id}>
                <CardContent className="pt-4">
                  <div className="flex justify-between items-start mb-2">
                    <div className="flex-1">
                      <h4 className="font-medium">{conversation.conversation_title}</h4>
                      <div className="flex items-center gap-4 text-sm text-gray-500 mt-1">
                        <span>#{conversation.channel_name}</span>
                        <span>{conversation.participant_count} participants</span>
                        <span>{conversation.message_count} messages</span>
                        <span>{formatDuration(conversation.duration_minutes)}</span>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <div className={`px-2 py-1 rounded text-xs ${getBusinessValueColor(conversation.business_value_score)}`}>
                        {(conversation.business_value_score * 100).toFixed(0)}% value
                      </div>
                      <div className={`text-sm ${getSentimentColor(conversation.sentiment_score)}`}>
                        {conversation.sentiment_score > 0 ? '😊' : conversation.sentiment_score < 0 ? '😞' : '😐'}
                      </div>
                    </div>
                  </div>
                  
                  <p className="text-sm text-gray-600 mb-3">{conversation.conversation_summary}</p>
                  
                  <div className="flex items-center justify-between">
                    <div className="flex gap-2">
                      {conversation.key_topics.map((topic, index) => (
                        <Badge key={index} variant="secondary" className="text-xs">
                          {topic}
                        </Badge>
                      ))}
                    </div>
                    <div className="flex gap-2">
                      {conversation.contains_decisions && (
                        <Badge className="text-xs bg-blue-100 text-blue-800">
                          <CheckCircle className="h-3 w-3 mr-1" />
                          Decisions
                        </Badge>
                      )}
                      {conversation.contains_action_items && (
                        <Badge className="text-xs bg-orange-100 text-orange-800">
                          <Clock className="h-3 w-3 mr-1" />
                          Action Items
                        </Badge>
                      )}
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      )}

      {/* Insights Tab */}
      {activeView === 'insights' && (
        <div className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>AI-Extracted Knowledge Insights</CardTitle>
              <CardDescription>
                Insights extracted from Slack conversations that may be valuable for the knowledge base
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {/* Mock insights for demo */}
                {[
                  {
                    insight_id: 'insight_1',
                    insight_type: 'customer_feedback',
                    insight_category: 'product',
                    insight_title: 'Enterprise Dashboard Performance Issues',
                    insight_description: 'Multiple enterprise customers reported slow dashboard loading times, particularly with large datasets. Suggested optimization of data queries and caching mechanisms.',
                    confidence_score: 0.89,
                    business_impact: 'high',
                    is_actionable: true,
                    human_validated: false,
                    extracted_at: '2024-01-21T15:30:00Z',
                    conversation_title: 'Product Feature Feedback from Enterprise Client',
                    channel_name: 'product-discussions'
                  },
                  {
                    insight_id: 'insight_2',
                    insight_type: 'competitive_intel',
                    insight_category: 'sales',
                    insight_title: 'Competitor Pricing Strategy Change',
                    insight_description: 'Sales team discussed a major competitor reducing their pricing by 15% for enterprise deals. This may impact our Q4 deal closure rates.',
                    confidence_score: 0.92,
                    business_impact: 'high',
                    is_actionable: true,
                    human_validated: false,
                    extracted_at: '2024-01-21T14:45:00Z',
                    conversation_title: 'Q4 Sales Strategy Discussion',
                    channel_name: 'sales-team'
                  }
                ].map((insight) => (
                  <div key={insight.insight_id} className="border rounded-lg p-4">
                    <div className="flex justify-between items-start mb-3">
                      <div className="flex items-center gap-2">
                        {getInsightTypeIcon(insight.insight_type)}
                        <h5 className="font-medium">{insight.insight_title}</h5>
                        <Badge variant="outline">{insight.insight_category}</Badge>
                        <Badge className={`text-xs ${
                          insight.business_impact === 'high' ? 'bg-red-100 text-red-800' :
                          insight.business_impact === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                          'bg-green-100 text-green-800'
                        }`}>
                          {insight.business_impact} impact
                        </Badge>
                      </div>
                      <div className="text-sm text-gray-500">
                        {(insight.confidence_score * 100).toFixed(0)}% confidence
                      </div>
                    </div>
                    
                    <p className="text-sm text-gray-600 mb-3">{insight.insight_description}</p>
                    
                    <div className="flex justify-between items-center">
                      <div className="text-xs text-gray-500">
                        From #{insight.channel_name} • {insight.conversation_title}
                      </div>
                      
                      {!insight.human_validated && (
                        <div className="flex gap-2">
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => validateInsight(insight.insight_id, false)}
                          >
                            <XCircle className="h-3 w-3 mr-1" />
                            Reject
                          </Button>
                          <Button
                            size="sm"
                            onClick={() => validateInsight(insight.insight_id, true)}
                          >
                            <CheckCircle className="h-3 w-3 mr-1" />
                            Validate
                          </Button>
                        </div>
                      )}
                      
                      {insight.human_validated && (
                        <Badge className="text-xs bg-green-100 text-green-800">
                          <CheckCircle className="h-3 w-3 mr-1" />
                          Validated
                        </Badge>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
};

export default SlackKnowledgeTab; 
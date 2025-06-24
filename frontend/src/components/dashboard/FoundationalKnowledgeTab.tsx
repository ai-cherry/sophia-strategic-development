import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../ui/card';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Badge } from '../ui/badge';
import { Alert, AlertDescription } from '../ui/alert';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '../ui/table';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '../ui/select';
import {
  Users,
  Building2,
  Package,
  Target,
  FileText,
  Heart,
  Workflow,
  Search,
  RefreshCw,
  CheckCircle,
  AlertCircle,
  TrendingUp,
  BarChart3,
  Loader2
} from 'lucide-react';

interface FoundationalStats {
  total_foundational_records: number;
  data_types: {
    [key: string]: {
      count: number;
      avg_importance: number;
      last_updated: string;
    };
  };
  last_sync: string | null;
}

interface FoundationalInsights {
  departments: Array<{
    department: string;
    employee_count: number;
    job_titles: string[];
    avg_tenure_years: number;
  }>;
  customer_segments: Array<{
    segment: string;
    customer_count: number;
    avg_monthly_volume: number;
    industry_diversity: number;
  }>;
  competitive_landscape: Array<{
    threat_level: string;
    competitor_count: number;
    avg_win_rate_against_us: number;
    competitors: string[];
  }>;
  product_portfolio: Array<{
    category: string;
    product_count: number;
    total_mrr: number;
    avg_satisfaction: number;
  }>;
}

interface SearchResult {
  record_id: string;
  data_type: string;
  title: string;
  description: string;
  metadata: any;
  relevance_score: number;
}

const DATA_TYPE_CONFIG = {
  employee: {
    name: 'Employees',
    icon: Users,
    color: 'bg-blue-100 text-blue-800',
    description: 'Team members and organizational structure'
  },
  customer: {
    name: 'Customers',
    icon: Building2,
    color: 'bg-green-100 text-green-800',
    description: 'Customer profiles and relationship data'
  },
  product: {
    name: 'Products',
    icon: Package,
    color: 'bg-purple-100 text-purple-800',
    description: 'Product catalog and features'
  },
  competitor: {
    name: 'Competitors',
    icon: Target,
    color: 'bg-red-100 text-red-800',
    description: 'Competitive intelligence'
  },
  business_process: {
    name: 'Processes',
    icon: Workflow,
    color: 'bg-orange-100 text-orange-800',
    description: 'Business processes and procedures'
  },
  organizational_value: {
    name: 'Values',
    icon: Heart,
    color: 'bg-pink-100 text-pink-800',
    description: 'Mission, vision, and values'
  },
  knowledge_article: {
    name: 'Articles',
    icon: FileText,
    color: 'bg-gray-100 text-gray-800',
    description: 'Knowledge base articles'
  }
};

export const FoundationalKnowledgeTab: React.FC = () => {
  const [stats, setStats] = useState<FoundationalStats | null>(null);
  const [insights, setInsights] = useState<FoundationalInsights | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<SearchResult[]>([]);
  const [selectedDataTypes, setSelectedDataTypes] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [syncing, setSyncing] = useState(false);
  const [searching, setSearching] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Load foundational data on component mount
  useEffect(() => {
    loadFoundationalData();
  }, []);

  const loadFoundationalData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Load stats and insights in parallel
      const [statsResponse, insightsResponse] = await Promise.all([
        fetch('/api/v1/knowledge/foundational/stats'),
        fetch('/api/v1/knowledge/foundational/insights')
      ]);

      if (statsResponse.ok) {
        setStats(await statsResponse.json());
      }

      if (insightsResponse.ok) {
        const insightsData = await insightsResponse.json();
        setInsights(insightsData.insights);
      }

    } catch (error) {
      console.error('Failed to load foundational data:', error);
      setError('Failed to load foundational knowledge data');
    } finally {
      setLoading(false);
    }
  };

  const handleSync = async () => {
    try {
      setSyncing(true);
      setError(null);

      const response = await fetch('/api/v1/knowledge/foundational/sync', {
        method: 'POST'
      });

      if (response.ok) {
        const result = await response.json();
        // Reload data after successful sync
        await loadFoundationalData();
        // Show success message (you might want to add a toast notification here)
      } else {
        throw new Error('Sync failed');
      }

    } catch (error) {
      console.error('Sync failed:', error);
      setError('Failed to sync foundational knowledge');
    } finally {
      setSyncing(false);
    }
  };

  const handleSearch = async () => {
    if (!searchQuery.trim()) return;

    try {
      setSearching(true);
      setError(null);

      const params = new URLSearchParams({
        query: searchQuery,
        limit: '20'
      });

      // Add data type filters if selected
      selectedDataTypes.forEach(type => {
        params.append('data_types', type);
      });

      const response = await fetch(`/api/v1/knowledge/foundational/search?${params}`);
      
      if (response.ok) {
        const data = await response.json();
        setSearchResults(data.results);
      } else {
        throw new Error('Search failed');
      }

    } catch (error) {
      console.error('Search failed:', error);
      setError('Failed to search foundational knowledge');
      setSearchResults([]);
    } finally {
      setSearching(false);
    }
  };

  const getDataTypeIcon = (dataType: string) => {
    const config = DATA_TYPE_CONFIG[dataType as keyof typeof DATA_TYPE_CONFIG];
    const IconComponent = config?.icon || FileText;
    return <IconComponent className="h-4 w-4" />;
  };

  const getDataTypeBadge = (dataType: string) => {
    const config = DATA_TYPE_CONFIG[dataType as keyof typeof DATA_TYPE_CONFIG];
    return (
      <Badge className={config?.color || 'bg-gray-100 text-gray-800'}>
        {config?.name || dataType}
      </Badge>
    );
  };

  const formatNumber = (num: number) => {
    if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M`;
    if (num >= 1000) return `${(num / 1000).toFixed(1)}K`;
    return num.toString();
  };

  return (
    <div className="space-y-6">
      {/* Header with Sync Button */}
      <div className="flex justify-between items-center">
        <div>
          <h3 className="text-lg font-semibold">Foundational Knowledge</h3>
          <p className="text-sm text-gray-600">
            Pay Ready's core business information and organizational knowledge
          </p>
        </div>
        <Button 
          onClick={handleSync} 
          disabled={syncing}
          variant="outline"
        >
          {syncing ? (
            <Loader2 className="h-4 w-4 mr-2 animate-spin" />
          ) : (
            <RefreshCw className="h-4 w-4 mr-2" />
          )}
          {syncing ? 'Syncing...' : 'Sync Data'}
        </Button>
      </div>

      {/* Error Alert */}
      {error && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* Stats Overview */}
      {stats && (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-gray-600">
                Total Records
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {formatNumber(stats.total_foundational_records)}
              </div>
              <p className="text-xs text-gray-500">
                Across all data types
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-gray-600">
                Data Types
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {Object.keys(stats.data_types).length}
              </div>
              <p className="text-xs text-gray-500">
                Active categories
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-gray-600">
                Last Sync
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-sm font-bold">
                {stats.last_sync ? new Date(stats.last_sync).toLocaleDateString() : 'Never'}
              </div>
              <p className="text-xs text-gray-500">
                Most recent update
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-gray-600">
                Status
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center gap-1">
                <CheckCircle className="h-4 w-4 text-green-600" />
                <span className="text-sm font-bold">Active</span>
              </div>
              <p className="text-xs text-gray-500">
                Knowledge base ready
              </p>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Data Types Breakdown */}
      {stats && (
        <Card>
          <CardHeader>
            <CardTitle>Knowledge Categories</CardTitle>
            <CardDescription>
              Breakdown of foundational knowledge by data type
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid gap-3 md:grid-cols-2 lg:grid-cols-3">
              {Object.entries(stats.data_types).map(([dataType, info]) => (
                <div key={dataType} className="flex items-center justify-between p-3 border rounded-lg">
                  <div className="flex items-center gap-2">
                    {getDataTypeIcon(dataType)}
                    <div>
                      <div className="font-medium">
                        {DATA_TYPE_CONFIG[dataType as keyof typeof DATA_TYPE_CONFIG]?.name || dataType}
                      </div>
                      <div className="text-sm text-gray-500">
                        {formatNumber(info.count)} records
                      </div>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-sm font-medium">
                      {(info.avg_importance * 100).toFixed(0)}%
                    </div>
                    <div className="text-xs text-gray-500">importance</div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Search Interface */}
      <Card>
        <CardHeader>
          <CardTitle>Search Foundational Knowledge</CardTitle>
          <CardDescription>
            Search across all Pay Ready foundational data
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Search Input */}
          <div className="flex gap-2">
            <Input
              placeholder="Search employees, customers, products, competitors..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
              className="flex-1"
            />
            <Button onClick={handleSearch} disabled={searching || !searchQuery.trim()}>
              {searching ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Search className="h-4 w-4" />
              )}
            </Button>
          </div>

          {/* Data Type Filters */}
          <div className="flex flex-wrap gap-2">
            <span className="text-sm font-medium text-gray-600">Filter by type:</span>
            {Object.entries(DATA_TYPE_CONFIG).map(([type, config]) => (
              <Button
                key={type}
                variant={selectedDataTypes.includes(type) ? "default" : "outline"}
                size="sm"
                onClick={() => {
                  setSelectedDataTypes(prev => 
                    prev.includes(type) 
                      ? prev.filter(t => t !== type)
                      : [...prev, type]
                  );
                }}
              >
                <config.icon className="h-3 w-3 mr-1" />
                {config.name}
              </Button>
            ))}
          </div>

          {/* Search Results */}
          {searchResults.length > 0 && (
            <div className="space-y-2">
              <h4 className="font-medium">Search Results ({searchResults.length})</h4>
              <div className="space-y-2 max-h-96 overflow-y-auto">
                {searchResults.map((result, index) => (
                  <div key={index} className="p-3 border rounded-lg hover:bg-gray-50">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-2">
                          {getDataTypeIcon(result.data_type)}
                          <h5 className="font-medium">{result.title}</h5>
                          {getDataTypeBadge(result.data_type)}
                        </div>
                        <p className="text-sm text-gray-600 mt-1">{result.description}</p>
                        {result.metadata && (
                          <div className="text-xs text-gray-500 mt-2">
                            {Object.entries(result.metadata).slice(0, 3).map(([key, value]) => (
                              <span key={key} className="mr-3">
                                {key}: {String(value)}
                              </span>
                            ))}
                          </div>
                        )}
                      </div>
                      <div className="text-sm text-gray-500">
                        {(result.relevance_score * 100).toFixed(0)}% match
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Business Insights */}
      {insights && (
        <div className="grid gap-6 lg:grid-cols-2">
          {/* Department Analysis */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Users className="h-5 w-5" />
                Team Composition
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {insights.departments.slice(0, 5).map((dept, index) => (
                  <div key={index} className="flex items-center justify-between">
                    <div>
                      <div className="font-medium">{dept.department}</div>
                      <div className="text-sm text-gray-500">
                        {dept.avg_tenure_years.toFixed(1)} years avg tenure
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="font-medium">{dept.employee_count}</div>
                      <div className="text-xs text-gray-500">employees</div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Customer Segments */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Building2 className="h-5 w-5" />
                Customer Portfolio
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {insights.customer_segments.map((segment, index) => (
                  <div key={index} className="flex items-center justify-between">
                    <div>
                      <div className="font-medium">{segment.segment}</div>
                      <div className="text-sm text-gray-500">
                        ${formatNumber(segment.avg_monthly_volume)}/mo avg
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="font-medium">{segment.customer_count}</div>
                      <div className="text-xs text-gray-500">customers</div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Competitive Landscape */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Target className="h-5 w-5" />
                Competitive Landscape
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {insights.competitive_landscape.map((level, index) => (
                  <div key={index} className="flex items-center justify-between">
                    <div>
                      <div className="font-medium">{level.threat_level} Threat</div>
                      <div className="text-sm text-gray-500">
                        {(level.avg_win_rate_against_us * 100).toFixed(0)}% win rate
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="font-medium">{level.competitor_count}</div>
                      <div className="text-xs text-gray-500">competitors</div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Product Portfolio */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Package className="h-5 w-5" />
                Product Performance
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {insights.product_portfolio.map((category, index) => (
                  <div key={index} className="flex items-center justify-between">
                    <div>
                      <div className="font-medium">{category.category}</div>
                      <div className="text-sm text-gray-500">
                        {category.avg_satisfaction.toFixed(1)}/5 satisfaction
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="font-medium">${formatNumber(category.total_mrr)}</div>
                      <div className="text-xs text-gray-500">MRR</div>
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

export default FoundationalKnowledgeTab; 
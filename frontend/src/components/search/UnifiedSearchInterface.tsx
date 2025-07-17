import React, { useState, useEffect } from 'react';
import {
  Search,
  Globe,
  Code,
  BookOpen,
  Settings,
  Loader2,
  Link,
  Hash,
  TrendingUp,
  Brain,
  Zap,
  Shield,
  BarChart3,
  AlertCircle,
  CheckCircle
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Badge } from '../ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';
import { Alert, AlertDescription } from '../ui/alert';
import { Checkbox } from '../ui/checkbox';
import { Label } from '../ui/label';
import { ScrollArea } from '../ui/scroll-area';
import { useToast } from '../ui/use-toast';

interface SearchResult {
  title: string;
  snippet: string;
  url: string;
  source: string;
  score: number;
  timestamp?: string;
}

interface SearchStats {
  total_searches: number;
  playwright_searches: number;
  apify_searches: number;
  zenrows_searches: number;
  cache_hits: number;
  avg_response_time: number;
}

export const UnifiedSearchInterface: React.FC = () => {
  const [query, setQuery] = useState('');
  const [strategy, setStrategy] = useState('auto');
  const [sources, setSources] = useState<string[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [results, setResults] = useState<SearchResult[]>([]);
  const [stats, setStats] = useState<SearchStats | null>(null);
  const [activeTab, setActiveTab] = useState('web');
  const { toast } = useToast();

  // Available sources by category
  const sourcesConfig = {
    general: ['duckduckgo', 'wikipedia', 'news'],
    technical: ['github', 'stackoverflow', 'hackernews'],
    academic: ['arxiv', 'scholar', 'pubmed'],
    social: ['reddit', 'linkedin', 'twitter']
  };

  const allSources = Object.values(sourcesConfig).flat();

  const handleSearch = async () => {
    if (!query.trim()) {
      toast({
        title: "Search query required",
        description: "Please enter a search query",
        variant: "destructive"
      });
      return;
    }

    setIsSearching(true);
    setResults([]);

    try {
      // Call the search API based on active tab
      let endpoint = '/api/search/web';
      let payload: any = {
        query,
        strategy,
        sources: sources.length > 0 ? sources : undefined,
        max_results: 30
      };

      if (activeTab === 'code') {
        endpoint = '/api/search/code';
      } else if (activeTab === 'academic') {
        endpoint = '/api/search/academic';
      }

      const response = await fetch(endpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload)
      });

      if (!response.ok) {
        throw new Error('Search failed');
      }

      const data = await response.json();
      
      // Parse results from the response
      if (data.results) {
        setResults(data.results);
      }

      toast({
        title: "Search completed",
        description: `Found ${data.results?.length || 0} results in ${data.response_time?.toFixed(2) || '0'}s`
      });

    } catch (error) {
      console.error('Search error:', error);
      toast({
        title: "Search failed",
        description: "An error occurred while searching",
        variant: "destructive"
      });
    } finally {
      setIsSearching(false);
    }
  };

  const handleSourceToggle = (source: string) => {
    setSources(prev => 
      prev.includes(source) 
        ? prev.filter(s => s !== source)
        : [...prev, source]
    );
  };

  const loadStats = async () => {
    try {
      const response = await fetch('/api/search/stats');
      const data = await response.json();
      setStats(data);
    } catch (error) {
      console.error('Failed to load stats:', error);
    }
  };

  useEffect(() => {
    loadStats();
    const interval = setInterval(loadStats, 30000); // Refresh every 30s
    return () => clearInterval(interval);
  }, []);

  const getStrategyIcon = (strat: string) => {
    switch (strat) {
      case 'fast': return <Zap className="w-4 h-4" />;
      case 'scale': return <TrendingUp className="w-4 h-4" />;
      case 'stealth': return <Shield className="w-4 h-4" />;
      case 'hybrid': return <Brain className="w-4 h-4" />;
      default: return <Search className="w-4 h-4" />;
    }
  };

  const getSourceIcon = (source: string) => {
    if (source.includes('github')) return <Code className="w-4 h-4" />;
    if (source.includes('stackoverflow')) return <Hash className="w-4 h-4" />;
    if (source.includes('arxiv') || source.includes('scholar')) return <BookOpen className="w-4 h-4" />;
    return <Globe className="w-4 h-4" />;
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">Unified Search</h2>
          <p className="text-muted-foreground">
            Intelligent web search with Playwright, Apify, and ZenRows
          </p>
        </div>
        {stats && (
          <Card className="p-4">
            <div className="flex items-center space-x-4 text-sm">
              <div>
                <p className="font-medium">{stats.total_searches}</p>
                <p className="text-muted-foreground">Total Searches</p>
              </div>
              <div>
                <p className="font-medium">{((stats.cache_hits / Math.max(stats.total_searches, 1)) * 100).toFixed(0)}%</p>
                <p className="text-muted-foreground">Cache Hit Rate</p>
              </div>
              <div>
                <p className="font-medium">{stats.avg_response_time.toFixed(2)}s</p>
                <p className="text-muted-foreground">Avg Response</p>
              </div>
            </div>
          </Card>
        )}
      </div>

      {/* Search Interface */}
      <Card>
        <CardContent className="p-6">
          <Tabs value={activeTab} onValueChange={setActiveTab}>
            <TabsList className="grid w-full grid-cols-3">
              <TabsTrigger value="web">
                <Globe className="w-4 h-4 mr-2" />
                Web Search
              </TabsTrigger>
              <TabsTrigger value="code">
                <Code className="w-4 h-4 mr-2" />
                Code Search
              </TabsTrigger>
              <TabsTrigger value="academic">
                <BookOpen className="w-4 h-4 mr-2" />
                Academic Search
              </TabsTrigger>
            </TabsList>

            <TabsContent value="web" className="space-y-4">
              <div className="flex space-x-2">
                <Input
                  placeholder="Search the web..."
                  value={query}
                  onChange={(e: React.ChangeEvent<HTMLInputElement>) => setQuery(e.target.value)}
                  onKeyPress={(e: React.KeyboardEvent) => e.key === 'Enter' && handleSearch()}
                  className="flex-1"
                />
                <Select value={strategy} onValueChange={setStrategy}>
                  <SelectTrigger className="w-[180px]">
                    <div className="flex items-center">
                      {getStrategyIcon(strategy)}
                      <SelectValue placeholder="Strategy" className="ml-2" />
                    </div>
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="auto">
                      <div className="flex items-center">
                        <Search className="w-4 h-4 mr-2" />
                        Auto (Smart)
                      </div>
                    </SelectItem>
                    <SelectItem value="fast">
                      <div className="flex items-center">
                        <Zap className="w-4 h-4 mr-2" />
                        Fast (Playwright)
                      </div>
                    </SelectItem>
                    <SelectItem value="scale">
                      <div className="flex items-center">
                        <TrendingUp className="w-4 h-4 mr-2" />
                        Scale (Apify)
                      </div>
                    </SelectItem>
                    <SelectItem value="stealth">
                      <div className="flex items-center">
                        <Shield className="w-4 h-4 mr-2" />
                        Stealth (ZenRows)
                      </div>
                    </SelectItem>
                    <SelectItem value="hybrid">
                      <div className="flex items-center">
                        <Brain className="w-4 h-4 mr-2" />
                        Hybrid (All)
                      </div>
                    </SelectItem>
                  </SelectContent>
                </Select>
                <Button 
                  onClick={handleSearch} 
                  disabled={isSearching}
                  className="min-w-[100px]"
                >
                  {isSearching ? (
                    <>
                      <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                      Searching...
                    </>
                  ) : (
                    <>
                      <Search className="w-4 h-4 mr-2" />
                      Search
                    </>
                  )}
                </Button>
              </div>

              {/* Source Selection */}
              <div className="space-y-2">
                <Label>Sources (optional)</Label>
                <div className="grid grid-cols-4 gap-2">
                  {Object.entries(sourcesConfig).map(([category, categorySources]) => (
                    <div key={category} className="space-y-2">
                      <p className="text-sm font-medium capitalize">{category}</p>
                      {categorySources.map(source => (
                        <div key={source} className="flex items-center space-x-2">
                          <Checkbox
                            id={source}
                            checked={sources.includes(source)}
                            onCheckedChange={() => handleSourceToggle(source)}
                          />
                          <Label
                            htmlFor={source}
                            className="text-sm font-normal cursor-pointer flex items-center"
                          >
                            {getSourceIcon(source)}
                            <span className="ml-1">{source}</span>
                          </Label>
                        </div>
                      ))}
                    </div>
                  ))}
                </div>
              </div>
            </TabsContent>

            <TabsContent value="code" className="space-y-4">
              <div className="flex space-x-2">
                <Input
                  placeholder="Search for code, functions, repositories..."
                  value={query}
                  onChange={(e: React.ChangeEvent<HTMLInputElement>) => setQuery(e.target.value)}
                  onKeyPress={(e: React.KeyboardEvent) => e.key === 'Enter' && handleSearch()}
                  className="flex-1"
                />
                <Button 
                  onClick={handleSearch} 
                  disabled={isSearching}
                >
                  {isSearching ? (
                    <>
                      <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                      Searching...
                    </>
                  ) : (
                    <>
                      <Code className="w-4 h-4 mr-2" />
                      Search Code
                    </>
                  )}
                </Button>
              </div>
              <Alert>
                <Code className="w-4 h-4" />
                <AlertDescription>
                  Searches GitHub repositories and Stack Overflow for code examples
                </AlertDescription>
              </Alert>
            </TabsContent>

            <TabsContent value="academic" className="space-y-4">
              <div className="flex space-x-2">
                <Input
                  placeholder="Search academic papers and research..."
                  value={query}
                  onChange={(e: React.ChangeEvent<HTMLInputElement>) => setQuery(e.target.value)}
                  onKeyPress={(e: React.KeyboardEvent) => e.key === 'Enter' && handleSearch()}
                  className="flex-1"
                />
                <Button 
                  onClick={handleSearch} 
                  disabled={isSearching}
                >
                  {isSearching ? (
                    <>
                      <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                      Searching...
                    </>
                  ) : (
                    <>
                      <BookOpen className="w-4 h-4 mr-2" />
                      Search Papers
                    </>
                  )}
                </Button>
              </div>
              <Alert>
                <BookOpen className="w-4 h-4" />
                <AlertDescription>
                  Searches arXiv, Google Scholar, and PubMed for academic content
                </AlertDescription>
              </Alert>
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>

      {/* Search Results */}
      {results.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Search Results ({results.length})</CardTitle>
          </CardHeader>
          <CardContent>
            <ScrollArea className="h-[600px] pr-4">
              <div className="space-y-4">
                {results.map((result, index) => (
                  <div key={index} className="p-4 border rounded-lg hover:bg-accent/50 transition-colors">
                    <div className="flex items-start justify-between">
                      <div className="flex-1 space-y-1">
                        <div className="flex items-center space-x-2">
                          {getSourceIcon(result.source)}
                          <Badge variant="secondary">{result.source}</Badge>
                          <Badge variant="outline">
                            Score: {result.score.toFixed(2)}
                          </Badge>
                        </div>
                        <h3 className="font-semibold text-lg">
                          <a 
                            href={result.url} 
                            target="_blank" 
                            rel="noopener noreferrer"
                            className="hover:underline flex items-center"
                          >
                            {result.title}
                            <Link className="w-4 h-4 ml-1" />
                          </a>
                        </h3>
                        <p className="text-muted-foreground">
                          {result.snippet}
                        </p>
                        <p className="text-sm text-muted-foreground">
                          {result.url}
                        </p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </ScrollArea>
          </CardContent>
        </Card>
      )}

      {/* Search Stats */}
      {stats && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <BarChart3 className="w-5 h-5 mr-2" />
              Search Performance Stats
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-3 gap-4">
              <div className="space-y-2">
                <p className="text-sm font-medium">Playwright (Fast)</p>
                <p className="text-2xl font-bold">{stats.playwright_searches}</p>
                <p className="text-xs text-muted-foreground">For standard sites</p>
              </div>
              <div className="space-y-2">
                <p className="text-sm font-medium">Apify (Scale)</p>
                <p className="text-2xl font-bold">{stats.apify_searches}</p>
                <p className="text-xs text-muted-foreground">For volume searches</p>
              </div>
              <div className="space-y-2">
                <p className="text-sm font-medium">ZenRows (Stealth)</p>
                <p className="text-2xl font-bold">{stats.zenrows_searches}</p>
                <p className="text-xs text-muted-foreground">For protected sites</p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

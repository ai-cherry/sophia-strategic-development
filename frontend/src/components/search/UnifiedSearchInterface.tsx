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
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Checkbox } from '@/components/ui/checkbox';
import { Label } from '@/components/ui/label';
import { ScrollArea } from '@/components/ui/scroll-area';
import { useToast } from '@/components/ui/use-toast';

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

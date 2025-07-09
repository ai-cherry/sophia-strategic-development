import React, { useState, useEffect, useRef } from 'react';
import { Search, Filter, Settings, Loader, ExternalLink, Clock, Star, AlertCircle } from 'lucide-react';

interface SearchResult {
  type: string;
  provider?: string;
  data?: any[];
  metadata?: any;
  processing_time?: number;
  confidence?: number;
  cached?: boolean;
  message?: string;
  timestamp?: string;
  error?: string;
}

interface SearchProvider {
  name: string;
  display_name: string;
  description: string;
  supported_tiers: string[];
}

interface SearchTier {
  name: string;
  display_name: string;
  description: string;
  aliases: string[];
}

interface ProvidersResponse {
  providers: SearchProvider[];
  tiers: SearchTier[];
}

const EnhancedSearchInterface: React.FC = () => {
  const [query, setQuery] = useState('');
  const [selectedTier, setSelectedTier] = useState('tier_1');
  const [selectedProviders, setSelectedProviders] = useState<string[]>([]);
  const [results, setResults] = useState<SearchResult[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [availableProviders, setAvailableProviders] = useState<SearchProvider[]>([]);
  const [availableTiers, setAvailableTiers] = useState<SearchTier[]>([]);
  const [showSettings, setShowSettings] = useState(false);
  const [maxResults, setMaxResults] = useState(10);
  const [safeSearch, setSafeSearch] = useState(true);
  const [searchDomains, setSearchDomains] = useState('');
  const [excludeDomains, setExcludeDomains] = useState('');
  const [useIntelligentRouting, setUseIntelligentRouting] = useState(false);
  
  const eventSourceRef = useRef<EventSource | null>(null);
  const resultsRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    loadProviders();
    return () => {
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
      }
    };
  }, []);

  const loadProviders = async () => {
    try {
      const response = await fetch('/api/v1/search/providers');
      const data: ProvidersResponse = await response.json();
      setAvailableProviders(data.providers);
      setAvailableTiers(data.tiers);
    } catch (error) {
      console.error('Failed to load providers:', error);
    }
  };

  const handleSearch = async () => {
    if (!query.trim()) return;
    
    setIsSearching(true);
    setResults([]);
    
    try {
      if (useIntelligentRouting) {
        await performIntelligentSearch();
      } else {
        await performStreamingSearch();
      }
    } catch (error) {
      console.error('Search failed:', error);
      setResults([{
        type: 'error',
        message: 'Search failed. Please try again.',
        timestamp: new Date().toISOString()
      }]);
    } finally {
      setIsSearching(false);
    }
  };

  const performIntelligentSearch = async () => {
    const params = new URLSearchParams({
      query,
      user_id: 'anonymous',
      session_id: 'default'
    });

    const response = await fetch(`/api/v1/search/search/intelligent?${params}`);
    const data = await response.json();
    
    if (data.results) {
      setResults(data.results);
    }
  };

  const performStreamingSearch = async () => {
    const params = new URLSearchParams({
      query,
      tier: selectedTier,
      providers: selectedProviders.join(','),
      max_results: maxResults.toString(),
      user_id: 'anonymous',
      session_id: 'default',
      search_domains: searchDomains,
      exclude_domains: excludeDomains,
      safe_search: safeSearch.toString()
    });

    const eventSource = new EventSource(`/api/v1/search/search/stream?${params}`);
    eventSourceRef.current = eventSource;

    eventSource.onmessage = (event) => {
      try {
        const result: SearchResult = JSON.parse(event.data);
        setResults(prev => [...prev, result]);
        
        // Auto-scroll to bottom
        if (resultsRef.current) {
          resultsRef.current.scrollTop = resultsRef.current.scrollHeight;
        }
      } catch (error) {
        console.error('Failed to parse search result:', error);
      }
    };

    eventSource.onerror = (error) => {
      console.error('EventSource failed:', error);
      eventSource.close();
      setIsSearching(false);
    };

    // Close connection after 5 minutes
    setTimeout(() => {
      eventSource.close();
      setIsSearching(false);
    }, 300000);
  };

  const handleProviderToggle = (provider: string) => {
    setSelectedProviders(prev => 
      prev.includes(provider) 
        ? prev.filter(p => p !== provider)
        : [...prev, provider]
    );
  };

  const getTierColor = (tier: string) => {
    switch (tier) {
      case 'tier_1': return 'text-green-400';
      case 'tier_2': return 'text-yellow-400';
      case 'tier_3': return 'text-red-400';
      default: return 'text-gray-400';
    }
  };

  const getProviderIcon = (provider: string) => {
    switch (provider) {
      case 'brave': return '🦁';
      case 'searxng': return '🔍';
      case 'perplexity': return '🤖';
      case 'browser': return '🌐';
      case 'internal': return '🏠';
      default: return '📡';
    }
  };

  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleTimeString();
  };

  const renderResult = (result: SearchResult, index: number) => {
    if (result.type === 'status') {
      return (
        <div key={index} className="flex items-center space-x-2 p-3 mb-2 bg-blue-500/10 backdrop-blur-sm rounded-lg border border-blue-500/20">
          <Loader className="w-4 h-4 animate-spin text-blue-400" />
          <span className="text-blue-400">{result.message}</span>
          <span className="text-xs text-gray-400">{result.timestamp && formatTimestamp(result.timestamp)}</span>
        </div>
      );
    }

    if (result.type === 'error') {
      return (
        <div key={index} className="flex items-center space-x-2 p-3 mb-2 bg-red-500/10 backdrop-blur-sm rounded-lg border border-red-500/20">
          <AlertCircle className="w-4 h-4 text-red-400" />
          <span className="text-red-400">{result.message}</span>
        </div>
      );
    }

    if (result.type === 'cache_hit') {
      return (
        <div key={index} className="flex items-center space-x-2 p-3 mb-2 bg-green-500/10 backdrop-blur-sm rounded-lg border border-green-500/20">
          <Star className="w-4 h-4 text-green-400" />
          <span className="text-green-400">{result.message}</span>
        </div>
      );
    }

    if (result.type === 'result' && result.data) {
      return (
        <div key={index} className="mb-4 p-4 bg-white/5 backdrop-blur-sm rounded-lg border border-white/10">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center space-x-2">
              <span className="text-lg">{getProviderIcon(result.provider || '')}</span>
              <span className="text-sm font-medium text-gray-300">{result.provider}</span>
              {result.cached && <span className="text-xs bg-green-500/20 text-green-400 px-2 py-1 rounded">Cached</span>}
            </div>
            <div className="flex items-center space-x-2 text-xs text-gray-400">
              {result.processing_time && (
                <div className="flex items-center space-x-1">
                  <Clock className="w-3 h-3" />
                  <span>{result.processing_time.toFixed(2)}s</span>
                </div>
              )}
              {result.confidence && (
                <div className="flex items-center space-x-1">
                  <Star className="w-3 h-3" />
                  <span>{(result.confidence * 100).toFixed(0)}%</span>
                </div>
              )}
            </div>
          </div>
          
          <div className="space-y-2">
            {result.data.map((item, itemIndex) => (
              <div key={itemIndex} className="p-3 bg-white/5 rounded-lg border border-white/10">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <h4 className="font-medium text-white mb-1">{item.title}</h4>
                    <p className="text-sm text-gray-300 mb-2">{item.snippet || item.content}</p>
                    {item.url && (
                      <a 
                        href={item.url} 
                        target="_blank" 
                        rel="noopener noreferrer"
                        className="text-xs text-blue-400 hover:text-blue-300 flex items-center space-x-1"
                      >
                        <ExternalLink className="w-3 h-3" />
                        <span>{item.url}</span>
                      </a>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      );
    }

    if (result.type === 'synthesis') {
      return (
        <div key={index} className="mb-4 p-4 bg-purple-500/10 backdrop-blur-sm rounded-lg border border-purple-500/20">
          <h3 className="font-medium text-purple-400 mb-2">AI Synthesis</h3>
          <p className="text-gray-300 whitespace-pre-wrap">{result.data?.synthesis}</p>
          {result.data?.confidence && (
            <div className="mt-2 text-xs text-gray-400">
              Confidence: {(result.data.confidence * 100).toFixed(0)}%
            </div>
          )}
        </div>
      );
    }

    return null;
  };

  return (
    <div className="max-w-6xl mx-auto p-6">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-white mb-2">Enhanced Search</h1>
        <p className="text-gray-400">Multi-tier search with AI-powered analysis</p>
      </div>

      {/* Search Form */}
      <div className="mb-6 p-6 bg-white/5 backdrop-blur-sm rounded-lg border border-white/10">
        <div className="flex space-x-4 mb-4">
          <div className="flex-1">
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
              placeholder="Enter your search query..."
              className="w-full p-3 bg-white/10 backdrop-blur-sm rounded-lg border border-white/20 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <button
            onClick={handleSearch}
            disabled={isSearching || !query.trim()}
            className="px-6 py-3 bg-blue-500 hover:bg-blue-600 disabled:bg-gray-600 disabled:cursor-not-allowed rounded-lg text-white font-medium flex items-center space-x-2"
          >
            {isSearching ? (
              <Loader className="w-4 h-4 animate-spin" />
            ) : (
              <Search className="w-4 h-4" />
            )}
            <span>{isSearching ? 'Searching...' : 'Search'}</span>
          </button>
          <button
            onClick={() => setShowSettings(!showSettings)}
            className="p-3 bg-gray-600 hover:bg-gray-700 rounded-lg text-white"
          >
            <Settings className="w-4 h-4" />
          </button>
        </div>

        {/* Tier Selection */}
        <div className="flex items-center space-x-4 mb-4">
          <span className="text-sm text-gray-300">Search Tier:</span>
          {availableTiers.map((tier) => (
            <button
              key={tier.name}
              onClick={() => setSelectedTier(tier.name)}
              className={`px-3 py-1 rounded-lg text-sm font-medium border ${
                selectedTier === tier.name
                  ? 'bg-blue-500 border-blue-500 text-white'
                  : 'bg-gray-700 border-gray-600 text-gray-300 hover:bg-gray-600'
              }`}
            >
              {tier.display_name}
            </button>
          ))}
        </div>

        {/* Intelligent Routing Toggle */}
        <div className="flex items-center space-x-2 mb-4">
          <input
            type="checkbox"
            id="intelligent-routing"
            checked={useIntelligentRouting}
            onChange={(e) => setUseIntelligentRouting(e.target.checked)}
            className="rounded"
          />
          <label htmlFor="intelligent-routing" className="text-sm text-gray-300">
            Use intelligent routing (automatically select best tier)
          </label>
        </div>

        {/* Settings Panel */}
        {showSettings && (
          <div className="mt-4 p-4 bg-white/5 backdrop-blur-sm rounded-lg border border-white/10">
            <h3 className="font-medium text-white mb-3">Search Settings</h3>
            
            {/* Providers */}
            <div className="mb-4">
              <label className="block text-sm text-gray-300 mb-2">Providers:</label>
              <div className="flex flex-wrap gap-2">
                {availableProviders.map((provider) => (
                  <button
                    key={provider.name}
                    onClick={() => handleProviderToggle(provider.name)}
                    className={`px-3 py-1 rounded-lg text-sm border ${
                      selectedProviders.includes(provider.name)
                        ? 'bg-blue-500 border-blue-500 text-white'
                        : 'bg-gray-700 border-gray-600 text-gray-300 hover:bg-gray-600'
                    }`}
                  >
                    {getProviderIcon(provider.name)} {provider.display_name}
                  </button>
                ))}
              </div>
            </div>

            {/* Other Settings */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm text-gray-300 mb-1">Max Results:</label>
                <input
                  type="number"
                  value={maxResults}
                  onChange={(e) => setMaxResults(parseInt(e.target.value))}
                  min="1"
                  max="100"
                  className="w-full p-2 bg-white/10 backdrop-blur-sm rounded border border-white/20 text-white"
                />
              </div>
              <div>
                <label className="block text-sm text-gray-300 mb-1">Safe Search:</label>
                <input
                  type="checkbox"
                  checked={safeSearch}
                  onChange={(e) => setSafeSearch(e.target.checked)}
                  className="rounded"
                />
              </div>
              <div>
                <label className="block text-sm text-gray-300 mb-1">Search Domains:</label>
                <input
                  type="text"
                  value={searchDomains}
                  onChange={(e) => setSearchDomains(e.target.value)}
                  placeholder="domain1.com,domain2.com"
                  className="w-full p-2 bg-white/10 backdrop-blur-sm rounded border border-white/20 text-white"
                />
              </div>
              <div>
                <label className="block text-sm text-gray-300 mb-1">Exclude Domains:</label>
                <input
                  type="text"
                  value={excludeDomains}
                  onChange={(e) => setExcludeDomains(e.target.value)}
                  placeholder="spam.com,ads.com"
                  className="w-full p-2 bg-white/10 backdrop-blur-sm rounded border border-white/20 text-white"
                />
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Results */}
      <div 
        ref={resultsRef}
        className="space-y-4 max-h-96 overflow-y-auto"
      >
        {results.length === 0 && !isSearching && (
          <div className="text-center py-12 text-gray-400">
            <Search className="w-12 h-12 mx-auto mb-4 opacity-50" />
            <p>Enter a search query to get started</p>
          </div>
        )}

        {results.map((result, index) => renderResult(result, index))}
      </div>
    </div>
  );
};

export default EnhancedSearchInterface; 
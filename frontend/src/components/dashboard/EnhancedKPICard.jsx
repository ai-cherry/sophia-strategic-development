import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Badge } from '../ui/badge';
import { Button } from '../ui/button';
import { TrendingUp, TrendingDown, AlertTriangle, Info, Brain, ChevronDown, ChevronUp } from 'lucide-react';
import { cn } from '../../lib/utils';

const EnhancedKPICard = ({ 
  title, 
  value, 
  previousValue, 
  format = 'number',
  insight = null,
  prediction = null,
  className = '',
}) => {
  const [showDetails, setShowDetails] = useState(false);

  const calculateChange = () => {
    if (previousValue === null || previousValue === undefined || value === null || value === undefined || previousValue === 0) return 0;
    return ((value - previousValue) / previousValue) * 100;
  };

  const formatValue = (val) => {
    if (val === null || val === undefined) return 'N/A';
    switch (format) {
      case 'currency':
        return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', minimumFractionDigits: 0, maximumFractionDigits: 0 }).format(val);
      case 'percentage':
        return `${val.toFixed(1)}%`;
      case 'score':
        return val.toFixed(1);
      default:
        return new Intl.NumberFormat('en-US').format(val);
    }
  };

  const change = calculateChange();
  const isPositive = change > 0;
  const isNegative = change < 0;

  const getInsightColor = (priority) => {
    switch (priority) {
      case 'critical': return 'bg-red-500/20 text-red-400 border-red-500/50';
      case 'high': return 'bg-orange-500/20 text-orange-400 border-orange-500/50';
      case 'medium': return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/50';
      default: return 'bg-blue-500/20 text-blue-400 border-blue-500/50';
    }
  };

  return (
    <Card className={cn("bg-white/10 backdrop-blur-xl border-white/20 text-white", className)}>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="text-sm font-medium">{title}</CardTitle>
          {insight && (
            <Badge variant="outline" className={cn("text-xs", getInsightColor(insight.priority))}>
              <Brain className="w-3 h-3 mr-1" /> AI Insight
            </Badge>
          )}
        </div>
      </CardHeader>
      
      <CardContent className="pt-0">
        <p className="text-3xl font-bold">{formatValue(value)}</p>
        {previousValue !== null && previousValue !== undefined && (
          <div className={`flex items-center text-sm ${isPositive ? "text-green-400" : isNegative ? "text-red-400" : "text-gray-400"}`}>
            {isPositive && <TrendingUp className="w-4 h-4 mr-1" />}
            {isNegative && <TrendingDown className="w-4 h-4 mr-1" />}
            {change.toFixed(1)}% vs previous period
          </div>
        )}

        {prediction && (
          <div className="mt-4 p-3 bg-purple-500/20 rounded-lg border border-purple-500/30">
            <div className="text-sm font-medium text-purple-300">AI Prediction</div>
            <p className="text-sm text-white/90">Predicted {formatValue(prediction.prediction_value)}</p>
          </div>
        )}

        {insight && (
          <div className="mt-4">
            <Button variant="ghost" size="sm" onClick={() => setShowDetails(!showDetails)} className="text-xs text-white/70 hover:text-white">
              {showDetails ? <ChevronUp className="w-4 h-4 mr-1" /> : <ChevronDown className="w-4 h-4 mr-1" />}
              {showDetails ? 'Hide Details' : 'Show Insight'}
            </Button>
            {showDetails && (
              <div className={cn("mt-2 p-3 rounded-lg border", getInsightColor(insight.priority))}>
                <p className="text-sm font-medium">{insight.title}</p>
                <p className="text-xs opacity-90 mt-1">{insight.description}</p>
                {insight.actionable_recommendations?.length > 0 && (
                  <div className="mt-2 pt-2 border-t border-current/20">
                    <p className="text-xs font-bold">Recommendations:</p>
                    <ul className="list-disc list-inside text-xs mt-1">
                      {insight.actionable_recommendations.map((rec, i) => <li key={i}>{rec}</li>)}
                    </ul>
                  </div>
                )}
              </div>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default EnhancedKPICard; 
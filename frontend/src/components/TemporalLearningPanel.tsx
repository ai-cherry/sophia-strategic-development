import React, { useState, useEffect } from 'react';
import { Clock, Brain, TrendingUp, AlertCircle, CheckCircle, XCircle } from 'lucide-react';

interface TemporalLearningPanelProps {
  onCorrection?: (interactionId: string, correction: string) => void;
  onValidation?: (interactionId: string, isCorrect: boolean, feedback?: string) => void;
}

interface LearningInteraction {
  id: string;
  user_question: string;
  system_response: string;
  user_correction: string;
  learning_type: string;
  confidence: string;
  timestamp: string;
  validated: boolean;
  applied: boolean;
  context: Record<string, any>;
}

interface LearningInsights {
  total_interactions: number;
  learning_accuracy: number;
  knowledge_concepts: number;
  system_status: string;
  recent_interactions: LearningInteraction[];
  learning_suggestions: string[];
}

export const TemporalLearningPanel: React.FC<TemporalLearningPanelProps> = ({
  onCorrection,
  onValidation
}) => {
  const [insights, setInsights] = useState<LearningInsights | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'overview' | 'interactions' | 'suggestions'>('overview');
  const [correctionText, setCorrectionText] = useState('');
  const [selectedInteraction, setSelectedInteraction] = useState<string | null>(null);

  useEffect(() => {
    loadTemporalLearningData();
    const interval = setInterval(loadTemporalLearningData, 30000); // Refresh every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const loadTemporalLearningData = async () => {
    try {
      const response = await fetch('/api/v1/temporal-learning/dashboard/data');
      if (!response.ok) {
        throw new Error('Failed to load temporal learning data');
      }
      const data = await response.json();
      setInsights(data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      console.error('Error loading temporal learning data:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCorrection = async (interactionId: string) => {
    if (!correctionText.trim()) return;
    
    try {
      const response = await fetch('/api/v1/temporal-learning/chat/correct', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          interaction_id: interactionId,
          correction: correctionText,
          context: { timestamp: new Date().toISOString() }
        })
      });
      
      if (!response.ok) {
        throw new Error('Failed to submit correction');
      }
      
      setCorrectionText('');
      setSelectedInteraction(null);
      onCorrection?.(interactionId, correctionText);
      await loadTemporalLearningData(); // Refresh data
    } catch (err) {
      console.error('Error submitting correction:', err);
    }
  };

  const handleValidation = async (interactionId: string, isCorrect: boolean, feedback?: string) => {
    try {
      const response = await fetch(`/api/v1/temporal-learning/interactions/${interactionId}/validate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          interaction_id: interactionId,
          is_correct: isCorrect,
          feedback
        })
      });
      
      if (!response.ok) {
        throw new Error('Failed to validate interaction');
      }
      
      onValidation?.(interactionId, isCorrect, feedback);
      await loadTemporalLearningData(); // Refresh data
    } catch (err) {
      console.error('Error validating interaction:', err);
    }
  };

  const getConfidenceColor = (confidence: string) => {
    switch (confidence) {
      case 'high':
      case 'verified':
        return 'text-green-600';
      case 'medium':
        return 'text-yellow-600';
      case 'low':
        return 'text-red-600';
      default:
        return 'text-gray-600';
    }
  };

  const getLearningTypeIcon = (type: string) => {
    switch (type) {
      case 'date_correction':
        return <Clock className="w-4 h-4 text-blue-600" />;
      case 'time_context':
        return <Clock className="w-4 h-4 text-purple-600" />;
      case 'current_events':
        return <TrendingUp className="w-4 h-4 text-green-600" />;
      default:
        return <Brain className="w-4 h-4 text-gray-600" />;
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
          <p className="text-gray-600">Error loading temporal learning data</p>
          <p className="text-sm text-gray-500 mt-2">{error}</p>
          <button
            onClick={loadTemporalLearningData}
            className="mt-4 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center">
          <Brain className="w-6 h-6 text-blue-600 mr-3" />
          <h3 className="text-xl font-semibold">Temporal Learning System</h3>
        </div>
        <div className="flex space-x-2">
          <button
            onClick={() => setActiveTab('overview')}
            className={`px-4 py-2 rounded ${
              activeTab === 'overview' 
                ? 'bg-blue-600 text-white' 
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            Overview
          </button>
          <button
            onClick={() => setActiveTab('interactions')}
            className={`px-4 py-2 rounded ${
              activeTab === 'interactions' 
                ? 'bg-blue-600 text-white' 
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            Interactions
          </button>
          <button
            onClick={() => setActiveTab('suggestions')}
            className={`px-4 py-2 rounded ${
              activeTab === 'suggestions' 
                ? 'bg-blue-600 text-white' 
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            Suggestions
          </button>
        </div>
      </div>

      {activeTab === 'overview' && insights && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
          <div className="bg-blue-50 p-4 rounded-lg">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-blue-900">Total Interactions</p>
                <p className="text-2xl font-bold text-blue-600">{insights.total_interactions}</p>
              </div>
              <Brain className="w-8 h-8 text-blue-600" />
            </div>
          </div>
          
          <div className="bg-green-50 p-4 rounded-lg">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-green-900">Learning Accuracy</p>
                <p className="text-2xl font-bold text-green-600">{insights.learning_accuracy}%</p>
              </div>
              <CheckCircle className="w-8 h-8 text-green-600" />
            </div>
          </div>
          
          <div className="bg-purple-50 p-4 rounded-lg">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-purple-900">Knowledge Concepts</p>
                <p className="text-2xl font-bold text-purple-600">{insights.knowledge_concepts}</p>
              </div>
              <TrendingUp className="w-8 h-8 text-purple-600" />
            </div>
          </div>
          
          <div className="bg-gray-50 p-4 rounded-lg">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-900">System Status</p>
                <p className="text-2xl font-bold text-gray-600 capitalize">{insights.system_status}</p>
              </div>
              <AlertCircle className={`w-8 h-8 ${
                insights.system_status === 'healthy' ? 'text-green-600' : 'text-red-600'
              }`} />
            </div>
          </div>
        </div>
      )}

      {activeTab === 'interactions' && insights && (
        <div className="space-y-4">
          <h4 className="text-lg font-semibold mb-4">Recent Learning Interactions</h4>
          {insights.recent_interactions.map((interaction) => (
            <div key={interaction.id} className="border rounded-lg p-4 bg-gray-50">
              <div className="flex items-start justify-between mb-2">
                <div className="flex items-center">
                  {getLearningTypeIcon(interaction.learning_type)}
                  <span className="ml-2 text-sm font-medium capitalize">
                    {interaction.learning_type.replace('_', ' ')}
                  </span>
                </div>
                <div className="flex items-center space-x-2">
                  <span className={`text-sm ${getConfidenceColor(interaction.confidence)}`}>
                    {interaction.confidence}
                  </span>
                  {interaction.validated ? (
                    <CheckCircle className="w-4 h-4 text-green-600" />
                  ) : (
                    <XCircle className="w-4 h-4 text-red-600" />
                  )}
                </div>
              </div>
              
              <div className="space-y-2 text-sm">
                <p><strong>Question:</strong> {interaction.user_question}</p>
                <p><strong>Response:</strong> {interaction.system_response}</p>
                {interaction.user_correction && (
                  <p><strong>Correction:</strong> {interaction.user_correction}</p>
                )}
              </div>
              
              <div className="mt-4 flex items-center space-x-2">
                {selectedInteraction === interaction.id ? (
                  <div className="flex-1 flex items-center space-x-2">
                    <input
                      type="text"
                      value={correctionText}
                      onChange={(e) => setCorrectionText(e.target.value)}
                      placeholder="Enter correction..."
                      className="flex-1 px-3 py-1 border rounded text-sm"
                    />
                    <button
                      onClick={() => handleCorrection(interaction.id)}
                      className="px-3 py-1 bg-blue-600 text-white rounded text-sm hover:bg-blue-700"
                    >
                      Submit
                    </button>
                    <button
                      onClick={() => setSelectedInteraction(null)}
                      className="px-3 py-1 bg-gray-600 text-white rounded text-sm hover:bg-gray-700"
                    >
                      Cancel
                    </button>
                  </div>
                ) : (
                  <div className="flex items-center space-x-2">
                    <button
                      onClick={() => setSelectedInteraction(interaction.id)}
                      className="px-3 py-1 bg-yellow-600 text-white rounded text-sm hover:bg-yellow-700"
                    >
                      Correct
                    </button>
                    <button
                      onClick={() => handleValidation(interaction.id, true)}
                      className="px-3 py-1 bg-green-600 text-white rounded text-sm hover:bg-green-700"
                    >
                      Validate
                    </button>
                    <button
                      onClick={() => handleValidation(interaction.id, false)}
                      className="px-3 py-1 bg-red-600 text-white rounded text-sm hover:bg-red-700"
                    >
                      Reject
                    </button>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {activeTab === 'suggestions' && insights && (
        <div className="space-y-4">
          <h4 className="text-lg font-semibold mb-4">Learning Suggestions</h4>
          {insights.learning_suggestions.map((suggestion, index) => (
            <div key={index} className="border-l-4 border-blue-500 pl-4 py-2">
              <p className="text-gray-700">{suggestion}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default TemporalLearningPanel; 
import React, { useState } from 'react';
import { ChevronRightIcon, ChevronDownIcon, ExternalLinkIcon, DocumentTextIcon } from '@heroicons/react/24/outline';

export interface Citation {
  id: number;
  source: string;
  title: string;
  excerpt: string;
  url?: string;
  confidence?: number;
  type?: 'document' | 'web' | 'database' | 'api';
}

interface CitationMarkerProps {
  citationId: number;
  onClick: (id: number) => void;
}

export const CitationMarker: React.FC<CitationMarkerProps> = ({ citationId, onClick }) => {
  return (
    <sup
      className="text-blue-600 hover:text-blue-800 cursor-pointer ml-0.5 font-medium text-xs"
      onClick={() => onClick(citationId)}
    >
      [{citationId}]
    </sup>
  );
};

interface CitationSidebarProps {
  citations: Citation[];
  isOpen: boolean;
  onToggle: () => void;
  highlightedCitation?: number;
}

export const CitationSidebar: React.FC<CitationSidebarProps> = ({
  citations,
  isOpen,
  onToggle,
  highlightedCitation
}) => {
  return (
    <div className={`
      fixed right-0 top-20 h-[calc(100vh-5rem)] bg-white shadow-lg transition-all duration-300 z-40
      ${isOpen ? 'w-80' : 'w-12'}
    `}>
      {/* Toggle Button */}
      <button
        onClick={onToggle}
        className="absolute left-0 top-4 -ml-3 bg-white rounded-l-lg shadow-md p-2 hover:bg-gray-50"
        aria-label={isOpen ? "Close citations" : "Open citations"}
      >
        {isOpen ? <ChevronRightIcon className="h-4 w-4" /> : <ChevronDownIcon className="h-4 w-4" />}
      </button>

      {/* Content */}
      {isOpen && (
        <div className="p-4 overflow-y-auto h-full">
          <h3 className="text-lg font-semibold mb-4">Sources</h3>

          {citations.length === 0 ? (
            <p className="text-gray-500 text-sm">No citations available</p>
          ) : (
            <div className="space-y-3">
              {citations.map((citation) => (
                <CitationCard
                  key={citation.id}
                  citation={citation}
                  isHighlighted={citation.id === highlightedCitation}
                />
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

interface CitationCardProps {
  citation: Citation;
  isHighlighted?: boolean;
}

const CitationCard: React.FC<CitationCardProps> = ({ citation, isHighlighted }) => {
  const getTypeIcon = () => {
    switch (citation.type) {
      case 'web':
        return <ExternalLinkIcon className="h-4 w-4" />;
      case 'document':
      case 'database':
      case 'api':
      default:
        return <DocumentTextIcon className="h-4 w-4" />;
    }
  };

  return (
    <div className={`
      border rounded-lg p-3 transition-all duration-200
      ${isHighlighted ? 'border-blue-500 bg-blue-50' : 'border-gray-200 hover:border-gray-300'}
    `}>
      <div className="flex items-start justify-between mb-2">
        <div className="flex items-center space-x-2">
          <span className="text-sm font-medium text-gray-700">[{citation.id}]</span>
          {getTypeIcon()}
        </div>
        {citation.confidence && (
          <span className="text-xs text-gray-500">
            {Math.round(citation.confidence * 100)}% confidence
          </span>
        )}
      </div>

      <h4 className="font-medium text-sm mb-1 line-clamp-2">{citation.title}</h4>
      <p className="text-xs text-gray-600 mb-2">{citation.source}</p>
      <p className="text-xs text-gray-700 line-clamp-3">{citation.excerpt}</p>

      {citation.url && (
        <a
          href={citation.url}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center space-x-1 text-xs text-blue-600 hover:text-blue-800 mt-2"
        >
          <span>View source</span>
          <ExternalLinkIcon className="h-3 w-3" />
        </a>
      )}
    </div>
  );
};

interface MessageWithCitationsProps {
  content: string;
  citations: Citation[];
  onCitationClick: (id: number) => void;
}

export const MessageWithCitations: React.FC<MessageWithCitationsProps> = ({
  content,
  citations,
  onCitationClick
}) => {
  // Parse content and replace citation markers with interactive components
  const renderContentWithCitations = () => {
    const citationPattern = /\[(\d+)\]/g;
    const parts = content.split(citationPattern);

    return parts.map((part, index) => {
      // Every odd index is a citation number
      if (index % 2 === 1) {
        const citationId = parseInt(part);
        return (
          <CitationMarker
            key={`citation-${index}`}
            citationId={citationId}
            onClick={onCitationClick}
          />
        );
      }
      return <span key={`text-${index}`}>{part}</span>;
    });
  };

  return <div className="message-content">{renderContentWithCitations()}</div>;
};

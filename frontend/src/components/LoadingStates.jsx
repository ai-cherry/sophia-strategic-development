import React from 'react';

/**
 * Loading state components for enhanced user experience
 */

// Skeleton loader for KPI cards
export const KPICardSkeleton = () => (
  <div className="bg-gray-800/50 backdrop-blur-sm border border-gray-700/50 rounded-xl p-6 animate-pulse">
    <div className="flex items-center justify-between mb-4">
      <div className="h-4 bg-gray-700 rounded w-24"></div>
      <div className="h-8 w-8 bg-gray-700 rounded"></div>
    </div>
    <div className="space-y-2">
      <div className="h-8 bg-gray-700 rounded w-20"></div>
      <div className="h-4 bg-gray-700 rounded w-16"></div>
    </div>
  </div>
);

// Skeleton loader for charts
export const ChartSkeleton = ({ height = "300px" }) => (
  <div className="bg-gray-800/50 backdrop-blur-sm border border-gray-700/50 rounded-xl p-6 animate-pulse">
    <div className="h-6 bg-gray-700 rounded w-32 mb-4"></div>
    <div 
      className="bg-gray-700 rounded" 
      style={{ height }}
    ></div>
  </div>
);

// Skeleton loader for team performance
export const TeamPerformanceSkeleton = () => (
  <div className="bg-gray-800/50 backdrop-blur-sm border border-gray-700/50 rounded-xl p-6 animate-pulse">
    <div className="h-6 bg-gray-700 rounded w-40 mb-6"></div>
    <div className="space-y-4">
      {[1, 2, 3, 4, 5].map(i => (
        <div key={i} className="flex items-center justify-between">
          <div className="h-4 bg-gray-700 rounded w-24"></div>
          <div className="h-4 bg-gray-700 rounded w-12"></div>
        </div>
      ))}
    </div>
  </div>
);

// Skeleton loader for alerts
export const AlertsSkeleton = () => (
  <div className="bg-gray-800/50 backdrop-blur-sm border border-gray-700/50 rounded-xl p-6 animate-pulse">
    <div className="h-6 bg-gray-700 rounded w-32 mb-4"></div>
    <div className="space-y-3">
      {[1, 2, 3].map(i => (
        <div key={i} className="flex items-start space-x-3">
          <div className="h-4 w-4 bg-gray-700 rounded-full mt-1"></div>
          <div className="flex-1">
            <div className="h-4 bg-gray-700 rounded w-full mb-1"></div>
            <div className="h-3 bg-gray-700 rounded w-3/4"></div>
          </div>
        </div>
      ))}
    </div>
  </div>
);

// Loading spinner component
export const LoadingSpinner = ({ size = "medium", className = "" }) => {
  const sizeClasses = {
    small: "h-4 w-4",
    medium: "h-6 w-6",
    large: "h-8 w-8"
  };

  return (
    <div className={`animate-spin rounded-full border-2 border-gray-300 border-t-blue-500 ${sizeClasses[size]} ${className}`}></div>
  );
};

// Button loading state
export const LoadingButton = ({ children, loading, disabled, onClick, className = "", ...props }) => (
  <button
    onClick={onClick}
    disabled={disabled || loading}
    className={`relative flex items-center justify-center space-x-2 ${className} ${
      (disabled || loading) ? 'opacity-50 cursor-not-allowed' : ''
    }`}
    {...props}
  >
    {loading && (
      <LoadingSpinner size="small" className="absolute left-3" />
    )}
    <span className={loading ? 'ml-6' : ''}>{children}</span>
  </button>
);

// Error state component
export const ErrorState = ({ error, onRetry, className = "" }) => (
  <div className={`bg-red-900/20 border border-red-500/30 rounded-xl p-6 text-center ${className}`}>
    <div className="text-red-400 mb-2">
      <svg className="h-8 w-8 mx-auto" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
      </svg>
    </div>
    <h3 className="text-lg font-medium text-red-300 mb-2">Something went wrong</h3>
    <p className="text-red-200 text-sm mb-4">
      {error?.message || 'An unexpected error occurred'}
    </p>
    {onRetry && (
      <button
        onClick={onRetry}
        className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg text-sm transition-colors"
      >
        Try Again
      </button>
    )}
  </div>
);

// Empty state component
export const EmptyState = ({ title, description, action, className = "" }) => (
  <div className={`text-center py-12 ${className}`}>
    <div className="text-gray-400 mb-4">
      <svg className="h-12 w-12 mx-auto" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
      </svg>
    </div>
    <h3 className="text-lg font-medium text-gray-300 mb-2">{title}</h3>
    <p className="text-gray-400 text-sm mb-4">{description}</p>
    {action}
  </div>
);

// Connection status indicator
export const ConnectionStatus = ({ status, onReconnect }) => {
  const statusConfig = {
    connected: {
      color: 'text-green-400',
      bg: 'bg-green-900/20 border-green-500/30',
      icon: '●',
      text: 'Connected'
    },
    connecting: {
      color: 'text-yellow-400',
      bg: 'bg-yellow-900/20 border-yellow-500/30',
      icon: '◐',
      text: 'Connecting...'
    },
    disconnected: {
      color: 'text-gray-400',
      bg: 'bg-gray-900/20 border-gray-500/30',
      icon: '○',
      text: 'Disconnected'
    },
    error: {
      color: 'text-red-400',
      bg: 'bg-red-900/20 border-red-500/30',
      icon: '✕',
      text: 'Connection Error'
    }
  };

  const config = statusConfig[status] || statusConfig.disconnected;

  return (
    <div className={`inline-flex items-center space-x-2 px-3 py-1 rounded-full border text-xs ${config.bg} ${config.color}`}>
      <span className="animate-pulse">{config.icon}</span>
      <span>{config.text}</span>
      {(status === 'disconnected' || status === 'error') && onReconnect && (
        <button
          onClick={onReconnect}
          className="ml-2 text-xs underline hover:no-underline"
        >
          Retry
        </button>
      )}
    </div>
  );
};


import React from 'react';
import { Card, CardContent, CardHeader } from '@/components/ui';
import { Alert, AlertDescription } from '@/components/ui';
import { Button } from '@/components/ui';
import { AlertTriangle, RefreshCw, WifiOff, Database } from 'lucide-react';

// =================================
// Skeleton Loaders
// =================================

export const DealSkeleton = () => (
  <Card className="animate-pulse">
    <CardHeader>
      <div className="h-4 bg-gray-200 rounded w-3/4"></div>
    </CardHeader>
    <CardContent>
      <div className="space-y-2">
        <div className="h-4 bg-gray-200 rounded"></div>
        <div className="h-4 bg-gray-200 rounded w-5/6"></div>
        <div className="h-4 bg-gray-200 rounded w-4/6"></div>
      </div>
    </CardContent>
  </Card>
);

export const ChartSkeleton = () => (
  <div className="animate-pulse">
    <div className="h-64 bg-gray-200 rounded"></div>
    <div className="mt-4 grid grid-cols-4 gap-2">
      {[...Array(4)].map((_, i) => (
        <div key={i} className="h-4 bg-gray-200 rounded"></div>
      ))}
    </div>
  </div>
);

export const FullDashboardSkeleton = () => (
    <div className="p-4 md:p-8">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="md:col-span-2 space-y-6">
                <ChartSkeleton />
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <DealSkeleton />
                    <DealSkeleton />
                </div>
            </div>
            <div className="space-y-6">
                <Card className="animate-pulse"><CardHeader><div className="h-6 bg-gray-200 rounded w-1/2"></div></CardHeader><CardContent><div className="h-48 bg-gray-200 rounded"></div></CardContent></Card>
                <Card className="animate-pulse"><CardHeader><div className="h-6 bg-gray-200 rounded w-1/2"></div></CardHeader><CardContent><div className="h-32 bg-gray-200 rounded"></div></CardContent></Card>
            </div>
        </div>
    </div>
);


// =================================
// Data Fetch Error Component
// =================================

interface DataFetchErrorProps {
  error: Error;
  source?: string;
  onRetry?: () => void;
}

export const DataFetchError: React.FC<DataFetchErrorProps> = ({
  error,
  source,
  onRetry,
}) => {
  const isNetworkError = error.message.toLowerCase().includes('network') ||
                        error.message.toLowerCase().includes('fetch');
  const isDataSourceError = error.message.toLowerCase().includes('snowflake') ||
                           error.message.toLowerCase().includes('gong') ||
                           error.message.toLowerCase().includes('hubspot');

  return (
    <Alert variant="destructive" className="my-4">
      <div className="flex items-start space-x-3">
        {isNetworkError ? (
          <WifiOff className="h-5 w-5 mt-1" />
        ) : isDataSourceError ? (
          <Database className="h-5 w-5 mt-1" />
        ) : (
          <AlertTriangle className="h-5 w-5 mt-1" />
        )}
        <div className="flex-1">
          <AlertDescription>
            <p className="font-semibold mb-1">
              {isNetworkError && 'Connection Problem'}
              {isDataSourceError && `${source || 'Data Source'} Unavailable`}
              {!isNetworkError && !isDataSourceError && 'Error Loading Data'}
            </p>
            <p className="text-sm mb-3">
              {isNetworkError &&
                'Please check your internet connection and try again.'}
              {isDataSourceError &&
                `We're having trouble connecting to ${source || 'the data source'}. This is usually temporary.`}
              {!isNetworkError && !isDataSourceError &&
                'An unexpected error occurred while loading your data.'}
            </p>
            {onRetry && (
              <Button size="sm" variant="outline" onClick={onRetry}>
                <RefreshCw className="h-4 w-4 mr-2" />
                Retry
              </Button>
            )}
          </AlertDescription>
        </div>
      </div>
    </Alert>
  );
};

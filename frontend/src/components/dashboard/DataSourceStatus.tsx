import React from 'react';

const DataSourceStatus: React.FC = () => {
    // This data would come from a health check endpoint
    const sources = [
        { name: 'Gong', status: 'ok' },
        { name: 'Slack', status: 'ok' },
        { name: 'Snowflake', status: 'ok' },
        { name: 'OpenAI', status: 'error' },
    ];

    const getStatusColor = (status: string) => {
        if (status === 'ok') return 'bg-green-500';
        if (status === 'error') return 'bg-red-500';
        return 'bg-yellow-500';
    };

    return (
        <div className="flex items-center space-x-2">
            {sources.map(source => (
                <div key={source.name} className="flex items-center space-x-1 text-xs">
                    <span className={`w-2 h-2 rounded-full ${getStatusColor(source.status)}`}></span>
                    <span>{source.name}</span>
                </div>
            ))}
        </div>
    );
};

export default DataSourceStatus;

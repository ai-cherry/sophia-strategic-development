import React from 'react';
import useMetrics from '../../hooks/use-metrics';

const KPIMetrics: React.FC = () => {
    const { data: metrics, loading, error } = useMetrics();

    if (loading) {
        return <p>Loading metrics...</p>;
    }

    if (error || !metrics) {
        return <p className="text-red-500">Failed to load metrics</p>;
    }

    return (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="bg-white p-6 rounded-lg shadow">
                <h3 className="text-sm font-medium text-gray-500">Revenue Growth (QTD)</h3>
                <p className="text-3xl font-bold mt-1">{metrics.revenue_growth}%</p>
            </div>
            <div className="bg-white p-6 rounded-lg shadow">
                <h3 className="text-sm font-medium text-gray-500">Client Health Score</h3>
                <p className="text-3xl font-bold mt-1">{metrics.client_health_score}</p>
            </div>
            <div className="bg-white p-6 rounded-lg shadow">
                <h3 className="text-sm font-medium text-gray-500">Sales Efficiency</h3>
                <p className="text-3xl font-bold mt-1">{metrics.sales_efficiency}%</p>
            </div>
            <div className="bg-white p-6 rounded-lg shadow">
                <h3 className="text-sm font-medium text-gray-500">AI Task Completion</h3>
                <p className="text-3xl font-bold mt-1">{metrics.ai_task_completion_rate}%</p>
            </div>
        </div>
    );
};

export default KPIMetrics;

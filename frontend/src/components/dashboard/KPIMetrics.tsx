import React, { useState, useEffect } from 'react';
// import { getDashboardMetrics } from '../../services/api_v1';

const KPIMetrics: React.FC = () => {
    // const [metrics, setMetrics] = useState(null);

    // useEffect(() => {
    //     const fetchMetrics = async () => {
    //         const data = await getDashboardMetrics();
    //         setMetrics(data);
    //     };
    //     fetchMetrics();
    // }, []);

    // Placeholder data until API service is created
    const metrics = {
        revenue_growth: 15.3,
        client_health_score: 87.5,
        sales_efficiency: 92.1,
        ai_task_completion_rate: 98.9,
    };

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

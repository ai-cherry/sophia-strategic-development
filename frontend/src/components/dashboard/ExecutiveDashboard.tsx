import React, { useState, useEffect } from 'react';

// Import sub-components that we will create next
import KPIMetrics from './KPIMetrics';
import SalesAnalytics from './SalesAnalytics';
import CommunicationInsights from './CommunicationInsights';
import AIInsights from './AIInsights';
import DataSourceStatus from './DataSourceStatus';
import RealTimeUpdates from './RealTimeUpdates';
import LLMStrategyHub from './LLMStrategyHub';
import UnifiedChatInterface from '../shared/UnifiedChatInterface';

const ExecutiveDashboard: React.FC = () => {
    // Executive dashboard state
    const [executiveMetrics, setExecutiveMetrics] = useState({
        totalRevenue: 2500000,
        totalCustomers: 1250,
        pipelineValue: 850000,
        healthScore: 92
    });

    return (
        <div className="bg-gray-100 min-h-screen p-8 font-sans">
            <header className="flex justify-between items-center mb-8">
                <div>
                    <h1 className="text-3xl font-bold text-gray-800">Sophia AI Executive Dashboard</h1>
                    <p className="text-sm text-gray-500">Real-time business intelligence and strategic insights</p>
                </div>
                <DataSourceStatus />
            </header>

            <main className="grid grid-cols-12 gap-8">
                {/* Main Content */}
                <div className="col-span-12 lg:col-span-9 space-y-8">
                    <KPIMetrics />
                    <SalesAnalytics />
                    <CommunicationInsights />
                </div>

                {/* Right Sidebar */}
                <aside className="col-span-12 lg:col-span-3 space-y-8">
                    <AIInsights />
                    <RealTimeUpdates />
                </aside>
            </main>

            {/* Add LLM Strategy Hub Section */}
            <div className="mt-8 mb-8">
                <LLMStrategyHub />
            </div>

            {/* Unified Chat Interface */}
            <div className="mb-8">
                <UnifiedChatInterface 
                    context={{
                        revenue: executiveMetrics.totalRevenue,
                        customers: executiveMetrics.totalCustomers,
                        pipeline: executiveMetrics.pipelineValue,
                        healthScore: executiveMetrics.healthScore
                    }}
                    dashboardType="ceo"
                    userId="ceo"
                    height="500px"
                    title="🎯 Executive AI Assistant"
                />
            </div>
        </div>
    );
};

export default ExecutiveDashboard;

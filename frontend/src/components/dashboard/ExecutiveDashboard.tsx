import React from 'react';

// Import sub-components that we will create next
import KPIMetrics from './KPIMetrics';
import SalesAnalytics from './SalesAnalytics';
import CommunicationInsights from './CommunicationInsights';
import AIInsights from './AIInsights';
import DataSourceStatus from './DataSourceStatus';
import RealTimeUpdates from './RealTimeUpdates';

const ExecutiveDashboard: React.FC = () => {
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
        </div>
    );
};

export default ExecutiveDashboard;

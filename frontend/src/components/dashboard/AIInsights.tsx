import React from 'react';

const AIInsights: React.FC = () => {
    return (
        <div className="bg-white p-6 rounded-lg shadow h-full">
            <h3 className="text-xl font-bold mb-4">AI-Powered Insights</h3>
            <div className="space-y-4">
                <div className="bg-blue-50 border-l-4 border-blue-500 p-4 rounded">
                    <p className="font-bold text-blue-800">Churn Risk Detected</p>
                    <p className="text-sm text-blue-700">Client "Innovate Inc." has shown a 30% drop in usage. Recommend immediate outreach.</p>
                </div>
                <div className="bg-green-50 border-l-4 border-green-500 p-4 rounded">
                    <p className="font-bold text-green-800">Upsell Opportunity</p>
                    <p className="text-sm text-green-700">"QuantumLeap Solutions" has high usage of feature X. They are a prime candidate for the new enterprise tier.</p>
                </div>
            </div>
        </div>
    );
};

export default AIInsights;

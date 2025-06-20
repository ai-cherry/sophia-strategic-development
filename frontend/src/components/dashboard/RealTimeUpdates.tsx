import React from 'react';

const RealTimeUpdates: React.FC = () => {
    return (
        <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-xl font-bold mb-4">Real-Time Events</h3>
            <div className="space-y-3 text-sm">
                <div className="flex items-start">
                    <span className="text-green-500 w-5 h-5 mr-3"><i className="fas fa-check-circle"></i></span>
                    <p><span className="font-bold">New Deal Closed:</span> Acme Corp - $250k ARR</p>
                </div>
                <div className="flex items-start">
                     <span className="text-red-500 w-5 h-5 mr-3"><i className="fas fa-exclamation-triangle"></i></span>
                    <p><span className="font-bold">High-Risk Call:</span> Innovate Inc. mentioned competitor "SynergySoft".</p>
                </div>
            </div>
        </div>
    );
};

export default RealTimeUpdates;

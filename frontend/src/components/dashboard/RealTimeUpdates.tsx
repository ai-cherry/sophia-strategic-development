import React from 'react';
import useRealTimeEvents from '../../hooks/use-real-time-events';

const RealTimeUpdates: React.FC = () => {
    const { events, status } = useRealTimeEvents();

    return (
        <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-xl font-bold mb-4">Real-Time Events</h3>
            {status !== 'connected' && (
                <p className="text-sm text-gray-500">Connecting...</p>
            )}
            <div className="space-y-3 text-sm">
                {events.map((evt, idx) => (
                    <div key={idx} className="flex items-start">
                        <span className="text-green-500 w-5 h-5 mr-3"><i className="fas fa-bolt"></i></span>
                        <p>{evt.message || JSON.stringify(evt)}</p>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default RealTimeUpdates;

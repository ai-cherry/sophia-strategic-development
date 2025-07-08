import React from 'react';
import { Badge } from '@/components/ui/badge';
import {
    DollarSign,
    Users,
    MessageSquare,
    TrendingUp,
    Calendar,
    CheckCircle,
    AlertCircle,
    Info
} from 'lucide-react';

interface Activity {
    id: string;
    type: 'deal' | 'client' | 'message' | 'metric' | 'event';
    title: string;
    description: string;
    timestamp: string;
    status?: 'success' | 'warning' | 'info';
}

interface ActivityFeedProps {
    activities: Activity[];
}

const ActivityFeed: React.FC<ActivityFeedProps> = ({ activities }) => {
    const getIcon = (type: string) => {
        switch (type) {
            case 'deal':
                return <DollarSign className="h-4 w-4" />;
            case 'client':
                return <Users className="h-4 w-4" />;
            case 'message':
                return <MessageSquare className="h-4 w-4" />;
            case 'metric':
                return <TrendingUp className="h-4 w-4" />;
            case 'event':
                return <Calendar className="h-4 w-4" />;
            default:
                return <Info className="h-4 w-4" />;
        }
    };

    const getStatusIcon = (status?: string) => {
        switch (status) {
            case 'success':
                return <CheckCircle className="h-4 w-4 text-emerald-500" />;
            case 'warning':
                return <AlertCircle className="h-4 w-4 text-amber-500" />;
            default:
                return null;
        }
    };

    const getStatusColor = (status?: string) => {
        switch (status) {
            case 'success':
                return 'bg-emerald-500/10 text-emerald-500 border-emerald-500/20';
            case 'warning':
                return 'bg-amber-500/10 text-amber-500 border-amber-500/20';
            default:
                return 'bg-blue-500/10 text-blue-500 border-blue-500/20';
        }
    };

    if (!activities || activities.length === 0) {
        return (
            <div className="text-center py-8 text-gray-400">
                No recent activity
            </div>
        );
    }

    return (
        <div className="space-y-4">
            {activities.map((activity) => (
                <div
                    key={activity.id}
                    className="flex items-start space-x-3 p-4 rounded-lg bg-gray-800/50 border border-gray-700/50 hover:bg-gray-800 transition-colors"
                >
                    <div className="flex-shrink-0 mt-0.5">
                        <div className="p-2 rounded-full bg-gray-700/50 text-gray-400">
                            {getIcon(activity.type)}
                        </div>
                    </div>
                    <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2">
                            <p className="text-sm font-medium text-gray-50">
                                {activity.title}
                            </p>
                            {activity.status && (
                                <Badge
                                    variant="outline"
                                    className={`text-xs ${getStatusColor(activity.status)}`}
                                >
                                    <span className="flex items-center gap-1">
                                        {getStatusIcon(activity.status)}
                                        {activity.status}
                                    </span>
                                </Badge>
                            )}
                        </div>
                        <p className="text-sm text-gray-400 mt-1">
                            {activity.description}
                        </p>
                        <p className="text-xs text-gray-500 mt-2">
                            {new Date(activity.timestamp).toLocaleString()}
                        </p>
                    </div>
                </div>
            ))}
        </div>
    );
};

export default ActivityFeed;

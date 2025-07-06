import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui';
import { Badge } from '@/components/ui';

const ActivityFeed = ({ activities }) => {
    if (!activities) return null;

    return (
        <Card>
            <CardHeader>
                <CardTitle>Activity Feed</CardTitle>
            </CardHeader>
            <CardContent>
                <ul className="space-y-4">
                    {activities.map((activity) => (
                        <li key={activity.id} className="flex items-center space-x-4">
                            <div className="flex-shrink-0">
                                <Badge variant={activity.type === 'alert' ? 'destructive' : 'default'}>
                                    {activity.type}
                                </Badge>
                            </div>
                            <div className="flex-1 min-w-0">
                                <p className="text-sm font-medium text-gray-900 truncate">
                                    {activity.title}
                                </p>
                                <p className="text-sm text-gray-500 truncate">
                                    {activity.description}
                                </p>
                            </div>
                            <div className="inline-flex items-center text-base font-semibold text-gray-900">
                                {activity.time}
                            </div>
                        </li>
                    ))}
                </ul>
            </CardContent>
        </Card>
    );
};

export default ActivityFeed;

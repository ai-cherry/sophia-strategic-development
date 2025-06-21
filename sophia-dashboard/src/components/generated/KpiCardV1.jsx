import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';

const KpiCardV1 = ({ title, value, change, changeType, icon: Icon }) => {
  const trendColor = changeType === 'increase' ? 'text-green-500' : 'text-red-500';
  const TrendIcon = changeType === 'increase' ? TrendingUp : changeType === 'decrease' ? TrendingDown : Minus;

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium text-gray-500">{title}</CardTitle>
        {Icon && <Icon className="h-4 w-4 text-gray-400" />}
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold text-gray-800">{value}</div>
        <p className="text-xs text-gray-500 flex items-center">
          <TrendIcon className={`h-4 w-4 mr-1 ${trendColor}`} />
          <span className={`${trendColor} mr-1`}>{change}</span>
          from last month
        </p>
      </CardContent>
    </Card>
  );
};

export default KpiCardV1;

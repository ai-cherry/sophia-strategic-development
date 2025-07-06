import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui';
import { TrendingUp, Users, Target, DollarSign } from 'lucide-react';

const iconMap = {
    revenue: DollarSign,
    deals: Target,
    health: TrendingUp,
    users: Users,
};

const KPICard = ({ title, value, change, icon }) => {
    const Icon = iconMap[icon] || DollarSign;
    const isPositive = change.startsWith('+');

    return (
        <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">{title}</CardTitle>
                <Icon className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
                <div className="text-2xl font-bold">{value}</div>
                <p className={`text-xs ${isPositive ? 'text-green-500' : 'text-red-500'}`}>
                    {change} from last month
                </p>
            </CardContent>
        </Card>
    );
};


const KPICards = ({ kpiData }) => {
    if (!kpiData) return null;

    return (
        <>
            {kpiData.map((kpi) => (
                <KPICard key={kpi.title} {...kpi} />
            ))}
        </>
    );
};

export default KPICards;

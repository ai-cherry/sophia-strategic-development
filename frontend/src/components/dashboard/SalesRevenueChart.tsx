import React from 'react';
import { Line } from 'react-chartjs-2';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui';

const SalesRevenueChart = ({ salesData }) => {
    if (!salesData) return null;

    const data = {
        labels: salesData.labels,
        datasets: [
            {
                label: 'Revenue',
                data: salesData.revenue,
                borderColor: 'rgb(75, 192, 192)',
                backgroundColor: 'rgba(75, 192, 192, 0.5)',
            },
        ],
    };

    return (
        <Card>
            <CardHeader>
                <CardTitle>Sales Revenue</CardTitle>
            </CardHeader>
            <CardContent>
                <div className="h-80">
                    <Line data={data} options={{ maintainAspectRatio: false }} />
                </div>
            </CardContent>
        </Card>
    );
};

export default SalesRevenueChart;

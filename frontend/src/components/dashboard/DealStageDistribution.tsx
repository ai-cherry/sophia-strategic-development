import React from 'react';
import { Doughnut } from 'react-chartjs-2';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui';

const DealStageDistribution = ({ dealData }) => {
    if (!dealData) return null;

    const data = {
        labels: dealData.labels,
        datasets: [
            {
                label: 'Deals by Stage',
                data: dealData.values,
                backgroundColor: [
                    'rgba(255, 99, 132, 0.8)',
                    'rgba(54, 162, 235, 0.8)',
                    'rgba(255, 206, 86, 0.8)',
                    'rgba(75, 192, 192, 0.8)',
                    'rgba(153, 102, 255, 0.8)',
                ],
            },
        ],
    };

    return (
        <Card>
            <CardHeader>
                <CardTitle>Deal Stage Distribution</CardTitle>
            </CardHeader>
            <CardContent>
                <div className="h-80">
                    <Doughnut data={data} options={{ maintainAspectRatio: false }} />
                </div>
            </CardContent>
        </Card>
    );
};

export default DealStageDistribution;

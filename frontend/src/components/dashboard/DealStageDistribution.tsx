import React from 'react';
import { Doughnut } from 'react-chartjs-2';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

const DealStageDistribution = ({ dealData }) => {
    if (!dealData) return null;

    const data = {
        labels: dealData.labels,
        datasets: [
            {
                label: 'Deals by Stage',
                data: dealData.values,
                backgroundColor: [
                    'rgba(139, 92, 246, 0.8)',   // Purple
                    'rgba(16, 185, 129, 0.8)',   // Emerald
                    'rgba(245, 158, 11, 0.8)',   // Amber
                    'rgba(59, 130, 246, 0.8)',   // Blue
                    'rgba(236, 72, 153, 0.8)',   // Pink
                ],
                borderColor: [
                    'rgba(139, 92, 246, 1)',
                    'rgba(16, 185, 129, 1)',
                    'rgba(245, 158, 11, 1)',
                    'rgba(59, 130, 246, 1)',
                    'rgba(236, 72, 153, 1)',
                ],
                borderWidth: 2,
            },
        ],
    };

    const options = {
        maintainAspectRatio: false,
        plugins: {
            legend: {
                position: 'bottom',
                labels: {
                    color: '#9ca3af',
                    padding: 20,
                    font: {
                        size: 12,
                    },
                },
            },
            tooltip: {
                backgroundColor: 'rgba(17, 24, 39, 0.95)',
                titleColor: '#f3f4f6',
                bodyColor: '#e5e7eb',
                borderColor: 'rgba(255, 255, 255, 0.2)',
                borderWidth: 1,
                cornerRadius: 8,
                padding: 12,
                displayColors: true,
                callbacks: {
                    label: function(context) {
                        const label = context.label || '';
                        const value = context.parsed || 0;
                        const total = context.dataset.data.reduce((a, b) => a + b, 0);
                        const percentage = (total > 0 && value != null) ? ((value / total) * 100).toFixed(1) : '0';
                        return `${label}: ${value} (${percentage}%)`;
                    }
                }
            },
        },
    };

    return (
        <Card className="bg-gray-900 border-gray-800">
            <CardHeader>
                <CardTitle className="text-gray-50">Deal Stage Distribution</CardTitle>
            </CardHeader>
            <CardContent>
                <div className="h-80">
                    <Doughnut data={data} options={options} />
                </div>
            </CardContent>
        </Card>
    );
};

export default DealStageDistribution;

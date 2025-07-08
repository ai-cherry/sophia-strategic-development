import React from 'react';
import { Line, LineChart, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";

interface SalesRevenueChartProps {
    salesData: Array<{
        month: string;
        revenue: number;
        deals: number;
    }>;
}

const EnhancedSalesRevenueChart: React.FC<SalesRevenueChartProps> = ({ salesData }) => {
    if (!salesData || salesData.length === 0) {
        return (
            <div className="flex items-center justify-center h-[250px] text-gray-400">
                No sales data available
            </div>
        );
    }

    // Transform data for the chart
    const chartData = salesData.map(item => ({
        name: item.month,
        revenue: item.revenue,
        deals: item.deals,
    }));

    return (
        <ResponsiveContainer width="100%" height={250}>
            <LineChart
                data={chartData}
                margin={{
                    top: 5,
                    right: 30,
                    left: 20,
                    bottom: 5,
                }}
            >
                {/* Grid with subtle dark theme styling */}
                <CartesianGrid
                    strokeDasharray="3 3"
                    stroke="rgba(255, 255, 255, 0.1)"
                    vertical={false}
                />

                {/* X-Axis with dark theme colors */}
                <XAxis
                    dataKey="name"
                    stroke="#888888"
                    fontSize={12}
                    tickLine={false}
                    axisLine={false}
                    tick={{ fill: '#9ca3af' }}
                />

                {/* Y-Axis with formatted values */}
                <YAxis
                    stroke="#888888"
                    fontSize={12}
                    tickLine={false}
                    axisLine={false}
                    tick={{ fill: '#9ca3af' }}
                    tickFormatter={(value) => `$${(value / 1000).toFixed(0)}k`}
                />

                {/* Dark themed tooltip */}
                <Tooltip
                    contentStyle={{
                        backgroundColor: "rgba(17, 24, 39, 0.95)",
                        borderColor: "rgba(255, 255, 255, 0.2)",
                        borderRadius: "8px",
                        boxShadow: "0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)"
                    }}
                    labelStyle={{
                        color: "#f3f4f6",
                        fontWeight: 600,
                        marginBottom: "4px"
                    }}
                    itemStyle={{
                        color: "#e5e7eb"
                    }}
                    formatter={(value: number, name: string) => {
                        if (name === 'revenue') {
                            return [`$${value.toLocaleString()}`, 'Revenue'];
                        }
                        return [value.toString(), 'Deals'];
                    }}
                />

                {/* Revenue line with gradient */}
                <defs>
                    <linearGradient id="revenueGradient" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.8}/>
                        <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0.2}/>
                    </linearGradient>
                    <linearGradient id="dealsGradient" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#10b981" stopOpacity={0.8}/>
                        <stop offset="95%" stopColor="#10b981" stopOpacity={0.2}/>
                    </linearGradient>
                </defs>

                {/* Revenue line */}
                <Line
                    type="monotone"
                    dataKey="revenue"
                    stroke="#8b5cf6"
                    strokeWidth={3}
                    activeDot={{
                        r: 6,
                        fill: '#8b5cf6',
                        stroke: '#1f2937',
                        strokeWidth: 2
                    }}
                    dot={{
                        r: 4,
                        strokeWidth: 2,
                        fill: "#8b5cf6",
                        stroke: '#1f2937'
                    }}
                />

                {/* Deals line */}
                <Line
                    type="monotone"
                    dataKey="deals"
                    stroke="#10b981"
                    strokeWidth={3}
                    strokeDasharray="5 5"
                    activeDot={{
                        r: 6,
                        fill: '#10b981',
                        stroke: '#1f2937',
                        strokeWidth: 2
                    }}
                    dot={{
                        r: 4,
                        strokeWidth: 2,
                        fill: "#10b981",
                        stroke: '#1f2937'
                    }}
                    yAxisId="right"
                />

                {/* Secondary Y-Axis for deals */}
                <YAxis
                    yAxisId="right"
                    orientation="right"
                    stroke="#888888"
                    fontSize={12}
                    tickLine={false}
                    axisLine={false}
                    tick={{ fill: '#9ca3af' }}
                />
            </LineChart>
        </ResponsiveContainer>
    );
};

export default EnhancedSalesRevenueChart;

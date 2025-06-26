/**
 * Executive Chart Component
 * Professional charts with glassmorphism design for executive dashboards
 */

import React from 'react';
import {
  AreaChart,
  Area,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';
import { glassmorphism, colors, typography } from '../lib/design-system.js';

// Custom tooltip component
const CustomTooltip = ({ active, payload, label, labelFormatter, valueFormatter }) => {
  if (active && payload && payload.length) {
    return (
      <div 
        className="p-3 rounded-lg border backdrop-blur-xl shadow-xl"
        style={{
          ...glassmorphism.getStyles(0.15, 20),
          border: '1px solid rgba(255, 255, 255, 0.3)'
        }}
      >
        {label && (
          <p className="text-sm font-medium text-white/90 mb-2">
            {labelFormatter ? labelFormatter(label) : label}
          </p>
        )}
        {payload.map((entry, index) => (
          <div key={index} className="flex items-center space-x-2">
            <div 
              className="w-3 h-3 rounded-full"
              style={{ backgroundColor: entry.color }}
            />
            <span className="text-sm text-white/80">
              {entry.name}: 
            </span>
            <span className="text-sm font-semibold text-white">
              {valueFormatter ? valueFormatter(entry.value) : entry.value}
            </span>
          </div>
        ))}
      </div>
    );
  }
  return null;
};

// Executive color palette
const executiveColors = [
  '#6366f1', // Primary blue
  '#8b5cf6', // Purple
  '#06b6d4', // Cyan
  '#10b981', // Emerald
  '#f59e0b', // Amber
  '#ef4444', // Red
  '#ec4899', // Pink
  '#84cc16'  // Lime
];

const ExecutiveChart = ({
  type = 'area',
  data = [],
  title = '',
  subtitle = '',
  height = 300,
  colors: customColors = executiveColors,
  dataKeys = [],
  xAxisKey = 'name',
  className = '',
  showGrid = true,
  showLegend = true,
  showTooltip = true,
  gradient = true,
  animate = true,
  valueFormatter = null,
  labelFormatter = null,
  ...props
}) => {
  // Chart container styles
  const chartContainerStyles = {
    ...glassmorphism.getStyles(0.05, 15),
    borderRadius: '12px',
    padding: '1.5rem'
  };

  // Render chart title
  const renderTitle = () => {
    if (!title) return null;
    
    return (
      <div className="mb-6">
        <h3 
          className="text-lg font-semibold text-white tracking-tight"
          style={typography.getHeadingStyles(3)}
        >
          {title}
        </h3>
        {subtitle && (
          <p 
            className="text-sm text-white/70 mt-1"
            style={typography.getTextStyles('small')}
          >
            {subtitle}
          </p>
        )}
      </div>
    );
  };

  // Render area chart
  const renderAreaChart = () => (
    <ResponsiveContainer width="100%" height={height}>
      <AreaChart data={data} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
        {showGrid && (
          <CartesianGrid 
            strokeDasharray="3 3" 
            stroke="rgba(255, 255, 255, 0.1)"
            vertical={false}
          />
        )}
        <XAxis 
          dataKey={xAxisKey}
          axisLine={false}
          tickLine={false}
          tick={{ fill: 'rgba(255, 255, 255, 0.7)', fontSize: 12 }}
        />
        <YAxis 
          axisLine={false}
          tickLine={false}
          tick={{ fill: 'rgba(255, 255, 255, 0.7)', fontSize: 12 }}
        />
        {showTooltip && (
          <Tooltip 
            content={<CustomTooltip valueFormatter={valueFormatter} labelFormatter={labelFormatter} />}
          />
        )}
        {showLegend && (
          <Legend 
            wrapperStyle={{ color: 'rgba(255, 255, 255, 0.8)' }}
          />
        )}
        {dataKeys.map((key, index) => (
          <Area
            key={key}
            type="monotone"
            dataKey={key}
            stroke={customColors[index % customColors.length]}
            fill={gradient ? `url(#gradient${index})` : customColors[index % customColors.length]}
            fillOpacity={0.3}
            strokeWidth={2}
            animationDuration={animate ? 1000 : 0}
          />
        ))}
        {/* Gradient definitions */}
        <defs>
          {gradient && dataKeys.map((key, index) => (
            <linearGradient key={`gradient${index}`} id={`gradient${index}`} x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor={customColors[index % customColors.length]} stopOpacity={0.8}/>
              <stop offset="95%" stopColor={customColors[index % customColors.length]} stopOpacity={0.1}/>
            </linearGradient>
          ))}
        </defs>
      </AreaChart>
    </ResponsiveContainer>
  );

  // Render bar chart
  const renderBarChart = () => (
    <ResponsiveContainer width="100%" height={height}>
      <BarChart data={data} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
        {showGrid && (
          <CartesianGrid 
            strokeDasharray="3 3" 
            stroke="rgba(255, 255, 255, 0.1)"
            vertical={false}
          />
        )}
        <XAxis 
          dataKey={xAxisKey}
          axisLine={false}
          tickLine={false}
          tick={{ fill: 'rgba(255, 255, 255, 0.7)', fontSize: 12 }}
        />
        <YAxis 
          axisLine={false}
          tickLine={false}
          tick={{ fill: 'rgba(255, 255, 255, 0.7)', fontSize: 12 }}
        />
        {showTooltip && (
          <Tooltip 
            content={<CustomTooltip valueFormatter={valueFormatter} labelFormatter={labelFormatter} />}
          />
        )}
        {showLegend && (
          <Legend 
            wrapperStyle={{ color: 'rgba(255, 255, 255, 0.8)' }}
          />
        )}
        {dataKeys.map((key, index) => (
          <Bar
            key={key}
            dataKey={key}
            fill={customColors[index % customColors.length]}
            radius={[4, 4, 0, 0]}
            animationDuration={animate ? 1000 : 0}
          />
        ))}
      </BarChart>
    </ResponsiveContainer>
  );

  // Render pie chart
  const renderPieChart = () => (
    <ResponsiveContainer width="100%" height={height}>
      <PieChart>
        <Pie
          data={data}
          cx="50%"
          cy="50%"
          outerRadius={Math.min(height * 0.35, 120)}
          fill="#8884d8"
          dataKey={dataKeys[0] || 'value'}
          animationDuration={animate ? 1000 : 0}
        >
          {data.map((entry, index) => (
            <Cell 
              key={`cell-${index}`} 
              fill={customColors[index % customColors.length]} 
            />
          ))}
        </Pie>
        {showTooltip && (
          <Tooltip 
            content={<CustomTooltip valueFormatter={valueFormatter} labelFormatter={labelFormatter} />}
          />
        )}
        {showLegend && (
          <Legend 
            wrapperStyle={{ color: 'rgba(255, 255, 255, 0.8)' }}
          />
        )}
      </PieChart>
    </ResponsiveContainer>
  );

  // Render line chart
  const renderLineChart = () => (
    <ResponsiveContainer width="100%" height={height}>
      <LineChart data={data} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
        {showGrid && (
          <CartesianGrid 
            strokeDasharray="3 3" 
            stroke="rgba(255, 255, 255, 0.1)"
            vertical={false}
          />
        )}
        <XAxis 
          dataKey={xAxisKey}
          axisLine={false}
          tickLine={false}
          tick={{ fill: 'rgba(255, 255, 255, 0.7)', fontSize: 12 }}
        />
        <YAxis 
          axisLine={false}
          tickLine={false}
          tick={{ fill: 'rgba(255, 255, 255, 0.7)', fontSize: 12 }}
        />
        {showTooltip && (
          <Tooltip 
            content={<CustomTooltip valueFormatter={valueFormatter} labelFormatter={labelFormatter} />}
          />
        )}
        {showLegend && (
          <Legend 
            wrapperStyle={{ color: 'rgba(255, 255, 255, 0.8)' }}
          />
        )}
        {dataKeys.map((key, index) => (
          <Line
            key={key}
            type="monotone"
            dataKey={key}
            stroke={customColors[index % customColors.length]}
            strokeWidth={3}
            dot={{ fill: customColors[index % customColors.length], strokeWidth: 2, r: 4 }}
            activeDot={{ r: 6, stroke: customColors[index % customColors.length], strokeWidth: 2 }}
            animationDuration={animate ? 1000 : 0}
          />
        ))}
      </LineChart>
    </ResponsiveContainer>
  );

  // Render appropriate chart type
  const renderChart = () => {
    switch (type) {
      case 'area':
        return renderAreaChart();
      case 'bar':
        return renderBarChart();
      case 'pie':
        return renderPieChart();
      case 'line':
        return renderLineChart();
      default:
        return renderAreaChart();
    }
  };

  return (
    <div 
      className={`backdrop-blur-xl bg-white/5 border border-white/10 rounded-xl p-6 ${className}`}
      style={chartContainerStyles}
    >
      {renderTitle()}
      {renderChart()}
    </div>
  );
};

// Predefined chart components
export const RevenueChart = (props) => (
  <ExecutiveChart
    type="area"
    title="Revenue Trends"
    gradient={true}
    {...props}
  />
);

export const PerformanceChart = (props) => (
  <ExecutiveChart
    type="bar"
    title="Team Performance"
    {...props}
  />
);

export const MarketShareChart = (props) => (
  <ExecutiveChart
    type="pie"
    title="Market Share Analysis"
    {...props}
  />
);

export const GrowthChart = (props) => (
  <ExecutiveChart
    type="line"
    title="Growth Metrics"
    {...props}
  />
);

export default ExecutiveChart;


/**
 * KPI Card Component
 * Professional executive-level KPI display with glassmorphism design
 */

import React from 'react';
import { TrendingUp, TrendingDown, Minus, Target, AlertTriangle } from 'lucide-react';
import { glassmorphism, colors, typography, animations } from '../lib/design-system.js';

const KPICard = ({
  title,
  value,
  unit = '',
  trend = null,
  trendValue = null,
  description = '',
  status = 'neutral',
  icon: Icon = Target,
  variant = 'default',
  className = '',
  onClick = null
}) => {
  // Determine trend icon and color
  const getTrendIcon = () => {
    if (trend === 'up') return TrendingUp;
    if (trend === 'down') return TrendingDown;
    return Minus;
  };

  const getTrendColor = () => {
    if (trend === 'up') return colors.getStatusColor('success');
    if (trend === 'down') return colors.getStatusColor('error');
    return colors.getStatusColor('neutral');
  };

  const getStatusColor = () => {
    return colors.getStatusColor(status);
  };

  const TrendIcon = getTrendIcon();

  // Component styles
  const cardStyles = {
    ...glassmorphism.getStyles(0.1, 20),
    ...animations.getTransition('all', '300ms'),
    cursor: onClick ? 'pointer' : 'default',
    position: 'relative',
    overflow: 'hidden'
  };

  const hoverStyles = onClick ? {
    ...glassmorphism.getStyles(0.15, 25),
    transform: 'translateY(-2px)',
    boxShadow: '0 12px 40px rgba(0, 0, 0, 0.15)'
  } : {};

  return (
    <div
      className={`
        relative p-6 rounded-xl border backdrop-blur-xl
        ${glassmorphism.getClasses(variant)}
        ${onClick ? 'hover:bg-white/15 hover:-translate-y-1 cursor-pointer' : ''}
        transition-all duration-300 group
        ${className}
      `}
      style={cardStyles}
      onClick={onClick}
      onMouseEnter={(e) => {
        if (onClick) {
          Object.assign(e.target.style, hoverStyles);
        }
      }}
      onMouseLeave={(e) => {
        if (onClick) {
          Object.assign(e.target.style, cardStyles);
        }
      }}
    >
      {/* Background gradient overlay */}
      <div 
        className="absolute inset-0 opacity-5 rounded-xl"
        style={{
          background: `linear-gradient(135deg, ${getStatusColor()}, transparent)`
        }}
      />

      {/* Header with icon and title */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center space-x-3">
          <div 
            className="p-2 rounded-lg backdrop-blur-md border border-white/20"
            style={{
              backgroundColor: `${getStatusColor()}20`,
              borderColor: `${getStatusColor()}40`
            }}
          >
            <Icon 
              size={20} 
              style={{ color: getStatusColor() }}
              className="transition-transform duration-300 group-hover:scale-110"
            />
          </div>
          <div>
            <h3 
              className="text-sm font-medium text-white/90 tracking-wide uppercase"
              style={typography.getTextStyles('small')}
            >
              {title}
            </h3>
          </div>
        </div>

        {/* Status indicator */}
        {status !== 'neutral' && (
          <div 
            className="w-2 h-2 rounded-full"
            style={{ backgroundColor: getStatusColor() }}
          />
        )}
      </div>

      {/* Main value */}
      <div className="mb-3">
        <div className="flex items-baseline space-x-2">
          <span 
            className="text-3xl font-bold text-white tracking-tight"
            style={typography.getHeadingStyles(2)}
          >
            {value}
          </span>
          {unit && (
            <span className="text-lg text-white/70 font-medium">
              {unit}
            </span>
          )}
        </div>
      </div>

      {/* Trend indicator */}
      {trend && trendValue && (
        <div className="flex items-center space-x-2 mb-3">
          <div 
            className="flex items-center space-x-1 px-2 py-1 rounded-md backdrop-blur-sm"
            style={{
              backgroundColor: `${getTrendColor()}20`,
              border: `1px solid ${getTrendColor()}40`
            }}
          >
            <TrendIcon 
              size={14} 
              style={{ color: getTrendColor() }}
            />
            <span 
              className="text-sm font-semibold"
              style={{ color: getTrendColor() }}
            >
              {trendValue}
            </span>
          </div>
        </div>
      )}

      {/* Description */}
      {description && (
        <p 
          className="text-sm text-white/70 leading-relaxed"
          style={typography.getTextStyles('small')}
        >
          {description}
        </p>
      )}

      {/* Alert indicator for attention-needed items */}
      {status === 'warning' && (
        <div className="absolute top-4 right-4">
          <AlertTriangle 
            size={16} 
            className="text-yellow-400 animate-pulse"
          />
        </div>
      )}

      {/* Hover effect overlay */}
      {onClick && (
        <div className="absolute inset-0 bg-gradient-to-r from-white/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300 rounded-xl" />
      )}
    </div>
  );
};

// Predefined KPI card variants
export const RevenueCard = (props) => (
  <KPICard
    icon={TrendingUp}
    status="success"
    variant="default"
    {...props}
  />
);

export const MetricCard = (props) => (
  <KPICard
    icon={Target}
    status="info"
    variant="subtle"
    {...props}
  />
);

export const AlertCard = (props) => (
  <KPICard
    icon={AlertTriangle}
    status="warning"
    variant="strong"
    {...props}
  />
);

export default KPICard;


import React, { useState, useEffect } from 'react';
import { TrendingUp, TrendingDown, Minus, Activity, AlertCircle } from 'lucide-react';
import { cn } from '../../../lib/utils';
import GlassCard from './GlassCard';

/**
 * MetricCard - Advanced KPI display component with trend analysis and animations
 * 
 * Features:
 * - Trend indicators with color coding
 * - Loading states with skeleton animation
 * - Interactive hover effects
 * - Value formatting and animation
 * - Error state handling
 * - Customizable icons and styling
 */
const MetricCard = ({
  title,
  value,
  previousValue,
  change,
  changeType,
  trend = 'neutral',
  icon: Icon,
  className,
  loading = false,
  error = null,
  onClick,
  animate = true,
  format = 'number',
  precision = 1,
  prefix = '',
  suffix = '',
  size = 'default',
  variant = 'default',
  ...props
}) => {
  const [displayValue, setDisplayValue] = useState(loading ? '0' : value);
  const [isAnimating, setIsAnimating] = useState(false);

  // Animate value changes
  useEffect(() => {
    if (!loading && value !== displayValue && animate) {
      setIsAnimating(true);
      const timer = setTimeout(() => {
        setDisplayValue(value);
        setIsAnimating(false);
      }, 150);
      return () => clearTimeout(timer);
    }
  }, [value, loading, animate, displayValue]);

  // Calculate trend automatically if not provided
  const calculatedTrend = changeType || (
    change && change.includes('+') ? 'increase' :
    change && change.includes('-') ? 'decrease' : 'neutral'
  );

  // Size variants
  const sizeClasses = {
    sm: {
      container: 'p-4',
      title: 'text-xs',
      value: 'text-xl',
      change: 'text-xs',
      icon: 'h-4 w-4'
    },
    default: {
      container: 'p-6',
      title: 'text-sm',
      value: 'text-3xl',
      change: 'text-sm',
      icon: 'h-5 w-5'
    },
    lg: {
      container: 'p-8',
      title: 'text-base',
      value: 'text-4xl',
      change: 'text-base',
      icon: 'h-6 w-6'
    }
  };

  // Variant styles
  const variantClasses = {
    default: 'bg-slate-800/40',
    success: 'bg-green-900/20 border-green-500/30',
    warning: 'bg-yellow-900/20 border-yellow-500/30',
    danger: 'bg-red-900/20 border-red-500/30',
    info: 'bg-blue-900/20 border-blue-500/30'
  };

  // Format value based on type
  const formatValue = (val) => {
    if (loading || val === null || val === undefined) return '—';
    
    switch (format) {
      case 'currency':
        return new Intl.NumberFormat('en-US', {
          style: 'currency',
          currency: 'USD',
          minimumFractionDigits: 0,
          maximumFractionDigits: precision
        }).format(val);
      case 'percentage':
        return `${parseFloat(val).toFixed(precision)}%`;
      case 'compact':
        return new Intl.NumberFormat('en-US', {
          notation: 'compact',
          maximumFractionDigits: precision
        }).format(val);
      default:
        return new Intl.NumberFormat('en-US', {
          maximumFractionDigits: precision
        }).format(val);
    }
  };

  // Trend icon and color
  const getTrendDisplay = () => {
    const trendConfig = {
      increase: {
        icon: TrendingUp,
        color: 'text-green-400',
        bgColor: 'bg-green-400/10'
      },
      decrease: {
        icon: TrendingDown,
        color: 'text-red-400',
        bgColor: 'bg-red-400/10'
      },
      neutral: {
        icon: Minus,
        color: 'text-gray-400',
        bgColor: 'bg-gray-400/10'
      }
    };

    return trendConfig[calculatedTrend] || trendConfig.neutral;
  };

  const trendDisplay = getTrendDisplay();
  const TrendIcon = trendDisplay.icon;
  const currentSize = sizeClasses[size];

  if (error) {
    return (
      <GlassCard 
        className={cn(
          "border-red-500/30 bg-red-900/20",
          currentSize.container,
          className
        )}
        hover={false}
        {...props}
      >
        <div className="flex items-center gap-3">
          <AlertCircle className={cn("text-red-400", currentSize.icon)} />
          <div>
            <h3 className={cn("font-medium text-red-300", currentSize.title)}>
              {title}
            </h3>
            <p className="text-red-400 text-xs mt-1">{error}</p>
          </div>
        </div>
      </GlassCard>
    );
  }

  return (
    <GlassCard
      className={cn(
        "group cursor-pointer transition-all duration-300",
        variantClasses[variant],
        onClick && "hover:scale-[1.02] active:scale-[0.98]",
        currentSize.container,
        className
      )}
      onClick={onClick}
      glowEffect={variant !== 'default'}
      {...props}
    >
      {/* Header with title and icon */}
      <div className="flex items-center justify-between mb-4">
        <h3 className={cn(
          "font-medium text-gray-400 group-hover:text-gray-300 transition-colors",
          currentSize.title
        )}>
          {title}
        </h3>
        {Icon && (
          <div className={cn(
            "text-purple-400 group-hover:text-purple-300 transition-all duration-200",
            "group-hover:scale-110 group-hover:rotate-3",
            onClick && "group-active:scale-95"
          )}>
            <Icon className={currentSize.icon} />
          </div>
        )}
      </div>

      {loading ? (
        /* Loading state */
        <div className="space-y-3">
          <div className={cn(
            "bg-slate-700 rounded animate-pulse",
            size === 'sm' ? 'h-6' : size === 'lg' ? 'h-10' : 'h-8'
          )} />
          <div className="flex items-center space-x-2">
            <div className="h-4 w-4 bg-slate-700 rounded animate-pulse" />
            <div className="h-4 w-16 bg-slate-700 rounded animate-pulse" />
          </div>
        </div>
      ) : (
        /* Content */
        <>
          {/* Main value */}
          <div className={cn(
            "font-bold text-white mb-3 transition-all duration-300",
            isAnimating && "scale-105 text-purple-300",
            currentSize.value
          )}>
            {prefix}{formatValue(displayValue)}{suffix}
          </div>

          {/* Trend indicator */}
          {change && (
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <div className={cn(
                  "flex items-center justify-center rounded-full p-1",
                  trendDisplay.bgColor
                )}>
                  <TrendIcon className={cn(
                    "transition-transform duration-200 group-hover:scale-110",
                    trendDisplay.color,
                    currentSize.icon
                  )} />
                </div>
                <span className={cn(
                  "font-medium transition-colors",
                  trendDisplay.color,
                  currentSize.change
                )}>
                  {change}
                </span>
              </div>
              
              {/* Time period indicator */}
              <span className="text-xs text-gray-500">
                vs last period
              </span>
            </div>
          )}

          {/* Additional metrics row */}
          {previousValue && (
            <div className="mt-2 pt-2 border-t border-slate-700/50">
              <div className="flex justify-between text-xs text-gray-500">
                <span>Previous</span>
                <span>{prefix}{formatValue(previousValue)}{suffix}</span>
              </div>
            </div>
          )}
        </>
      )}

      {/* Interactive indicator */}
      {onClick && (
        <div className="absolute inset-0 rounded-lg bg-gradient-to-r from-transparent via-purple-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none" />
      )}
    </GlassCard>
  );
};

// Pre-configured metric card variants
export const MetricCardVariants = {
  // Revenue metrics
  Revenue: (props) => (
    <MetricCard 
      format="currency"
      variant="success"
      size="default"
      {...props} 
    />
  ),
  
  // Percentage metrics
  Percentage: (props) => (
    <MetricCard 
      format="percentage"
      precision={1}
      suffix=""
      {...props} 
    />
  ),
  
  // Count metrics
  Count: (props) => (
    <MetricCard 
      format="compact"
      precision={0}
      {...props} 
    />
  ),
  
  // Performance metrics
  Performance: (props) => (
    <MetricCard 
      variant="info"
      animate={true}
      {...props} 
    />
  )
};

export default MetricCard;

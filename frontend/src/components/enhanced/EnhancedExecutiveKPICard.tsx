import React from 'react';
import { ExecutiveKPICardProps } from './executive-kpi-card.types';

/**
 * Professional KPI card with glassmorphism design
 * Auto-generated from Figma design using Sophia AI UI/UX Agent
 */
export const ExecutiveKPICard: React.FC<ExecutiveKPICardProps> = ({
  title,
  value,
  trend,
  className,
  onClick,
  ...props
}) => {
  return (
    <div 
      className={`
        backdrop-blur-xl bg-white/10 border border-white/20 shadow-xl
        rounded-lg p-6 transition-all duration-300 hover:scale-105
        cursor-pointer ${className}
      `}
      onClick={onClick}
      role="button"
      tabIndex={0}
      {...props}
    >
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-white">{title}</h3>
        <div className={`
          text-sm px-2 py-1 rounded-full
          ${trend === 'up' ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'}
        `}>
          {trend === 'up' ? '↗' : '↘'}
        </div>
      </div>
      <div className="text-2xl font-bold text-white mb-2">{value}</div>
      <div className="text-sm text-white/70">Professional executive component</div>
    </div>
  );
};

export default ExecutiveKPICard;
import React from 'react';
import { cn } from '../../../lib/utils';

/**
 * GlassCard - Modern glassmorphism card component with gradient borders and animations
 * 
 * Features:
 * - Glassmorphism backdrop blur effect
 * - Optional gradient borders
 * - Hover animations and scaling
 * - Responsive padding options
 * - Customizable styling
 */
const GlassCard = ({
  children,
  className,
  hover = true,
  gradient = false,
  padding = 'default',
  glowEffect = false,
  borderRadius = 'lg',
  backdrop = 'md',
  ...props
}) => {
  const paddingSizes = {
    none: '',
    sm: 'p-3',
    default: 'p-6',
    lg: 'p-8',
    xl: 'p-10',
  };

  const borderRadiusOptions = {
    sm: 'rounded-md',
    default: 'rounded-lg',
    lg: 'rounded-xl',
    xl: 'rounded-2xl',
  };

  const backdropOptions = {
    sm: 'backdrop-blur-sm',
    md: 'backdrop-blur-md',
    lg: 'backdrop-blur-lg',
    xl: 'backdrop-blur-xl',
  };

  // Gradient border wrapper component
  if (gradient) {
    return (
      <div 
        className={cn(
          "relative group",
          borderRadiusOptions[borderRadius],
          className
        )}
        {...props}
      >
        {/* Gradient border background */}
        <div className={cn(
          "absolute inset-0 bg-gradient-to-r from-purple-500/20 via-blue-500/20 to-purple-500/20",
          "opacity-60 group-hover:opacity-100 transition-opacity duration-300",
          borderRadiusOptions[borderRadius],
          glowEffect && "shadow-glow group-hover:shadow-glow-lg"
        )} />
        
        {/* Inner content with glass effect */}
        <div className={cn(
          "relative",
          "bg-slate-800/40 border border-slate-700/50",
          backdropOptions[backdrop],
          borderRadiusOptions[borderRadius],
          paddingSizes[padding],
          hover && "hover:bg-slate-800/60 hover:border-slate-600/50 hover:scale-[1.01]",
          "transition-all duration-300 ease-out",
          "shadow-xl shadow-black/10",
          // Inset border for extra depth
          "before:absolute before:inset-0 before:rounded-[inherit] before:border before:border-white/10 before:pointer-events-none"
        )}>
          {children}
        </div>
      </div>
    );
  }

  // Standard glass card without gradient border
  return (
    <div
      className={cn(
        "relative group",
        // Glass effect background
        "bg-slate-800/40 border border-slate-700/50",
        backdropOptions[backdrop],
        borderRadiusOptions[borderRadius],
        paddingSizes[padding],
        
        // Hover effects
        hover && [
          "hover:bg-slate-800/60",
          "hover:border-slate-600/50", 
          "hover:scale-[1.01]",
          "hover:shadow-xl hover:shadow-purple-500/10"
        ],
        
        // Animations
        "transition-all duration-300 ease-out",
        
        // Base shadows
        "shadow-lg shadow-black/20",
        
        // Glow effect
        glowEffect && "shadow-glow group-hover:shadow-glow-lg",
        
        // Inner border highlight
        "before:absolute before:inset-0 before:rounded-[inherit] before:border before:border-white/5 before:pointer-events-none",
        
        // Custom class overrides
        className
      )}
      {...props}
    >
      {/* Content wrapper for additional styling if needed */}
      <div className="relative z-10">
        {children}
      </div>
      
      {/* Optional inner glow effect */}
      {glowEffect && (
        <div className={cn(
          "absolute inset-0 opacity-0 group-hover:opacity-20",
          "bg-gradient-to-br from-purple-400/20 via-transparent to-blue-400/20",
          "transition-opacity duration-500",
          borderRadiusOptions[borderRadius],
          "pointer-events-none"
        )} />
      )}
    </div>
  );
};

// Pre-configured variants for common use cases
export const GlassCardVariants = {
  // Executive dashboard cards
  Executive: (props) => (
    <GlassCard 
      gradient={true}
      glowEffect={true}
      borderRadius="lg"
      backdrop="md"
      {...props} 
    />
  ),
  
  // Metric display cards
  Metric: (props) => (
    <GlassCard 
      padding="lg"
      hover={true}
      glowEffect={false}
      borderRadius="xl"
      {...props} 
    />
  ),
  
  // Chat interface container
  Chat: (props) => (
    <GlassCard 
      padding="none"
      gradient={false}
      backdrop="lg"
      borderRadius="lg"
      {...props} 
    />
  ),
  
  // Sidebar panels
  Sidebar: (props) => (
    <GlassCard 
      padding="default"
      hover={false}
      backdrop="sm"
      borderRadius="lg"
      {...props} 
    />
  )
};

export default GlassCard;

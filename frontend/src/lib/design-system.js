/**
 * Design System Utilities
 * Provides utilities for applying design tokens and creating consistent styling
 */

import { defaultDesignTokens } from './figma-integration.js';

/**
 * Design System Class
 * Manages design tokens and provides utility functions for styling
 */
export class DesignSystem {
  constructor(tokens = defaultDesignTokens) {
    this.tokens = tokens;
    this.cssVariables = this.generateCSSVariables();
  }

  /**
   * Update design tokens
   */
  updateTokens(newTokens) {
    this.tokens = { ...this.tokens, ...newTokens };
    this.cssVariables = this.generateCSSVariables();
    this.injectCSSVariables();
  }

  /**
   * Generate CSS custom properties from design tokens
   */
  generateCSSVariables() {
    let css = ':root {\n';

    // Colors
    if (this.tokens.colors) {
      Object.entries(this.tokens.colors).forEach(([key, value]) => {
        const cleanKey = key.toLowerCase().replace(/[^a-z0-9]/g, '-');
        css += `  --color-${cleanKey}: ${value};\n`;
      });
    }

    // Typography
    if (this.tokens.typography) {
      css += `  --font-family-primary: ${this.tokens.typography.fontFamily};\n`;
      
      if (this.tokens.typography.fontSize) {
        Object.entries(this.tokens.typography.fontSize).forEach(([key, value]) => {
          css += `  --font-size-${key}: ${value};\n`;
        });
      }
    }

    // Glassmorphism
    if (this.tokens.glassmorphism) {
      Object.entries(this.tokens.glassmorphism).forEach(([key, value]) => {
        css += `  --glassmorphism-${key}: ${value};\n`;
      });
    }

    css += '}\n';
    return css;
  }

  /**
   * Inject CSS variables into the document
   */
  injectCSSVariables() {
    // Remove existing style element if it exists
    const existingStyle = document.getElementById('design-system-variables');
    if (existingStyle) {
      existingStyle.remove();
    }

    // Create and inject new style element
    const style = document.createElement('style');
    style.id = 'design-system-variables';
    style.textContent = this.cssVariables;
    document.head.appendChild(style);
  }

  /**
   * Get color value by key
   */
  getColor(key) {
    return this.tokens.colors?.[key] || '#000000';
  }

  /**
   * Get glassmorphism styles
   */
  getGlassmorphismStyles() {
    const glass = this.tokens.glassmorphism || {};
    return {
      backdropFilter: glass.backdrop || 'blur(20px)',
      background: glass.background || 'rgba(255, 255, 255, 0.1)',
      border: glass.border || '1px solid rgba(255, 255, 255, 0.2)',
      boxShadow: glass.shadow || '0 8px 32px rgba(0, 0, 0, 0.1)'
    };
  }

  /**
   * Generate component class names with design tokens
   */
  getComponentClasses(componentType) {
    const baseClasses = {
      card: 'rounded-lg p-6 transition-all duration-300',
      button: 'px-4 py-2 rounded-md font-medium transition-all duration-200',
      input: 'px-3 py-2 rounded-md border transition-all duration-200',
      heading: 'font-semibold tracking-tight',
      text: 'text-sm leading-relaxed'
    };

    const glassmorphismClasses = {
      card: 'backdrop-blur-xl bg-white/10 border border-white/20 shadow-xl',
      button: 'backdrop-blur-md bg-white/20 border border-white/30 hover:bg-white/30',
      input: 'backdrop-blur-md bg-white/10 border border-white/20 focus:border-white/40'
    };

    return {
      base: baseClasses[componentType] || '',
      glassmorphism: glassmorphismClasses[componentType] || ''
    };
  }
}

/**
 * Glassmorphism utility functions
 */
export const glassmorphism = {
  /**
   * Get glassmorphism CSS properties
   */
  getStyles: (opacity = 0.1, blur = 20) => ({
    backdropFilter: `blur(${blur}px)`,
    background: `rgba(255, 255, 255, ${opacity})`,
    border: `1px solid rgba(255, 255, 255, ${opacity * 2})`,
    boxShadow: '0 8px 32px rgba(0, 0, 0, 0.1)'
  }),

  /**
   * Get glassmorphism Tailwind classes
   */
  getClasses: (variant = 'default') => {
    const variants = {
      default: 'backdrop-blur-xl bg-white/10 border border-white/20 shadow-xl',
      subtle: 'backdrop-blur-lg bg-white/5 border border-white/10 shadow-lg',
      strong: 'backdrop-blur-2xl bg-white/20 border border-white/30 shadow-2xl',
      dark: 'backdrop-blur-xl bg-black/10 border border-black/20 shadow-xl'
    };
    return variants[variant] || variants.default;
  }
};

/**
 * Color utility functions
 */
export const colors = {
  /**
   * Convert hex to rgba
   */
  hexToRgba: (hex, alpha = 1) => {
    const r = parseInt(hex.slice(1, 3), 16);
    const g = parseInt(hex.slice(3, 5), 16);
    const b = parseInt(hex.slice(5, 7), 16);
    return `rgba(${r}, ${g}, ${b}, ${alpha})`;
  },

  /**
   * Get gradient styles
   */
  getGradient: (from, to, direction = 'to right') => ({
    background: `linear-gradient(${direction}, ${from}, ${to})`
  }),

  /**
   * Get status colors
   */
  getStatusColor: (status) => {
    const statusColors = {
      success: 'rgb(34, 197, 94)',
      warning: 'rgb(251, 191, 36)',
      error: 'rgb(239, 68, 68)',
      info: 'rgb(59, 130, 246)',
      neutral: 'rgb(148, 163, 184)'
    };
    return statusColors[status] || statusColors.neutral;
  }
};

/**
 * Typography utility functions
 */
export const typography = {
  /**
   * Get heading styles
   */
  getHeadingStyles: (level = 1) => {
    const styles = {
      1: { fontSize: '2.25rem', fontWeight: '700', lineHeight: '2.5rem' },
      2: { fontSize: '1.875rem', fontWeight: '600', lineHeight: '2.25rem' },
      3: { fontSize: '1.5rem', fontWeight: '600', lineHeight: '2rem' },
      4: { fontSize: '1.25rem', fontWeight: '600', lineHeight: '1.75rem' },
      5: { fontSize: '1.125rem', fontWeight: '600', lineHeight: '1.5rem' },
      6: { fontSize: '1rem', fontWeight: '600', lineHeight: '1.5rem' }
    };
    return styles[level] || styles[1];
  },

  /**
   * Get text styles
   */
  getTextStyles: (variant = 'body') => {
    const variants = {
      body: { fontSize: '1rem', lineHeight: '1.5rem' },
      small: { fontSize: '0.875rem', lineHeight: '1.25rem' },
      caption: { fontSize: '0.75rem', lineHeight: '1rem' },
      lead: { fontSize: '1.125rem', lineHeight: '1.75rem' }
    };
    return variants[variant] || variants.body;
  }
};

/**
 * Animation utility functions
 */
export const animations = {
  /**
   * Get transition styles
   */
  getTransition: (properties = 'all', duration = '200ms', easing = 'ease-in-out') => ({
    transition: `${properties} ${duration} ${easing}`
  }),

  /**
   * Get hover transform styles
   */
  getHoverTransform: (scale = 1.02, translateY = -2) => ({
    transform: `scale(${scale}) translateY(${translateY}px)`
  }),

  /**
   * Get fade in animation
   */
  getFadeIn: (duration = '300ms', delay = '0ms') => ({
    animation: `fadeIn ${duration} ${delay} ease-in-out forwards`,
    opacity: 0
  })
};

/**
 * Layout utility functions
 */
export const layout = {
  /**
   * Get flexbox utilities
   */
  getFlex: (direction = 'row', align = 'center', justify = 'start', gap = '1rem') => ({
    display: 'flex',
    flexDirection: direction,
    alignItems: align,
    justifyContent: justify,
    gap
  }),

  /**
   * Get grid utilities
   */
  getGrid: (columns = 'repeat(auto-fit, minmax(300px, 1fr))', gap = '1.5rem') => ({
    display: 'grid',
    gridTemplateColumns: columns,
    gap
  }),

  /**
   * Get responsive padding
   */
  getResponsivePadding: () => ({
    padding: 'clamp(1rem, 4vw, 2rem)'
  })
};

// Create default design system instance
export const designSystem = new DesignSystem();

// Initialize CSS variables on module load
if (typeof document !== 'undefined') {
  designSystem.injectCSSVariables();
}

export default designSystem;


/**
 * Figma API Integration for Design Token Extraction
 * Extracts design tokens, components, and styles from Figma files
 */

const FIGMA_API_BASE = 'https://api.figma.com/v1';

// Securely retrieve Figma token from environment variables
// This is populated by Pulumi ESC from GitHub Organization Secrets
const FIGMA_TOKEN = process.env.FIGMA_PERSONAL_ACCESS_TOKEN;

class FigmaIntegration {
  constructor(accessToken = FIGMA_TOKEN) {
    if (!accessToken) {
      console.warn('Figma token not found in environment variables. Design token extraction will be disabled.');
    }
    this.accessToken = accessToken;
    this.headers = {
      'X-Figma-Token': accessToken,
      'Content-Type': 'application/json'
    };
  }

  /**
   * Get file information and structure
   */
  async getFileInfo(fileKey) {
    if (!this.accessToken) {
      console.warn('Figma token not available. Using default design tokens.');
      return null;
    }

    try {
      const response = await fetch(`${FIGMA_API_BASE}/files/${fileKey}`, {
        headers: this.headers
      });
      
      if (!response.ok) {
        throw new Error(`Figma API error: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error fetching Figma file:', error);
      console.warn('Falling back to default design tokens.');
      return null;
    }
  }

  /**
   * Extract design tokens from file data
   */
  extractDesignTokens(fileData) {
    const tokens = {
      colors: {},
      typography: {},
      spacing: {},
      shadows: {},
      borders: {},
      glassmorphism: {}
    };

    const traverseNode = (node, path = '') => {
      const nodeName = node.name || '';
      const currentPath = path ? `${path}/${nodeName}` : nodeName;

      // Extract fills (colors)
      if (node.fills && node.fills.length > 0) {
        node.fills.forEach((fill, index) => {
          if (fill.type === 'SOLID' && fill.color) {
            const color = fill.color;
            const rgb = `rgb(${Math.round(color.r * 255)}, ${Math.round(color.g * 255)}, ${Math.round(color.b * 255)})`;
            const rgba = `rgba(${Math.round(color.r * 255)}, ${Math.round(color.g * 255)}, ${Math.round(color.b * 255)}, ${fill.opacity || 1})`;
            
            tokens.colors[`${currentPath}_${index}`] = {
              rgb,
              rgba,
              opacity: fill.opacity || 1
            };
          }
        });
      }

      // Extract text styles
      if (node.type === 'TEXT' && node.style) {
        const style = node.style;
        tokens.typography[currentPath] = {
          fontFamily: style.fontFamily || 'Inter',
          fontSize: style.fontSize || 16,
          fontWeight: style.fontWeight || 400,
          lineHeight: style.lineHeightPx || style.fontSize * 1.2,
          letterSpacing: style.letterSpacing || 0,
          textAlign: style.textAlignHorizontal || 'left'
        };
      }

      // Extract effects (shadows, blur)
      if (node.effects && node.effects.length > 0) {
        node.effects.forEach((effect, index) => {
          if (effect.type === 'DROP_SHADOW') {
            tokens.shadows[`${currentPath}_${index}`] = {
              x: effect.offset?.x || 0,
              y: effect.offset?.y || 0,
              blur: effect.radius || 0,
              spread: effect.spread || 0,
              color: effect.color ? 
                `rgba(${Math.round(effect.color.r * 255)}, ${Math.round(effect.color.g * 255)}, ${Math.round(effect.color.b * 255)}, ${effect.color.a || 1})` : 
                'rgba(0, 0, 0, 0.1)'
            };
          } else if (effect.type === 'BACKGROUND_BLUR') {
            tokens.glassmorphism[`${currentPath}_${index}`] = {
              backdropFilter: `blur(${effect.radius || 20}px)`,
              background: 'rgba(255, 255, 255, 0.1)',
              border: '1px solid rgba(255, 255, 255, 0.2)'
            };
          }
        });
      }

      // Extract corner radius
      if (node.cornerRadius !== undefined) {
        tokens.borders[`${currentPath}_radius`] = {
          borderRadius: node.cornerRadius
        };
      }

      // Recursively process children
      if (node.children) {
        node.children.forEach(child => traverseNode(child, currentPath));
      }
    };

    // Start traversal from document root
    if (fileData.document) {
      traverseNode(fileData.document);
    }

    return tokens;
  }

  /**
   * Find dashboard-related components
   */
  findDashboardComponents(fileData) {
    const dashboardComponents = [];
    const dashboardKeywords = [
      'dashboard', 'kpi', 'card', 'chart', 'metric', 'widget',
      'panel', 'executive', 'analytics', 'graph', 'table', 'ceo'
    ];

    const searchComponents = (node) => {
      const nodeName = (node.name || '').toLowerCase();
      const nodeType = node.type || '';

      // Check if node matches dashboard keywords
      const isRelevant = dashboardKeywords.some(keyword => 
        nodeName.includes(keyword)
      );

      if (isRelevant) {
        dashboardComponents.push({
          name: node.name || '',
          type: nodeType,
          id: node.id || '',
          bounds: node.absoluteBoundingBox || {},
          styles: {
            fills: node.fills || [],
            effects: node.effects || [],
            cornerRadius: node.cornerRadius || 0,
            constraints: node.constraints || {}
          }
        });
      }

      // Recursively search children
      if (node.children) {
        node.children.forEach(child => searchComponents(child));
      }
    };

    if (fileData.document) {
      searchComponents(fileData.document);
    }

    return dashboardComponents;
  }

  /**
   * Generate CSS custom properties from design tokens
   */
  generateCSSVariables(tokens) {
    let css = ':root {\n';

    // Colors
    Object.entries(tokens.colors).forEach(([key, value]) => {
      const cleanKey = key.toLowerCase().replace(/[^a-z0-9]/g, '-');
      css += `  --color-${cleanKey}: ${value.rgba};\n`;
    });

    // Typography
    Object.entries(tokens.typography).forEach(([key, value]) => {
      const cleanKey = key.toLowerCase().replace(/[^a-z0-9]/g, '-');
      css += `  --font-family-${cleanKey}: ${value.fontFamily};\n`;
      css += `  --font-size-${cleanKey}: ${value.fontSize}px;\n`;
      css += `  --font-weight-${cleanKey}: ${value.fontWeight};\n`;
      css += `  --line-height-${cleanKey}: ${value.lineHeight}px;\n`;
    });

    // Shadows
    Object.entries(tokens.shadows).forEach(([key, value]) => {
      const cleanKey = key.toLowerCase().replace(/[^a-z0-9]/g, '-');
      css += `  --shadow-${cleanKey}: ${value.x}px ${value.y}px ${value.blur}px ${value.spread}px ${value.color};\n`;
    });

    // Glassmorphism
    Object.entries(tokens.glassmorphism).forEach(([key, value]) => {
      const cleanKey = key.toLowerCase().replace(/[^a-z0-9]/g, '-');
      css += `  --glassmorphism-backdrop-${cleanKey}: ${value.backdropFilter};\n`;
      css += `  --glassmorphism-bg-${cleanKey}: ${value.background};\n`;
      css += `  --glassmorphism-border-${cleanKey}: ${value.border};\n`;
    });

    css += '}\n';
    return css;
  }

  /**
   * Generate Tailwind CSS configuration from design tokens
   */
  generateTailwindConfig(tokens) {
    const config = {
      theme: {
        extend: {
          colors: {},
          fontFamily: {},
          fontSize: {},
          fontWeight: {},
          boxShadow: {},
          backdropBlur: {}
        }
      }
    };

    // Process colors
    Object.entries(tokens.colors).forEach(([key, value]) => {
      const cleanKey = key.toLowerCase().replace(/[^a-z0-9]/g, '-');
      config.theme.extend.colors[cleanKey] = value.rgba;
    });

    // Process typography
    Object.entries(tokens.typography).forEach(([key, value]) => {
      const cleanKey = key.toLowerCase().replace(/[^a-z0-9]/g, '-');
      config.theme.extend.fontFamily[cleanKey] = [value.fontFamily];
      config.theme.extend.fontSize[cleanKey] = [`${value.fontSize}px`, `${value.lineHeight}px`];
      config.theme.extend.fontWeight[cleanKey] = value.fontWeight;
    });

    // Process shadows
    Object.entries(tokens.shadows).forEach(([key, value]) => {
      const cleanKey = key.toLowerCase().replace(/[^a-z0-9]/g, '-');
      config.theme.extend.boxShadow[cleanKey] = `${value.x}px ${value.y}px ${value.blur}px ${value.spread}px ${value.color}`;
    });

    return config;
  }
}

// Default design tokens for fallback
export const defaultDesignTokens = {
  colors: {
    primary: 'rgb(99, 102, 241)',
    secondary: 'rgb(139, 92, 246)',
    background: 'rgb(15, 23, 42)',
    surface: 'rgba(255, 255, 255, 0.1)',
    text: 'rgb(248, 250, 252)',
    textSecondary: 'rgb(148, 163, 184)',
    success: 'rgb(34, 197, 94)',
    warning: 'rgb(251, 191, 36)',
    error: 'rgb(239, 68, 68)',
    info: 'rgb(59, 130, 246)'
  },
  glassmorphism: {
    backdrop: 'blur(20px)',
    background: 'rgba(255, 255, 255, 0.1)',
    border: '1px solid rgba(255, 255, 255, 0.2)',
    shadow: '0 8px 32px rgba(0, 0, 0, 0.1)'
  },
  typography: {
    fontFamily: 'Inter, system-ui, sans-serif',
    fontSize: {
      xs: '0.75rem',
      sm: '0.875rem',
      base: '1rem',
      lg: '1.125rem',
      xl: '1.25rem',
      '2xl': '1.5rem',
      '3xl': '1.875rem',
      '4xl': '2.25rem'
    }
  }
};

export default FigmaIntegration;


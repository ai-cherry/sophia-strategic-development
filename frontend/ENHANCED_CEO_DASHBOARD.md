# 🚀 Enhanced Unified Dashboard

A professional, executive-level dashboard built with React, ShadCN/UI, and glassmorphism design principles. Features Figma API integration for automated design token extraction and a comprehensive component library for business intelligence interfaces.

## ✨ Features

- **🎨 Professional Design**: Glassmorphism effects with executive-appropriate aesthetics
- **📊 Interactive Charts**: Advanced data visualization with Recharts
- **🔧 Figma Integration**: Automated design token extraction from Figma files
- **📱 Responsive Design**: Perfect on desktop, tablet, and mobile devices
- **🛡️ Secure**: Environment-based credential management via Pulumi ESC
- **⚡ Performance**: Optimized for fast loading and smooth animations

## 🏗️ Architecture

```
src/
├── lib/
│   ├── figma-integration.js     # Figma API & design token extraction
│   └── design-system.js         # Design system utilities & glassmorphism
├── components/
│   ├── KPICard.jsx             # Professional KPI metric cards
│   ├── ExecutiveChart.jsx       # Advanced chart components
│   └── UnifiedDashboard.jsx        # Main dashboard layout
└── App.jsx                     # Application entry point
```

## 🔐 Security & Environment Setup

### Figma Token Management

The dashboard integrates with Figma API for design token extraction. The Figma Personal Access Token is managed securely through:

1. **GitHub Organization Secrets** - Store `FIGMA_PERSONAL_ACCESS_TOKEN`
2. **Pulumi ESC** - Centralized secret management and distribution
3. **Environment Variables** - Runtime access via `process.env.FIGMA_PERSONAL_ACCESS_TOKEN`

### Environment Variables

```bash
# Required for Figma integration
FIGMA_PERSONAL_ACCESS_TOKEN=your_figma_token_here

# Optional: Figma file key for design token extraction
FIGMA_FILE_KEY=your_figma_file_key_here
```

## 🚀 Quick Start

### Development

```bash
# Install dependencies
pnpm install

# Start development server
pnpm run dev

# Build for production
pnpm run build
```

### Production Deployment

The dashboard is designed for deployment via Vercel with proper environment variable injection through Pulumi ESC.

```bash
# Deploy to Vercel
vercel --prod
```

## 📊 Components

### KPI Cards

Professional metric cards with trend indicators and status-based styling.

```jsx
import KPICard from './components/KPICard.jsx';

<KPICard
  title="Total Revenue"
  value="$2.4M"
  trend="up"
  trendValue="+12.5%"
  description="Trending up this month"
  status="success"
  icon={DollarSign}
  onClick={() => handleKPIClick('revenue')}
/>
```

### Executive Charts

Advanced chart components with glassmorphism styling and professional color schemes.

```jsx
import { RevenueChart } from './components/ExecutiveChart.jsx';

<RevenueChart
  data={revenueData}
  dataKeys={['revenue', 'projected']}
  title="Revenue Trends"
  subtitle="Actual vs Projected Revenue"
  height={300}
  valueFormatter={(value) => `$${(value / 1000).toFixed(1)}k`}
/>
```

### Design System

Comprehensive design system with glassmorphism utilities and professional styling.

```jsx
import { glassmorphism, colors, typography } from './lib/design-system.js';

// Apply glassmorphism effects
const glassStyles = glassmorphism.getStyles(0.1, 20);

// Get status colors
const statusColor = colors.getStatusColor('success');

// Apply typography styles
const headingStyles = typography.getHeadingStyles(1);
```

## 🎨 Design System

### Glassmorphism Effects

The dashboard uses a sophisticated glassmorphism design system with multiple variants:

- **Subtle**: `glassmorphism.getClasses('subtle')` - Low opacity for background elements
- **Default**: `glassmorphism.getClasses('default')` - Standard glassmorphism
- **Strong**: `glassmorphism.getClasses('strong')` - High opacity for focal elements

### Color Palette

- **Primary**: `#6366f1` - Main brand color
- **Secondary**: `#8b5cf6` - Accent color
- **Success**: `#10b981` - Positive metrics
- **Warning**: `#f59e0b` - Attention needed
- **Error**: `#ef4444` - Critical issues

### Typography

- **Font Family**: Inter, system-ui, sans-serif
- **Hierarchy**: H1 (36px) → H6 (16px)
- **Weights**: 400 (regular), 600 (semibold), 700 (bold)

## 🔧 Figma Integration

### Design Token Extraction

The dashboard can automatically extract design tokens from Figma files:

```javascript
import FigmaIntegration from './lib/figma-integration.js';

const figma = new FigmaIntegration();
const fileData = await figma.getFileInfo('your-figma-file-key');
const tokens = figma.extractDesignTokens(fileData);
const cssVariables = figma.generateCSSVariables(tokens);
```

### Supported Design Tokens

- **Colors**: Fill colors with opacity support
- **Typography**: Font families, sizes, weights, line heights
- **Effects**: Shadows and blur effects for glassmorphism
- **Spacing**: Margins, padding, and layout spacing
- **Borders**: Corner radius and border styles

## 📱 Responsive Design

### Breakpoints

- **Mobile**: `< 768px` - Single column layout
- **Tablet**: `768px - 1024px` - 2-column grid
- **Desktop**: `> 1024px` - Full 4-column grid

### Touch-Friendly

- **Large Touch Targets**: Minimum 44px touch areas
- **Gesture Support**: Swipe navigation on mobile
- **Accessible Controls**: Proper ARIA labels and keyboard navigation

## 🚀 Performance

### Optimizations

- **Code Splitting**: Lazy loading for better performance
- **Tree Shaking**: Eliminates unused code
- **Asset Optimization**: Compressed images and fonts
- **Progressive Loading**: Skeleton screens and loading states

### Browser Support

- **Modern Browsers**: Chrome 90+, Firefox 88+, Safari 14+
- **Fallbacks**: Graceful degradation for older browsers
- **Performance**: 60fps animations, smooth scrolling

## 🧪 Testing

### Development Testing

```bash
# Run development server
pnpm run dev

# Open browser to http://localhost:5173
```

### Production Testing

```bash
# Build and preview
pnpm run build
pnpm run preview
```

## 📦 Dependencies

### Core Dependencies

- **React 18+**: Modern React with hooks
- **Vite**: Fast build tool and dev server
- **Tailwind CSS**: Utility-first CSS framework
- **Recharts**: Professional chart library
- **Lucide React**: Consistent icon library

### Development Dependencies

- **ESLint**: Code linting and quality
- **PostCSS**: CSS processing
- **Autoprefixer**: CSS vendor prefixes

## 🤝 Contributing

1. **Security First**: Never commit API keys or tokens
2. **Component-Driven**: Build reusable, modular components
3. **Design System**: Follow established design patterns
4. **Performance**: Optimize for speed and accessibility
5. **Documentation**: Update README for new features

## 📄 License

This project is part of the Sophia AI platform and follows the organization's licensing terms.

## 🔗 Related Projects

- **Sophia Main**: Core AI platform backend
- **Admin Interface**: Management dashboard
- **Pay Ready Platform**: Business intelligence suite

---

**Built with ❤️ for executive-level business intelligence**

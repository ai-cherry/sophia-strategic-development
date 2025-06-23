---
title: Sophia AI Design System Integration Guide
description: 
tags: mcp, docker, monitoring
last_updated: 2025-06-23
dependencies: none
related_docs: none
---

# Sophia AI Design System Integration Guide


## Table of Contents

- [🎨 Overview](#🎨-overview)
- [🌑 Dark Theme Design Principles](#🌑-dark-theme-design-principles)
  - [Color Palette](#color-palette)
  - [Typography](#typography)
  - [Spacing System](#spacing-system)
- [🔌 Backend Integration](#🔌-backend-integration)
  - [API Service Layer](#api-service-layer)
  - [Available Endpoints](#available-endpoints)
    - [Company Metrics](#company-metrics)
    - [Strategy](#strategy)
    - [Operations](#operations)
    - [AI Insights](#ai-insights)
- [🧩 Component Architecture](#🧩-component-architecture)
  - [Core Design System Components](#core-design-system-components)
  - [Dashboard Layout Pattern](#dashboard-layout-pattern)
- [🚀 Implementation Patterns](#🚀-implementation-patterns)
  - [1. Creating New Dashboard Pages](#1.-creating-new-dashboard-pages)
  - [2. Connecting to MCP Servers](#2.-connecting-to-mcp-servers)
  - [3. Real-time Updates](#3.-real-time-updates)
- [🎯 Best Practices](#🎯-best-practices)
  - [Performance](#performance)
  - [Accessibility](#accessibility)
  - [State Management](#state-management)
- [📱 Responsive Design](#📱-responsive-design)
  - [Breakpoints](#breakpoints)
  - [Mobile Optimizations](#mobile-optimizations)
- [🔧 Extending the Design System](#🔧-extending-the-design-system)
  - [Adding New Components](#adding-new-components)
  - [Custom Animations](#custom-animations)
- [🚦 Testing](#🚦-testing)
  - [Component Testing](#component-testing)
  - [Integration Testing](#integration-testing)
- [🚀 Deployment](#🚀-deployment)
  - [Environment Variables](#environment-variables)
  - [Build Process](#build-process)
  - [Performance Optimization](#performance-optimization)
- [📊 Monitoring](#📊-monitoring)
  - [Frontend Analytics](#frontend-analytics)
  - [Error Tracking](#error-tracking)
- [🎉 Conclusion](#🎉-conclusion)

## 🎨 Overview

The Sophia AI admin interface now implements a modern, dark-themed design system that seamlessly integrates with the backend infrastructure. This guide explains how the design system connects with backend APIs and provides patterns for extending the interface.

## 🌑 Dark Theme Design Principles

### Color Palette
- **Background Primary:** `#0f172a` (slate-900) - Main app background
- **Background Secondary:** `#1e293b` (slate-800) - Cards, panels
- **Background Tertiary:** `#334155` (slate-700) - Borders, dividers
- **Primary Action:** `#8b5cf6` (purple-500) - CTAs, active states
- **Success:** `#10b981` (green-500) - Positive metrics
- **Warning:** `#f59e0b` (yellow-500) - Alerts
- **Error:** `#ef4444` (red-500) - Critical states

### Typography
- **Primary Font:** Inter (300-800 weights)
- **Code Font:** JetBrains Mono
- **Scale:** Display (48px) → Caption (12px)

### Spacing System
- Based on 8px grid: 8px, 16px, 24px, 32px, 48px, 64px
- Consistent padding/margin using Tailwind classes

## 🔌 Backend Integration

### API Service Layer

Located at `frontend/src/services/api.js`, the API service provides:

```javascript
// Example usage in components
import api from '@/services/api';

// Fetch company metrics
const metrics = await api.getCompanyMetrics();

// Get AI insights
const insights = await api.getAIInsights();

// Search property units
const units = await api.searchUnits({
  bedrooms: 2,
  maxRent: 3000
});
```python

### Available Endpoints

#### Company Metrics
- `GET /api/company/metrics` - Overall business KPIs
- `GET /api/company/revenue` - Revenue data
- `GET /api/company/customers` - Customer metrics
- `GET /api/company/health-score` - Business health score

#### Strategy
- `GET /api/strategy/insights` - Strategic insights
- `GET /api/strategy/growth-opportunities` - Growth analysis
- `GET /api/strategy/market-analysis` - Market positioning

#### Operations
- `GET /api/operations/metrics` - Operational KPIs
- `GET /api/operations/workflows` - Active workflows
- `GET /api/operations/status` - System status

#### AI Insights
- `GET /api/ai/insights` - AI-generated insights
- `GET /api/ai/predictions` - Predictive analytics
- `GET /api/ai/recommendations` - Action recommendations

## 🧩 Component Architecture

### Core Design System Components

1. **MetricCard** (`/components/design-system/cards/MetricCard.jsx`)
   - Displays KPIs with trend indicators
   - Supports loading states
   - Interactive hover effects

2. **GlassCard** (`/components/design-system/cards/GlassCard.jsx`)
   - Glassmorphism effect container
   - Optional gradient borders
   - Configurable padding

3. **Button** (`/components/design-system/buttons/Button.jsx`)
   - Multiple variants: primary, secondary, ghost, destructive
   - Loading states with spinner
   - Icon support

4. **Input** (`/components/design-system/forms/Input.jsx`)
   - Dark theme optimized
   - Error state handling
   - Icon support

5. **Header** (`/components/design-system/navigation/Header.jsx`)
   - Fixed navigation with glass effect
   - Search functionality
   - User menu

### Dashboard Layout Pattern

The main dashboard (`/components/dashboard/DashboardLayout.jsx`) demonstrates:

```jsx
# Example usage:
jsx
```python

## 🚀 Implementation Patterns

### 1. Creating New Dashboard Pages

```jsx
# Example usage:
jsx
```python

### 2. Connecting to MCP Servers

The frontend can interact with MCP servers through the backend API:

```javascript
# Example usage:
javascript
```python

### 3. Real-time Updates

For real-time data, implement WebSocket connections:

```javascript
# Example usage:
javascript
```python

## 🎯 Best Practices

### Performance
1. **Lazy Loading:** Load components on demand
2. **Memoization:** Use React.memo for expensive components
3. **Virtual Scrolling:** For large data tables
4. **Image Optimization:** Use next-gen formats

### Accessibility
1. **ARIA Labels:** All interactive elements
2. **Keyboard Navigation:** Full support
3. **Screen Readers:** Semantic HTML
4. **Color Contrast:** WCAG 2.1 AA compliant

### State Management
1. **Local State:** For component-specific data
2. **Context API:** For global UI state
3. **API Cache:** Using React Query or SWR
4. **Form State:** React Hook Form

## 📱 Responsive Design

### Breakpoints
- **Mobile:** 320px - 640px
- **Tablet:** 768px - 1024px
- **Desktop:** 1024px+

### Mobile Optimizations
- Collapsed navigation
- Stack layouts vertically
- Touch-friendly tap targets (44px minimum)
- Swipe gestures for navigation

## 🔧 Extending the Design System

### Adding New Components

1. Create component in appropriate directory:
   ```python
# Example usage:
python
```javascript
animation: {
  'custom-slide': 'customSlide 0.3s ease-out',
},
keyframes: {
  customSlide: {
    '0%': { transform: 'translateX(-100%)' },
    '100%': { transform: 'translateX(0)' },
  },
}
```python
# Example usage:
python
```javascript
import { render, screen } from '@testing-library/react';
import MetricCard from '@/components/design-system/cards/MetricCard';

test('renders metric card with value', () => {
  render(
    <MetricCard
      title="Revenue"
      value="$100K"
      change="+15%"
      trend="up"
    />
  );

  expect(screen.getByText('$100K')).toBeInTheDocument();
  expect(screen.getByText('+15%')).toBeInTheDocument();
});
```python
# Example usage:
python
```javascript
import { rest } from 'msw';
import { setupServer } from 'msw/node';

const server = setupServer(
  rest.get('/api/company/metrics', (req, res, ctx) => {
    return res(ctx.json({
      revenue: { value: '$100K', change: '+15%', trend: 'up' }
    }));
  })
);
```python
# Example usage:
python
```bash
# Frontend environment variables
VITE_API_URL=https://api.sophiaai.payready.com
VITE_WS_URL=wss://api.sophiaai.payready.com/ws
```python
# Example usage:
python
```bash
# Build for production
npm run build

# Preview production build
npm run preview
```python
# Example usage:
python
```javascript
// Track metric card clicks
const handleMetricClick = (metricType) => {
  analytics.track('Metric Card Clicked', {
    metric_type: metricType,
    timestamp: new Date()
  });
};
```python
# Example usage:
python
```javascript
import * as Sentry from "@sentry/react";

Sentry.init({
  dsn: process.env.VITE_SENTRY_DSN,
  environment: process.env.NODE_ENV,
});
```python

## 🎉 Conclusion

The Sophia AI design system provides a cohesive, modern interface that seamlessly integrates with the powerful backend infrastructure. By following these patterns and best practices, you can extend the platform while maintaining consistency and performance.

For questions or contributions, please refer to the main project documentation or contact the development team.

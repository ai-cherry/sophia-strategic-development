/**
 * Frontend Performance Monitor
 * Tracks real-time performance metrics and optimizes based on data
 */

export interface PerformanceMetrics {
  renderTime: number;
  apiResponseTime: number;
  memoryUsage: number;
  networkRequests: number;
  errorCount: number;
  timestamp: number;
}

export interface PerformanceThresholds {
  maxRenderTime: number;
  maxApiResponseTime: number;
  maxMemoryUsage: number;
  maxErrorRate: number;
}

class FrontendPerformanceMonitor {
  private metrics: PerformanceMetrics[] = [];
  private thresholds: PerformanceThresholds;
  private observers: Map<string, ((metrics: PerformanceMetrics) => void)[]> = new Map();
  private performanceObserver: PerformanceObserver | null = null;
  
  constructor(thresholds: Partial<PerformanceThresholds> = {}) {
    this.thresholds = {
      maxRenderTime: 16, // 60fps = 16ms per frame
      maxApiResponseTime: 1000, // 1 second
      maxMemoryUsage: 50 * 1024 * 1024, // 50MB
      maxErrorRate: 0.05, // 5%
      ...thresholds
    };
    
    this.initializePerformanceObserver();
    this.startMetricsCollection();
  }
  
  private initializePerformanceObserver() {
    if ('PerformanceObserver' in window) {
      this.performanceObserver = new PerformanceObserver((list) => {
        for (const entry of list.getEntries()) {
          this.processPerformanceEntry(entry);
        }
      });
      
      this.performanceObserver.observe({ 
        entryTypes: ['measure', 'navigation', 'paint', 'largest-contentful-paint'] 
      });
    }
  }
  
  private processPerformanceEntry(entry: PerformanceEntry) {
    switch (entry.entryType) {
      case 'measure':
        if (entry.name.startsWith('react-render')) {
          this.recordRenderTime(entry.duration);
        }
        break;
        
      case 'navigation':
        const navEntry = entry as PerformanceNavigationTiming;
        this.recordApiResponseTime(navEntry.responseEnd - navEntry.requestStart);
        break;
        
      case 'largest-contentful-paint':
        console.log('🎨 LCP:', entry.startTime + 'ms');
        break;
    }
  }
  
  private startMetricsCollection() {
    // Collect metrics every 5 seconds
    setInterval(() => {
      this.collectCurrentMetrics();
    }, 5000);
  }
  
  private collectCurrentMetrics() {
    const now = Date.now();
    
    // Memory usage (if available)
    let memoryUsage = 0;
    if ('memory' in performance) {
      const memInfo = (performance as any).memory;
      memoryUsage = memInfo.usedJSHeapSize;
    }
    
    // Network requests (approximate from last 5 seconds)
    const recentMetrics = this.metrics.filter(m => now - m.timestamp < 5000);
    const networkRequests = recentMetrics.length;
    
    // Error count from recent metrics
    const errorCount = recentMetrics.reduce((sum, m) => sum + m.errorCount, 0);
    
    const metrics: PerformanceMetrics = {
      renderTime: this.getAverageRenderTime(),
      apiResponseTime: this.getAverageApiResponseTime(),
      memoryUsage,
      networkRequests,
      errorCount,
      timestamp: now
    };
    
    this.addMetrics(metrics);
    this.checkThresholds(metrics);
  }
  
  private getAverageRenderTime(): number {
    const recent = this.metrics.slice(-10).filter(m => m.renderTime > 0);
    if (recent.length === 0) return 0;
    
    return recent.reduce((sum, m) => sum + m.renderTime, 0) / recent.length;
  }
  
  private getAverageApiResponseTime(): number {
    const recent = this.metrics.slice(-10).filter(m => m.apiResponseTime > 0);
    if (recent.length === 0) return 0;
    
    return recent.reduce((sum, m) => sum + m.apiResponseTime, 0) / recent.length;
  }
  
  recordRenderTime(duration: number) {
    if (duration > this.thresholds.maxRenderTime) {
      console.warn(`⚠️ Slow render detected: ${duration.toFixed(2)}ms`);
    }
  }
  
  recordApiResponseTime(duration: number) {
    if (duration > this.thresholds.maxApiResponseTime) {
      console.warn(`⚠️ Slow API response: ${duration.toFixed(2)}ms`);
    }
  }
  
  recordError(error: Error) {
    console.error('❌ Frontend error recorded:', error);
    // Increment error count in latest metrics
    if (this.metrics.length > 0) {
      this.metrics[this.metrics.length - 1].errorCount++;
    }
  }
  
  private addMetrics(metrics: PerformanceMetrics) {
    this.metrics.push(metrics);
    
    // Keep only last 100 metrics
    if (this.metrics.length > 100) {
      this.metrics = this.metrics.slice(-100);
    }
    
    this.notifyObservers('metrics', metrics);
  }
  
  private checkThresholds(metrics: PerformanceMetrics) {
    const warnings = [];
    
    if (metrics.renderTime > this.thresholds.maxRenderTime) {
      warnings.push(`Render time: ${metrics.renderTime.toFixed(2)}ms`);
    }
    
    if (metrics.apiResponseTime > this.thresholds.maxApiResponseTime) {
      warnings.push(`API response: ${metrics.apiResponseTime.toFixed(2)}ms`);
    }
    
    if (metrics.memoryUsage > this.thresholds.maxMemoryUsage) {
      warnings.push(`Memory usage: ${(metrics.memoryUsage / 1024 / 1024).toFixed(1)}MB`);
    }
    
    const errorRate = metrics.errorCount / Math.max(1, metrics.networkRequests);
    if (errorRate > this.thresholds.maxErrorRate) {
      warnings.push(`Error rate: ${(errorRate * 100).toFixed(1)}%`);
    }
    
    if (warnings.length > 0) {
      console.warn('⚠️ Performance thresholds exceeded:', warnings);
      this.notifyObservers('threshold_exceeded', { metrics, warnings });
    }
  }
  
  subscribe(event: string, callback: (data: any) => void) {
    if (!this.observers.has(event)) {
      this.observers.set(event, []);
    }
    
    this.observers.get(event)!.push(callback);
    
    // Return unsubscribe function
    return () => {
      const callbacks = this.observers.get(event);
      if (callbacks) {
        const index = callbacks.indexOf(callback);
        if (index > -1) {
          callbacks.splice(index, 1);
        }
      }
    };
  }
  
  private notifyObservers(event: string, data: any) {
    const callbacks = this.observers.get(event) || [];
    callbacks.forEach(callback => {
      try {
        callback(data);
      } catch (error) {
        console.error(`❌ Performance monitor callback error:`, error);
      }
    });
  }
  
  getMetrics(): PerformanceMetrics[] {
    return [...this.metrics];
  }
  
  getCurrentPerformance() {
    const recent = this.metrics.slice(-5);
    if (recent.length === 0) return null;
    
    return {
      averageRenderTime: recent.reduce((sum, m) => sum + m.renderTime, 0) / recent.length,
      averageApiResponseTime: recent.reduce((sum, m) => sum + m.apiResponseTime, 0) / recent.length,
      currentMemoryUsage: recent[recent.length - 1].memoryUsage,
      recentErrorCount: recent.reduce((sum, m) => sum + m.errorCount, 0),
      timestamp: Date.now()
    };
  }
  
  exportMetrics(): string {
    return JSON.stringify({
      metrics: this.metrics,
      thresholds: this.thresholds,
      summary: this.getCurrentPerformance()
    }, null, 2);
  }
}

// Create singleton performance monitor
export const performanceMonitor = new FrontendPerformanceMonitor();

// Auto-track React renders
if (process.env.NODE_ENV === 'development') {
  // Hook into React DevTools if available
  if (window.__REACT_DEVTOOLS_GLOBAL_HOOK__) {
    window.__REACT_DEVTOOLS_GLOBAL_HOOK__.onCommitFiberRoot = (id, root) => {
      performance.mark('react-render-start');
      setTimeout(() => {
        performance.mark('react-render-end');
        performance.measure('react-render', 'react-render-start', 'react-render-end');
      }, 0);
    };
  }
}

export default performanceMonitor;

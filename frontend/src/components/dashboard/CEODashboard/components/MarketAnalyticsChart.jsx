import React from 'react';
import { Doughnut, Bar } from 'react-chartjs-2';
import { 
  chartColors, 
  createDoughnutChartData, 
  createBarChartData,
  doughnutChartOptions,
  performanceChartOptions 
} from '../../../../utils/chartUtils';

const MarketAnalyticsChart = ({ data, loading, error, timeRange }) => {
  if (loading) {
    return (
      <div className="glassmorphism-card p-6">
        <div className="flex items-center space-x-3 mb-6">
          <div className="executive-icon gradient-purple-blue">
            <i className="fas fa-globe"></i>
          </div>
          <div>
            <h3 className="text-xl font-bold text-white">Market Analytics</h3>
            <p className="text-executive-secondary">Competitive intelligence</p>
          </div>
        </div>
        <div className="chart-container skeleton"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="glassmorphism-card p-6">
        <div className="flex items-center space-x-3 mb-6">
          <div className="executive-icon gradient-red">
            <i className="fas fa-exclamation-triangle"></i>
          </div>
          <div>
            <h3 className="text-xl font-bold text-white">Market Analytics</h3>
            <p className="text-executive-secondary">Error loading data</p>
          </div>
        </div>
        <div className="glassmorphism-light p-4 rounded-lg alert-error">
          <div className="flex items-center space-x-3">
            <i className="fas fa-exclamation-triangle text-red-500"></i>
            <span className="text-executive-secondary">
              Failed to load market data: {error}
            </span>
          </div>
        </div>
      </div>
    );
  }

  // Generate mock market data
  const marketData = data || {
    marketShare: [
      { name: 'Pay Ready', value: 12.3, color: chartColors.primary },
      { name: 'Competitor A', value: 24.8, color: chartColors.danger },
      { name: 'Competitor B', value: 18.5, color: chartColors.warning },
      { name: 'Competitor C', value: 15.2, color: chartColors.info },
      { name: 'Others', value: 29.2, color: chartColors.secondary }
    ],
    trends: [
      { category: 'Market Growth', value: 8.5, trend: 'up' },
      { category: 'Customer Acquisition', value: 15.2, trend: 'up' },
      { category: 'Competitive Position', value: 68.9, trend: 'up' },
      { category: 'Brand Recognition', value: 42.3, trend: 'neutral' }
    ]
  };

  // Prepare market share chart data
  const marketShareData = createDoughnutChartData(
    marketData.marketShare.map(item => item.name),
    marketData.marketShare.map(item => item.value),
    marketData.marketShare.map(item => item.color)
  );

  // Prepare trends chart data
  const trendsData = createBarChartData(
    marketData.trends.map(item => item.category),
    [{
      label: 'Performance %',
      data: marketData.trends.map(item => item.value),
      backgroundColor: marketData.trends.map(item => 
        item.trend === 'up' ? chartColors.success : 
        item.trend === 'down' ? chartColors.danger : chartColors.warning
      ),
      borderColor: 'transparent',
      borderRadius: 8
    }]
  );

  return (
    <div className="space-y-6">
      {/* Market Share */}
      <div className="glassmorphism-card p-6 hover-scale">
        <div className="flex items-center space-x-3 mb-6">
          <div className="executive-icon gradient-purple-blue">
            <i className="fas fa-chart-pie"></i>
          </div>
          <div>
            <h3 className="text-xl font-bold text-white">Market Share</h3>
            <p className="text-executive-secondary">Competitive positioning</p>
          </div>
        </div>
        
        <div className="chart-wrapper mb-4">
          <div className="chart-container" style={{ height: '250px' }}>
            <Doughnut data={marketShareData} options={doughnutChartOptions} />
          </div>
        </div>

        {/* Market Share Stats */}
        <div className="space-y-2">
          {marketData.marketShare.map((item, index) => (
            <div key={index} className="flex items-center justify-between text-sm">
              <div className="flex items-center space-x-2">
                <div 
                  className="w-3 h-3 rounded-full" 
                  style={{ backgroundColor: item.color }}
                ></div>
                <span className="text-executive-secondary">{item.name}</span>
              </div>
              <span className="text-white font-medium">{item.value}%</span>
            </div>
          ))}
        </div>
      </div>

      {/* Market Trends */}
      <div className="glassmorphism-card p-6 hover-scale">
        <div className="flex items-center space-x-3 mb-6">
          <div className="executive-icon gradient-orange">
            <i className="fas fa-trending-up"></i>
          </div>
          <div>
            <h3 className="text-xl font-bold text-white">Market Trends</h3>
            <p className="text-executive-secondary">Performance indicators</p>
          </div>
        </div>
        
        <div className="chart-wrapper mb-4">
          <div className="chart-container" style={{ height: '200px' }}>
            <Bar data={trendsData} options={performanceChartOptions} />
          </div>
        </div>

        {/* Trend Indicators */}
        <div className="space-y-3">
          {marketData.trends.map((trend, index) => (
            <div key={index} className="flex items-center justify-between">
              <span className="text-sm text-executive-secondary">{trend.category}</span>
              <div className="flex items-center space-x-2">
                <span className="text-white font-medium">{trend.value}%</span>
                <div className={`w-2 h-2 rounded-full pulse-dot ${
                  trend.trend === 'up' ? 'status-online' : 
                  trend.trend === 'down' ? 'status-offline' : 'status-warning'
                }`}></div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Market Insights */}
      <div className="glassmorphism-card p-6">
        <div className="flex items-center space-x-3 mb-4">
          <div className="executive-icon gradient-pink">
            <i className="fas fa-lightbulb"></i>
          </div>
          <div>
            <h3 className="text-lg font-bold text-white">Key Insights</h3>
          </div>
        </div>

        <div className="space-y-3 text-sm">
          <div className="glassmorphism-light p-3 rounded-lg">
            <div className="flex items-start space-x-2">
              <i className="fas fa-arrow-up trend-up mt-1"></i>
              <div>
                <p className="text-executive-secondary">
                  Market share increased by <span className="text-white font-medium">2.1%</span> this quarter
                </p>
              </div>
            </div>
          </div>
          
          <div className="glassmorphism-light p-3 rounded-lg">
            <div className="flex items-start space-x-2">
              <i className="fas fa-star text-yellow-500 mt-1"></i>
              <div>
                <p className="text-executive-secondary">
                  Leading in <span className="text-white font-medium">customer satisfaction</span> metrics
                </p>
              </div>
            </div>
          </div>
          
          <div className="glassmorphism-light p-3 rounded-lg">
            <div className="flex items-start space-x-2">
              <i className="fas fa-target text-blue-500 mt-1"></i>
              <div>
                <p className="text-executive-secondary">
                  Opportunity in <span className="text-white font-medium">enterprise segment</span> growth
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MarketAnalyticsChart;

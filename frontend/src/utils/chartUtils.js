// Chart.js utilities for executive dashboard
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  RadialLinearScale,
  Filler
} from 'chart.js';

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  RadialLinearScale,
  Filler
);

export const chartColors = {
  primary: '#8B5CF6',
  secondary: '#3B82F6',
  success: '#10B981',
  warning: '#F59E0B',
  danger: '#EF4444',
  info: '#06B6D4',
  light: '#F8FAFC',
  dark: '#0F172A',
  purple: '#8B5CF6',
  gradient: {
    purple: 'linear-gradient(135deg, #8B5CF6 0%, #3B82F6 100%)',
    green: 'linear-gradient(135deg, #10B981 0%, #059669 100%)',
    orange: 'linear-gradient(135deg, #F59E0B 0%, #D97706 100%)',
    red: 'linear-gradient(135deg, #EF4444 0%, #DC2626 100%)'
  }
};

export const defaultChartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: 'bottom',
      labels: {
        color: '#D1D5DB',
        font: {
          family: 'Inter',
          size: 12
        },
        padding: 20,
        usePointStyle: true
      }
    },
    tooltip: {
      backgroundColor: 'rgba(15, 23, 42, 0.95)',
      titleColor: '#FFFFFF',
      bodyColor: '#D1D5DB',
      borderColor: 'rgba(139, 92, 246, 0.2)',
      borderWidth: 1,
      cornerRadius: 8,
      displayColors: true,
      font: {
        family: 'Inter'
      }
    }
  },
  scales: {
    x: {
      grid: {
        color: 'rgba(139, 92, 246, 0.1)',
        borderColor: 'rgba(139, 92, 246, 0.2)'
      },
      ticks: {
        color: '#9CA3AF',
        font: {
          family: 'Inter',
          size: 11
        }
      }
    },
    y: {
      grid: {
        color: 'rgba(139, 92, 246, 0.1)',
        borderColor: 'rgba(139, 92, 246, 0.2)'
      },
      ticks: {
        color: '#9CA3AF',
        font: {
          family: 'Inter',
          size: 11
        }
      }
    }
  }
};

export const createLineChartData = (labels, datasets) => {
  return {
    labels,
    datasets: datasets.map((dataset, index) => ({
      ...dataset,
      borderColor: dataset.borderColor || chartColors.primary,
      backgroundColor: dataset.backgroundColor || chartColors.primary + '20',
      borderWidth: 2,
      fill: dataset.fill !== undefined ? dataset.fill : true,
      tension: 0.4,
      pointBackgroundColor: dataset.borderColor || chartColors.primary,
      pointBorderColor: '#FFFFFF',
      pointBorderWidth: 2,
      pointRadius: 4,
      pointHoverRadius: 6
    }))
  };
};

export const createBarChartData = (labels, datasets) => {
  return {
    labels,
    datasets: datasets.map((dataset, index) => ({
      ...dataset,
      backgroundColor: dataset.backgroundColor || chartColors.primary,
      borderColor: dataset.borderColor || chartColors.primary,
      borderWidth: 0,
      borderRadius: 8,
      borderSkipped: false
    }))
  };
};

export const createDoughnutChartData = (labels, data, colors) => {
  return {
    labels,
    datasets: [{
      data,
      backgroundColor: colors || [
        chartColors.primary,
        chartColors.success,
        chartColors.warning,
        chartColors.danger,
        chartColors.info
      ],
      borderWidth: 0,
      cutout: '70%'
    }]
  };
};

export const revenueChartOptions = {
  ...defaultChartOptions,
  plugins: {
    ...defaultChartOptions.plugins,
    title: {
      display: false
    }
  },
  scales: {
    ...defaultChartOptions.scales,
    y: {
      ...defaultChartOptions.scales.y,
      ticks: {
        ...defaultChartOptions.scales.y.ticks,
        callback: function(value) {
          return '$' + (value / 1000) + 'K';
        }
      }
    }
  }
};

export const performanceChartOptions = {
  ...defaultChartOptions,
  plugins: {
    ...defaultChartOptions.plugins,
    legend: {
      display: false
    }
  },
  scales: {
    ...defaultChartOptions.scales,
    y: {
      ...defaultChartOptions.scales.y,
      max: 100,
      ticks: {
        ...defaultChartOptions.scales.y.ticks,
        callback: function(value) {
          return value + '%';
        }
      }
    }
  }
};

export const doughnutChartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: 'right',
      labels: {
        color: '#D1D5DB',
        font: {
          family: 'Inter',
          size: 12
        },
        padding: 15,
        usePointStyle: true
      }
    },
    tooltip: {
      backgroundColor: 'rgba(15, 23, 42, 0.95)',
      titleColor: '#FFFFFF',
      bodyColor: '#D1D5DB',
      borderColor: 'rgba(139, 92, 246, 0.2)',
      borderWidth: 1,
      cornerRadius: 8,
      font: {
        family: 'Inter'
      }
    }
  },
  cutout: '70%'
};

export const formatChartData = (rawData, type = 'line') => {
  switch (type) {
    case 'line':
      return createLineChartData(rawData.labels, rawData.datasets);
    case 'bar':
      return createBarChartData(rawData.labels, rawData.datasets);
    case 'doughnut':
      return createDoughnutChartData(rawData.labels, rawData.data, rawData.colors);
    default:
      return rawData;
  }
};

export const generateGradient = (ctx, color1, color2) => {
  const gradient = ctx.createLinearGradient(0, 0, 0, 400);
  gradient.addColorStop(0, color1);
  gradient.addColorStop(1, color2);
  return gradient;
}; 
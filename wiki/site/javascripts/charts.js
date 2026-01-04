/**
 * COST Action CA19130 Wiki - Chart Utilities
 * Uses Chart.js for visualizations
 */

// COST Color Palette
const COST_COLORS = {
  purple: '#5B2D8A',
  purpleLight: '#7B4DAA',
  blue: '#2B5F9E',
  blueLight: '#4B7FBE',
  teal: '#00A0B0',
  orange: '#E87722',
  green: '#7AB800',
  red: '#D62728',
  gray: '#666666'
};

// Color arrays for charts
const CHART_COLORS = [
  COST_COLORS.purple,
  COST_COLORS.blue,
  COST_COLORS.teal,
  COST_COLORS.orange,
  COST_COLORS.green,
  COST_COLORS.purpleLight,
  COST_COLORS.blueLight,
  COST_COLORS.red
];

// Default chart options
const DEFAULT_OPTIONS = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: 'bottom',
      labels: {
        padding: 20,
        usePointStyle: true,
        font: { size: 11 }
      }
    },
    tooltip: {
      backgroundColor: 'rgba(0,0,0,0.8)',
      padding: 12,
      titleFont: { size: 13 },
      bodyFont: { size: 12 },
      cornerRadius: 4
    }
  }
};

/**
 * Create a bar chart
 */
function createBarChart(canvasId, labels, data, options = {}) {
  const ctx = document.getElementById(canvasId);
  if (!ctx) return null;

  return new Chart(ctx, {
    type: 'bar',
    data: {
      labels: labels,
      datasets: [{
        label: options.label || 'Value',
        data: data,
        backgroundColor: options.colors || COST_COLORS.purple,
        borderRadius: 4
      }]
    },
    options: {
      ...DEFAULT_OPTIONS,
      ...options.chartOptions,
      scales: {
        y: {
          beginAtZero: true,
          ticks: {
            callback: options.yTickCallback || ((value) => value)
          }
        }
      }
    }
  });
}

/**
 * Create a doughnut/pie chart
 */
function createDoughnutChart(canvasId, labels, data, options = {}) {
  const ctx = document.getElementById(canvasId);
  if (!ctx) return null;

  return new Chart(ctx, {
    type: options.type || 'doughnut',
    data: {
      labels: labels,
      datasets: [{
        data: data,
        backgroundColor: options.colors || CHART_COLORS,
        borderWidth: 2,
        borderColor: '#fff'
      }]
    },
    options: {
      ...DEFAULT_OPTIONS,
      cutout: options.cutout || '60%',
      plugins: {
        ...DEFAULT_OPTIONS.plugins,
        tooltip: {
          ...DEFAULT_OPTIONS.plugins.tooltip,
          callbacks: {
            label: function(context) {
              const total = context.dataset.data.reduce((a, b) => a + b, 0);
              const percentage = ((context.raw / total) * 100).toFixed(1);
              return `${context.label}: ${context.raw.toLocaleString()} (${percentage}%)`;
            }
          }
        }
      }
    }
  });
}

/**
 * Create a line chart
 */
function createLineChart(canvasId, labels, datasets, options = {}) {
  const ctx = document.getElementById(canvasId);
  if (!ctx) return null;

  const formattedDatasets = datasets.map((ds, i) => ({
    label: ds.label,
    data: ds.data,
    borderColor: ds.color || CHART_COLORS[i],
    backgroundColor: (ds.color || CHART_COLORS[i]) + '20',
    fill: ds.fill !== false,
    tension: 0.3,
    pointRadius: 4,
    pointHoverRadius: 6
  }));

  return new Chart(ctx, {
    type: 'line',
    data: {
      labels: labels,
      datasets: formattedDatasets
    },
    options: {
      ...DEFAULT_OPTIONS,
      ...options.chartOptions,
      scales: {
        y: {
          beginAtZero: true
        }
      }
    }
  });
}

/**
 * Create a horizontal bar chart
 */
function createHorizontalBarChart(canvasId, labels, data, options = {}) {
  const ctx = document.getElementById(canvasId);
  if (!ctx) return null;

  return new Chart(ctx, {
    type: 'bar',
    data: {
      labels: labels,
      datasets: [{
        label: options.label || 'Value',
        data: data,
        backgroundColor: options.colors || COST_COLORS.purple,
        borderRadius: 4
      }]
    },
    options: {
      ...DEFAULT_OPTIONS,
      indexAxis: 'y',
      scales: {
        x: {
          beginAtZero: true,
          ticks: {
            callback: options.xTickCallback || ((value) => value)
          }
        }
      }
    }
  });
}

/**
 * Create a grouped bar chart
 */
function createGroupedBarChart(canvasId, labels, datasets, options = {}) {
  const ctx = document.getElementById(canvasId);
  if (!ctx) return null;

  const formattedDatasets = datasets.map((ds, i) => ({
    label: ds.label,
    data: ds.data,
    backgroundColor: ds.color || CHART_COLORS[i],
    borderRadius: 4
  }));

  return new Chart(ctx, {
    type: 'bar',
    data: {
      labels: labels,
      datasets: formattedDatasets
    },
    options: {
      ...DEFAULT_OPTIONS,
      ...options.chartOptions,
      scales: {
        y: {
          beginAtZero: true,
          ticks: {
            callback: options.yTickCallback || ((value) => value)
          }
        }
      }
    }
  });
}

/**
 * Format currency for tooltips
 */
function formatCurrency(value) {
  return 'EUR ' + value.toLocaleString();
}

/**
 * Format large numbers
 */
function formatNumber(value) {
  if (value >= 1000000) {
    return (value / 1000000).toFixed(1) + 'M';
  } else if (value >= 1000) {
    return (value / 1000).toFixed(1) + 'K';
  }
  return value.toLocaleString();
}

/**
 * Initialize charts when DOM is ready
 */
document.addEventListener('DOMContentLoaded', function() {
  // Check if Chart.js is loaded
  if (typeof Chart === 'undefined') {
    console.warn('Chart.js not loaded');
    return;
  }

  // Set global Chart.js defaults
  Chart.defaults.font.family = "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif";
  Chart.defaults.color = '#666';
});

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    COST_COLORS,
    CHART_COLORS,
    createBarChart,
    createDoughnutChart,
    createLineChart,
    createHorizontalBarChart,
    createGroupedBarChart,
    formatCurrency,
    formatNumber
  };
}

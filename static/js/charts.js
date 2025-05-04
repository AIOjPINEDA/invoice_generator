/**
 * Invoice Generator 2025
 * Charts and data visualization using ApexCharts
 */

document.addEventListener('DOMContentLoaded', function() {
  // Initialize all charts if their containers exist
  initializeCharts();
});

/**
 * Initialize all charts if their containers exist
 */
function initializeCharts() {
  if (document.getElementById('invoiceChart')) {
    initializeInvoiceChart();
  }

  if (document.getElementById('revenueChart')) {
    initializeRevenueChart();
  }

  if (document.getElementById('clientDistributionChart')) {
    initializeClientDistributionChart();
  }
}

/**
 * Initialize the main invoice chart (monthly invoices)
 */
function initializeInvoiceChart() {
  // Get current year from URL or use current year
  const urlParams = new URLSearchParams(window.location.search);
  const year = urlParams.get('year') || new Date().getFullYear();

  // Fetch data from the server
  fetch(`/api/invoice_stats?year=${year}`)
    .then(response => response.json())
    .then(data => {
      renderInvoiceChart(data);
    })
    .catch(error => {
      console.error('Error fetching invoice stats:', error);
      // Render with sample data if fetch fails
      renderInvoiceChart(getSampleInvoiceData());
    });
}

/**
 * Render the invoice chart with the provided data
 */
function renderInvoiceChart(data) {
  const options = {
    series: [{
      name: 'Invoices',
      data: data.counts
    }],
    chart: {
      height: 300,
      type: 'bar',
      fontFamily: 'Inter, sans-serif',
      toolbar: {
        show: false
      },
      animations: {
        enabled: true,
        easing: 'easeinout',
        speed: 800,
        animateGradually: {
          enabled: true,
          delay: 150
        },
        dynamicAnimation: {
          enabled: true,
          speed: 350
        }
      }
    },
    colors: [getComputedStyle(document.documentElement).getPropertyValue('--accent-color').trim()],
    plotOptions: {
      bar: {
        borderRadius: 6,
        columnWidth: '60%',
        dataLabels: {
          position: 'top'
        }
      }
    },
    dataLabels: {
      enabled: false
    },
    stroke: {
      show: true,
      width: 2,
      colors: ['transparent']
    },
    xaxis: {
      categories: data.months,
      labels: {
        style: {
          colors: getComputedStyle(document.documentElement).getPropertyValue('--text-secondary').trim(),
          fontSize: '12px'
        }
      }
    },
    yaxis: {
      title: {
        text: 'Number of Invoices',
        style: {
          color: getComputedStyle(document.documentElement).getPropertyValue('--text-secondary').trim()
        }
      },
      labels: {
        style: {
          colors: getComputedStyle(document.documentElement).getPropertyValue('--text-secondary').trim()
        }
      }
    },
    fill: {
      opacity: 1,
      type: 'gradient',
      gradient: {
        shade: 'light',
        type: 'vertical',
        shadeIntensity: 0.2,
        gradientToColors: undefined,
        inverseColors: false,
        opacityFrom: 0.85,
        opacityTo: 0.95,
        stops: [0, 100]
      }
    },
    tooltip: {
      y: {
        formatter: function(val) {
          return val + " invoices"
        }
      },
      theme: document.body.classList.contains('dark-mode') ? 'dark' : 'light'
    },
    grid: {
      borderColor: getComputedStyle(document.documentElement).getPropertyValue('--border-color').trim(),
      strokeDashArray: 4
    },
    states: {
      hover: {
        filter: {
          type: 'darken',
          value: 0.9
        }
      }
    }
  };

  const chart = new ApexCharts(document.getElementById('invoiceChart'), options);
  chart.render();

  // Update chart theme when dark mode is toggled
  setupChartThemeToggle(chart);
}

/**
 * Initialize the revenue chart
 */
function initializeRevenueChart() {
  // Get current year from URL or use current year
  const urlParams = new URLSearchParams(window.location.search);
  const year = urlParams.get('year') || new Date().getFullYear();

  // Fetch data from the server
  fetch(`/api/revenue_stats?year=${year}`)
    .then(response => response.json())
    .then(data => {
      renderRevenueChart(data);
    })
    .catch(error => {
      console.error('Error fetching revenue stats:', error);
      // Render with sample data if fetch fails
      renderRevenueChart(getSampleRevenueData());
    });
}

/**
 * Render the revenue chart with the provided data
 */
function renderRevenueChart(data) {
  const options = {
    series: [{
      name: 'Revenue',
      data: data.amounts
    }],
    chart: {
      height: 300,
      type: 'area',
      fontFamily: 'Inter, sans-serif',
      toolbar: {
        show: false
      },
      animations: {
        enabled: true,
        easing: 'easeinout',
        speed: 800
      }
    },
    colors: [getComputedStyle(document.documentElement).getPropertyValue('--primary-color').trim()],
    dataLabels: {
      enabled: false
    },
    stroke: {
      curve: 'smooth',
      width: 3
    },
    xaxis: {
      categories: data.months,
      labels: {
        style: {
          colors: getComputedStyle(document.documentElement).getPropertyValue('--text-secondary').trim(),
          fontSize: '12px'
        }
      }
    },
    yaxis: {
      title: {
        text: 'Revenue',
        style: {
          color: getComputedStyle(document.documentElement).getPropertyValue('--text-secondary').trim()
        }
      },
      labels: {
        formatter: function(val) {
          return data.currency + val.toFixed(2);
        },
        style: {
          colors: getComputedStyle(document.documentElement).getPropertyValue('--text-secondary').trim()
        }
      }
    },
    tooltip: {
      y: {
        formatter: function(val) {
          return data.currency + val.toFixed(2)
        }
      },
      theme: document.body.classList.contains('dark-mode') ? 'dark' : 'light'
    },
    fill: {
      type: 'gradient',
      gradient: {
        shade: 'dark',
        type: 'vertical',
        shadeIntensity: 0.3,
        gradientToColors: undefined,
        inverseColors: false,
        opacityFrom: 0.7,
        opacityTo: 0.2,
        stops: [0, 100]
      }
    },
    grid: {
      borderColor: getComputedStyle(document.documentElement).getPropertyValue('--border-color').trim(),
      strokeDashArray: 4
    },
    markers: {
      size: 5,
      colors: [getComputedStyle(document.documentElement).getPropertyValue('--background-color').trim()],
      strokeColors: getComputedStyle(document.documentElement).getPropertyValue('--primary-color').trim(),
      strokeWidth: 2
    }
  };

  const chart = new ApexCharts(document.getElementById('revenueChart'), options);
  chart.render();

  // Update chart theme when dark mode is toggled
  setupChartThemeToggle(chart, {
    markers: {
      colors: [getComputedStyle(document.documentElement).getPropertyValue('--background-color').trim()]
    }
  });
}

/**
 * Initialize the client distribution chart
 */
function initializeClientDistributionChart() {
  // Get current year from URL or use current year
  const urlParams = new URLSearchParams(window.location.search);
  const year = urlParams.get('year') || new Date().getFullYear();

  // Fetch data from the server
  fetch(`/api/client_stats?year=${year}`)
    .then(response => response.json())
    .then(data => {
      renderClientDistributionChart(data);
    })
    .catch(error => {
      console.error('Error fetching client stats:', error);
      // Render with sample data if fetch fails
      renderClientDistributionChart(getSampleClientData());
    });
}

/**
 * Render the client distribution chart with the provided data
 */
function renderClientDistributionChart(data) {
  const options = {
    series: data.values,
    chart: {
      height: 300,
      type: 'donut',
      fontFamily: 'Inter, sans-serif',
      animations: {
        enabled: true,
        easing: 'easeinout',
        speed: 800,
        animateGradually: {
          enabled: true,
          delay: 150
        },
        dynamicAnimation: {
          enabled: true,
          speed: 350
        }
      }
    },
    labels: data.labels,
    colors: [
      getComputedStyle(document.documentElement).getPropertyValue('--primary-color').trim(),
      getComputedStyle(document.documentElement).getPropertyValue('--accent-color').trim(),
      getComputedStyle(document.documentElement).getPropertyValue('--success-color').trim(),
      getComputedStyle(document.documentElement).getPropertyValue('--warning-color').trim(),
      getComputedStyle(document.documentElement).getPropertyValue('--danger-color').trim()
    ],
    plotOptions: {
      pie: {
        donut: {
          size: '55%',
          labels: {
            show: true,
            name: {
              show: true,
              fontSize: '16px',
              fontWeight: 600,
              color: getComputedStyle(document.documentElement).getPropertyValue('--text-primary').trim()
            },
            value: {
              show: true,
              fontSize: '20px',
              fontWeight: 700,
              color: getComputedStyle(document.documentElement).getPropertyValue('--text-primary').trim(),
              formatter: function(val) {
                return val + '%';
              }
            },
            total: {
              show: true,
              label: 'Total',
              fontSize: '16px',
              fontWeight: 600,
              color: getComputedStyle(document.documentElement).getPropertyValue('--text-primary').trim(),
              formatter: function(w) {
                return w.globals.seriesTotals.reduce((a, b) => a + b, 0) + '%';
              }
            }
          }
        }
      }
    },
    dataLabels: {
      enabled: false
    },
    legend: {
      show: false
    },
    tooltip: {
      y: {
        formatter: function(val) {
          return val + '%';
        }
      },
      theme: document.body.classList.contains('dark-mode') ? 'dark' : 'light'
    },
    stroke: {
      width: 2,
      colors: [getComputedStyle(document.documentElement).getPropertyValue('--background-color').trim()]
    },
    states: {
      hover: {
        filter: {
          type: 'darken',
          value: 0.9
        }
      }
    }
  };

  const chart = new ApexCharts(document.getElementById('clientDistributionChart'), options);
  chart.render();

  // Update chart theme when dark mode is toggled
  setupChartThemeToggle(chart, {
    stroke: {
      colors: [getComputedStyle(document.documentElement).getPropertyValue('--background-color').trim()]
    },
    plotOptions: {
      pie: {
        donut: {
          labels: {
            name: {
              color: getComputedStyle(document.documentElement).getPropertyValue('--text-primary').trim()
            },
            value: {
              color: getComputedStyle(document.documentElement).getPropertyValue('--text-primary').trim()
            },
            total: {
              color: getComputedStyle(document.documentElement).getPropertyValue('--text-primary').trim()
            }
          }
        }
      }
    },
    legend: {
      labels: {
        colors: getComputedStyle(document.documentElement).getPropertyValue('--text-primary').trim()
      }
    }
  });
}

/**
 * Get sample invoice data for demonstration
 */
function getSampleInvoiceData() {
  return {
    months: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
    counts: [4, 6, 8, 5, 7, 9, 11, 8, 10, 12, 9, 7]
  };
}

/**
 * Get sample revenue data for demonstration
 */
function getSampleRevenueData() {
  return {
    months: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
    amounts: [1500, 2200, 1800, 2400, 2800, 3100, 2950, 3300, 3700, 3500, 4000, 4200],
    currency: '€'
  };
}

/**
 * Get sample client distribution data for demonstration
 */
function getSampleClientData() {
  return {
    labels: ['AIO', 'Ayuntamiento', 'Other Clients'],
    values: [65, 25, 10]
  };
}

/**
 * Setup theme toggle for chart
 * @param {ApexCharts} chart - The ApexCharts instance
 * @param {Object} options - Additional options for theme update
 */
function setupChartThemeToggle(chart, options = {}) {
  const themeToggle = document.getElementById('theme-toggle');
  if (themeToggle) {
    themeToggle.addEventListener('click', function() {
      setTimeout(() => {
        const defaultOptions = {
          tooltip: {
            theme: document.body.classList.contains('dark-mode') ? 'dark' : 'light'
          },
          grid: {
            borderColor: getComputedStyle(document.documentElement).getPropertyValue('--border-color').trim()
          }
        };

        // Merge default options with custom options
        const updateOptions = {...defaultOptions, ...options};
        chart.updateOptions(updateOptions);
      }, 100);
    });
  }
}

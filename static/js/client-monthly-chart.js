/**
 * Initialize the client monthly chart
 */
function initializeClientMonthlyChart() {
  // Get current year from URL or use current year
  const urlParams = new URLSearchParams(window.location.search);
  const year = urlParams.get('year') || new Date().getFullYear();

  // Fetch data from the server
  fetch(`/api/client_monthly_stats?year=${year}`)
    .then(response => response.json())
    .then(data => {
      renderClientMonthlyChart(data);
    })
    .catch(error => {
      console.error('Error fetching client monthly stats:', error);
      // Render with sample data if fetch fails
      renderClientMonthlyChart(getSampleClientMonthlyData());
    });
}

/**
 * Render the client monthly chart with the provided data
 */
function renderClientMonthlyChart(data) {
  const options = {
    series: data.series,
    chart: {
      type: 'bar',
      height: 400,
      stacked: true,
      fontFamily: 'Inter, sans-serif',
      toolbar: {
        show: true,
        tools: {
          download: true,
          selection: false,
          zoom: false,
          zoomin: false,
          zoomout: false,
          pan: false,
          reset: false
        }
      },
      animations: {
        enabled: true,
        easing: 'easeinout',
        speed: 800
      }
    },
    plotOptions: {
      bar: {
        horizontal: false,
        columnWidth: '70%',
        borderRadius: 4,
        dataLabels: {
          total: {
            enabled: true,
            style: {
              fontSize: '13px',
              fontWeight: 900
            }
          }
        }
      },
    },
    dataLabels: {
      enabled: false
    },
    stroke: {
      width: 1,
      colors: ['#fff']
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
    tooltip: {
      y: {
        formatter: function(val) {
          return val + " invoices"
        }
      },
      theme: document.body.classList.contains('dark-mode') ? 'dark' : 'light'
    },
    fill: {
      opacity: 1
    },
    legend: {
      position: 'bottom',
      horizontalAlign: 'center',
      fontSize: '14px',
      fontWeight: 500,
      markers: {
        width: 12,
        height: 12,
        strokeWidth: 0,
        radius: 12
      },
      itemMargin: {
        horizontal: 10,
        vertical: 5
      }
    },
    colors: [
      getComputedStyle(document.documentElement).getPropertyValue('--primary-color').trim(),
      getComputedStyle(document.documentElement).getPropertyValue('--accent-color').trim(),
      getComputedStyle(document.documentElement).getPropertyValue('--success-color').trim(),
      getComputedStyle(document.documentElement).getPropertyValue('--warning-color').trim(),
      getComputedStyle(document.documentElement).getPropertyValue('--danger-color').trim(),
      getComputedStyle(document.documentElement).getPropertyValue('--info-color').trim()
    ],
    grid: {
      borderColor: getComputedStyle(document.documentElement).getPropertyValue('--border-color').trim(),
      strokeDashArray: 4
    }
  };

  const chart = new ApexCharts(document.getElementById('clientMonthlyChart'), options);
  chart.render();

  // Update chart theme when dark mode is toggled
  if (typeof setupChartThemeToggle === 'function') {
    setupChartThemeToggle(chart);
  } else {
    console.warn('setupChartThemeToggle function not found. Make sure charts.js is loaded before client-monthly-chart.js');
    // Fallback implementation
    const themeToggle = document.getElementById('theme-toggle');
    if (themeToggle) {
      themeToggle.addEventListener('click', function() {
        setTimeout(() => {
          chart.updateOptions({
            tooltip: {
              theme: document.body.classList.contains('dark-mode') ? 'dark' : 'light'
            },
            grid: {
              borderColor: getComputedStyle(document.documentElement).getPropertyValue('--border-color').trim()
            }
          });
        }, 100);
      });
    }
  }
}

/**
 * Get sample client monthly data for demonstration
 */
function getSampleClientMonthlyData() {
  return {
    months: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
    series: [
      {
        name: 'AIO',
        data: [2, 3, 2, 1, 2, 3, 2, 3, 2, 3, 2, 3]
      },
      {
        name: 'Ayuntamiento',
        data: [1, 1, 2, 2, 1, 2, 3, 1, 2, 2, 1, 1]
      },
      {
        name: 'Others',
        data: [1, 2, 1, 0, 1, 1, 0, 1, 2, 1, 1, 0]
      }
    ]
  };
}

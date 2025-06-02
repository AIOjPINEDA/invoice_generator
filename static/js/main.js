/**
 * Invoice Generator 2025
 * Main JavaScript file for enhanced interactions
 */

document.addEventListener('DOMContentLoaded', function() {
  console.log('Invoice Generator 2025 initialized');

  // Initialize components
  initializeSelectionButtons();
  initializeDocumentTypeSwitcher(); // Added this call

  // Add entrance animations to bento items
  animateBentoItems();

  // Initialize custom cursor
  initializeCustomCursor();

  // Add button hover effects
  addButtonEffects();

  // Initialize dark mode toggle
  initializeDarkModeToggle();

  // Initialize sortable tables
  initializeSortableTables();
});

/**
 * Initialize document type switcher
 */
function initializeDocumentTypeSwitcher() {
    const docTypeRadios = document.querySelectorAll('input[name="document_type"]');
    const form = document.getElementById('document-form');
    const formTitle = document.getElementById('form-title');
    const generateButton = document.getElementById('generate-button');
    const estimateFields = document.querySelectorAll('.estimate-fields');
    const invoiceTaxOptions = document.getElementById('tax-options-invoice');
    const issueDateLabel = document.querySelector('label[for="issue_date"]');
    const recentDocumentsTitle = document.getElementById('recent-documents-title');
    // const documentsTable = document.getElementById('documents-table'); // To update table headers if needed
    // const documentsTableBody = document.getElementById('documents-table-body'); // To update table content

    docTypeRadios.forEach(radio => {
        radio.addEventListener('change', function() {
            const selectedType = this.value;
            
            // Update form action
            form.action = (selectedType === 'estimate') ? '/generate_estimate' : '/generate_invoice';
            
            // Update titles and button text
            if (selectedType === 'estimate') {
                formTitle.textContent = 'Generate New Estimate';
                generateButton.textContent = 'Generate Estimate';
                issueDateLabel.textContent = 'Estimate Date';
                recentDocumentsTitle.textContent = 'Recent Estimates'; // Or "Recent Documents"
                // Potentially fetch and display recent estimates here
            } else {
                formTitle.textContent = 'Generate New Invoice';
                generateButton.textContent = 'Generate Invoice';
                issueDateLabel.textContent = 'Invoice Date';
                recentDocumentsTitle.textContent = 'Recent Invoices'; // Or "Recent Documents"
                // Potentially fetch and display recent invoices here
            }

            // Toggle visibility of estimate-specific fields and invoice tax options
            estimateFields.forEach(field => {
                field.style.display = (selectedType === 'estimate') ? 'block' : 'none';
            });
            if (invoiceTaxOptions) {
                invoiceTaxOptions.style.display = (selectedType === 'invoice') ? 'block' : 'none';
            }

            // Update selected label style
            document.getElementById('doc-type-invoice-label').classList.toggle('selected', selectedType === 'invoice');
            document.getElementById('doc-type-estimate-label').classList.toggle('selected', selectedType === 'estimate');
        });
    });

    // Initial setup based on default checked (invoice)
    if (invoiceTaxOptions) {
        invoiceTaxOptions.style.display = 'block'; 
    }
    estimateFields.forEach(field => {
        field.style.display = 'none';
    });
    document.getElementById('doc-type-invoice-label').classList.add('selected');
}


/**
 * Initialize selection buttons for clients and services
 */
function initializeSelectionButtons() {
  // Client selection
  const clientButtons = document.querySelectorAll('#client-selection .selection-button');
  clientButtons.forEach(button => {
    button.addEventListener('click', function() {
      const radioInput = this.querySelector('input[type="radio"]');
      const clientId = radioInput.value;
      radioInput.checked = true;
      selectClient(this, clientId);

      // Add ripple effect
      createRippleEffect(this, event);
    });
  });

  // Service selection
  const serviceButtons = document.querySelectorAll('#service-selection .selection-button');
  serviceButtons.forEach(button => {
    button.addEventListener('click', function() {
      const radioInput = this.querySelector('input[type="radio"]');
      const serviceId = radioInput.value;
      radioInput.checked = true;
      selectService(this, serviceId);

      // Add ripple effect
      createRippleEffect(this, event);
    });
  });

  // Submit button ripple effect
  const submitButton = document.querySelector('.btn-primary');
  if (submitButton) {
    submitButton.addEventListener('click', function(event) {
      createRippleEffect(this, event);
    });
  }
}

/**
 * Create ripple effect on button click
 */
function createRippleEffect(button, event) {
  const ripple = document.createElement('span');
  const rect = button.getBoundingClientRect();

  const size = Math.max(rect.width, rect.height);
  const x = event.clientX - rect.left - size / 2;
  const y = event.clientY - rect.top - size / 2;

  ripple.style.width = ripple.style.height = `${size}px`;
  ripple.style.left = `${x}px`;
  ripple.style.top = `${y}px`;
  ripple.classList.add('ripple');

  button.appendChild(ripple);

  setTimeout(() => {
    ripple.remove();
  }, 600);
}

/**
 * Initialize cursor - Classic style
 */
function initializeCustomCursor() {
  // No custom cursor implementation - using system default cursor
  console.log('Using classic system cursor');

  // Add hover effects for interactive elements without custom cursor
  const interactiveElements = document.querySelectorAll('button, .btn, .selection-button, a, input, .action-btn');
  interactiveElements.forEach(el => {
    el.style.cursor = 'pointer';
  });
}

/**
 * Add hover effects to buttons
 */
function addButtonEffects() {
  const buttons = document.querySelectorAll('.btn, .action-btn');

  buttons.forEach(button => {
    button.addEventListener('mouseenter', function() {
      this.style.transform = 'translateY(-2px)';
    });

    button.addEventListener('mouseleave', function() {
      this.style.transform = 'translateY(0)';
    });

    button.addEventListener('mousedown', function() {
      this.style.transform = 'translateY(1px)';
    });

    button.addEventListener('mouseup', function() {
      this.style.transform = 'translateY(-2px)';
    });
  });
}

/**
 * Select a client
 */
function selectClient(buttonElement, clientId) {
  // Remove selected class from all client buttons
  const clientButtons = document.querySelectorAll('#client-selection .selection-button');
  clientButtons.forEach(button => button.classList.remove('selected'));

  // Add selected class to the clicked button with animation
  setTimeout(() => {
    buttonElement.classList.add('selected');
  }, 50);

  // Fetch client details
  fetchClientDetails(clientId);
}

/**
 * Select a service
 */
function selectService(buttonElement, serviceId) {
  // Remove selected class from all service buttons
  const serviceButtons = document.querySelectorAll('#service-selection .selection-button');
  serviceButtons.forEach(button => button.classList.remove('selected'));

  // Add selected class to the clicked button with animation
  setTimeout(() => {
    buttonElement.classList.add('selected');
  }, 50);

  // Fetch service details
  fetchServiceDetails(serviceId);
}

/**
 * Fetch client details
 */
function fetchClientDetails(clientId) {
  if (!clientId) {
    const detailsDiv = document.getElementById('client-details');
    if (detailsDiv) { // Check if element exists
        detailsDiv.style.display = 'none';
    }
    return;
  }

  fetch(`/get_client/${clientId}`)
    .then(response => response.json())
    .then(data => {
      const detailsDiv = document.getElementById('client-details');
      const contentDiv = document.getElementById('client-details-content');

      // Update content
      contentDiv.innerHTML = `
        <p><strong>Name:</strong> ${data.name}</p>
        <p><strong>Tax ID:</strong> ${data.tax_id}</p>
        <p><strong>Address:</strong> ${data.address}</p>
        <p><strong>Country:</strong> ${data.country}</p>
        <p><strong>Currency:</strong> ${data.currency_symbol}</p>
      `;

      // Show the details panel
      detailsDiv.style.display = 'block';
    })
    .catch(error => console.error('Error fetching client details:', error));
}

/**
 * Fetch service details
 */
function fetchServiceDetails(serviceId) {
  if (!serviceId) {
    const detailsDiv = document.getElementById('service-details');
    if (detailsDiv) { // Check if element exists
        detailsDiv.style.display = 'none';
    }
    return;
  }

  fetch(`/get_service/${serviceId}`)
    .then(response => response.json())
    .then(data => {
      const detailsDiv = document.getElementById('service-details');
      const contentDiv = document.getElementById('service-details-content');

      // Update content
      contentDiv.innerHTML = `
        <p><strong>Description:</strong> ${data.description}</p>
        <p><strong>Unit price:</strong> ${data.unit_price} / ${data.unit_type}</p>
      `;

      // Show the details panel
      detailsDiv.style.display = 'block';
    })
    .catch(error => console.error('Error fetching service details:', error));
}

/**
 * Animate bento items on page load
 */
function animateBentoItems() {
  const bentoItems = document.querySelectorAll('.bento-item');
  bentoItems.forEach((item, index) => {
    setTimeout(() => {
      item.style.opacity = '1';
      item.style.transform = 'translateY(0)';
    }, 150 * index);
  });

  // For backwards compatibility with old design
  const cards = document.querySelectorAll('.card');
  cards.forEach((card, index) => {
    setTimeout(() => {
      card.style.opacity = '1';
      card.style.transform = 'translateY(0)';
    }, 150 * index);
  });
}

/**
 * Confirm invoice deletion
 */
function confirmDelete(docType, docNumber) { // Added docType parameter
  if (confirm('Are you sure you want to delete ' + docType + ' ' + docNumber + '? This action cannot be undone.')) {
    window.location.href = '/delete_' + docType + '/' + docNumber;
  }
}

/**
 * Initialize dark mode toggle
 */
function initializeDarkModeToggle() {
  const themeToggle = document.getElementById('theme-toggle');
  const icon = themeToggle.querySelector('i');

  // Check for saved theme preference
  const savedTheme = localStorage.getItem('theme');
  if (savedTheme === 'dark') {
    document.body.classList.add('dark-mode');
    icon.classList.remove('fa-moon');
    icon.classList.add('fa-sun');
  }

  // Toggle theme on click
  themeToggle.addEventListener('click', function() {
    document.body.classList.toggle('dark-mode');

    // Update icon
    if (document.body.classList.contains('dark-mode')) {
      icon.classList.remove('fa-moon');
      icon.classList.add('fa-sun');
      localStorage.setItem('theme', 'dark');
    } else {
      icon.classList.remove('fa-sun');
      icon.classList.add('fa-moon');
      localStorage.setItem('theme', 'light');
    }

    // Add rotation animation
    themeToggle.classList.add('rotate');
    setTimeout(() => {
      themeToggle.classList.remove('rotate');
    }, 500);
  });
}

// Add CSS for ripple effect and animations
document.head.insertAdjacentHTML('beforeend', `
  <style>
    /* Ripple Effect */
    .btn, .selection-button, .action-btn {
      position: relative;
      overflow: hidden;
      cursor: pointer; /* Ensure pointer cursor on all interactive elements */
    }

    .ripple {
      position: absolute;
      border-radius: 50%;
      background-color: rgba(255, 255, 255, 0.3);
      transform: scale(0);
      animation: ripple 0.6s ease-out;
      pointer-events: none;
    }

    @keyframes ripple {
      to {
        transform: scale(3);
        opacity: 0;
      }
    }

    /* Theme Toggle Animation */
    .rotate {
      animation: rotate 0.5s ease-in-out;
    }

    @keyframes rotate {
      0% {
        transform: rotate(0);
      }
      100% {
        transform: rotate(360deg);
      }
    }

    /* Ensure classic cursor styles */
    a, button, .btn, .selection-button, .action-btn, input[type="checkbox"],
    .theme-toggle, input[type="number"], select {
      cursor: pointer !important;
    }

    body, html {
      cursor: default !important;
    }

    input[type="text"], textarea {
      cursor: text !important;
    }

    /* Details panel styles */
    .details-panel {
      background-color: rgba(var(--accent-color-rgb), 0.05);
      border-radius: var(--border-radius);
      padding: 1rem;
      margin-bottom: 1rem;
      border-left: 3px solid var(--accent-color);
      display: none;
    }

    .details-panel h3 {
      margin-top: 0;
      margin-bottom: 0.75rem;
      font-size: 1.1rem;
      color: var(--text-primary);
    }

    .details-panel p {
      margin: 0.5rem 0;
      font-size: 0.95rem;
    }

    /* Sortable table styles */
    .sortable {
      cursor: pointer;
      position: relative;
      user-select: none;
    }

    .sortable i {
      margin-left: 5px;
      font-size: 0.8em;
      opacity: 0.5;
      transition: all 0.2s ease;
    }

    .sortable.asc i {
      opacity: 1;
      transform: rotate(180deg);
    }

    .sortable.desc i {
      opacity: 1;
      transform: rotate(0deg);
    }

    .sortable:hover i {
      opacity: 0.8;
    }
  </style>
`);

/**
 * Initialize sortable tables
 */
function initializeSortableTables() {
  const tables = document.querySelectorAll('.sortable-table');

  tables.forEach(table => {
    const headers = table.querySelectorAll('th.sortable');

    headers.forEach(header => {
      header.addEventListener('click', function() {
        const sortBy = this.getAttribute('data-sort');
        const isAsc = !this.classList.contains('asc');

        // Reset all headers
        headers.forEach(h => {
          h.classList.remove('asc', 'desc');
        });

        // Set current header sort direction
        this.classList.add(isAsc ? 'asc' : 'desc');

        // Sort the table
        sortTable(table, sortBy, isAsc);
      });
    });

    // Sort by date by default (descending - newest first)
    const dateHeader = table.querySelector('th[data-sort="date"]');
    if (dateHeader) {
      dateHeader.classList.add('desc');
      sortTable(table, 'date', false);
    }
  });
}

/**
 * Sort table by column
 */
function sortTable(table, sortBy, ascending) {
  const tbody = table.querySelector('tbody');
  const rows = Array.from(tbody.querySelectorAll('tr'));

  // Sort rows
  rows.sort((a, b) => {
    let aValue, bValue;

    // Special handling for date column
    if (sortBy === 'date') {
      // Use data-date attribute for sorting (YYYYMMDD format)
      aValue = a.querySelector(`td[data-value][data-date]`).getAttribute('data-date');
      bValue = b.querySelector(`td[data-value][data-date]`).getAttribute('data-date');
    } else {
      // For other columns, use data-value attribute
      aValue = a.querySelector(`td[data-value]:nth-child(${getColumnIndex(table, sortBy) + 1})`).getAttribute('data-value');
      bValue = b.querySelector(`td[data-value]:nth-child(${getColumnIndex(table, sortBy) + 1})`).getAttribute('data-value');

      // Convert to number if possible
      if (!isNaN(aValue) && !isNaN(bValue)) {
        aValue = parseFloat(aValue);
        bValue = parseFloat(bValue);
      }
    }

    // Compare values
    if (aValue < bValue) return ascending ? -1 : 1;
    if (aValue > bValue) return ascending ? 1 : -1;
    return 0;
  });

  // Reorder rows in the DOM
  rows.forEach(row => {
    tbody.appendChild(row);
  });
}

/**
 * Get column index by data-sort attribute
 */
function getColumnIndex(table, sortBy) {
  const headers = Array.from(table.querySelectorAll('th'));
  return headers.findIndex(header => header.getAttribute('data-sort') === sortBy);
}

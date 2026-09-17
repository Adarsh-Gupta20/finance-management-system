/**
 * Main JavaScript file for Personal Finance Manager
 */

document.addEventListener('DOMContentLoaded', function() {
    // Auto-close alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            const closeButton = alert.querySelector('.btn-close');
            if (closeButton) {
                closeButton.click();
            }
        }, 5000);
    });
    
    // Format currency values
    const formatCurrency = (amount, currency) => {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: currency || 'USD',
            minimumFractionDigits: 2
        }).format(amount);
    };
    
    // Dynamic year for copyright in footer
    const currentYearElement = document.getElementById('current-year');
    if (currentYearElement) {
        currentYearElement.textContent = new Date().getFullYear();
    }
    
    // Make table rows clickable if they have a data-href attribute
    const clickableRows = document.querySelectorAll('tr[data-href]');
    clickableRows.forEach(row => {
        row.addEventListener('click', () => {
            window.location.href = row.dataset.href;
        });
        row.style.cursor = 'pointer';
    });
    
    // Confirm delete actions
    const confirmDeleteForms = document.querySelectorAll('.confirm-delete');
    confirmDeleteForms.forEach(form => {
        form.addEventListener('submit', (event) => {
            if (!confirm('Are you sure you want to delete this item?')) {
                event.preventDefault();
            }
        });
    });
}); 
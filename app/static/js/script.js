// Charity Chain JavaScript

// Enable tooltips
document.addEventListener('DOMContentLoaded', function() {
    // Initialize Bootstrap tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Add any additional functionality here
});

// Format currency amounts
function formatCurrency(amount) {
    return parseFloat(amount).toFixed(2) + ' SIM';
}

// Donation form validation
function validateDonationForm() {
    const amountInput = document.getElementById('amount');
    if (!amountInput) return true; // Form doesn't exist
    
    const amount = parseFloat(amountInput.value);
    const max = parseFloat(amountInput.getAttribute('max'));
    
    if (isNaN(amount) || amount <= 0) {
        alert('Please enter a valid donation amount greater than zero.');
        return false;
    }
    
    if (amount > max) {
        alert('You cannot donate more than your current balance.');
        return false;
    }
    
    return true;
} 
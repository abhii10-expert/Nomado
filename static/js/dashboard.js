// Payment Dashboard JavaScript Functions

// Show add method modal
function showAddMethodModal() {
    document.getElementById('addMethodModal').style.display = 'block';
}

// Hide add method modal
function hideAddMethodModal() {
    document.getElementById('addMethodModal').style.display = 'none';
    document.getElementById('addMethodForm').reset();
    document.getElementById('dynamicFields').innerHTML = '';
}

// Generate month options
function generateMonthOptions() {
    let options = '<option value="">MM</option>';
    for (let i = 1; i <= 12; i++) {
        const month = i.toString().padStart(2, '0');
        options += `<option value="${month}">${month}</option>`;
    }
    return options;
}

// Generate year options
function generateYearOptions() {
    let options = '<option value="">YYYY</option>';
    const currentYear = new Date().getFullYear();
    for (let i = 0; i < 20; i++) {
        const year = currentYear + i;
        options += `<option value="${year}">${year}</option>`;
    }
    return options;
}

// Event listeners for payment method actions
document.addEventListener('DOMContentLoaded', function() {
    // Handle make primary buttons
    const makePrimaryButtons = document.querySelectorAll('.make-primary-btn');
    makePrimaryButtons.forEach(button => {
        button.addEventListener('click', function() {
            const methodId = this.getAttribute('data-method-id');
            makePrimary(methodId);
        });
    });

    // Handle delete method buttons
    const deleteButtons = document.querySelectorAll('.delete-method-btn');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function() {
            const methodId = this.getAttribute('data-method-id');
            deleteMethod(methodId);
        });
    });

    // Handle payment type selection
    const methodTypeSelect = document.getElementById('methodType');
    if (methodTypeSelect) {
        methodTypeSelect.addEventListener('change', function() {
            const type = this.value;
            const dynamicFields = document.getElementById('dynamicFields');
            dynamicFields.innerHTML = '';

            if (type === 'CREDIT_CARD' || type === 'DEBIT_CARD') {
                dynamicFields.innerHTML = `
                    <div style="margin-bottom: 1rem;">
                        <label>Card Number (Last 4 digits)</label>
                        <input type="text" name="card_number" class="form-control" placeholder="1234" maxlength="4" required>
                    </div>
                    <div style="margin-bottom: 1rem;">
                        <label>Cardholder Name</label>
                        <input type="text" name="card_name" class="form-control" placeholder="Name on card" required>
                    </div>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-bottom: 1rem;">
                        <div>
                            <label>Expiry Month</label>
                            <select name="expiry_month" class="form-control" required>
                                ${generateMonthOptions()}
                            </select>
                        </div>
                        <div>
                            <label>Expiry Year</label>
                            <select name="expiry_year" class="form-control" required>
                                ${generateYearOptions()}
                            </select>
                        </div>
                    </div>
                `;
            } else if (type === 'UPI') {
                dynamicFields.innerHTML = `
                    <div style="margin-bottom: 1rem;">
                        <label>UPI ID</label>
                        <input type="text" name="upi_id" class="form-control" placeholder="yourname@upi" required>
                    </div>
                `;
            } else if (type === 'NET_BANKING') {
                dynamicFields.innerHTML = `
                    <div style="margin-bottom: 1rem;">
                        <label>Bank Name</label>
                        <select name="bank_name" class="form-control" required>
                            <option value="">Select your bank</option>
                            <option value="SBI">State Bank of India</option>
                            <option value="HDFC">HDFC Bank</option>
                            <option value="ICICI">ICICI Bank</option>
                            <option value="AXIS">Axis Bank</option>
                            <option value="KOTAK">Kotak Mahindra Bank</option>
                            <option value="PNB">Punjab National Bank</option>
                        </select>
                    </div>
                `;
            } else if (type === 'WALLET') {
                dynamicFields.innerHTML = `
                    <div style="margin-bottom: 1rem;">
                        <label>Wallet Provider</label>
                        <select name="wallet_provider" class="form-control" required>
                            <option value="">Select wallet</option>
                            <option value="PAYTM">Paytm</option>
                            <option value="PHONEPE">PhonePe</option>
                            <option value="GPAY">Google Pay</option>
                            <option value="AMAZONPAY">Amazon Pay</option>
                        </select>
                    </div>
                `;
            }
        });
    }

    // Handle form submission
    const addMethodForm = document.getElementById('addMethodForm');
    if (addMethodForm) {
        addMethodForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            const data = {
                method: document.getElementById('methodType').value,
                is_default: document.getElementById('makeDefault').checked
            };

            // Add type-specific fields
            for (let pair of formData.entries()) {
                data[pair[0]] = pair[1];
            }

            fetch('/payments/save-method/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify(data)
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    hideAddMethodModal();
                    location.reload();
                } else {
                    alert('Error: ' + data.message);
                }
            })
            .catch(error => {
                alert('Error adding payment method');
            });
        });
    }
});

// Make payment method primary
function makePrimary(methodId) {
    fetch('/payments/make-primary/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({method_id: methodId})
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            location.reload();
        } else {
            alert('Error: ' + data.message);
        }
    });
}

// Delete payment method
function deleteMethod(methodId) {
    if (confirm('Are you sure you want to remove this payment method?')) {
        fetch('/payments/delete-method/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({method_id: methodId})
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                location.reload();
            } else {
                alert('Error: ' + data.message);
            }
        });
    }
}

// Utility function to get CSRF token
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Close modal when clicking outside
window.onclick = function(event) {
    const modal = document.getElementById('addMethodModal');
    if (event.target === modal) {
        hideAddMethodModal();
    }
}
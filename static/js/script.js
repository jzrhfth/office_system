let rowCount = 0;
let inventoryItems = [];

// Fetch inventory items for dropdowns
async function fetchInventoryItems() {
    try {
        const response = await fetch('/api/inventory_items');
        if (response.ok) {
            inventoryItems = await response.json();
        }
    } catch (error) {
        console.error('Failed to fetch inventory items:', error);
    }
}

// Initialize with 5 rows
async function initializeTable() {
    await fetchInventoryItems(); // Load inventory data first
    const tableBody = document.getElementById('tableBody');
    if (tableBody) tableBody.innerHTML = '';
    rowCount = 0;
    for (let i = 0; i < 5; i++) {
        addRow();
    }
    // Set today's date
    const formDateEl = document.getElementById('formDate');
    if (formDateEl) formDateEl.valueAsDate = new Date();
    const mrsEl = document.getElementById('mrsNo');
    // Only generate if the value is the default placeholder or empty
    if (mrsEl && (mrsEl.value === 'MRS-2026-000' || mrsEl.value === '')) {
        mrsEl.value = generateMRSNumber();
    }
}

function generateMRSNumber() {
    const year = new Date().getFullYear();
    const storageKey = 'mrs_sequence_' + year;
    
    let sequence = localStorage.getItem(storageKey);
    if (!sequence) {
        sequence = 0;
    }
    
    sequence = parseInt(sequence) + 1;
    localStorage.setItem(storageKey, sequence);
    
    return `MRS-${year}-${String(sequence).padStart(3, '0')}`;
}

function addRow() {
    rowCount++;
    const tableBody = document.getElementById('tableBody');
    if (!tableBody) return;

    // Build Inventory Dropdown Options with Categories
    let itemOptions = '<option value="" disabled selected>Select Item</option>';

    inventoryItems.forEach(item => {
        // Store unit in data attribute for auto-fill
        itemOptions += `<option value="${item.item_name}" data-unit="${item.unit || ''}">${item.item_name}</option>`;
    });

    const newRow = document.createElement('tr');
    newRow.className = 'animate-row';
    newRow.innerHTML = `
        <td>${rowCount}</td>
        <td>
            <select name="description[]" class="item-desc empty-select" onchange="autoSelectUnit(this)">
                ${itemOptions}
            </select>
        </td>
        <td><input type="number" name="quantity[]" class="item-qty" min="0" placeholder=""></td>
        <td>
            <select name="unit[]" class="item-unit">
                <option value=""></option>
                <option value="Pcs">pcs</option>
                <option value="Box">box</option>
                <option value="Ream">ream</option>
                <option value="Pack">pack</option>
                <option value="Set">set</option>
                <option value="Roll">roll</option>
                <option value="Bundle">bundle</option>
                <option value="Unit">unit</option>
            </select>
        </td>
        <td><input type="text" name="purpose[]" class="item-purpose" placeholder=""></td>
        <td style="text-align: center; vertical-align: middle;">
            <button type="button" class="delete-btn">✕</button>
        </td>
    `;
    tableBody.appendChild(newRow);
    // Attach delete handler
    const delBtn = newRow.querySelector('.delete-btn');
    if (delBtn) delBtn.addEventListener('click', () => deleteRow(delBtn));
    updateRowNumbers();
}

function removeLastRow() {
    const tableBody = document.getElementById('tableBody');
    if (!tableBody) return;
    if (tableBody.rows.length > 0) {
        tableBody.deleteRow(tableBody.rows.length - 1);
        rowCount--;
        updateRowNumbers();
    }
}

function deleteRow(btn) {
    const row = btn.closest('tr');
    if (row) {
        row.parentNode.removeChild(row);
        updateRowNumbers();
    }
}

function updateRowNumbers() {
    const tableBody = document.getElementById('tableBody');
    if (!tableBody) return;
    const rows = tableBody.getElementsByTagName('tr');
    for (let i = 0; i < rows.length; i++) {
        if (rows[i].cells[0]) rows[i].cells[0].textContent = i + 1;
    }
    rowCount = rows.length;
}

function clearForm() {
    if (!confirm('Are you sure you want to clear all form data?')) return;
    // Clear form fields
    const dept = document.getElementById('department'); if (dept) dept.value = '';
    const mrs = document.getElementById('mrsNo'); if (mrs) mrs.value = generateMRSNumber();
    
    // Clear requester name
    const reqName = document.getElementById('reqName'); if (reqName) reqName.value = '';
    
    // Clear and reinitialize table
    const tableBody = document.getElementById('tableBody');
    if (tableBody) tableBody.innerHTML = '';
    rowCount = 0;
    for (let i = 0; i < 5; i++) {
        addRow();
    }
    
    // Reset date to today
    const formDateEl = document.getElementById('formDate');
    if (formDateEl) formDateEl.valueAsDate = new Date();
}

function submitAndPrint() {
    window.print();

    if (confirm("Do you want to save this request to the admin?")) {
        // Gather Form Data
        const formData = { 
            date: document.getElementById('formDate').value,
            department: document.getElementById('department').value,
            mrsNo: document.getElementById('mrsNo').value,
            requester: {
                name: document.getElementById('reqName').value,
                position: document.getElementById('reqPosition').value,
                date: document.getElementById('reqDate').value
            },
            approver: {
                name: document.getElementById('appName').value,
                position: document.getElementById('appPosition').value,
                date: document.getElementById('appDate').value
            },
            items: []
        };

        // Gather Table Items
        const tableBody = document.getElementById('tableBody');
        const rows = tableBody.getElementsByTagName('tr');
        
        for (let i = 0; i < rows.length; i++) {
            const cells = rows[i].getElementsByTagName('td');
            if (cells.length >= 5) {
                // Helper to get value from input/select inside a cell
                const getVal = (cell) => {
                    const input = cell.querySelector('input, select, textarea');
                    return input ? input.value : cell.innerText;
                };

                const description = getVal(cells[1]);
                // Only add item if description is not empty
                if (description && description.trim() !== "") {
                    formData.items.push({
                        description: description,
                        quantity: getVal(cells[2]),
                        unit: getVal(cells[3]),
                        purpose: getVal(cells[4])
                    });
                }
            }
        }

        // Submit to Backend
        fetch('/submit_request', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(formData)
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                window.location.reload();
            } else {
                alert('Error submitting request: ' + data.message);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred while submitting the request.');
        });
    }
}

// Auto-select unit based on inventory item selection
function autoSelectUnit(selectElement) {
    // Toggle empty class for print styling
    if (selectElement.value === "") {
        selectElement.classList.add('empty-select');
    } else {
        selectElement.classList.remove('empty-select');
    }

    const selectedOption = selectElement.options[selectElement.selectedIndex];
    const unit = selectedOption.getAttribute('data-unit');
    
    if (unit) {
        const row = selectElement.closest('tr');
        const unitSelect = row.querySelector('.item-unit');
        if (unitSelect) {
            unitSelect.value = unit;
        }
    }
}

// Expose functions to global scope so inline onclicks work
window.addRow = addRow;
window.removeLastRow = removeLastRow;
window.clearForm = clearForm;
window.deleteRow = deleteRow;
window.submitAndPrint = submitAndPrint;
window.autoSelectUnit = autoSelectUnit;

// Initialize once DOM is ready
if (document.readyState === 'loading') {
    window.addEventListener('DOMContentLoaded', initializeTable);
} else {
    initializeTable();
}

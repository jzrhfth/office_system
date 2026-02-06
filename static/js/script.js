let rowCount = 0;

// Initialize with 5 rows
function initializeTable() {
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
    const newRow = document.createElement('tr');
    newRow.className = 'animate-row';
    newRow.innerHTML = `
        <td>${rowCount}</td>
        <td><input type="text" name="description[]" class="item-desc" placeholder=""></td>
        <td><input type="number" name="quantity[]" class="item-qty" min="0" placeholder=""></td>
        <td>
            <select name="unit[]">
                <option value=""></option>
                <option value="pcs">pcs</option>
                <option value="box">box</option>
                <option value="pack">pack</option>
                <option value="ream">ream</option>
                <option value="set">set</option>
                <option value="unit">unit</option>
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

// Expose functions to global scope so inline onclicks work
window.addRow = addRow;
window.removeLastRow = removeLastRow;
window.clearForm = clearForm;
window.deleteRow = deleteRow;

// Initialize once DOM is ready
if (document.readyState === 'loading') {
    window.addEventListener('DOMContentLoaded', initializeTable);
} else {
    initializeTable();
}

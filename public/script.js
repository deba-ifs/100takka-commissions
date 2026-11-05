let commissionData = [];

// UI Tab Switching
function switchTab(tabId) {
    document.getElementById('dashboard').style.display = tabId === 'dashboard' ? 'block' : 'none';
    document.getElementById('upload').style.display = tabId === 'upload' ? 'block' : 'none';
    if(tabId === 'dashboard') fetchCommissions();
}

// Fetch Data from Backend
async function fetchCommissions() {
    try {
        const response = await fetch('/api/commissions');
        const result = await response.json();
        if (result.status === 'success') {
            commissionData = result.data;
            renderTable(commissionData);
        }
    } catch (error) {
        console.error("Failed to fetch commissions:", error);
    }
}

// Render Table Data
function renderTable(data) {
    const tbody = document.getElementById('tableBody');
    tbody.innerHTML = '';
    
    data.forEach(item => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td class="p-4">${item.amc_name}</td>
            <td class="p-4">
                <span class="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded">${item.scheme_category}</span>
            </td>
            <td class="p-4 font-medium">${item.scheme_name}</td>
            <td class="p-4 text-green-600 font-bold">${item.commission_rate}%</td>
        `;
        tbody.appendChild(row);
    });
}

// Client-side filtering
function filterTable() {
    const searchTerm = document.getElementById('searchInput').value.toLowerCase();
    const filtered = commissionData.filter(item => 
        item.amc_name.toLowerCase().includes(searchTerm) || 
        item.scheme_name.toLowerCase().includes(searchTerm) ||
        item.scheme_category.toLowerCase().includes(searchTerm)
    );
    renderTable(filtered);
}

// Handle File Upload
document.getElementById('uploadForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const fileInput = document.getElementById('pdfFile');
    const submitBtn = document.getElementById('submitBtn');
    const statusDiv = document.getElementById('uploadStatus');
    
    if (fileInput.files.length === 0) return;

    const formData = new FormData();
    formData.append('file', fileInput.files[0]);

    submitBtn.disabled = true;
    submitBtn.innerText = 'Processing via AI...';
    statusDiv.style.display = 'none';

    try {
        const response = await fetch('/api/upload', {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        statusDiv.style.display = 'block';
        if (response.ok) {
            statusDiv.className = "mt-4 text-sm font-semibold text-green-600";
            statusDiv.innerText = result.message;
            fileInput.value = ''; // Reset input
            fetchCommissions();   // Update state
        } else {
            throw new Error(result.detail || 'Upload failed');
        }
    } catch (error) {
        statusDiv.style.display = 'block';
        statusDiv.className = "mt-4 text-sm font-semibold text-red-600";
        statusDiv.innerText = error.message;
    } finally {
        submitBtn.disabled = false;
        submitBtn.innerText = 'Upload & Process Data';
    }
});

// Initial load
fetchCommissions();
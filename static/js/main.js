// Sidebar Toggle
function toggleSidebar() {
  document.getElementById('sidebar').classList.toggle('open');
}

// Close sidebar on outside click (mobile)
document.addEventListener('click', function(e) {
  const sidebar = document.getElementById('sidebar');
  const toggle  = document.querySelector('.sidebar-toggle');
  if (sidebar && !sidebar.contains(e.target) && toggle && !toggle.contains(e.target)) {
    sidebar.classList.remove('open');
  }
});

// Dark Mode Logic
function initTheme() {
  const savedTheme = localStorage.getItem('theme') || 'light';
  document.documentElement.setAttribute('data-theme', savedTheme);
}

function toggleTheme() {
  const currentTheme = document.documentElement.getAttribute('data-theme');
  const newTheme = currentTheme === 'light' ? 'dark' : 'light';
  
  document.documentElement.setAttribute('data-theme', newTheme);
  localStorage.setItem('theme', newTheme);
  
  showToast(`Switched to ${newTheme} mode`, 'info');
}

// Toast Notifications
function showToast(message, type = 'success') {
  const container = document.getElementById('toast-container');
  if (!container) return;

  const toast = document.createElement('div');
  toast.className = `toast-msg toast-${type}`;
  
  let icon = 'bi-check-circle-fill';
  if (type === 'danger') icon = 'bi-x-circle-fill';
  if (type === 'warning') icon = 'bi-exclamation-triangle-fill';
  if (type === 'info') icon = 'bi-info-circle-fill';

  toast.innerHTML = `
    <i class="bi ${icon}"></i>
    <span>${message}</span>
    <button class="toast-close"><i class="bi bi-x"></i></button>
  `;

  container.appendChild(toast);

  // Close on button click
  toast.querySelector('.toast-close').onclick = () => {
    toast.classList.add('toast-exit');
    setTimeout(() => toast.remove(), 300);
  };

  // Auto remove
  setTimeout(() => {
    if (toast.parentNode) {
      toast.classList.add('toast-exit');
      setTimeout(() => toast.remove(), 300);
    }
  }, 4000);
}

// Table Search Logic
function initTableSearch(inputId, tableId) {
  const input = document.getElementById(inputId);
  const table = document.getElementById(tableId);
  if (!input || !table) return;

  input.addEventListener('input', function() {
    const val = this.value.toLowerCase();
    const rows = table.querySelectorAll('tbody tr');
    let found = 0;

    rows.forEach(row => {
      if (row.classList.contains('no-results-row')) return;
      
      const text = row.textContent.toLowerCase();
      if (text.includes(val)) {
        row.style.display = '';
        found++;
      } else {
        row.style.display = 'none';
      }
    });

    // Handle empty state within table if no results found
    const tbody = table.querySelector('tbody');
    let noResultsRow = tbody.querySelector('.no-results-row');
    
    if (found === 0) {
      if (!noResultsRow) {
        noResultsRow = document.createElement('tr');
        noResultsRow.className = 'no-results-row';
        noResultsRow.innerHTML = `
          <td colspan="100%" class="text-center py-4">
            <i class="bi bi-search" style="font-size: 24px; color: var(--muted); opacity: 0.5;"></i>
            <p class="mt-2 mb-0" style="color: var(--muted); font-size: 13px;">No matching records found</p>
          </td>
        `;
        tbody.appendChild(noResultsRow);
      }
    } else if (noResultsRow) {
      noResultsRow.remove();
    }
  });
}

// Loading States
function setBtnLoading(btn, isLoading, text = 'Processing...') {
  if (isLoading) {
    btn.dataset.originalHtml = btn.innerHTML;
    btn.classList.add('btn-loading');
    btn.innerHTML = `<span class="btn-text">${text}</span>`;
  } else {
    btn.classList.remove('btn-loading');
    btn.innerHTML = btn.dataset.originalHtml || btn.innerHTML;
  }
}

// Initialize on Load
document.addEventListener('DOMContentLoaded', function() {
  initTheme();
  
  // Auto-dismiss standard alerts and convert to toasts if preferred
  document.querySelectorAll('.alert').forEach(a => {
    // We can keep standard alerts or auto-convert them. 
    // For now, just keep the auto-dismiss.
    setTimeout(() => {
      const bsAlert = bootstrap.Alert.getOrCreateInstance(a);
      if (bsAlert) bsAlert.close();
    }, 4000);
  });
});

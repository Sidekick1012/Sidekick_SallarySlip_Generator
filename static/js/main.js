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

// Theme Toggle
function toggleTheme() {
  const currentTheme = document.documentElement.getAttribute('data-theme');
  const newTheme = currentTheme === 'light' ? 'dark' : 'light';
  
  document.documentElement.setAttribute('data-theme', newTheme);
  localStorage.setItem('theme', newTheme);
  
  showToast(`Switched to ${newTheme} mode`, 'info');
}

// Confetti Celebration
function triggerCelebration() {
  const duration = 3 * 1000;
  const animationEnd = Date.now() + duration;
  const defaults = { startVelocity: 30, spread: 360, ticks: 60, zIndex: 10000 };

  function randomInRange(min, max) {
    return Math.random() * (max - min) + min;
  }

  const interval = setInterval(function() {
    const timeLeft = animationEnd - Date.now();

    if (timeLeft <= 0) {
      return clearInterval(interval);
    }

    const particleCount = 50 * (timeLeft / duration);
    // since particles fall down, start a bit higher than random
    confetti({ ...defaults, particleCount, origin: { x: randomInRange(0.1, 0.3), y: Math.random() - 0.2 } });
    confetti({ ...defaults, particleCount, origin: { x: randomInRange(0.7, 0.9), y: Math.random() - 0.2 } });
  }, 250);
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

    const tbody = table.querySelector('tbody');
    let noResultsRow = tbody.querySelector('.no-results-row');
    
    if (found === 0) {
      if (!noResultsRow) {
        noResultsRow = document.createElement('tr');
        noResultsRow.className = 'no-results-row';
        noResultsRow.innerHTML = `<td colspan="100%" class="text-center py-4"><i class="bi bi-search" style="font-size: 24px; color: var(--muted); opacity: 0.5;"></i><p class="mt-2 mb-0" style="color: var(--muted); font-size: 13px;">No matching records found</p></td>`;
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
  // Check for success/info flash messages that should trigger celebration
  document.querySelectorAll('.alert-success, .alert-info').forEach(a => {
    const txt = a.textContent.toLowerCase();
    const triggerWords = ['email', 'sent', 'success', 'generated', 'initiated', 'started'];
    
    if (triggerWords.some(word => txt.includes(word))) {
      // Small delay to ensure page is visually ready
      setTimeout(triggerCelebration, 300);
    }
  });

  // Auto-dismiss standard alerts
  document.querySelectorAll('.alert').forEach(a => {
    setTimeout(() => {
      const bsAlert = bootstrap.Alert.getOrCreateInstance(a);
      if (bsAlert) bsAlert.close();
    }, 5000);
  });
});

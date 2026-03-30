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

// Auto-dismiss alerts
setTimeout(() => {
  document.querySelectorAll('.alert').forEach(a => {
    const bsAlert = bootstrap.Alert.getOrCreateInstance(a);
    bsAlert.close();
  });
}, 4000);

/**
 * theme.js — Dark/Light mode toggle
 * Persists preference in localStorage. Applies on page load.
 */
(function () {
  const KEY = 'fitform-theme';

  function applyTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    const btns = document.querySelectorAll('.theme-toggle');
    btns.forEach(btn => {
      btn.textContent = theme === 'dark' ? '☀️' : '🌙';
      btn.title = theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode';
    });
  }

  function toggleTheme() {
    const current = document.documentElement.getAttribute('data-theme') || 'light';
    const next = current === 'dark' ? 'light' : 'dark';
    localStorage.setItem(KEY, next);
    applyTheme(next);
  }

  // Apply saved theme immediately (before paint to avoid flash)
  const saved = localStorage.getItem(KEY) || 'light';
  applyTheme(saved);

  // Expose toggle for button onclick
  window.toggleTheme = toggleTheme;

  // Wire up all toggle buttons after DOM ready
  document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.theme-toggle').forEach(btn => {
      btn.addEventListener('click', toggleTheme);
    });
    // Reapply so button icons are correct
    applyTheme(localStorage.getItem(KEY) || 'light');
  });
})();

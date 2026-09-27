(function () {
  const STORAGE_KEY = 'theme';

  function getSystemPreference() {
    return window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  }

  function getStoredTheme() {
    try {
      const val = localStorage.getItem(STORAGE_KEY);
      if (val === 'dark' || val === 'light') return val;
    } catch (e) {
      // localStorage disabled or blocked
    }
    return null;
  }

  function applyTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
  }

  // Set theme immediately to prevent screen flash (FOUC)
  const initialTheme = getStoredTheme() || getSystemPreference();
  applyTheme(initialTheme);

  function updateToggleUI(theme) {
    const btn = document.getElementById('themeToggle');
    if (!btn) return;
    const isDark = theme === 'dark';
    const label = isDark ? 'التبديل إلى المظهر الفاتح' : 'التبديل إلى المظهر الداكن';
    btn.setAttribute('aria-label', label);
    btn.setAttribute('title', label);
  }

  function toggleTheme() {
    const current = document.documentElement.getAttribute('data-theme') || initialTheme;
    const next = current === 'dark' ? 'light' : 'dark';
    applyTheme(next);
    try {
      localStorage.setItem(STORAGE_KEY, next);
    } catch (e) {}
    updateToggleUI(next);
  }

  function init() {
    const current = document.documentElement.getAttribute('data-theme') || initialTheme;
    updateToggleUI(current);

    const btn = document.getElementById('themeToggle');
    if (btn) {
      btn.addEventListener('click', toggleTheme);
    }

    if (window.matchMedia) {
      window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', function (e) {
        if (!getStoredTheme()) {
          const next = e.matches ? 'dark' : 'light';
          applyTheme(next);
          updateToggleUI(next);
        }
      });
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();

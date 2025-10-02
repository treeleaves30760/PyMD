// Dark Mode Toggle for PyMD
(function() {
    'use strict';

    // Check for saved theme preference or default to light mode
    const currentTheme = localStorage.getItem('pymd-theme') || 'light';

    // Apply theme on load
    document.documentElement.setAttribute('data-theme', currentTheme);

    // Create and inject dark mode toggle button
    function createToggleButton() {
        const button = document.createElement('button');
        button.id = 'pymd-theme-toggle';
        button.className = 'pymd-theme-toggle';
        button.setAttribute('aria-label', 'Toggle dark mode');
        button.innerHTML = currentTheme === 'dark' ? '☀️' : '🌙';

        button.addEventListener('click', toggleTheme);
        document.body.appendChild(button);
    }

    // Toggle theme function
    function toggleTheme() {
        const currentTheme = document.documentElement.getAttribute('data-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';

        document.documentElement.setAttribute('data-theme', newTheme);
        localStorage.setItem('pymd-theme', newTheme);

        const button = document.getElementById('pymd-theme-toggle');
        if (button) {
            button.innerHTML = newTheme === 'dark' ? '☀️' : '🌙';
        }
    }

    // Initialize on DOM ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', createToggleButton);
    } else {
        createToggleButton();
    }

    // Expose toggle function globally for programmatic use
    window.pymdToggleTheme = toggleTheme;
})();

window.initThemeToggle = function() {
    const themeToggle = document.getElementById('theme-toggle');
    const root = document.documentElement;
    
    const currentTheme = localStorage.getItem('theme') || 'dark';
    root.setAttribute('data-theme', currentTheme);
    
    const currentFontSize = localStorage.getItem('fontSize') || 'medium';
    document.body.classList.remove('font-small', 'font-medium', 'font-large', 'font-xlarge');
    document.body.classList.add('font-' + currentFontSize);

    function updateThemeIcon(theme) {
        if (!themeToggle) return;
        const icon = themeToggle.querySelector('#theme-icon') || themeToggle.querySelector('i');
        const text = themeToggle.querySelector('#theme-text');
        
        if (theme === 'dark') {
            if (icon) {
                icon.className = 'fa-solid fa-moon';
                icon.style.color = '#38bdf8';
            }
            if (text) {
                text.textContent = 'Modo Oscuro';
            }
            themeToggle.setAttribute('title', 'Modo Oscuro activo. Clic para cambiar a Modo Claro');
        } else {
            if (icon) {
                icon.className = 'fa-solid fa-sun';
                icon.style.color = '#f59e0b';
            }
            if (text) {
                text.textContent = 'Modo Claro';
            }
            themeToggle.setAttribute('title', 'Modo Claro activo. Clic para cambiar a Modo Oscuro');
        }
    }

    if (themeToggle) {
        updateThemeIcon(currentTheme);
        themeToggle.onclick = function() {
            let theme = root.getAttribute('data-theme');
            let newTheme = (theme === 'light') ? 'dark' : 'light';
            
            root.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);
            updateThemeIcon(newTheme);
        };
    }
};

document.addEventListener('DOMContentLoaded', () => {
    window.initThemeToggle();
});

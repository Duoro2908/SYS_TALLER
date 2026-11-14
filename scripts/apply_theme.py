import os

base_path = 'templates/base.html'
with open(base_path, 'r', encoding='utf-8') as f:
    content = f.read()

head_insert = """    <!-- Anti-flicker theme loader -->
    <script>
        (function() {
            try {
                var currentTheme = localStorage.getItem('theme') || 'dark';
                document.documentElement.setAttribute('data-theme', currentTheme);
            } catch(e) {}
        })();
    </script>
"""

if 'Anti-flicker theme loader' not in content:
    content = content.replace('{% block extra_css %}{% endblock %}', head_insert + '    {% block extra_css %}{% endblock %}')

old_profile_marker = '<div class="user-profile">'
if old_profile_marker in content and 'id="theme-toggle"' not in content:
    new_profile = """<div class="user-profile" style="display: flex; align-items: center; gap: 14px;">
                <button type="button" id="theme-toggle" class="theme-toggle-btn" title="Alternar Modo Oscuro / Modo Claro" aria-label="Cambiar tema">
                    <i class="fa-solid fa-moon" id="theme-icon"></i>
                    <span id="theme-text" class="theme-text">Modo Oscuro</span>
                </button>"""
    # Replace the container start and clear any comment inside
    import re
    content = re.sub(r'<div class="user-profile">\s*(?:<!--.*?-->)?\s*</div>', new_profile + "\n            </div>", content)

with open(base_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated base.html successfully")

# Update settings/index.html
settings_path = 'templates/settings/index.html'
if os.path.exists(settings_path):
    with open(settings_path, 'r', encoding='utf-8') as f:
        sc = f.read()
    if 'data-theme' not in sc:
        sc = sc.replace("localStorage.setItem('fontSize', newFontSize);", "localStorage.setItem('fontSize', newFontSize);\n            document.documentElement.setAttribute('data-theme', newTheme);")
        with open(settings_path, 'w', encoding='utf-8') as f:
            f.write(sc)
        print("Updated settings/index.html")

with open('templates/admin/registro_mensual.html', 'r', encoding='utf-8') as f:
    content = f.read()

idx_start = content.find("<style>")
idx_end = content.find("</style>")
style_block = content[idx_start:idx_end]

# Fix CSS variables in :root
style_block = style_block.replace("--atelier-surface: #14141c;", "--atelier-surface: var(--bg-surface);")
style_block = style_block.replace("--atelier-card: rgba(25, 25, 36, 0.7);", "--atelier-card: var(--bg-surface);")
style_block = style_block.replace("--atelier-border: rgba(255, 255, 255, 0.08);", "--atelier-border: var(--border-color);")
style_block = style_block.replace("--atelier-text-muted: #8E8E93;", "--atelier-text-muted: var(--text-muted);")

style_block = style_block.replace("color: #fff;", "color: var(--text-primary);")
style_block = style_block.replace("background: rgba(0, 0, 0, 0.4);", "background: var(--bg-primary);")
style_block = style_block.replace("border: 1px solid rgba(255, 255, 255, 0.15);", "border: 1px solid var(--border-color);")
style_block = style_block.replace("background: linear-gradient(135deg, rgba(20, 20, 30, 0.9) 0%, rgba(28, 28, 42, 0.95) 100%);",
                                  "background: var(--bg-surface); box-shadow: var(--shadow-sm);")
style_block = style_block.replace("background: rgba(0, 0, 0, 0.25);", "background: var(--bg-primary);")
style_block = style_block.replace("border: 1px solid rgba(255, 255, 255, 0.06);", "border: 1px solid var(--border-color);")
style_block = style_block.replace("background: rgba(255, 255, 255, 0.08);", "background: var(--bg-secondary);")
style_block = style_block.replace("background: rgba(0, 0, 0, 0.35);", "background: var(--bg-secondary);")
style_block = style_block.replace("border-bottom: 1px solid rgba(255, 255, 255, 0.05);", "border-bottom: 1px solid var(--border-color);")
style_block = style_block.replace("color: #e5e5ea;", "color: var(--text-primary);")
style_block = style_block.replace("background: rgba(255, 255, 255, 0.02);", "background: var(--bg-primary);")
style_block = style_block.replace("background: #181822;", "background: var(--bg-surface);")
style_block = style_block.replace("border: 1px solid rgba(255, 255, 255, 0.12);", "border: 1px solid var(--border-color);")

content = content[:idx_start] + style_block + content[idx_end:]

content = content.replace('<h1 style="color: #fff;', '<h1 style="color: var(--text-primary);')
content = content.replace('style="color: #fff;', 'style="color: var(--text-primary);')

with open('templates/admin/registro_mensual.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated templates/admin/registro_mensual.html successfully")


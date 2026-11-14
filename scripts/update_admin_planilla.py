with open('templates/admin/planilla.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace style block
idx_start = content.find("<style>")
idx_end = content.find("</style>")
style_block = content[idx_start:idx_end]

# Replacements in style block
style_block = style_block.replace("background: rgba(30, 30, 36, 0.7);", "background: var(--bg-surface);")
style_block = style_block.replace("border: 1px solid rgba(255, 255, 255, 0.08);", "border: 1px solid var(--border-color);")
style_block = style_block.replace("background: rgba(25, 25, 30, 0.65);", "background: var(--bg-surface);")
style_block = style_block.replace("background: rgba(255, 255, 255, 0.04);", "background: var(--bg-secondary);")
style_block = style_block.replace("border-bottom: 1px solid rgba(255, 255, 255, 0.1);", "border-bottom: 1px solid var(--border-color);")
style_block = style_block.replace("border-bottom: 1px solid rgba(255, 255, 255, 0.06);", "border-bottom: 1px solid var(--border-color);")
style_block = style_block.replace("color: #e5e5ea;", "color: var(--text-primary);")
style_block = style_block.replace("background: rgba(255, 255, 255, 0.03);", "background: var(--bg-primary);")
style_block = style_block.replace("background: rgba(255, 255, 255, 0.05);", "background: var(--bg-secondary);")
style_block = style_block.replace("border-top: 2px solid rgba(255, 255, 255, 0.15);", "border-top: 2px solid var(--border-color);")
style_block = style_block.replace("background: rgba(25, 25, 32, 0.7);", "background: var(--bg-surface);")
style_block = style_block.replace("background: #1a1a24;", "background: var(--bg-surface);")
style_block = style_block.replace("border: 1px solid rgba(255, 255, 255, 0.12);", "border: 1px solid var(--border-color);")
style_block = style_block.replace("color: #fff;", "color: var(--text-primary);")
style_block = style_block.replace("background: rgba(255, 255, 255, 0.08);", "background: var(--bg-secondary);")
style_block = style_block.replace("border: 1px solid rgba(255, 255, 255, 0.15);", "border: 1px solid var(--border-color);")

content = content[:idx_start] + style_block + content[idx_end:]

# Replace headers with white text
content = content.replace('<h1 style="font-size: 1.85rem; font-weight: 700; color: #fff; margin: 0 0 6px 0;">',
                          '<h1 style="font-size: 1.85rem; font-weight: 700; color: var(--text-primary); margin: 0 0 6px 0;">')
content = content.replace('<h3 style="margin: 8px 0 2px 0; font-size: 1.15rem; color: #fff;">',
                          '<h3 style="margin: 8px 0 2px 0; font-size: 1.15rem; color: var(--text-primary);">')
content = content.replace('<h3 id="ajusteColaboradorNombre" style="margin: 0; font-size: 1.1rem; color: #fff;">',
                          '<h3 id="ajusteColaboradorNombre" style="margin: 0; font-size: 1.1rem; color: var(--text-primary);">')

with open('templates/admin/planilla.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated templates/admin/planilla.html successfully")


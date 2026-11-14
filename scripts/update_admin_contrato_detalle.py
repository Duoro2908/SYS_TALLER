with open('templates/admin/contrato_detalle.html', 'r', encoding='utf-8') as f:
    content = f.read()

idx_start = content.find("<style>")
idx_end = content.find("</style>")
style_block = content[idx_start:idx_end]

style_block = style_block.replace("background: rgba(30, 30, 36, 0.7);", "background: var(--bg-surface);")
style_block = style_block.replace("border: 1px solid rgba(255, 255, 255, 0.1);", "border: 1px solid var(--border-color);")
style_block = style_block.replace("color: #fff;", "color: var(--text-primary);")
style_block = style_block.replace("border-bottom: 1px solid rgba(255, 255, 255, 0.06);", "border-bottom: 1px solid var(--border-color);")
style_block = style_block.replace("background: rgba(255, 255, 255, 0.08);", "background: var(--bg-secondary);")
style_block = style_block.replace("border: 1px solid rgba(255, 255, 255, 0.15);", "border: 1px solid var(--border-color);")

content = content[:idx_start] + style_block + content[idx_end:]

content = content.replace('<h1 style="font-size: 1.8rem; font-weight: 700; color: #fff; margin: 0;">',
                          '<h1 style="font-size: 1.8rem; font-weight: 700; color: var(--text-primary); margin: 0;">')

with open('templates/admin/contrato_detalle.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated templates/admin/contrato_detalle.html successfully")


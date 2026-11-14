import os
import re

template_dir = 'templates'
results = []

for root, dirs, files in os.walk(template_dir):
    for f in files:
        if f.endswith('.html'):
            path = os.path.join(root, f)
            with open(path, 'r', encoding='utf-8') as fp:
                content = fp.read()
            styles = re.findall(r'<style>(.*?)</style>', content, re.DOTALL)
            if styles:
                total_style = "\n".join(styles)
                has_hardcoded_dark = bool(re.search(r'rgba\(\s*(?:0|1\d|2\d|30)\s*,\s*(?:0|1\d|2\d|30)\s*,\s*(?:0|1\d|2\d|30)', total_style))
                has_white_text = bool(re.search(r'color:\s*(?:#fff|#ffffff|white)', total_style, re.IGNORECASE))
                results.append((path, has_hardcoded_dark, has_white_text, len(styles)))

print("Templates with internal <style>:")
for path, dark, white, cnt in sorted(results):
    print(f"{path}: dark_bg={dark}, white_text={white}, styles_cnt={cnt}")


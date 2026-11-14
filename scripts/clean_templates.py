import os

def clean_template(filepath, title_text, page_title_text):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    marker = '{% block content %}'
    if marker not in content:
        print(f"Marker not found in {filepath}")
        return

    parts = content.split(marker, 1)
    
    header = f"""{{% extends "base.html" %}}

{{% block title %}}{title_text}{{% endblock %}}
{{% block page_title %}}{page_title_text}{{% endblock %}}

{{% block content %}}"""

    new_content = header + parts[1]
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print(f"Cleaned {filepath} successfully!")

balance_path = r'c:\Users\Alexander\OneDrive\Music\Documents\Taller CR\templates\contador\balance.html'
clean_template(balance_path, 'Balance General - Taller y Lubricantes CR', 'Balance General')

estado_path = r'c:\Users\Alexander\OneDrive\Music\Documents\Taller CR\templates\contador\estado_resultados.html'
clean_template(estado_path, 'Estado de Resultados - Taller y Lubricantes CR', 'Estado de Resultados')


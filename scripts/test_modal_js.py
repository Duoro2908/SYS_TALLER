import sys
import os
import subprocess
import re
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import app

client = app.test_client()
with client.session_transaction() as sess:
    sess['user_id'] = 1
    sess['usuario_id'] = 1
    sess['rol_id'] = 1
    sess['username'] = 'elvin.admin'

resp = client.get('/admin/planilla')
html = resp.data.decode('utf-8')

test_snippet = """
<script>
window.testResults = [];
try {
    if (typeof abrirModalDGI === 'function') {
        window.testResults.push('abrirModalDGI is function: OK');
        abrirModalDGI(2);
        const modalDGI = document.getElementById('modalDesgloseDGI');
        if (modalDGI && (modalDGI.classList.contains('active') || modalDGI.style.display === 'flex')) {
            window.testResults.push('modalDesgloseDGI opened successfully: OK');
        } else {
            window.testResults.push('modalDesgloseDGI failed to open');
        }
        cerrarModalDGI();
    } else {
        window.testResults.push('abrirModalDGI is NOT a function');
    }
} catch(e) {
    window.testResults.push('abrirModalDGI error: ' + e.message);
}

try {
    if (typeof abrirModalAjusteNomina === 'function') {
        window.testResults.push('abrirModalAjusteNomina is function: OK');
        abrirModalAjusteNomina(2);
        const modalAjuste = document.getElementById('modalEditarAjusteNomina');
        if (modalAjuste && (modalAjuste.classList.contains('active') || modalAjuste.style.display === 'flex')) {
            window.testResults.push('modalEditarAjusteNomina opened successfully: OK');
        } else {
            window.testResults.push('modalEditarAjusteNomina failed to open');
        }
        cerrarModalAjusteNomina();
    } else {
        window.testResults.push('abrirModalAjusteNomina is NOT a function');
    }
} catch(e) {
    window.testResults.push('abrirModalAjusteNomina error: ' + e.message);
}

const div = document.createElement('div');
div.id = 'automatedTestOutput';
div.innerText = window.testResults.join(' || ');
document.body.appendChild(div);
</script>
"""

html_with_test = html.replace('</body>', test_snippet + '</body>')
test_file = os.path.abspath('test_rendered_page.html')
with open(test_file, 'w', encoding='utf-8') as f:
    f.write(html_with_test)

edge_path = r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'
file_url = 'file:///' + test_file.replace('\\', '/')
cmd = [edge_path, '--headless', '--disable-gpu', '--dump-dom', file_url]
p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8')

output = p.stdout
m = re.search(r'id="automatedTestOutput">([^<]+)</div>', output)
if m:
    print("TEST_RESULTS:")
    print(m.group(1))
else:
    print("Could not find test output in DOM.")
    if p.stderr:
        print("Stderr:", p.stderr[:500])

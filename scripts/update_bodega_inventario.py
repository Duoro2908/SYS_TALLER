with open('templates/bodega/inventario.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace <style> block in inventario.html
old_style_marker = "<style>"
end_style_marker = "</style>"
idx_start = content.find(old_style_marker)
idx_end = content.find(end_style_marker)

new_style = """<style>
    /* Premium Inventory Styles - Themed */
    .inventory-toolbar { 
        display: flex; justify-content: space-between; align-items: center; 
        margin-bottom: 25px; flex-wrap: wrap; gap: 16px;
        background: var(--bg-surface);
        padding: 18px 22px;
        border-radius: 16px;
        border: 1px solid var(--border-color);
        box-shadow: var(--shadow-sm);
    }
    
    .filters { display: flex; gap: 12px; flex-wrap: wrap; flex: 1; }
    
    .filters input {
        background: var(--bg-primary); border: 1px solid var(--border-color); color: var(--text-primary);
        padding: 10px 16px; border-radius: 10px; font-size: 0.92rem; flex: 1; min-width: 200px;
        transition: all 0.25s ease;
    }
    .filters input:focus { border-color: #2563eb; outline: none; box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.15); }
    
    .filters select {
        background: var(--bg-primary); border: 1px solid var(--border-color); color: var(--text-primary);
        padding: 10px 16px; border-radius: 10px; font-size: 0.92rem;
        cursor: pointer; transition: all 0.25s ease;
    }
    .filters select:hover { border-color: var(--text-muted); }
    .filters select:focus { border-color: #2563eb; outline: none; box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.15); }

    .btn-new { 
        background: linear-gradient(135deg, #2563eb, #1d4ed8);
        color: white; border: none; padding: 11px 22px; border-radius: 10px; 
        font-weight: 600; font-size: 0.92rem; cursor: pointer;
        transition: all 0.25s ease;
        box-shadow: 0 4px 14px rgba(37, 99, 235, 0.3);
        display: flex; align-items: center; gap: 8px;
    }
    .btn-new:hover { transform: translateY(-1px); box-shadow: 0 6px 18px rgba(37, 99, 235, 0.4); }
    
    /* Advanced Grid Layout */
    .product-grid { 
        display: grid; 
        grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); 
        gap: 24px; 
        margin-top: 15px;
    }

    .product-card { 
        background: var(--bg-surface); 
        border-radius: 16px; 
        overflow: hidden; 
        border: 1px solid var(--border-color); 
        display: flex; flex-direction: column; 
        transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275); 
        position: relative; 
        box-shadow: var(--shadow-sm);
    }
    
    .product-card:hover { 
        transform: translateY(-6px); 
        box-shadow: var(--shadow-md); 
        border-color: #2563eb;
    }

    .product-img-container { 
        height: 220px; 
        background: #ffffff; 
        display: flex; align-items: center; justify-content: center; 
        padding: 20px; position: relative;
        border-bottom: 1px solid var(--border-color);
    }
    
    .product-img-container img { 
        max-width: 100%; max-height: 100%; object-fit: contain; 
        transition: transform 0.4s ease;
        mix-blend-mode: multiply;
    }
    
    .product-card:hover .product-img-container img { transform: scale(1.08); }
    
    .product-details { padding: 20px; display: flex; flex-direction: column; flex: 1; }
    
    .product-sku { 
        font-size: 0.78rem; color: var(--text-muted); margin-bottom: 6px; 
        font-family: 'SFMono-Regular', Consolas, monospace; letter-spacing: 0.5px;
        font-weight: 600;
    }
    
    .product-title { 
        font-size: 1.15rem; font-weight: 700; color: var(--text-primary); 
        margin: 0 0 12px 0; line-height: 1.35;
    }
    
    .product-badges { display: flex; gap: 6px; margin-bottom: 16px; flex-wrap: wrap;}
    .badge {
        padding: 4px 9px; border-radius: 6px; font-size: 0.72rem; font-weight: 600;
        text-transform: uppercase; letter-spacing: 0.5px;
    }
    .cat-badge { background: rgba(139, 92, 246, 0.12); color: #8b5cf6; border: 1px solid rgba(139, 92, 246, 0.25); }
    .type-badge { background: rgba(59, 130, 246, 0.12); color: #2563eb; border: 1px solid rgba(59, 130, 246, 0.25); }

    .product-stock { margin-bottom: 16px; display: flex; align-items: center; gap: 8px; }
    .stock-indicator { width: 8px; height: 8px; border-radius: 50%; box-shadow: 0 0 8px currentColor; }
    .stock-text { font-size: 0.88rem; font-weight: 600; }
    
    .stock-high { color: #10b981; }
    .stock-low { color: #f59e0b; }
    .stock-out { color: #ef4444; }

    .product-price-row { 
        display: flex; justify-content: space-between; align-items: flex-end; 
        margin-top: auto; border-top: 1px dashed var(--border-color); padding-top: 16px;
    }
    
    .price-col { display: flex; flex-direction: column; }
    .price-label { font-size: 0.7rem; color: var(--text-secondary); text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 3px; font-weight: 600;}
    .price-val { 
        font-size: 1.35rem; font-weight: 800; 
        color: var(--text-primary);
    }
    .price-val-cost { font-size: 0.95rem; font-weight: 600; color: var(--text-muted); }
    
    .product-actions { 
        position: absolute; top: 12px; right: 12px; display: flex; gap: 8px; 
        background: var(--bg-surface); padding: 5px; border-radius: 10px; 
        border: 1px solid var(--border-color);
        opacity: 0; transform: translateY(-6px); transition: all 0.25s ease;
        z-index: 10;
        box-shadow: var(--shadow-sm);
    }
    .product-card:hover .product-actions { opacity: 1; transform: translateY(0); }
    
    .action-btn { 
        border: none; cursor: pointer; color: var(--text-secondary); border-radius: 6px; 
        width: 32px; height: 32px; display: flex; align-items: center; justify-content: center; 
        background: var(--bg-primary); transition: all 0.2s;
    }
    .action-btn:hover { background: var(--border-color); color: var(--text-primary); transform: scale(1.05); }
    .action-btn.btn-edit:hover { color: #2563eb; }
    .action-btn.btn-toggle:hover { color: #ef4444; }
    .action-btn.btn-toggle.inactive:hover { color: #10b981; }
    
    .no-image-placeholder { 
        width: 100%; height: 100%; display: flex; flex-direction: column; 
        align-items: center; justify-content: center; color: var(--text-muted); 
        font-size: 3.5rem; opacity: 0.4;
    }

    /* Modal Styles */
    .modal { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.6); z-index: 1000; align-items: center; justify-content: center; backdrop-filter: blur(5px); }
    .modal-content { background: var(--bg-surface); padding: 28px; border-radius: 16px; width: 100%; max-width: 500px; box-shadow: var(--shadow-lg); border: 1px solid var(--border-color); color: var(--text-primary); }
    .modal-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 22px; border-bottom: 1px solid var(--border-color); padding-bottom: 12px; }
    .modal-header h3 { margin: 0; color: var(--text-primary); font-weight: 700; font-size: 1.25rem; }
    .close-btn { background: none; border: none; font-size: 1.6rem; color: var(--text-muted); cursor: pointer; line-height: 1; }
    .close-btn:hover { color: var(--text-primary); }
    
    .form-group { margin-bottom: 16px; }
    .form-group label { display: block; margin-bottom: 6px; font-weight: 600; color: var(--text-secondary); font-size: 0.88rem; }
    .form-group input, .form-group select { width: 100%; padding: 10px 14px; border: 1px solid var(--border-color); border-radius: 8px; background: var(--bg-primary); color: var(--text-primary); font-size: 0.92rem; box-sizing: border-box; transition: all 0.25s; }
    .form-group input:focus, .form-group select:focus { border-color: #2563eb; outline: none; box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.15); }
</style>"""

content = content[:idx_start] + new_style + content[idx_end + len(end_style_marker):]

with open('templates/bodega/inventario.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated templates/bodega/inventario.html successfully")


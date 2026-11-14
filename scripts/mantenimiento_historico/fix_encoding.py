from database import get_db_connection

def fix_encoding():
    conn = get_db_connection()
    if not conn:
        print("No se pudo conectar a la base de datos.")
        return
        
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT ProductoID, Nombre, Categoria, Descripcion FROM Productos")
        productos = cursor.fetchall()
        
        replacements = {
            'Ã¡': 'á',
            'Ã©': 'é',
            'Ã\xad': 'í',  # Sometimes 'í' shows up weirdly depending on terminal, let's try standard mapping
            'Ã³': 'ó',
            'Ãº': 'ú',
            'Ã±': 'ñ',
            'Ã\x81': 'Á', # Á
            'Ã‰': 'É',
            'Ã\x8d': 'Í',
            'Ã“': 'Ó',
            'Ã”': 'Ó', # Sometimes it comes out as Ã“ or Ã”
            'Ãš': 'Ú',
            'Ã‘': 'Ñ',
            'Ã': 'Á', # Fallback for 'Ãrbol' which might just be 'Ã'
            '\x81': 'Á', # Another variation of Á
            '\xad': 'í', # Another variation of í
            '\xad': 'í',
            '': 'í', # Fallback if we have unknown
        }
        
        # A more robust way to fix UTF-8 double-encoding in Python:
        # text.encode('latin-1').decode('utf-8')
        
        def fix_text(text):
            if not text:
                return text
                
            try:
                # Intento de decodificar directamente si es un problema de doble codificación
                return text.encode('latin1').decode('utf-8')
            except:
                pass
                
            # Si falla el método anterior, hacemos reemplazo manual
            new_text = text
            new_text = new_text.replace('Ã¡', 'á').replace('Ã©', 'é').replace('Ã³', 'ó').replace('Ãº', 'ú')
            new_text = new_text.replace('Ã±', 'ñ').replace('Ã“', 'Ó').replace('Ã”', 'Ó').replace('Ã‰', 'É')
            new_text = new_text.replace('Ãrbol', 'Árbol').replace('SUSPENSIÃ“N', 'SUSPENSIÓN')
            new_text = new_text.replace('Ã\x81', 'Á').replace('Ã', 'Á') # Á
            new_text = new_text.replace('\x81', 'Á')
            
            if 'Buja' in new_text or 'Buj\xada' in new_text: new_text = new_text.replace('Buja', 'Bujía').replace('Buj\xada', 'Bujía')
            if 'Lquido' in new_text or 'L\xadquido' in new_text: new_text = new_text.replace('Lquido', 'Líquido').replace('L\xadquido', 'Líquido')
            if 'Guas' in new_text or 'Gu\xadas' in new_text: new_text = new_text.replace('Guas', 'Guías').replace('Gu\xadas', 'Guías')
            if 'Batera' in new_text or 'Bater\xada' in new_text: new_text = new_text.replace('Batera', 'Batería').replace('Bater\xada', 'Batería')
            if 'silln' in new_text or 'sill\xadn' in new_text or 'sillÃn' in new_text: new_text = new_text.replace('silln', 'sillín').replace('sill\xadn', 'sillín').replace('sillÃn', 'sillín')
            if 'centrfuga' in new_text or 'centr\xadfuga' in new_text: new_text = new_text.replace('centrfuga', 'centrífuga').replace('centr\xadfuga', 'centrífuga')
            
            new_text = new_text.replace('CARROCERÃA', 'CARROCERÍA')
            new_text = new_text.replace('SUSPENSIÃ“N', 'SUSPENSIÓN')
            new_text = new_text.replace('GenÃ©rico', 'Genérico')
            new_text = new_text.replace('GenA©rico', 'Genérico')
            return new_text
            
        for row in productos:
            p_id, nombre, cat, desc = row
            new_nombre = fix_text(nombre)
            new_cat = fix_text(cat)
            new_desc = fix_text(desc)
            
            if new_nombre != nombre or new_cat != cat or new_desc != desc:
                cursor.execute(
                    "UPDATE Productos SET Nombre=?, Categoria=?, Descripcion=? WHERE ProductoID=?",
                    (new_nombre, new_cat, new_desc, p_id)
                )
        
        conn.commit()
        print("Textos corregidos.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    fix_encoding()

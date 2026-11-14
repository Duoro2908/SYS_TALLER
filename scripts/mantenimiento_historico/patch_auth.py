import os

filepath = 'routes/auth.py'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace(
'''    if not mensaje:
        flash("El mensaje es obligatorio.", "error")
        return redirect(url_for('auth.login'))''',
'''    if not mensaje:
        return jsonify({'status': 'error', 'message': 'El mensaje es obligatorio.'})'''
)

content = content.replace(
'''            conn.commit()
            flash("Su mensaje ha sido enviado exitosamente a Atención al Cliente. Gracias por ayudarnos a mejorar.", "success")
        except Exception as e:
            flash(f"Ocurrió un error al enviar el mensaje: {e}", "error")
        finally:
            conn.close()
            
    return redirect(url_for('auth.login'))''',
'''            conn.commit()
            return jsonify({'status': 'success', 'message': 'Su mensaje ha sido enviado exitosamente a Atención al Cliente. Gracias por ayudarnos a mejorar.'})
        except Exception as e:
            return jsonify({'status': 'error', 'message': f"Ocurrió un error al enviar el mensaje: {e}"})
        finally:
            conn.close()
            
    return jsonify({'status': 'error', 'message': 'Error de conexión.'})'''
)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print("Replacement done.")

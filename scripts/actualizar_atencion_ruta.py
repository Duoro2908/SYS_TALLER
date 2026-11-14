with open('routes/atencion.py', 'r', encoding='utf-8') as f:
    c = f.read()

target = "@atencion_bp.route('/citas_whatsapp', methods=['GET'])"
replacement = """@atencion_bp.route('/eliminar_ticket/<int:id>', methods=['POST'])
def eliminar_ticket(id):
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM AtencionTickets WHERE TicketID = ?", (id,))
            conn.commit()
            flash("La queja o sugerencia ha sido eliminada del buzón.", "success")
        except Exception as e:
            flash(f"Error al eliminar el ticket: {e}", "error")
        finally:
            conn.close()
    return redirect(url_for('atencion.index'))

@atencion_bp.route('/citas_whatsapp', methods=['GET'])"""

if target in c:
    c = c.replace(target, replacement, 1)
    with open('routes/atencion.py', 'w', encoding='utf-8') as f:
        f.write(c)
    print("SUCCESS")
else:
    print("TARGET NOT FOUND")


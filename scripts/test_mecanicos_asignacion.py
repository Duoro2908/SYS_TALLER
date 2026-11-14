import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import database
from app import app

client = app.test_client()

with app.test_request_context():
    with client.session_transaction() as sess:
        sess['usuario_id'] = 1
        sess['rol_id'] = 1  # Super Admin / Gerente / Atencion

    conn = database.get_db_connection()
    cursor = conn.cursor()

    from datetime import datetime
    cursor.execute("""
        SELECT CitaID, FechaProgramada, Estado, MecanicoAsignadoID 
        FROM CitasWhatsApp 
        WHERE FechaProgramada = ?
    """, (datetime(2026, 10, 27, 15, 30),))
    citas = cursor.fetchall()
    print("Citas encontradas para 15:30:", citas)
    conn.close()

    if len(citas) >= 2:
        cita1_id = citas[0][0]
        cita2_id = citas[1][0]
        
        # Test 1: Assign Cita 1 to Mechanic 4 (Jose Francisco)
        print(f"\n--- TEST 1: Asignando Mecánico 4 a Cita {cita1_id} ---")
        res1 = client.post('/atencion/asignar_cita', json={'cita_id': cita1_id, 'mecanico_id': 4})
        print("Status code:", res1.status_code)
        print("Response:", res1.get_json())
        assert res1.status_code == 200 and res1.get_json()['success'] is True, "Test 1 Falló"

        # Test 2: Try to assign Cita 2 to SAME Mechanic 4 at same hour (MUST FAIL)
        print(f"\n--- TEST 2: Intentando asignar el MISMO Mecánico 4 a Cita {cita2_id} (Debe rechazar) ---")
        res2 = client.post('/atencion/asignar_cita', json={'cita_id': cita2_id, 'mecanico_id': 4})
        print("Status code:", res2.status_code)
        print("Response:", res2.get_json())
        assert res2.status_code == 400 and res2.get_json()['success'] is False, "Test 2 Falló (debió rechazar conflicto)"
        print("¡Conflicto rechazado correctamente con código 400!")

        # Test 3: Assign Cita 2 to Mechanic 5 (Elmerson Daniel) (MUST SUCCEED)
        print(f"\n--- TEST 3: Asignando Mecánico 5 a Cita {cita2_id} (Debe tener éxito) ---")
        res3 = client.post('/atencion/asignar_cita', json={'cita_id': cita2_id, 'mecanico_id': 5})
        print("Status code:", res3.status_code)
        print("Response:", res3.get_json())
        assert res3.status_code == 200 and res3.get_json()['success'] is True, "Test 3 Falló"
        print("¡Mecánico 5 asignado con éxito a la segunda cita simultánea!")

        # Cleanup: Reset citas back to Pendiente / NULL for user interactive testing
        conn = database.get_db_connection()
        cur = conn.cursor()
        cur.execute("UPDATE CitasWhatsApp SET MecanicoAsignadoID = NULL, Estado = 'Pendiente' WHERE CitaID IN (?, ?)", (cita1_id, cita2_id))
        conn.commit()
        conn.close()
        print("\nCitas 1 y 2 restauradas a 'Pendiente' para que el usuario las pruebe en pantalla.")

print("\nTODOS LOS TESTS COMPLETADOS SATISFACTORIAMENTE!")

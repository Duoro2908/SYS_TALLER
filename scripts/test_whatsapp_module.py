import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from whatsapp_bot import (
    get_whatsapp_config, set_bot_status, save_whatsapp_config,
    process_incoming_whatsapp_message, parse_appointment_details
)

def test_module():
    print("=== TEST 1: Configuración actual de WhatsApp ===")
    cfg = get_whatsapp_config()
    print("Config:", cfg)
    assert 'bot_activo' in cfg
    assert 'telefono_numero' in cfg
    
    print("\n=== TEST 2: Prueba Toggle Bot (Apagar y Encender) ===")
    # Apagar
    set_bot_status(False)
    cfg_off = get_whatsapp_config()
    print("Estado tras apagar:", cfg_off['bot_activo'])
    assert cfg_off['bot_activo'] is False
    
    # Procesar mensaje con Bot Apagado
    res_off = process_incoming_whatsapp_message("+505 8888 1111", "Hola quiero cita para mañana a las 11 am")
    print("Resultado con bot apagado:", res_off)
    assert res_off['success'] is True
    assert res_off['bot_activo'] is False
    
    # Encender
    set_bot_status(True)
    cfg_on = get_whatsapp_config()
    print("Estado tras encender:", cfg_on['bot_activo'])
    assert cfg_on['bot_activo'] is True
    
    print("\n=== TEST 3: Procesar mensaje con Bot Encendido ===")
    res_on = process_incoming_whatsapp_message("+505 8888 2222", "Hola quiero cita para el viernes a las 3 pm cambio de aceite preventivo")
    print("Resultado con bot encendido (exito):", res_on['success'])
    print("Cita agendada #:", res_on.get('cita_id'))
    assert res_on['success'] is True
    assert res_on['bot_activo'] is True
    assert 'cita_id' in res_on
    assert 'respuesta_bot' in res_on
    
    print("\n=== TEST 4: Guardar configuración ===")
    ok = save_whatsapp_config("+505 77326738", "", "", "¡Hola! Bienvenidos a Taller CR.")
    print("Guardar config:", ok)
    assert ok is True
    
    print("\n[EXITO] TODAS LAS PRUEBAS DEL MODULO DE WHATSAPP PASARON EXITOSAMENTE!")

if __name__ == '__main__':
    test_module()

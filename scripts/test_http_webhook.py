import requests

r1 = requests.get('http://127.0.0.1:5000/login')
print("Login status:", r1.status_code)

r2 = requests.get('http://127.0.0.1:5000/atencion/whatsapp/webhook?hub.mode=subscribe&hub.verify_token=taller_cr_whatsapp_token_2026&hub.challenge=12345')
print("Webhook verify status:", r2.status_code, "Respuesta:", r2.text)

r3 = requests.post('http://127.0.0.1:5000/atencion/whatsapp/webhook', json={
    'phone': '+505 7788 9900',
    'message': 'Hola quiero cita para mañana a las 10 am cambio de aceite'
})
print("Webhook incoming message status:", r3.status_code, "Respuesta:", r3.text)

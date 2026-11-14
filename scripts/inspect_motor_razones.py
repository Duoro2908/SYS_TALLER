with open('routes/contador.py', 'r', encoding='utf-8') as f:
    text = f.read()

idx = text.find("def calcular_motor_razones_financieras")
print(text[idx:idx+800])


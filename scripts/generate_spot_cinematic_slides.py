import os
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 1376, 768
OUT_DIR = os.path.join('static', 'img', 'comercial')
os.makedirs(OUT_DIR, exist_ok=True)

def create_base_canvas(accent_color=(242, 192, 41)):
    # Base dark gradient
    arr = np.zeros((H, W, 3), dtype=np.uint8)
    for y in range(H):
        ratio = y / H
        r = int(6 + ratio * 8)
        g = int(7 + ratio * 9)
        b = int(12 + ratio * 14)
        arr[y, :] = [r, g, b]
    
    img = Image.fromarray(arr).convert('RGBA')
    
    cx, cy = W // 2, int(H * 0.45)
    
    # Ambient Spotlight
    spot_img = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    spot_draw = ImageDraw.Draw(spot_img)
    spot_draw.ellipse([cx - 520, cy - 360, cx + 520, cy + 360], fill=(accent_color[0], accent_color[1], accent_color[2], 26))
    spot_img = spot_img.filter(ImageFilter.GaussianBlur(140))
    img = Image.alpha_composite(img, spot_img)
    
    # Tech grid floor
    floor_img = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    fd = ImageDraw.Draw(floor_img)
    horizon = int(H * 0.58)
    
    for i in range(1, 15):
        y = horizon + int((H - horizon) * (i / 14)**1.8)
        alpha = int(40 * (i / 14))
        fd.line([(0, y), (W, y)], fill=(255, 255, 255, alpha), width=1)
        
    for x in range(-W, W * 2, 80):
        alpha = 24
        fd.line([(cx, horizon), (x, H)], fill=(255, 255, 255, alpha), width=1)
        
    img = Image.alpha_composite(img, floor_img)
    
    # Pedestal platform ellipse
    ped_img = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    pd = ImageDraw.Draw(ped_img)
    ped_cx, ped_cy = cx, int(H * 0.72)
    pd.ellipse([ped_cx - 440, ped_cy - 70, ped_cx + 440, ped_cy + 70], fill=(16, 20, 30, 200), outline=(accent_color[0], accent_color[1], accent_color[2], 130), width=2)
    pd.ellipse([ped_cx - 410, ped_cy - 52, ped_cx + 410, ped_cy + 52], outline=(255, 255, 255, 35), width=1)
    img = Image.alpha_composite(img, ped_img)
    
    return img

def add_hud_box(draw, x, y, w, h, title, lines, color=(242, 192, 41)):
    overlay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    od.rounded_rectangle([x, y, x + w, y + h], radius=12, fill=(10, 13, 22, 220), outline=(color[0], color[1], color[2], 160), width=1)
    
    # Corner brackets subtle
    l = 10
    od.line([(x, y), (x + l, y)], fill=color, width=2)
    od.line([(x, y), (x, y + l)], fill=color, width=2)
    od.line([(x + w, y), (x + w - l, y)], fill=color, width=2)
    od.line([(x + w, y), (x + w, y + l)], fill=color, width=2)
    od.line([(x, y + h), (x + l, y + h)], fill=color, width=2)
    od.line([(x, y + h), (x, y + h - l)], fill=color, width=2)
    od.line([(x + w, y + h), (x + w - l, y + h)], fill=color, width=2)
    od.line([(x + w, y + h), (x + w, y + h - l)], fill=color, width=2)
    
    # Text
    od.text((x + 16, y + 12), title, fill=color)
    cur_y = y + 36
    for line in lines:
        od.text((x + 16, cur_y), line, fill=(255, 255, 255, 235))
        cur_y += 19
    return overlay

# ==========================================
# SLIDE 0: UBICACIÓN PRINCIPAL + GOOGLE MAPS
# ==========================================
print("Generating Slide 0: Ubicación...")
canvas0 = create_base_canvas(accent_color=(66, 133, 244))

# Background GPS Street Network
gps_img = Image.new('RGBA', (W, H), (0, 0, 0, 0))
gd = ImageDraw.Draw(gps_img)

# Main Roads simulating San Judas / Managua arterial grid
roads = [
    [(120, 180), (1250, 260)],
    [(180, 640), (1220, 480)],
    [(420, 60), (350, 710)],
    [(860, 70), (790, 710)],
    [(220, 390), (1180, 395)] # Calle principal San Judas
]
for road in roads:
    gd.line(road, fill=(35, 55, 85, 140), width=8)
    gd.line(road, fill=(66, 133, 244, 180), width=3)
    gd.line(road, fill=(242, 192, 41, 100), width=1)

# Secondary streets
np.random.seed(42)
for _ in range(40):
    x1 = np.random.randint(60, W - 60)
    y1 = np.random.randint(60, H - 60)
    length = np.random.randint(120, 380)
    angle = np.random.choice([0, 90, 45, 135]) * np.pi / 180
    x2 = int(x1 + length * np.cos(angle))
    y2 = int(y1 + length * np.sin(angle))
    gd.line([(x1, y1), (x2, y2)], fill=(30, 42, 60, 90), width=2)

canvas0 = Image.alpha_composite(canvas0, gps_img)

# Illuminated Location Pin & Radar Pulse
pin_x, pin_y = W // 2, int(H * 0.38)
pin_img = Image.new('RGBA', (W, H), (0, 0, 0, 0))
pind = ImageDraw.Draw(pin_img)

# Pulse waves
for r in [200, 140, 85, 45]:
    pind.ellipse([pin_x - r, pin_y + 110 - r//2, pin_x + r, pin_y + 110 + r//2], outline=(239, 68, 68, int(190 * (1 - r/230))), width=2)

# Red Google Maps style Pin
p_w, p_h = 36, 54
pind.polygon([
    (pin_x, pin_y + 105),
    (pin_x - p_w, pin_y + 54),
    (pin_x - p_w, pin_y),
    (pin_x + p_w, pin_y),
    (pin_x + p_w, pin_y + 54)
], fill=(234, 67, 53, 240), outline=(255, 255, 255, 250), width=2)
pind.ellipse([pin_x - 14, pin_y + 12, pin_x + 14, pin_y + 40], fill=(255, 255, 255, 255))

canvas0 = Image.alpha_composite(canvas0, pin_img)

# HUD Panels (Left: Address / Google Maps; Right: Hours & Contact)
hud1 = add_hud_box(None, 80, 160, 350, 155, "GOOGLE MAPS • UBICACION OFICIAL", [
    "SEDE PRINCIPAL TALLER CR:",
    "San Judas, del Ceibo",
    "2 1/2 cuadras arriba",
    "Managua, Nicaragua",
    "Toca para abrir en Google Maps"
], color=(66, 133, 244))
canvas0 = Image.alpha_composite(canvas0, hud1)

hud2 = add_hud_box(None, W - 430, 160, 350, 155, "HORARIO Y ATENCION", [
    "HORARIO DE SERVICIO:",
    "Lunes a Sabado: 8:00 AM - 5:00 PM",
    "Domingo: Cerrado",
    "LINEA OFICIAL: +505 7732 6738",
    "Sede Operativa en Tiempo Real"
], color=(34, 197, 94))
canvas0 = Image.alpha_composite(canvas0, hud2)

canvas0.convert('RGB').save(os.path.join(OUT_DIR, 'slide_0_ubicacion.jpg'), quality=94)
print("Slide 0 saved.")

# ==========================================
# SLIDE 1: GENESIS KA 150 - DIAGNOSTICO COMPUTARIZADO
# ==========================================
print("Generating Slide 1: KA 150...")
canvas1 = create_base_canvas(accent_color=(10, 132, 255))

if os.path.exists('static/img/comercial/genesis_ka150_isolated.png'):
    ka_img = Image.open('static/img/comercial/genesis_ka150_isolated.png').convert('RGBA')
    target_w = int(W * 0.58)
    aspect = ka_img.height / ka_img.width
    target_h = int(target_w * aspect)
    ka_img = ka_img.resize((target_w, target_h), Image.Resampling.LANCZOS)
    
    pos_x = (W - target_w) // 2 + 30
    pos_y = int(H * 0.72) - target_h + 30
    
    # Shadow under bike
    shadow = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.ellipse([pos_x + 60, pos_y + target_h - 40, pos_x + target_w - 60, pos_y + target_h + 20], fill=(0, 0, 0, 230))
    shadow = shadow.filter(ImageFilter.GaussianBlur(25))
    canvas1 = Image.alpha_composite(canvas1, shadow)
    
    # Paste clean bike
    canvas1.paste(ka_img, (pos_x, pos_y), ka_img)

# HUD Badges
hud_ka1 = add_hud_box(None, 70, 150, 320, 135, "MODELO: GENESIS KA 150", [
    "MOTOR: 150cc 4 Tiempos",
    "LINEA: Naked Urbana Sport",
    "SISTEMA: Diagnostico OBD-II",
    "TEST BANCO: 100% Calibrado"
], color=(10, 132, 255))
canvas1 = Image.alpha_composite(canvas1, hud_ka1)

hud_ka2 = add_hud_box(None, W - 390, 150, 320, 135, "TELEMETRIA DE TALLER", [
    "INYECCION / CARBURACION: OK",
    "PRESION DE COMPRESION: 150 PSI",
    "SISTEMA ELECTRICO: 14.2V",
    "FRENOS HIDRAULICOS: PURGADOS"
], color=(34, 197, 94))
canvas1 = Image.alpha_composite(canvas1, hud_ka2)

canvas1.convert('RGB').save(os.path.join(OUT_DIR, 'slide_1_ka150_diagnostico.jpg'), quality=94)
print("Slide 1 saved.")

# ==========================================
# SLIDE 2: LUBRICACION MOTUL & MANTENIMIENTO
# ==========================================
print("Generating Slide 2: Motul...")
if os.path.exists('static/img/comercial/genesis_motul_service.jpg'):
    canvas2 = Image.open('static/img/comercial/genesis_motul_service.jpg').convert('RGBA').resize((W, H))
else:
    canvas2 = create_base_canvas(accent_color=(239, 68, 68))

hud_motul = add_hud_box(None, 70, 150, 350, 145, "LUBRICACION OFICIAL MOTUL", [
    "MOTUL 7100: 100% Sintetico Ester",
    "MOTUL 5100: Technosynthese 4T",
    "MOTUL 3100: Multigrado Mineral",
    "NORMA JASO MA2 / API SN",
    "Proteccion Termica Extrema"
], color=(239, 68, 68))
canvas2 = Image.alpha_composite(canvas2, hud_motul)

canvas2.convert('RGB').save(os.path.join(OUT_DIR, 'slide_2_motul_lubricacion.jpg'), quality=94)
print("Slide 2 saved.")

# ==========================================
# SLIDE 3: GENESIS SX1 150 - DUAL-SPORT & REPUESTOS
# ==========================================
print("Generating Slide 3: SX1 150...")
canvas3 = create_base_canvas(accent_color=(239, 68, 68))

if os.path.exists('static/img/comercial/genesis_sx1_isolated.png'):
    sx_img = Image.open('static/img/comercial/genesis_sx1_isolated.png').convert('RGBA')
    target_w = int(W * 0.58)
    aspect = sx_img.height / sx_img.width
    target_h = int(target_w * aspect)
    sx_img = sx_img.resize((target_w, target_h), Image.Resampling.LANCZOS)
    
    pos_x = (W - target_w) // 2 + 20
    pos_y = int(H * 0.72) - target_h + 30
    
    # Shadow
    shadow = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.ellipse([pos_x + 50, pos_y + target_h - 40, pos_x + target_w - 50, pos_y + target_h + 20], fill=(0, 0, 0, 230))
    shadow = shadow.filter(ImageFilter.GaussianBlur(25))
    canvas3 = Image.alpha_composite(canvas3, shadow)
    
    # Paste clean SX1
    canvas3.paste(sx_img, (pos_x, pos_y), sx_img)

hud_sx1 = add_hud_box(None, 70, 150, 330, 140, "MODELO: GENESIS SX1 150", [
    "CATEGORIA: Enduro Dual-Sport",
    "SUSPENSION: Monoshock Trasero",
    "LLANTAS: Tacos Off-Road 21/18",
    "SISTEMA DE ARRASTRE: 428H Heavy"
], color=(239, 68, 68))
canvas3 = Image.alpha_composite(canvas3, hud_sx1)

hud_sx2 = add_hud_box(None, W - 390, 150, 320, 140, "REPUESTOS GENUINOS GENESIS", [
    "FILTROS DE AIRE SX1 / SX2 / SX3",
    "PASTILLAS DE FRENO CERAMICAS",
    "CHISPEROS NGK / CHAMPION",
    "GARANTIA TOTAL DE INSTALACION"
], color=(242, 192, 41))
canvas3 = Image.alpha_composite(canvas3, hud_sx2)

canvas3.convert('RGB').save(os.path.join(OUT_DIR, 'slide_3_sx1_repuestos.jpg'), quality=94)
print("Slide 3 saved.")

# ==========================================
# SLIDE 4: GRAN RIFA MENSUAL
# ==========================================
print("Generating Slide 4: Rifa...")
if os.path.exists('static/img/comercial/promo_rifa.jpg'):
    canvas4 = Image.open('static/img/comercial/promo_rifa.jpg').convert('RGBA').resize((W, H))
else:
    canvas4 = create_base_canvas(accent_color=(242, 192, 41))

hud_rifa = add_hud_box(None, W - 430, 140, 360, 155, "GRAN RIFA MENSUAL TALLER CR", [
    "PREMIOS EXTRAORDINARIOS:",
    "- Cascos Certificados DOT / ECE",
    "- Juegos de Llantas para Motos",
    "- Cambios de Aceite Motul Gratis",
    "Boleto automatico c/ C$ 1,000"
], color=(242, 192, 41))
canvas4 = Image.alpha_composite(canvas4, hud_rifa)

canvas4.convert('RGB').save(os.path.join(OUT_DIR, 'slide_4_gran_rifa.jpg'), quality=94)
print("Slide 4 saved.")

print("All 5 cinematic slides generated successfully!")

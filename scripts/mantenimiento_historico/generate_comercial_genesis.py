import sys
import os
import shutil
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import imageio

def generate_video():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    static_dir = os.path.join(base_dir, 'static')
    comercial_dir = os.path.join(static_dir, 'img', 'comercial')
    video_dir = os.path.join(static_dir, 'video')
    os.makedirs(comercial_dir, exist_ok=True)
    os.makedirs(video_dir, exist_ok=True)

    brain_dir = r"C:\Users\Alexander\.gemini\antigravity-ide\brain\63f81826-8db1-43ef-8c44-cb8960ee7697"

    # Buscar las imágenes exactas de motos genesis y promo
    genesis1 = None
    genesis2 = None
    promo_img = None
    original_bg = os.path.join(static_dir, 'img', 'bg_login_premium.png')

    for f in os.listdir(brain_dir):
        if f.startswith('moto_genesis_taller') and f.endswith('.jpg'):
            genesis1 = os.path.join(brain_dir, f)
        elif f.startswith('moto_genesis_service') and f.endswith('.jpg'):
            genesis2 = os.path.join(brain_dir, f)
        elif f.startswith('promo_rifa_spot') and f.endswith('.jpg'):
            promo_img = os.path.join(brain_dir, f)

    # Copiar a static/img/comercial
    if genesis1:
        shutil.copy(genesis1, os.path.join(comercial_dir, 'genesis_taller.jpg'))
    if genesis2:
        shutil.copy(genesis2, os.path.join(comercial_dir, 'genesis_service.jpg'))
    if os.path.exists(original_bg):
        shutil.copy(original_bg, os.path.join(comercial_dir, 'genesis_original.png'))
    if promo_img:
        shutil.copy(promo_img, os.path.join(comercial_dir, 'promo_rifa.jpg'))

    print("Imágenes copiadas a static/img/comercial/")

    # Generar MP4 de 20 segundos exactos (Banpro Style comercial breve de 20 segundos)
    # 4 escenas x 5 segundos cada una = 20 segundos
    target_w, target_h = 640, 360 # Resolución óptima para carga instantánea en login
    fps = 15 # 15 fps * 20 seg = 300 frames, super rápido de renderizar (< 5 segs)

    scenes = [
        {
            'file': os.path.join(comercial_dir, 'genesis_taller.jpg'),
            'dur': 5.0,
            'tag': 'TALLER Y LUBRICANTES CR',
            'title': 'ESPECIALISTAS EN MOTOS GÉNESIS',
            'sub': 'Mantenimiento preventivo, diagnóstico y repuestos de alta gama'
        },
        {
            'file': os.path.join(comercial_dir, 'genesis_service.jpg'),
            'dur': 5.0,
            'tag': 'LUBRICANTES Y MANTENIMIENTO',
            'title': 'MÁXIMO RENDIMIENTO PARA TU MOTOR',
            'sub': 'Aceites 100% sintéticos y servicio técnico certificado'
        },
        {
            'file': os.path.join(comercial_dir, 'genesis_original.png') if os.path.exists(os.path.join(comercial_dir, 'genesis_original.png')) else os.path.join(comercial_dir, 'genesis_taller.jpg'),
            'dur': 4.0,
            'tag': 'GARANTÍA Y CONFIANZA',
            'title': 'TECNOLOGÍA Y EFICIENCIA EN CADA SERVICIO',
            'sub': 'Tu moto Génesis en las mejores manos expertas'
        },
        {
            'file': os.path.join(comercial_dir, 'promo_rifa.jpg'),
            'dur': 6.0,
            'tag': '¡PROMOCIÓN EXCLUSIVA DEL MES!',
            'title': 'GRAN RIFA MENSUAL TALLER CR',
            'sub': 'Por cada C$ 1,000 en compras acumulas un boleto para la rifa'
        }
    ]

    video_path = os.path.join(video_dir, 'comercial_taller.mp4')
    writer = imageio.get_writer(video_path, fps=fps, codec='libx264', quality=8)

    def process_frame(img, tag, title, sub, prog):
        w, h = img.size
        overlay = Image.new('RGBA', (w, h), (0, 0, 0, 0))
        d = ImageDraw.Draw(overlay)

        # Gradiente inferior
        for y in range(h - 90, h):
            alpha = int(230 * ((y - (h - 90)) / 90))
            d.line([(0, y), (w, y)], fill=(0, 0, 0, alpha))

        # Barra superior TV Commercial
        d.rectangle([(0, 0), (w, 26)], fill=(15, 15, 20, 210))
        img = Image.alpha_composite(img.convert('RGBA'), overlay)
        d = ImageDraw.Draw(img)

        # Distintivo superior
        d.rectangle([(10, 6), (18, 20)], fill=(242, 192, 41, 255))
        d.text((24, 6), tag, fill=(255, 255, 255))
        d.text((w - 75, 6), "SPOT 20s", fill=(52, 199, 89))

        # Textos promocionales
        d.text((16, h - 75), title, fill=(242, 192, 41))
        d.text((16, h - 45), sub, fill=(255, 255, 255))

        # Barra de progreso Banpro
        d.rectangle([(0, h - 4), (int(w * prog), h)], fill=(242, 192, 41))
        return img.convert('RGB')

    total_dur = sum(s['dur'] for s in scenes)
    elapsed = 0.0

    for scene in scenes:
        if not os.path.exists(scene['file']):
            continue
        src_img = Image.open(scene['file']).convert('RGB')
        num_f = int(scene['dur'] * fps)
        for i in range(num_f):
            t = i / float(num_f)
            scale = 1.0 + (0.04 * t)
            cw, ch = int(src_img.width / scale), int(src_img.height / scale)
            cx, cy = (src_img.width - cw) // 2, (src_img.height - ch) // 2
            cropped = src_img.crop((cx, cy, cx + cw, cy + ch))
            resized = cropped.resize((target_w, target_h), Image.Resampling.LANCZOS)
            
            prog = (elapsed + (i / float(fps))) / total_dur
            frame = process_frame(resized, scene['tag'], scene['title'], scene['sub'], prog)
            writer.append_data(np.array(frame))

        elapsed += scene['dur']

    writer.close()
    print("Video comercial de 20 segundos generado exitosamente en:", video_path)

if __name__ == '__main__':
    generate_video()

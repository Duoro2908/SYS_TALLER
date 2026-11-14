import sys
import os
import shutil
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np
import imageio

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def create_commercial():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    video_dir = os.path.join(base_dir, 'static', 'video')
    img_comercial_dir = os.path.join(base_dir, 'static', 'img', 'comercial')
    os.makedirs(video_dir, exist_ok=True)
    os.makedirs(img_comercial_dir, exist_ok=True)

    # Rutas de las imágenes generadas en el brain
    brain_dir = r"C:\Users\Alexander\.gemini\antigravity-ide\brain\63f81826-8db1-43ef-8c44-cb8960ee7697"
    
    # Encontrar las imágenes por prefijo
    images_map = {
        'mecanica': None,
        'lubricantes': None,
        'atencion': None,
        'promo': None
    }
    
    for f in os.listdir(brain_dir):
        if f.startswith('taller_mecanica_spot') and f.endswith('.jpg'):
            images_map['mecanica'] = os.path.join(brain_dir, f)
        elif f.startswith('lubricantes_repuestos_spot') and f.endswith('.jpg'):
            images_map['lubricantes'] = os.path.join(brain_dir, f)
        elif f.startswith('cliente_atencion_spot') and f.endswith('.jpg'):
            images_map['atencion'] = os.path.join(brain_dir, f)
        elif f.startswith('promo_rifa_spot') and f.endswith('.jpg'):
            images_map['promo'] = os.path.join(brain_dir, f)

    print("Imágenes encontradas:", images_map)

    # Copiar a static/img/comercial
    for key, path in images_map.items():
        if path and os.path.exists(path):
            dest = os.path.join(img_comercial_dir, f"{key}.jpg")
            shutil.copy(path, dest)
            print(f"Copiada {key} a {dest}")

    # Configuración de video
    target_w, target_h = 854, 480 # 480p panorámico óptimo para web y peso ligero
    fps = 20
    
    scenes = [
        {
            'path': os.path.join(img_comercial_dir, 'mecanica.jpg'),
            'duration_sec': 3.5,
            'title': "TALLER Y LUBRICANTES CR",
            'subtitle': "Mecánica Especializada • Mantenimiento Preventivo y General"
        },
        {
            'path': os.path.join(img_comercial_dir, 'lubricantes.jpg'),
            'duration_sec': 3.5,
            'title': "REPUESTOS Y LUBRICANTES 100% GENUINOS",
            'subtitle': "Aceites Sintéticos • Baterías • Frenos • Bujías • Llantas"
        },
        {
            'path': os.path.join(img_comercial_dir, 'atencion.jpg'),
            'duration_sec': 3.5,
            'title': "SERVICIO PREMIUM GARANTIZADO",
            'subtitle': "Atención Personalizada • Máxima Confianza y Seguridad"
        },
        {
            'path': os.path.join(img_comercial_dir, 'promo.jpg'),
            'duration_sec': 5.0,
            'title': "¡GRAN RIFA MENSUAL TALLER CR!",
            'subtitle': "Por cada C$ 1,000 de compra en el mes acumulas 1 boleto ¡PARTICIPA Y GANA!"
        }
    ]

    output_video_path = os.path.join(video_dir, 'comercial_taller.mp4')
    writer = imageio.get_writer(output_video_path, fps=fps, codec='libx264', quality=8)

    print("Generando video comercial...")

    def draw_overlays(img_pil, title, subtitle, progress_ratio=0.0):
        draw = ImageDraw.Draw(img_pil, 'RGBA')
        w, h = img_pil.size

        # Degradado inferior para legibilidad del texto
        overlay = Image.new('RGBA', (w, h), (0, 0, 0, 0))
        d_overlay = ImageDraw.Draw(overlay)
        for y in range(h - 130, h):
            alpha = int(220 * ((y - (h - 130)) / 130))
            d_overlay.line([(0, y), (w, y)], fill=(5, 5, 10, alpha))
            
        # Barra superior con distintivo "COMERCIAL OFICIAL TALLER CR"
        d_overlay.rectangle([(0, 0), (w, 38)], fill=(10, 10, 15, 200))
        img_pil = Image.alpha_composite(img_pil.convert('RGBA'), overlay)
        draw = ImageDraw.Draw(img_pil)

        # Distintivo superior
        draw.rectangle([(16, 8), (28, 26)], fill=(242, 192, 41, 255)) # Badge amarillo dorado
        draw.text((36, 11), "TALLER Y LUBRICANTES CR  •  COMERCIAL OFICIAL 2026", fill=(255, 255, 255))
        draw.text((w - 120, 11), "EN EMISIÓN", fill=(52, 199, 89))

        # Textos inferiores promocionales
        draw.text((24, h - 100), title, fill=(242, 192, 41)) # Dorado corporativo
        draw.text((24, h - 65), subtitle, fill=(255, 255, 255))

        # Barra de progreso inferior animada (estilo TV)
        bar_w = int(w * progress_ratio)
        draw.rectangle([(0, h - 6), (bar_w, h)], fill=(242, 192, 41))

        return img_pil.convert('RGB')

    total_scenes = len(scenes)
    total_frames = 0

    for s_idx, scene in enumerate(scenes):
        base_img = Image.open(scene['path']).convert('RGB')
        num_frames = int(scene['duration_sec'] * fps)
        
        # Efecto Ken Burns (ligero zoom in)
        for f in range(num_frames):
            t = f / float(num_frames)
            scale = 1.0 + (0.06 * t) # Zoom de 1.00 a 1.06
            
            crop_w = int(base_img.width / scale)
            crop_h = int(base_img.height / scale)
            crop_x = (base_img.width - crop_w) // 2
            crop_y = (base_img.height - crop_h) // 2
            
            cropped = base_img.crop((crop_x, crop_y, crop_x + crop_w, crop_y + crop_h))
            frame_resized = cropped.resize((target_w, target_h), Image.Resampling.LANCZOS)

            # Transición de entrada (fade in al inicio del video y entre escenas)
            if s_idx == 0 and f < 10:
                alpha = f / 10.0
                frame_resized = Image.blend(Image.new('RGB', (target_w, target_h), (0, 0, 0)), frame_resized, alpha)

            prog = (s_idx + t) / float(total_scenes)
            final_frame = draw_overlays(frame_resized, scene['title'], scene['subtitle'], prog)
            
            writer.append_data(np.array(final_frame))
            total_frames += 1

    writer.close()
    file_size_kb = os.path.getsize(output_video_path) / 1024
    print(f"Video generado con éxito: {output_video_path} ({total_frames} frames, {file_size_kb:.1f} KB)")

if __name__ == '__main__':
    create_commercial()

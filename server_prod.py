import sys
import os
from waitress import serve
from app import app

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print("=" * 60)
    print(f"  TALLER Y LUBRICANTES CR - SERVIDOR DE PRODUCCION WAITRESS")
    print(f"  Escuchando en http://0.0.0.0:{port} (8 Hilos concurrentes)")
    print("=" * 60)
    sys.stdout.flush()
    serve(app, host='0.0.0.0', port=port, threads=8, channel_timeout=120)

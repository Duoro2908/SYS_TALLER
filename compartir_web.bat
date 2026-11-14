@echo off
chcp 65001 >nul
title Taller y Lubricantes CR - Servidor en Línea
echo ===================================================
echo   TALLER Y LUBRICANTES CR - ACCESO PÚBLICO EN LÍNEA
echo ===================================================
echo.
echo 1. Iniciando Servidor de Producción Multihilo (Waitress)...
start /b python server_prod.py > server_waitress.log 2>&1
timeout /t 2 >nul
echo.
echo 2. Iniciando Mantenedor de Conexión (Keep-Alive)...
start /b python tunnel_keepalive.py >nul 2>&1
echo.
echo 3. Iniciando Túnel Seguro HTTPS con Cloudflare...
echo Una vez iniciado, copia el enlace https://...trycloudflare.com
echo para compartirlo con tus compañeros o profesor.
echo.
"C:\Program Files (x86)\cloudflared\cloudflared.exe" tunnel --protocol http2 --url http://127.0.0.1:5000
pause

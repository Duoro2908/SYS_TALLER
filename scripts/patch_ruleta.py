import re

def patch_ruleta():
    filepath = 'templates/mercadotecnia/participantes.html'
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Add CSS for Ruleta in style section
    old_css_target = """.ruleta-spinner-box {
        margin: 25px auto;
        width: 100%;
        height: 120px;
        background: rgba(0, 0, 0, 0.4);
        border: 2px dashed #f2c029;
        border-radius: 16px;
        display: flex;
        justify-content: center;
        align-items: center;
        font-size: 1.5rem;
        font-weight: 700;
        color: #f2c029;
        overflow: hidden;
        position: relative;
    }"""

    new_css = """.ruleta-container {
        position: relative;
        width: 340px;
        height: 340px;
        margin: 20px auto 15px auto;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .ruleta-bezel {
        position: absolute;
        inset: -10px;
        border-radius: 50%;
        background: radial-gradient(circle, #2d1804 60%, #854d0e 95%, #eab308 100%);
        box-shadow: 0 0 35px rgba(234, 179, 8, 0.4), inset 0 0 15px rgba(0,0,0,0.8);
        border: 4px solid #facc15;
        z-index: 1;
    }
    .ruleta-canvas {
        position: relative;
        z-index: 2;
        border-radius: 50%;
        box-shadow: inset 0 0 18px rgba(0,0,0,0.6);
    }
    .ruleta-pointer {
        position: absolute;
        top: -18px;
        left: 50%;
        transform: translateX(-50%);
        width: 0;
        height: 0;
        border-left: 16px solid transparent;
        border-right: 16px solid transparent;
        border-top: 32px solid #ef4444;
        filter: drop-shadow(0 4px 8px rgba(0,0,0,0.65));
        z-index: 10;
        transition: transform 0.08s ease;
    }
    .ruleta-pointer::after {
        content: '';
        position: absolute;
        top: -32px;
        left: -8px;
        width: 16px;
        height: 16px;
        border-radius: 50%;
        background: #facc15;
        box-shadow: 0 0 8px #facc15;
    }
    .ruleta-center-pin {
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        width: 58px;
        height: 58px;
        border-radius: 50%;
        background: radial-gradient(circle, #facc15 0%, #ca8a04 70%, #854d0e 100%);
        border: 3px solid #fef08a;
        box-shadow: 0 4px 15px rgba(0,0,0,0.7), 0 0 12px rgba(250, 204, 21, 0.6);
        z-index: 5;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #713f12;
        font-weight: 900;
        font-size: 1.1rem;
        cursor: pointer;
        user-select: none;
    }
    .ruleta-ticker {
        font-size: 0.92rem;
        color: #fbbf24;
        margin-top: 8px;
        font-weight: 700;
        min-height: 24px;
    }
    .confetti-canvas {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        pointer-events: none;
        z-index: 20;
    }"""

    content = content.replace(old_css_target, new_css)

    # 2. Update Light theme for ruleta
    old_light_css = """    [data-theme="light"] .ruleta-spinner-box {
        background: #f8fafc !important;
        border: 2px dashed #d97706 !important;
        color: #b45309 !important;
        box-shadow: inset 0 2px 6px rgba(0, 0, 0, 0.04) !important;
    }"""
    new_light_css = """    [data-theme="light"] .ruleta-bezel {
        background: radial-gradient(circle, #fffbeb 60%, #fde68a 95%, #f59e0b 100%) !important;
        border: 4px solid #d97706 !important;
        box-shadow: 0 0 25px rgba(217, 119, 6, 0.25) !important;
    }
    [data-theme="light"] .ruleta-ticker {
        color: #b45309 !important;
    }"""
    content = content.replace(old_light_css, new_light_css)

    # 3. Update Modal HTML: Replace spinnerBox with ruleta-container
    old_html = """        <div id="spinnerBox" class="ruleta-spinner-box">
            <span>Presiona 'Iniciar Sorteo'</span>
        </div>

        <button id="btnSpin" class="btn-sorteo-modal" style="font-size: 1.1rem; padding: 12px 30px; margin: 10px 0;" onclick="ejecutarSorteo()">
            <i class="fa-solid fa-play"></i> Iniciar Sorteo Aleatorio
        </button>"""

    new_html = """        <!-- Ruleta Visual Interactiva -->
        <div class="ruleta-container" id="ruletaWrap">
            <canvas id="confettiCanvas" class="confetti-canvas"></canvas>
            <div class="ruleta-bezel"></div>
            <div class="ruleta-pointer" id="ruletaPointer"></div>
            <canvas id="ruletaCanvas" class="ruleta-canvas" width="340" height="340"></canvas>
            <div class="ruleta-center-pin" onclick="ejecutarSorteo()" title="Girar Ruleta">
                <i class="fa-solid fa-trophy" style="font-size: 1.3rem;"></i>
            </div>
        </div>

        <div id="ruletaTicker" class="ruleta-ticker">
            <i class="fa-solid fa-sparkles"></i> ¡Presiona el botón para girar la Ruleta de la Suerte!
        </div>

        <button id="btnSpin" class="btn-sorteo-modal" style="font-size: 1.15rem; padding: 13px 34px; margin: 12px 0; font-weight: 800; letter-spacing: 0.5px; box-shadow: 0 6px 20px rgba(16, 185, 129, 0.35);" onclick="ejecutarSorteo()">
            <i class="fa-solid fa-rotate"></i> ¡Girar Ruleta de la Suerte!
        </button>"""

    content = content.replace(old_html, new_html)

    # 4. Replace script functions abrirSorteoModal and ejecutarSorteo
    old_script_start = "    function abrirSorteoModal() {"
    idx = content.find(old_script_start)
    if idx != -1:
        script_code = """    // --- Ruleta de la Suerte Engine ---
    let ruletaAngle = 0;
    let isSpinning = false;
    let audioCtx = null;

    const ruletaColors = [
        '#2563eb', '#10b981', '#f59e0b', '#dc2626', '#8b5cf6', 
        '#06b6d4', '#ec4899', '#14b8a6', '#d97706', '#6366f1',
        '#059669', '#ea580c', '#4f46e5', '#0284c7', '#7c3aed'
    ];

    function playTickSound() {
        try {
            if (!audioCtx) audioCtx = new (window.AudioContext || window.webkitAudioContext)();
            const osc = audioCtx.createOscillator();
            const gain = audioCtx.createGain();
            osc.type = 'triangle';
            osc.frequency.setValueAtTime(580, audioCtx.currentTime);
            osc.frequency.exponentialRampToValueAtTime(120, audioCtx.currentTime + 0.04);
            gain.gain.setValueAtTime(0.12, audioCtx.currentTime);
            gain.gain.linearRampToValueAtTime(0.001, audioCtx.currentTime + 0.04);
            osc.connect(gain);
            gain.connect(audioCtx.destination);
            osc.start();
            osc.stop(audioCtx.currentTime + 0.04);
        } catch(e) {}
    }

    function playWinFanfare() {
        try {
            if (!audioCtx) audioCtx = new (window.AudioContext || window.webkitAudioContext)();
            const notes = [440, 554, 659, 880];
            notes.forEach((freq, i) => {
                const osc = audioCtx.createOscillator();
                const gain = audioCtx.createGain();
                osc.type = 'sine';
                osc.frequency.setValueAtTime(freq, audioCtx.currentTime + i * 0.12);
                gain.gain.setValueAtTime(0.2, audioCtx.currentTime + i * 0.12);
                gain.gain.linearRampToValueAtTime(0.001, audioCtx.currentTime + i * 0.12 + 0.35);
                osc.connect(gain);
                gain.connect(audioCtx.destination);
                osc.start(audioCtx.currentTime + i * 0.12);
                osc.stop(audioCtx.currentTime + i * 0.12 + 0.35);
            });
        } catch(e) {}
    }

    function dibujarRuleta(angle = 0) {
        const canvas = document.getElementById('ruletaCanvas');
        if (!canvas) return;
        const ctx = canvas.getContext('2d');
        const W = canvas.width;
        const H = canvas.height;
        const cx = W / 2;
        const cy = H / 2;
        const R = (W / 2) - 8;

        ctx.clearRect(0, 0, W, H);

        const items = (participantesData && participantesData.length > 0) 
            ? participantesData 
            : [{ nombre: 'Sin Participantes', boletos: 1 }];

        const totalSlices = items.length;
        const arc = (2 * Math.PI) / totalSlices;

        ctx.save();
        ctx.translate(cx, cy);
        ctx.rotate(angle);

        for (let i = 0; i < totalSlices; i++) {
            const startAngle = i * arc;
            const endAngle = startAngle + arc;
            const color = ruletaColors[i % ruletaColors.length];

            // Slice arc
            ctx.beginPath();
            ctx.moveTo(0, 0);
            ctx.arc(0, 0, R, startAngle, endAngle);
            ctx.fillStyle = color;
            ctx.fill();

            // Border
            ctx.strokeStyle = '#ffffff';
            ctx.lineWidth = 2.5;
            ctx.stroke();

            // Text
            ctx.save();
            ctx.rotate(startAngle + arc / 2);
            ctx.textAlign = 'right';
            ctx.fillStyle = '#ffffff';
            ctx.font = totalSlices > 10 ? 'bold 10px Inter, sans-serif' : 'bold 12px Inter, sans-serif';
            ctx.shadowColor = 'rgba(0,0,0,0.6)';
            ctx.shadowBlur = 4;
            
            let label = items[i].nombre || 'Cliente';
            if (label.length > 14) label = label.substring(0, 12) + '..';
            ctx.fillText(label, R - 20, 4);

            // Perimeter pin
            ctx.beginPath();
            ctx.arc(R - 6, 0, 3, 0, 2 * Math.PI);
            ctx.fillStyle = '#fef08a';
            ctx.fill();

            ctx.restore();
        }

        ctx.restore();
    }

    function dispararConfetti() {
        const canvas = document.getElementById('confettiCanvas');
        if (!canvas) return;
        const parent = document.getElementById('ruletaWrap');
        canvas.width = parent.clientWidth;
        canvas.height = parent.clientHeight;
        const ctx = canvas.getContext('2d');
        const particles = [];
        const colors = ['#f59e0b', '#10b981', '#3b82f6', '#ec4899', '#8b5cf6', '#ef4444', '#facc15'];

        for (let i = 0; i < 70; i++) {
            particles.push({
                x: canvas.width / 2,
                y: canvas.height / 2,
                vx: (Math.random() - 0.5) * 14,
                vy: (Math.random() - 0.5) * 14 - 3,
                size: Math.random() * 7 + 4,
                color: colors[Math.floor(Math.random() * colors.length)],
                alpha: 1,
                rot: Math.random() * 360,
                vrot: (Math.random() - 0.5) * 12
            });
        }

        let frame = 0;
        function anim() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            particles.forEach(p => {
                p.x += p.vx;
                p.y += p.vy;
                p.vy += 0.25; // gravity
                p.alpha -= 0.015;
                p.rot += p.vrot;

                if (p.alpha > 0) {
                    ctx.save();
                    ctx.globalAlpha = Math.max(0, p.alpha);
                    ctx.translate(p.x, p.y);
                    ctx.rotate((p.rot * Math.PI) / 180);
                    ctx.fillStyle = p.color;
                    ctx.fillRect(-p.size / 2, -p.size / 2, p.size, p.size);
                    ctx.restore();
                }
            });
            frame++;
            if (frame < 80) requestAnimationFrame(anim);
            else ctx.clearRect(0, 0, canvas.width, canvas.height);
        }
        anim();
    }

    function abrirSorteoModal() {
        document.getElementById('modalSorteo').style.display = 'flex';
        document.getElementById('winnerBanner').style.display = 'none';
        const btn = document.getElementById('btnSpin');
        btn.style.display = 'inline-flex';
        btn.disabled = false;
        btn.style.opacity = '1';
        document.getElementById('ruletaTicker').innerHTML = '<i class=\"fa-solid fa-sparkles\"></i> ¡Presiona el botón para girar la Ruleta de la Suerte!';
        dibujarRuleta(ruletaAngle);
    }

    function cerrarSorteoModal() {
        document.getElementById('modalSorteo').style.display = 'none';
    }

    function ejecutarSorteo() {
        if (isSpinning) return;
        if (!participantesData || participantesData.length === 0) {
            alert('No hay participantes registrados para la rifa.');
            return;
        }

        const btn = document.getElementById('btnSpin');
        btn.disabled = true;
        btn.style.opacity = '0.5';
        isSpinning = true;

        // Construir candidatos ponderados por boletos
        let candidatos = [];
        participantesData.forEach(p => {
            const b = Math.max(1, p.boletos || 1);
            for (let i = 0; i < b; i++) candidatos.push(p);
        });

        // Seleccionar ganador
        const finalWinner = candidatos[Math.floor(Math.random() * candidatos.length)];
        const winnerIndex = participantesData.findIndex(p => p.cliente_id === finalWinner.cliente_id);
        const totalSlices = participantesData.length;
        const sliceArc = (2 * Math.PI) / totalSlices;

        // El puntero está arriba (-PI/2). El ángulo del centro del slice ganador relativo al puntero
        // targetAngle = -PI/2 - (winnerIndex * sliceArc + sliceArc/2)
        const extraRotations = 6 + Math.floor(Math.random() * 4); // 6-9 giros completos
        const targetSliceAngle = (3 * Math.PI / 2) - (winnerIndex * sliceArc + sliceArc / 2);
        const finalTotalAngle = (extraRotations * 2 * Math.PI) + (targetSliceAngle % (2 * Math.PI));

        const startAngle = ruletaAngle % (2 * Math.PI);
        const totalDelta = finalTotalAngle - startAngle;
        const duration = 5200; // 5.2 segundos
        const startTime = performance.now();
        let lastTickSegment = -1;

        const ticker = document.getElementById('ruletaTicker');
        const pointer = document.getElementById('ruletaPointer');

        function easeOutCubic(t) {
            return 1 - Math.pow(1 - t, 3);
        }

        function frame(now) {
            const elapsed = now - startTime;
            const progress = Math.min(1, elapsed / duration);
            const eased = easeOutCubic(progress);

            const currentAngle = startAngle + (totalDelta * eased);
            ruletaAngle = currentAngle;
            dibujarRuleta(currentAngle);

            // Audio & tick effect
            const normalizedAngle = (currentAngle % (2 * Math.PI) + 2 * Math.PI) % (2 * Math.PI);
            const currentSegment = Math.floor(normalizedAngle / sliceArc);
            if (currentSegment !== lastTickSegment) {
                lastTickSegment = currentSegment;
                playTickSound();
                if (pointer) {
                    pointer.style.transform = 'translateX(-50%) rotate(-12deg)';
                    setTimeout(() => { if (pointer) pointer.style.transform = 'translateX(-50%) rotate(0deg)'; }, 40);
                }
            }

            if (progress < 1) {
                ticker.innerHTML = '<i class=\"fa-solid fa-spinner fa-spin\"></i> Seleccionando ganador de la rifa mensual...';
                requestAnimationFrame(frame);
            } else {
                // Detenido en el ganador
                isSpinning = false;
                playWinFanfare();
                dispararConfetti();

                ticker.innerHTML = `<span style=\"color: #10b981; font-weight: 800;\">🏆 ¡Boleto Ganador: ${finalWinner.nombre}!</span>`;
                btn.style.display = 'none';

                document.getElementById('winnerNombre').innerText = finalWinner.nombre;
                document.getElementById('winnerTel').innerText = "Contacto: " + finalWinner.telefono + " • Boletos: " + finalWinner.boletos + " • Compras: C$ " + Number(finalWinner.total_acumulado).toLocaleString('es-NI', {minimumFractionDigits: 2});
                document.getElementById('formWinnerNombre').value = finalWinner.nombre;
                document.getElementById('formWinnerTel').value = finalWinner.telefono;
                document.getElementById('formWinnerId').value = finalWinner.cliente_id;
                document.getElementById('winnerBanner').style.display = 'block';
            }
        }

        requestAnimationFrame(frame);
    }
</script>
{% endblock %}"""

        content = content[:idx] + script_code

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Ruleta patched successfully in templates/mercadotecnia/participantes.html!")

if __name__ == '__main__':
    patch_ruleta()


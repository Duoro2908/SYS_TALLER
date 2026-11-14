with open('templates/base.html', 'r', encoding='utf-8') as f:
    content = f.read()

target = """            // Funcionalidad para el menú lateral (Accordion)
            $('.module-header').click(function() {
                // Alternar la clase activa
                $(this).toggleClass('active');
                
                // Deslizar (abrir/cerrar) la lista de submenú que le sigue
                $(this).next('.submodule-list').slideToggle(250);
                
                // Opcional: Cerrar los demás menús al abrir uno (estilo acordeón estricto)
                // Si quieres que varios puedan estar abiertos, comenta las dos líneas de abajo.
                // $('.module-header').not(this).removeClass('active');
                // $('.module-header').not(this).next('.submodule-list').slideUp(250);
            });"""

replacement = """            // Funcionalidad Persistente para el Menú Lateral (Accordion que no se cierra al dar clic)
            function getOpenModules() {
                try {
                    return JSON.parse(localStorage.getItem('open_sidebar_modules')) || [];
                } catch(e) {
                    return [];
                }
            }

            function saveOpenModules(modules) {
                try {
                    localStorage.setItem('open_sidebar_modules', JSON.stringify(modules));
                } catch(e) {}
            }

            // 1. Restaurar módulos guardados en localStorage
            const savedOpen = getOpenModules();
            $('.module-header').each(function() {
                const title = $(this).find('.module-title span').text().trim();
                const $subList = $(this).next('.submodule-list');
                
                // Si está guardado o contiene la página activa o coincide con la URL actual
                const hasActive = $subList.find('a.active').length > 0 || 
                                  $subList.find('a[href="' + window.location.pathname + '"]').length > 0;
                
                if (savedOpen.includes(title) || hasActive) {
                    $(this).addClass('active');
                    $subList.show();
                    if (!savedOpen.includes(title)) {
                        savedOpen.push(title);
                        saveOpenModules(savedOpen);
                    }
                }
            });

            // 2. Manejador de clic en cabecera de módulo
            $('.module-header').click(function() {
                const title = $(this).find('.module-title span').text().trim();
                const $subList = $(this).next('.submodule-list');
                const isOpening = !$(this).hasClass('active');
                
                $(this).toggleClass('active');
                $subList.slideToggle(200);
                
                let currentOpen = getOpenModules();
                if (isOpening) {
                    if (!currentOpen.includes(title)) currentOpen.push(title);
                } else {
                    currentOpen = currentOpen.filter(t => t !== title);
                }
                saveOpenModules(currentOpen);
            });

            // 3. Al hacer clic en un enlace de submódulo, asegurar que el módulo padre permanezca guardado como abierto
            $('.submodule-list a').click(function() {
                const $parentHeader = $(this).closest('.submodule-list').prev('.module-header');
                if ($parentHeader.length) {
                    const title = $parentHeader.find('.module-title span').text().trim();
                    let currentOpen = getOpenModules();
                    if (!currentOpen.includes(title)) {
                        currentOpen.push(title);
                        saveOpenModules(currentOpen);
                    }
                }
            });"""

if target in content:
    content = content.replace(target, replacement)
    with open('templates/base.html', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Updated base.html with persistent sidebar accordion successfully")
else:
    print("Target not found in base.html")


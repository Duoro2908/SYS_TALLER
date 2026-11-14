"""
====================================================================
MÓDULO DE GERENCIA (routes/gerencia.py)
Taller y Lubricantes CR
Controlador y alias directo hacia routes/estadisticas.py.
Permite acceder a los controladores tanto por Gerencia como por Estadísticas.
====================================================================
"""

from routes.estadisticas import estadisticas_bp, gerencia_bp, obtener_estadisticas_taller, estadisticas

__all__ = ['estadisticas_bp', 'gerencia_bp', 'obtener_estadisticas_taller', 'estadisticas']

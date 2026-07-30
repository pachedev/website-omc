# -*- coding: utf-8 -*-
{
    "name": "Pachedev - Monitoreo de Instancia",
    "summary": "Endpoint de salud de la instancia para monitoreo externo (Uptime Kuma).",
    "description": """
Expone un endpoint HTTP público autenticado por API Key para monitorear la
salud de la instancia Odoo desde herramientas externas como Uptime Kuma.

Al instalarse genera automáticamente:
  * un UUID que identifica la instancia,
  * una API Key (UUID) para autenticar las peticiones al endpoint.

El acceso al menú y a la configuración requiere el grupo "Usuario de
monitoreo"; solo el grupo "Administrador de monitoreo" puede regenerar la
API Key. Los detalles del endpoint solo son visibles para administradores
del sistema.
""",
    "author": "Pachedev",
    "website": "https://pachedev.com",
    "support": "contact@pachedev.com",
    "category": "Administration",
    "version": "19.0.1.1.0",
    "license": "LGPL-3",
    "depends": ["base"],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "data/monitoring_data.xml",
        "views/instance_monitoring_views.xml",
        "menus/menus.xml",
    ],
    "installable": True,
    "auto_install": False,
    "application": True,
}

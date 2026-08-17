# -*- coding: utf-8 -*-
{
    'name': 'Escáner Móvil Pro de Productos y Conteos Cíclicos (Standalone Edition)',
    'summary': 'Consulta instantánea de productos, stock multialmacén dinámico y conteos cíclicos con exportación Excel sin dependencias externas',
    'description': """
Escáner Móvil Pro de Productos y Conteos Cíclicos para Odoo 19 (Edición Independiente / App Store).
====================================================================================================
- Módulo de consulta rápida de productos mediante lector óptico de códigos de barra o cámara de smartphone (iOS/Android).
- Muestreo dinámico de Stock Multialmacén compatible con cualquier estructura de inventarios estándar de Odoo.
- Módulo de Conteos Cíclicos de Inventario en vivo con comparación de stock inicial vs. contado en tiempo real.
- Reporte detallado en pantalla y exportación a hojas de cálculo Excel (.xlsx).
- 100% independiente: No requiere módulos propietarios ni dependencias de terceros.
    """,
    'version': '19.0.1.0.0',
    'category': 'Inventory/Management',
    'author': 'Omar Martinez',
    'website': '',
    'license': 'OPL-1',
    'price': 269.00,
    'currency': 'USD',
    'depends': ['base', 'product', 'stock'],
    'data': [
        'security/scanner_security.xml',
        'security/ir.model.access.csv',
        'views/scanner_cycle_count_views.xml',
        'views/barcode_scanner_views.xml',
    ],
    'images': ['static/description/icon_banner.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
}

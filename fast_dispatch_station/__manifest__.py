# -*- coding: utf-8 -*-
{
    'name': 'Estación de Despacho Rápido Pro (Fast Dispatch Station)',
    'version': '19.0.1.3.0',
    'category': 'Inventory/Dispatch',
    'summary': 'Verificación de empacado por código de barras y validación de despacho en 1-Click',
    'description': """
Estación de Despacho Rápido para Odoo 19.
========================================
- Verificación de empacado mediante escaneo de código de barras en tiempo real.
- Comparación táctil de productos solicitados en el pedido vs. productos empacados.
- Validación de despacho y finalización de transferencias de inventario en 1-Click.
- Dashboard de almacén táctil de alta velocidad sin errores de empaque.
    """,
    'author': 'Omar Martinez',
    'website': '',
    'license': 'OPL-1',
    'price': 299.00,
    'currency': 'USD',
    'images': ['static/description/icon_banner.png'],
    'depends': ['stock', 'sale'],
    'data': [
        'security/ir.model.access.csv',
        'views/fast_dispatch_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'fast_dispatch_station/static/src/scss/fast_dispatch.scss',
            'fast_dispatch_station/static/src/js/fast_dispatch_form.js',
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
}

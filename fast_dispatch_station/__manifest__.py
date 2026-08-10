# -*- coding: utf-8 -*-
{
    'name': 'Estación de Despacho Rápido',
    'version': '19.0.1.3.0',
    'category': 'Inventory/Inventory',
    'summary': 'Barcode Order Verification & Ultra-Fast Warehouse Dispatch Station',
    'description': """
Fast Dispatch Station for Odoo 19.
=================================
- Real-time barcode scanning & item packing verification.
- Compare ordered sale items vs physically packed items.
- 1-Click dispatch validation & stock picking transfer completion.
- Touch & scanner friendly full-screen warehouse dashboard.
    """,
    'author': 'Omar Martinez',
    'website': '',
    'license': 'OPL-1',
    'price': 249.00,
    'currency': 'USD',
    'images': ['static/description/banner.png'],
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

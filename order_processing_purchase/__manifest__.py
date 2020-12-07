# -*- coding: utf-8 -*-
{
    'name': 'Order Processing Purchase',
    'version': '1.0',
    'summary': 'This module allows you to add the purchase functionality to the order processing model',
    'sequence': 3,
    'description': """

    """,
    'category': 'Inventory/Purchase',
    'depends': ['order_processing','purchase','product'],
    'data': [
        'security/ir.model.access.csv',
        'views/order_processing_views.xml',
        'views/product_views.xml',
        'views/purchase_term_views.xml',
        'views/purchase_order_views.xml',
        'views/menu_views.xml',
        'report/purchase_order_templates.xml',
    ],

    'installable': True,
    'application': True,
    'auto_install': False,
}

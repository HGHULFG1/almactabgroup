# -*- coding: utf-8 -*-
{
    'name': 'Order Processing freight and documentation',
    'version': '1.0',
    'summary': 'This module allows you to add the freight documentation functionality to the freight and documentation model',
    'sequence': 5,
    'description': """

    """,
    'category': 'Sales/Purchase',
    'depends': ['order_processing','order_processing_sale','account'],
    'data': [
        'security/ir.model.access.csv',
        'views/order_processing_views.xml',
        'views/sale_order_views.xml',
    ],

    'installable': True,
    'application': True,
    'auto_install': False,
}

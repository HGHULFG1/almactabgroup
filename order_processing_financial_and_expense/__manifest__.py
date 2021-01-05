# -*- coding: utf-8 -*-
{
    'name': 'Order Processing Financial & Expenses',
    'version': '1.0',
    'summary': 'This module allows you to add the sale functionality to the order processing financial model',
    'sequence': 8,
    'description': """

    """,
    'category': 'Sales/Sales',
    'depends': ['order_processing','order_processing_sale','order_processing_freight_documentation'],
    'data': [
        'security/ir.model.access.csv',
        'views/order_processing_views.xml',
    ],

    'installable': True,
    'application': True,
    'auto_install': False,
}

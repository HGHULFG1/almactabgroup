# -*- coding: utf-8 -*-
{
    'name': 'Order Processing Sale',
    'version': '1.0',
    'summary': 'This module allows you to add the sale functionality to the order processing model',
    'sequence': 4,
    'description': """

    """,
    'category': 'Sales/Sales',
    'depends': ['order_processing','sale','account'],
    'data': [
        'security/ir.model.access.csv',
        'views/order_processing_views.xml',
        'views/sale_order_views.xml',
        'report/sale_report_templates.xml',
        'wizard/order_processing_sale_wizard.xml',
    ],

    'installable': True,
    'application': True,
    'auto_install': False,
}

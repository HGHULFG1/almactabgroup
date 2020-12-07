# -*- coding: utf-8 -*-
{
    'name': 'Order Processing Log Book',
    'version': '1.0',
    'summary': 'This module allows you to add the log book functionality to the order processing model',
    'sequence': 7,
    'description': """

    """,
    'category': 'Sales/Purchase',
    'depends': ['order_processing'],
    'data': [
        'security/ir.model.access.csv',

        'data/log_book_data.xml',

        'views/order_processing_views.xml',
        'views/log_book_views.xml',
    ],

    'installable': True,
    'application': True,
    'auto_install': False,
}

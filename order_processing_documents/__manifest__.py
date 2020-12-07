# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Order Processing Documents',
    'version': '1.0',
'sequence': 2,
    'category': 'Productivity/Documents',
    'summary': 'Access documents from the order processing',
    'description': """
Easily access your documents from order processing.
""",
    'website': ' ',
    'depends': ['base','documents', 'order_processing'],
    'data': [
        'data/documents_data.xml',
        'views/order_processing_views.xml',
        'views/res_config_settings_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}

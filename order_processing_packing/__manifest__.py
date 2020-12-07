# -*- coding: utf-8 -*-
{
    'name': 'Order Processing Packing',
    'version': '1.0',
    'summary': 'This module allows you to add a packing list tab in processing order',
    'sequence': 9,

    'category': 'Sales/CRM',
    'depends': ['order_processing'],
    'data': [
        'security/ir.model.access.csv',
        'views/order_processing_views.xml',
        'report/packing_report.xml',
        'report/packing_standard_report_templates.xml',
        'report/packing_advanced_report_templates.xml',
    ],

    'installable': True,
    'application': True,
    'auto_install': False,
}

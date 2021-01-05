# -*- coding: utf-8 -*-
{
    'name': 'Order Processing',
    'version': '1.0',
    'summary': 'This module allows you to duplicate a lead or opportunity in order processing',
    'sequence': 1,
    'description': """
    A new add button in the form view of crm lead. 
    As soon as we click on this button, it will duplicate the current opportunity or lead in model order processing 
    with all its information
    """,
    'category': 'Sales/CRM',
    'depends': ['base', 'crm'],
    'data': [
        'security/ir.model.access.csv',

        'data/order_processing_stage_data.xml',

        'views/crm_lead_views.xml',
        'views/order_processing_views.xml',
        'views/order_processing_stage_views.xml',
        'views/order_processing_menu.xml',
    ],

    'installable': True,
    'application': True,
    'auto_install': False,
}

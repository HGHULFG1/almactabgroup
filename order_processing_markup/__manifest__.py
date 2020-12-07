# -*- coding: utf-8 -*-
{
    'name': 'Order Processing Markups',
    'version': '1.0',
    'summary': 'This module gives an overview of the Markups',
    'sequence': 6,
    'description': """
        Overview of the markups: 
        Purchase: 
        • Unit purchase 
        • Total purchase 
        Sales: 
        • Unit price 
        • Total price 
        Margin 
        • Unit Margin 
        • Total Margin 
        Expenses 
        • Unit Expenses 
        • Total Expenses 
        Profit percentage 
        VAT 
        Markup 
        Commission 
        Fluctuation 
        Inspection fees
    """,
    'category': 'Sales/CRM/Purchase',
    'depends': ['base', 'crm', 'sale', 'purchase', 'product', 'order_processing', 'order_processing_sale',
                'order_processing_purchase'],
    'data': [
        'security/ir.model.access.csv',
        'views/order_processing_views.xml',
        'views/product_views.xml',
    ],

    'installable': True,
    'application': True,
    'auto_install': False,
}

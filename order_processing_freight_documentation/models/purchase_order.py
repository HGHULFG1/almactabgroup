# -*- coding: utf-8 -*-


from odoo import api, fields, models, SUPERUSER_ID, _


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    freight_documentation_id = fields.Many2one('freight.documentation', string='Freight And Documentation')
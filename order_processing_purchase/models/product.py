# -*- coding: utf-8 -*-


from odoo import api, fields, models, SUPERUSER_ID, _


class SupplierInfo(models.Model):
    _inherit = "product.supplierinfo"

    order_processing_id = fields.Many2one('order.processing')
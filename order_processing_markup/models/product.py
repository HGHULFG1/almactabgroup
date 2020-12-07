from odoo import api, fields, models, tools, SUPERUSER_ID


class ProductCategory(models.Model):
    _inherit = 'product.category'

    markup = fields.Integer('Markup %', default=0, readonly=False, store=True)

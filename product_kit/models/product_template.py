from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'
    is_kit = fields.Boolean(string='Is Kit', default=False,
                            help='Use a service product as a kit of storable products.')

from odoo import api, fields, models, _


class ContainerType(models.Model):
    _name = 'container.type'

    name = fields.Char('Name', required=True)

class ContainerShippingCompany(models.Model):
    _name = 'container.shipping.company'

    name = fields.Char('Name', required=True)

class Container(models.Model):
    _name = 'container'

    name = fields.Char('Reference', required=True)
    type_id = fields.Many2one('container.type', string='Type')
    shipping_id = fields.Many2one('container.shipping.company', string='Shipping company')
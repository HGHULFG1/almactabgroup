from odoo import api, fields, models, tools, SUPERUSER_ID


class SaleTermName(models.Model):
    _name = "sale.term.name"

    name = fields.Char('Name', required=True)

class SaleTerm(models.Model):
    _name = "sale.term"
    _description = 'Sale Term'
    _order = 'sequence, id'

    name = fields.Many2one("sale.term.name",'Name', required=True)
    sequence = fields.Integer(string='Sequence', default=1)
    sequence_number = fields.Integer(string='#', related='sequence',readonly=False)
    description = fields.Text('Description', required=True)
    order_processing_id = fields.Many2one('order.processing', string='Order Processing Reference')
    sale_order_id = fields.Many2one('sale.order', string='Sale Order Reference', index=True)

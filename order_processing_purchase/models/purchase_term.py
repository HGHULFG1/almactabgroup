from odoo import api, fields, models, tools, SUPERUSER_ID


class PurchaseTermName(models.Model):
    _name = "purchase.term.name"

    name = fields.Char('Name', required=True)

class PurchaseTerm(models.Model):
    _name = "purchase.term"
    _description = 'Purchase Term'
    _order = 'sequence, id'

    name = fields.Many2one("purchase.term.name",'Name', required=True)
    sequence = fields.Integer(string='Sequence', default=1)
    sequence_number = fields.Integer(string='#', related='sequence',readonly=False)
    description = fields.Text('Description', required=True)
    order_processing_id = fields.Many2one('order.processing', string='Order Processing Reference')
    purchase_order_id = fields.Many2one('purchase.order', string='Purchase Order Reference')

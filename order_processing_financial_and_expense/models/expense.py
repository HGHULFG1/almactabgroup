from odoo import api, fields, models, SUPERUSER_ID, _


class Expense(models.Model):
    _name = 'expense'

    order_id = fields.Many2one('order.processing', string='Order Reference', required=True, ondelete='cascade',
                               index=True, copy=False)
    name = fields.Text(string='Description', required=True)
    sequence = fields.Integer(string='Sequence', default=1)
    sequence_number = fields.Integer(string='#', related='sequence', readonly=False)

    qty = fields.Float(string='Quantity', required=True, default=1.0)
    currency_id = fields.Many2one(related='order_id.currency_id', depends=['order_id.currency_id'], store=True,
                                  string='Currency', readonly=True)
    price_unit = fields.Float('Unit Price', required=True, digits='Product Price', default=0.0)
    price_subtotal = fields.Monetary(compute='_compute_amount', string='Subtotal', readonly=True, store=True)

    @api.depends('qty', 'price_unit')
    def _compute_amount(self):
        for line in self:
            line.price_subtotal = line.price_unit * line.qty

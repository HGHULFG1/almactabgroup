from odoo import api, fields, models, tools, SUPERUSER_ID


class PackingTermName(models.Model):
    _name = "packing.term.name"

    name = fields.Char('Name', required=True)

class PackingTerm(models.Model):
    _name = "packing.term"
    _description = 'Packing Term'
    _order = 'sequence, id'

    name = fields.Many2one("packing.term.name",'Name', required=True)
    sequence = fields.Integer(string='Sequence', default=1)
    sequence_number = fields.Integer(string='#', related='sequence',readonly=False)
    description = fields.Text('Description', required=True)
    order_processing_id = fields.Many2one('order.processing', string='Order Processing Reference')

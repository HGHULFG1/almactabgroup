from odoo import api, fields, models


class OrderProcessing(models.Model):
    _inherit = "order.processing"

    packing_line = fields.One2many('packing', 'order_id', string='Market Lines', copy=True, auto_join=True)

    def action_update_from_sale(self):
        for record in self:
            for line in record.order_processing_sale_line:
                record.env['packing'].sudo().create({
                    'sequence': line.sequence,
                    'sequence_number': line.sequence_number,
                    'country_id': record.country_id.id,
                    'default_code': line.default_code,
                    'product_id': line.product_id.id,
                    'name': line.name,
                    'product_uom_qty': line.product_uom_qty,
                    'order_id': record.id
                })

    packing_term_ids = fields.One2many('packing.term', 'order_processing_id', string='Packing term')
    shipping_to_id = fields.Many2one('res.partner', string='Shipping to')
    vendor_ids = fields.Many2many('res.partner', string='Vendors')

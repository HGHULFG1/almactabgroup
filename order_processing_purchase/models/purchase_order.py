# -*- coding: utf-8 -*-


from odoo import api, fields, models, SUPERUSER_ID, _


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    purchase_term_ids = fields.One2many('purchase.term', 'purchase_order_id', string='Purchase term')
    order_processing_id = fields.Many2one('order.processing', string='Order Processing Reference')

    def action_update_rfq_line_processing(self):
        for line in self.order_line:
            vals = {
                'partner_id': line.partner_id.id,
                'sequence': line.sequence,
                'order_id': self.order_processing_id.id,
                'product_id': line.product_id.id,
                'default_code': line.default_code,
                'name': line.name,
                'product_qty': line.product_qty,
                'product_uom': line.product_uom.id,
                'price_unit': line.price_unit,
                'price_subtotal': line.price_subtotal,
                'taxes_id': [(6, 0, line.taxes_id.ids)], }
            if line.processing_rfq_line_id.id in self.order_processing_id.order_line_rfq.ids:
                line.processing_rfq_line_id.write(vals)
            else:
                processing_rfq_line_id = self.env['order.processing.rfq.line'].create(vals)
                line.processing_rfq_line_id = processing_rfq_line_id

            # Delete RFQ line
            order_line_ids = self.env['purchase.order'].search([('order_processing_id', '=', self.order_processing_id.id),('state', 'in', ['draft', 'sent']) ]).order_line.processing_rfq_line_id.ids
            line_rfq_delete = self.order_processing_id.order_line_rfq.filtered(lambda l: l.id not in order_line_ids)
            if line_rfq_delete:
                line_rfq_delete.unlink()

        return True


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"
    default_code = fields.Char('Part No')
    sequence = fields.Integer(string='Sequence', default=1)
    sequence_number = fields.Integer(string='#', related='sequence', readonly=False)
    processing_rfq_line_id = fields.Many2one('order.processing.rfq.line')

    @api.onchange('product_id')
    def onchange_product_id_default_code(self):
        self.default_code = self.product_id.default_code

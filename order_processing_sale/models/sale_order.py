# -*- coding: utf-8 -*-


from odoo import api, fields, models, SUPERUSER_ID, _


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"
    processing_sale_line_id = fields.Many2one('order.processing.sale.line')
    default_code = fields.Char('Part No')
    sequence = fields.Integer(string='Sequence', default=1)
    sequence_number = fields.Integer(string='#', related='sequence',readonly=False)

    @api.onchange('product_id')
    def onchange_product_id_default_code(self):
        self.default_code = self.product_id.default_code





class SaleOrder(models.Model):
    _inherit = "sale.order"

    sale_term_ids = fields.One2many('sale.term', 'sale_order_id', string='Sale term')
    order_processing_id = fields.Many2one('order.processing', string='Order Processing Reference')
    bank_account_id = fields.Many2one(
        'res.partner.bank', 'Bank Account Number',
        domain="[('company_id', '=', company_id)]",
        tracking=True,
        help='Employee bank salary account')

    def action_update_sale_line_processing(self):
        for line in self.order_line:
            vals = {
                'order_partner_id': line.order_partner_id.id,
                'sequence': line.sequence,
                'order_id': self.order_processing_id.id,
                'product_id': line.product_id.id,
                'default_code': line.default_code,
                'name': line.name,
                'product_uom_qty': line.product_uom_qty,
                'product_uom': line.product_uom.id,
                'price_unit': line.price_unit,
                'price_tax': line.price_tax,
                'price_subtotal': line.price_subtotal,
                'price_total': line.price_total,
                'company_id': line.company_id.id,
                'tax_id': [(6, 0, line.tax_id.ids)], }
            if line.processing_sale_line_id.id in self.order_processing_id.order_processing_sale_line.ids:
                line.processing_sale_line_id.write(vals)
            else:
                processing_sale_line_id = self.env['order.processing.sale.line'].create(vals)
                line.processing_sale_line_id = processing_sale_line_id

            # Delete Sale line
            order_line_ids = self.env['sale.order'].search([('order_processing_id', '=', self.order_processing_id.id), (
            'state', 'in', ['draft', 'sent'])]).order_line.processing_sale_line_id.ids
            line_sale_delete = self.order_processing_id.order_processing_sale_line.filtered(lambda l: l.id not in order_line_ids)
            if line_sale_delete:
                line_sale_delete.unlink()

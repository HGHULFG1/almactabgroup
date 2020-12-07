from odoo import api, fields, models, tools, SUPERUSER_ID


class OrderProcessing(models.Model):
    _inherit = "order.processing"

    processing_markup_line = fields.One2many('order.processing.markup', 'order_id', copy=True)
    commission_markup = fields.Float('Commission', default=0.0)
    fluctuation_markup = fields.Float('Fluctuation', default=0.0)
    inspection_fees_markup = fields.Float('Inspection fees', default=0.0)

    def action_update_markup(self):
        """This function is an action of the update button in the Markup page,
        it allows to update the lines of markups according to the lines existing in sales"""
        markup_line_ids = self.env['order.processing.markup'].search([('order_id', '=', self.id)]).filtered(
            lambda l: l.processing_sale_line_id.id not in self.order_processing_sale_line.ids)
        if markup_line_ids:
            markup_line_ids.unlink()
        if self.order_processing_sale_line:
            # Browse the sale info lines
            for line in self.order_processing_sale_line:
                markup_line = self.env['order.processing.markup'].search(
                    [('processing_sale_line_id', '=', line.id), ('order_id', '=', self.id)])

                # Returns the current product purchase price and total if it exists in the RFQ line else returned null
                # if line.rfq_line_id.id in self.order_line_rfq.ids:
                #     price_unit_purchase = line.rfq_line_id.price_unit
                #     price_total_purchase = line.rfq_line_id.price_total
                # else:
                #     price_unit_purchase = 0
                #     price_total_purchase = 0
                if self.order_line_rfq:
                    for rec in self.order_line_rfq:
                        price_unit_purchase = rec.price_unit

                # else:
                #     price_unit_purchase = 0.0



                price_unit_sale = line.price_unit

                #sum_fees = self.commission_markup + self.fluctuation_markup + self.inspection_fees_markup
                # markup = line.product_id.categ_id.markup
                # if markup:
                #     price_unit_sale = price_unit_sale / markup
                # if sum_fees:
                #     price_unit_sale = price_unit_sale / sum_fees

                # Prepare values in a dictionary
                vals = {'product_id': line.product_id.id,
                        'default_code': line.default_code,
                        'name': line.name,
                        'product_qty': line.product_uom_qty,
                        'price_unit_purchase': price_unit_purchase,
                        'price_total_purchase': price_unit_purchase*rec.product_qty,
                        'price_unit_sale': price_unit_sale,
                        'price_total_sale': price_unit_sale * line.product_uom_qty,
                        'price_unit_margin': 0,
                        'price_total_margin': 0,
                        'price_unit_freight_documentation': 0,
                        'price_total_freight_documentation': 0,
                        'profit': 0,
                        'markup': line.product_id.categ_id.markup,
                        'processing_sale_line_id': line.id,
                        'order_id': self.id
                        }
                print('vals========', vals)
                if markup_line:
                    markup_line.sudo().write(vals)
                else:
                    self.env['order.processing.markup'].sudo().create(vals)

    # @api.onchange('commission_markup', 'fluctuation_markup', 'inspection_fees_markup')
    # def _calcul_price_unit_sale(self):
    #     for record in self:
    #         record.processing_markup_line._calcul_price_unit_sale()
    #         record.processing_markup_line._calcul_profit()

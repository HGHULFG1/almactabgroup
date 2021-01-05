from odoo import api, fields, models, tools, SUPERUSER_ID


class OrderProcessing(models.Model):
    _inherit = "order.processing"

    processing_markup_line = fields.One2many('order.processing.markup', 'order_id', copy=True)
    commission_id = fields.One2many('markup.commission','commission_id',"Commissions")


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

                if self.order_line_rfq:
                    for rec in self.order_line_rfq:
                        price_unit_purchase = rec.price_unit

                price_unit_sale = line.price_unit

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
                        'profit': 0,
                        'markup': line.product_id.categ_id.markup,
                        'custom_fees': line.product_id.categ_id.custom_fees,
                        'processing_sale_line_id': line.id,
                        'order_id': self.id
                        }
                if markup_line:
                    markup_line.sudo().write(vals)
                else:
                    self.env['order.processing.markup'].sudo().create(vals)


class CommissionMarkup(models.Model):
    _name = 'markup.commission'
    _description = 'Commission Markup'

    commission_id = fields.Many2one('order.processing',required=True, ondelete='cascade',
                               index=True, copy=False)
    name = fields.Char("Name")
    type = fields.Selection([('multiply','Multiplying'),
                             ('dividing','Dividing')],
                            string="Type",default='dividing')
    commission_value = fields.Float('Value')



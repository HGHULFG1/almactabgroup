from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import ValidationError


class OrderProcessingMarkup(models.Model):
    _name = 'order.processing.markup'
    _description = 'Order Processing Markup'
    _order = 'order_id, sequence, id'
    _check_company_auto = True

    order_id = fields.Many2one('order.processing', string='Order Reference', required=True, ondelete='cascade',
                               index=True, copy=False)

    sequence = fields.Integer(string='Sequence', default=1)
    sequence_number = fields.Integer(string='#', related='sequence', readonly=False)
    product_id = fields.Many2one('product.product', string='Product',
                                 domain="[('purchase_ok', '=', True),('sale_ok', '=', True), '|', ('company_id', '=', False), ('company_id', '=', company_id)]",
                                 change_default=True, ondelete='restrict', check_company=True, readonly=True)
    default_code = fields.Char('Part No', readonly=True)
    name = fields.Text(string='Description', required=True, readonly=True)
    product_qty = fields.Float(string='Quantity', digits='Product Unit of Measure', required=True, default=1.0)
    currency_id = fields.Many2one(related='order_id.currency_id', depends=['order_id.currency_id'], store=True,
                                  string='Currency', readonly=True)
    company_id = fields.Many2one(related='order_id.company_id', string='Company', store=True, readonly=True, index=True)

    price_unit_purchase = fields.Float('Unit Purchase', required=True, digits='Product Price', default=0.0,
                                       readonly=False, store=True)
    price_total_purchase = fields.Monetary(string='Total Purchase', compute='_get_product_qty', store=True)

    price_unit_sale = fields.Float('Sales unit Price', compute='_get_price_unit_sale',
                                   readonly=True, store=True)
    price_total_sale = fields.Monetary(string='Total Sales', compute='_get_product_qty', store=True)

    price_unit_margin = fields.Float('Uit Margin', compute='_get_price_unit_margin', store=True, readonly=False)
    price_total_margin = fields.Monetary(string='Total Margin', compute='_get_product_qty', store=True)

    # price_unit_freight_documentation = fields.Float('Unit Freight Documentation', required=True, digits='Product Price',
    #                                                 default=0.0,
    #                                                 readonly=False, store=True)
    # price_total_freight_documentation = fields.Monetary(string='Total Freight Documentation',
    #                                                     compute='_get_product_qty', store=True)

    profit = fields.Float('Profit %', compute='_get_product_profit', store=True)
    markup = fields.Float('Markup', readonly=False, store=True)
    custom_fees = fields.Float('Custom Fees', readonly=False, store=True)

    processing_sale_line_id = fields.Many2one('order.processing.sale.line')

    cost = fields.Float("Cost", compute='_get_product_cost')

    @api.depends('price_unit_purchase')
    def _get_product_cost(self):
        for rec in self:
            rec.cost = rec.price_unit_purchase

    @api.depends('cost', 'price_unit_sale','price_unit_purchase')
    def _get_price_unit_margin(self):
        for rec in self:
            rec.price_unit_margin = rec.price_unit_sale - rec.cost

    @api.constrains('markup')
    def _check_markup_value(self):
        if self.markup > 1.0:
            raise ValidationError(_('You can not set markup bigger than 1.'))

    # @api.depends('price_unit_margin', 'cost')
    # def _get_product_markup(self):
    #     for rec in self:
    #         if rec.cost:
    #             rec.markup = (rec.price_unit_margin / rec.cost) * 100

    @api.depends('markup','cost','order_id.commission_id.commission_value','custom_fees')
    def _get_price_unit_sale(self):
        for rec in self:
            # rec.price_unit_sale = ((rec.cost * rec.markup) / 100) + rec.cost
            x = (rec.cost * rec.custom_fees) / rec.markup
            for commission in rec.order_id.commission_id:
                if commission.commission_value:
                    if commission.type == 'dividing':
                        x /= commission.commission_value
                    else:
                        x *= commission.commission_value
            rec.price_unit_sale = x


    @api.depends('price_unit_margin', 'cost', 'order_id.commission_id.commission_value')
    def _get_product_profit(self):
        for rec in self:
            y = ((rec.price_unit_margin / rec.price_unit_sale) * 100)
            if rec.price_unit_sale:
                for commission in rec.order_id.commission_id:
                    if commission.commission_value:
                        y -= commission.commission_value
            rec.profit = y


    @api.depends('product_qty')
    def _get_product_qty(self):
        for record in self:
            record.price_total_purchase = record.price_unit_purchase * record.product_qty
            record.price_total_sale = record.price_unit_sale * record.product_qty
            #record.price_total_freight_documentation = record.price_unit_freight_documentation * record.product_qty
            record.price_total_margin = record.price_unit_margin * record.product_qty



from odoo import api, fields, models, SUPERUSER_ID, _


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
                                   readonly=False, store=True)
    price_total_sale = fields.Monetary(string='Total Sales', compute='_get_product_qty', store=True)

    price_unit_margin = fields.Float('Uit Margin', compute='_get_price_unit_margin', store=True,readonly=False)
    price_total_margin = fields.Monetary(string='Total Margin', compute='_get_product_qty', store=True)

    price_unit_freight_documentation = fields.Float('Unit Freight Documentation', required=True, digits='Product Price', default=0.0,
                                      readonly=False, store=True)
    price_total_freight_documentation = fields.Monetary(string='Total Freight Documentation', compute='_get_product_qty', store=True)

    profit = fields.Float('Profit %',compute='_get_product_profit', store=True)
    markup = fields.Float('Markup', compute='_get_product_markup', readonly=False, store=True)

    processing_sale_line_id = fields.Many2one('order.processing.sale.line')

    cost = fields.Float("Cost",compute='_get_product_cost')


    @api.depends('price_unit_purchase', 'price_unit_freight_documentation')
    def _get_product_cost(self):
        for rec in self:
            rec.cost = rec.price_unit_purchase + rec.price_unit_freight_documentation

    @api.depends('cost', 'price_unit_sale')
    def _get_price_unit_margin(self):
        for rec in self:
            rec.price_unit_margin = rec.price_unit_sale - rec.cost

    @api.depends('price_unit_margin', 'cost')
    def _get_product_markup(self):
        for rec in self:
            if rec.cost:
                rec.markup = (rec.price_unit_margin / rec.cost) * 100

    @api.depends('markup')
    def _get_price_unit_sale(self):
        for rec in self:
            rec.price_unit_sale = ((rec.cost * rec.markup) / 100) + rec.cost


    @api.depends('price_unit_margin', 'cost', 'order_id.commission_markup', 'order_id.fluctuation_markup',
                 'order_id.inspection_fees_markup')
    def _get_product_profit(self):
        for rec in self:
            if rec.price_unit_sale:
                rec.profit = ((rec.price_unit_margin / rec.price_unit_sale) * 100) - (
                        rec.order_id.commission_markup + rec.order_id.fluctuation_markup + rec.order_id.inspection_fees_markup)

    @api.depends('product_qty')
    def _get_product_qty(self):
        for record in self:
            record.price_total_purchase = record.price_unit_purchase * record.product_qty
            record.price_total_sale = record.price_unit_sale * record.product_qty
            record.price_total_freight_documentation = record.price_unit_freight_documentation * record.product_qty
            record.price_total_margin = record.price_unit_margin * record.product_qty

    # @api.onchange('price_unit_purchase', 'price_unit_freight_documentation', 'markup')
    # def _calcul_price_unit_sale(self):
    #     for record in self:
    #         price_unit_sale = record.price_unit_purchase + record.price_unit_freight_documentation or record.price_unit_sale
    #         sum_fees = record.order_id.commission_markup + record.order_id.fluctuation_markup + record.order_id.inspection_fees_markup
    #         if price_unit_sale:
    #             if record.markup:
    #                 price_unit_sale = price_unit_sale / record.markup
    #             if sum_fees:
    #                 price_unit_sale = price_unit_sale / sum_fees
    #             record.price_unit_sale = price_unit_sale
    #
    # @api.onchange('price_unit_sale', 'price_unit_purchase', 'price_unit_freight_documentation')
    # def _calcul_margin_markup(self):
    #     for record in self:
    #         record.price_unit_margin = record.price_unit_sale - record.price_unit_purchase - record.price_unit_freight_documentation
    #         record.price_total_margin = record.price_unit_margin * record.product_qty
    #         record.markup = (record.price_unit_purchase + record.price_unit_freight_documentation) / record.price_unit_sale
    #
    # @api.onchange('price_unit_margin', 'price_unit_sale')
    # def _calcul_profit(self):
    #     for record in self:
    #         sum_fees = record.order_id.commission_markup + record.order_id.fluctuation_markup + record.order_id.inspection_fees_markup
    #         record.profit = ((record.price_unit_margin / record.price_unit_sale) - sum_fees) * 100
    #



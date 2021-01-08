
from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.tools.misc import formatLang, get_lang

class ProductAttributeCustomValue(models.Model):
    _inherit = "product.attribute.custom.value"

    freight_documentation_id = fields.Many2one('freight.documentation', string="Freight And Documentation", required=True,
                                            ondelete='cascade')


class OrderProcessingFreightDocumentation(models.Model):
    _name = 'freight.documentation'
    _description = 'Freight And Documentation'
    _order = 'order_id, sequence, id'
    _check_company_auto = True


    order_id = fields.Many2one('order.processing', string='Order Reference', required=True, ondelete='cascade',
                               index=True, copy=False)
    name = fields.Text(string='Description', required=True)
    sequence = fields.Integer(string='Sequence', default=1)
    sequence_number = fields.Integer(string='#', related='sequence',readonly=False)
    product_id = fields.Many2one('product.product', string='Product',
                                 domain="[('sale_ok', '=', True), '|', ('company_id', '=', False), ('company_id', '=', company_id)]",
                                 change_default=True, ondelete='restrict', check_company=True)
    default_code = fields.Char('Part No')
    company_id = fields.Many2one(related='order_id.company_id', string='Company', store=True, readonly=True, index=True)
    partner_id = fields.Many2one('res.partner', 'Vendor', ondelete='cascade', required=True,
                                 help="Vendor of this product",
                                 check_company=True)
    currency_id = fields.Many2one(related='order_id.currency_id', depends=['order_id.currency_id'], store=True,
                                  string='Currency', readonly=True)
    product_uom_qty = fields.Float(string='Quantity', digits='Product Unit of Measure', required=True, default=1.0)
    product_uom = fields.Many2one('uom.uom', string='UoM')
    price_cost = fields.Float('Cost Price', required=True, digits='Product Price', default=0.0)
    price_unit = fields.Float('Unit Price', required=True, digits='Product Price', default=0.0)
    tax_id = fields.Many2many('account.tax', string='Taxes',
                              domain=['|', ('active', '=', False), ('active', '=', True)])

    price_subtotal_sale = fields.Monetary(compute='_compute_amount', string='Subtotal Sales', readonly=True, store=True)
    price_tax_sale = fields.Float(compute='_compute_amount', string='Total Tax Sales', readonly=True, store=True)
    price_total_sale = fields.Monetary(compute='_compute_amount', string='Total Sales', readonly=True, store=True)

    price_subtotal_cost = fields.Monetary(compute='_compute_amount', string='Subtotal Cost', readonly=True, store=True)
    price_tax_cost = fields.Float(compute='_compute_amount', string='Total Tax Cost', readonly=True, store=True)
    price_total_cost = fields.Monetary(compute='_compute_amount', string='Total Cost', readonly=True, store=True)

    display_type = fields.Selection([
        ('line_section', "Section"),
        ('line_note', "Note")], default=False, help="Technical field for UX purpose.")

    product_custom_attribute_value_ids = fields.One2many('product.attribute.custom.value', 'op_sale_order_line_id',
                                                         string="Custom Values", copy=True)
    product_no_variant_attribute_value_ids = fields.Many2many('product.template.attribute.value', string="Extra Values",
                                                              ondelete='restrict')

    order_partner_id = fields.Many2one(related='order_id.partner_id', store=True, string='Customer', readonly=False)
    sale_order_line_id = fields.Many2one('sale.order.line')

    @api.depends('product_uom_qty','price_cost', 'price_unit', 'tax_id')
    def _compute_amount(self):
        for line in self:
            vals = line._prepare_compute_all_values()
            taxes_sale = line.tax_id.compute_all(
                vals['price_unit'],
                vals['currency_id'],
                vals['product_uom_qty'],
                vals['product'],
                vals['partner'])
            taxes_cost = line.tax_id.compute_all(
                vals['price_cost'],
                vals['currency_id'],
                vals['product_uom_qty'],
                vals['product'],
                vals['partner'])
            line.update({
                'price_tax_sale': sum(t.get('amount', 0.0) for t in taxes_sale.get('taxes', [])),
                'price_total_sale': taxes_sale['total_included'],
                'price_subtotal_sale': taxes_sale['total_excluded'],
                'price_tax_cost': sum(t.get('amount', 0.0) for t in taxes_cost.get('taxes', [])),
                'price_total_cost': taxes_cost['total_included'],
                'price_subtotal_cost': taxes_cost['total_excluded'],
            })

    def _prepare_compute_all_values(self):
        self.ensure_one()
        return {
            'price_cost': self.price_cost,
            'price_unit': self.price_unit,
            'currency_id': self.order_id.currency_id,
            'product_uom_qty': self.product_uom_qty,
            'product': self.product_id,
            'partner': self.order_id.partner_id,
        }

    def _get_product_purchase_description(self, product_lang):
        self.ensure_one()
        name = product_lang.display_name
        if product_lang.description_purchase:
            name += '\n' + product_lang.description_purchase
        return name

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        self.price_cost = self.product_id.standard_price
        for seller in self.product_id.seller_ids:
            if seller.name == self.partner_id:
                self.price_cost = seller.price
                # self.currency_id = seller.currency_id.id

    def _get_product_price(self):
        price = self.product_id.standard_price
        for seller in self.product_id.seller_ids:
            if seller.name == self.partner_id:
                price = seller.price
        return price

    @api.onchange('product_id')
    def product_id_change(self):
        if not self.product_id:
            return
        self.default_code = self.product_id.default_code
        valid_values = self.product_id.product_tmpl_id.valid_product_template_attribute_line_ids.product_template_value_ids
        # remove the is_custom values that don't belong to this template
        for pacv in self.product_custom_attribute_value_ids:
            if pacv.custom_product_template_attribute_value_id not in valid_values:
                self.product_custom_attribute_value_ids -= pacv

        # remove the no_variant attributes that don't belong to this template
        for ptav in self.product_no_variant_attribute_value_ids:
            if ptav._origin not in valid_values:
                self.product_no_variant_attribute_value_ids -= ptav

        vals = {}
        if not self.product_uom or (self.product_id.uom_id.id != self.product_uom.id):
            vals['product_uom'] = self.product_id.uom_id
            vals['product_uom_qty'] = self.product_uom_qty or 1.0

        product = self.product_id.with_context(
            lang=get_lang(self.env, self.order_id.partner_id.lang).code,
            partner=self.order_id.partner_id,
            quantity=vals.get('product_uom_qty') or self.product_uom_qty,
            date=self.order_id.date_order,
            pricelist=self.order_id.pricelist_id.id,
            uom=self.product_uom.id
        )

        vals.update(name=self.get_sale_order_line_multiline_description_sale(product))

        self._compute_tax_id()

        if self.order_id.pricelist_id and self.order_id.partner_id:
            vals['price_unit'] = self.env['account.tax']._fix_tax_included_price_company(
                self._get_display_price(product), product.taxes_id, self.tax_id, self.company_id)
        self.update(vals)

        title = False
        message = False
        result = {}
        warning = {}
        if product.sale_line_warn != 'no-message':
            title = _("Warning for %s", product.name)
            message = product.sale_line_warn_msg
            warning['title'] = title
            warning['message'] = message
            result = {'warning': warning}
            if product.sale_line_warn == 'block':
                self.product_id = False

        # Purchase
        self.price_cost = self._get_product_price()

        return result

    def get_sale_order_line_multiline_description_sale(self, product):
        """ Compute a default multiline description for this sales order line.

        In most cases the product description is enough but sometimes we need to append information that only
        exists on the sale order line itself.
        e.g:
        - custom attributes and attributes that don't create variants, both introduced by the "product configurator"
        - in event_sale we need to know specifically the sales order line as well as the product to generate the name:
          the product is not sufficient because we also need to know the event_id and the event_ticket_id (both which belong to the sale order line).
        """
        return product.get_product_multiline_description_sale() + self._get_sale_order_line_multiline_description_variants()

    def _get_sale_order_line_multiline_description_variants(self):
        """When using no_variant attributes or is_custom values, the product
        itself is not sufficient to create the description: we need to add
        information about those special attributes and values.

        :return: the description related to special variant attributes/values
        :rtype: string
        """
        if not self.product_custom_attribute_value_ids and not self.product_no_variant_attribute_value_ids:
            return ""

        name = "\n"

        custom_ptavs = self.product_custom_attribute_value_ids.custom_product_template_attribute_value_id
        no_variant_ptavs = self.product_no_variant_attribute_value_ids._origin

        # display the no_variant attributes, except those that are also
        # displayed by a custom (avoid duplicate description)
        for ptav in (no_variant_ptavs - custom_ptavs):
            name += "\n" + ptav.with_context(lang=self.order_id.partner_id.lang).display_name

        # display the is_custom values
        for pacv in self.product_custom_attribute_value_ids:
            name += "\n" + pacv.with_context(lang=self.order_id.partner_id.lang).display_name

        return name

    def _compute_tax_id(self):
        for line in self:
            line = line.with_company(line.company_id)
            fpos = line.order_id.fiscal_position_id or line.order_id.fiscal_position_id.get_fiscal_position(
                line.order_partner_id.id)
            # If company_id is set, always filter taxes by the company
            taxes = line.product_id.taxes_id.filtered(lambda t: t.company_id == line.env.company)
            line.tax_id = fpos.map_tax(taxes, line.product_id, line.order_id.partner_id)

    def _get_display_price(self, product):
        # TO DO: move me in master/saas-16 on sale.order
        # awa: don't know if it's still the case since we need the "product_no_variant_attribute_value_ids" field now
        # to be able to compute the full price

        # it is possible that a no_variant attribute is still in a variant if
        # the type of the attribute has been changed after creation.
        no_variant_attributes_price_extra = [
            ptav.price_extra for ptav in self.product_no_variant_attribute_value_ids.filtered(
                lambda ptav:
                ptav.price_extra and
                ptav not in product.product_template_attribute_value_ids
            )
        ]
        if no_variant_attributes_price_extra:
            product = product.with_context(
                no_variant_attributes_price_extra=tuple(no_variant_attributes_price_extra)
            )

        if self.order_id.pricelist_id.discount_policy == 'with_discount':
            return product.with_context(pricelist=self.order_id.pricelist_id.id).price
        product_context = dict(self.env.context, partner_id=self.order_id.partner_id.id, date=self.order_id.date_order,
                               uom=self.product_uom.id)

        final_price, rule_id = self.order_id.pricelist_id.with_context(product_context).get_product_price_rule(
            product or self.product_id, self.product_uom_qty or 1.0, self.order_id.partner_id)
        base_price, currency = self.with_context(product_context)._get_real_price_currency(product, rule_id,
                                                                                           self.product_uom_qty,
                                                                                           self.product_uom,
                                                                                           self.order_id.pricelist_id.id)
        if currency != self.order_id.pricelist_id.currency_id:
            base_price = currency._convert(
                base_price, self.order_id.pricelist_id.currency_id,
                self.order_id.company_id or self.env.company, self.order_id.date_order or fields.Date.today())
        # negative discounts (= surcharge) are included in the display price
        return max(base_price, final_price)

    @api.onchange('product_uom', 'product_uom_qty')
    def product_uom_change(self):
        if not self.product_uom or not self.product_id:
            self.price_unit = 0.0
            return
        if self.order_id.pricelist_id and self.order_id.partner_id:
            product = self.product_id.with_context(
                lang=self.order_id.partner_id.lang,
                partner=self.order_id.partner_id,
                quantity=self.product_uom_qty,
                date=self.order_id.date_order,
                pricelist=self.order_id.pricelist_id.id,
                uom=self.product_uom.id,
                fiscal_position=self.env.context.get('fiscal_position')
            )
            self.price_unit = self.env['account.tax']._fix_tax_included_price_company(self._get_display_price(product),
                                                                                      product.taxes_id, self.tax_id,
                                                                                      self.company_id)


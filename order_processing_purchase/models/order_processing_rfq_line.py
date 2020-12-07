# -*- coding: utf-8 -*-

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.tools.misc import formatLang, get_lang


class OrderProcessingRFQ(models.Model):
    _name = 'order.processing.rfq.line'
    _description = 'Order Processing RFQ Line'
    _order = 'order_id, sequence, id'
    _check_company_auto = True

    name = fields.Text(string='Description', required=True)
    sequence = fields.Integer(string='Sequence', default=1)
    sequence_number = fields.Integer(string='#', related='sequence', readonly=False)
    product_id = fields.Many2one('product.product', string='Product', domain=[('purchase_ok', '=', True)],
                                 change_default=True)
    default_code = fields.Char('Part No')
    product_uom_qty = fields.Float(string='Total Quantity', compute='_compute_product_uom_qty', store=True)
    company_id = fields.Many2one(
        'res.company', required=True, default=lambda self: self.env.company
    )
    partner_id = fields.Many2one('res.partner', 'Vendor', ondelete='cascade', required=True,
                                 help="Vendor of this product",
                                 check_company=True)
    product_qty = fields.Float(string='Quantity', digits='Product Unit of Measure', required=True)
    product_uom = fields.Many2one('uom.uom', string='Unit of Measure')
    taxes_id = fields.Many2many('account.tax', string='Taxes',
                                domain=['|', ('active', '=', False), ('active', '=', True)])
    price_unit = fields.Float(string='Unit Price', required=True, digits='Product Price')

    price_subtotal = fields.Monetary(compute='_compute_amount', string='Subtotal', store=True)
    price_total = fields.Monetary(compute='_compute_amount', string='Total', store=True)
    price_tax = fields.Float(compute='_compute_amount', string='Tax', store=True)

    order_id = fields.Many2one('order.processing', string='Order Processing Reference', index=True, required=True,
                               ondelete='cascade')
    currency_id = fields.Many2one('res.currency', 'Currency', required=True,
                                  default=lambda self: self.env.company.currency_id.id)
    display_type = fields.Selection([
        ('line_section', "Section"),
        ('line_note', "Note")], default=False, help="Technical field for UX purpose.")

    @api.depends('product_qty', 'price_unit', 'taxes_id')
    def _compute_amount(self):
        for line in self:
            vals = line._prepare_compute_all_values()
            taxes = line.taxes_id.compute_all(
                vals['price_unit'],
                vals['currency_id'],
                vals['product_qty'],
                vals['product'],
                vals['partner'])
            line.update({
                'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                'price_total': taxes['total_included'],
                'price_subtotal': taxes['total_excluded'],
            })

    def _prepare_compute_all_values(self):
        self.ensure_one()
        return {
            'price_unit': self.price_unit,
            'currency_id': self.order_id.currency_id,
            'product_qty': self.product_qty,
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
        self.price_unit = self.product_id.standard_price
        for seller in self.product_id.seller_ids:
            if seller.name == self.partner_id:
                self.price_unit = seller.price
                self.currency_id = seller.currency_id.id

    def _get_product_price(self):
        price = self.product_id.standard_price
        for seller in self.product_id.seller_ids:
            if seller.name == self.partner_id:
                price = seller.price
        return price

    @api.onchange('product_id')
    def onchange_product_id(self):
        if not self.product_id:
            return
        self.product_uom = self.product_id.uom_po_id or self.product_id.uom_id
        self.price_unit = self._get_product_price()
        self.default_code = self.product_id.default_code
        product_lang = self.product_id.with_context(
            lang=get_lang(self.env, self.partner_id.lang).code,
            partner_id=self.partner_id.id,
            company_id=self.company_id.id,
        )
        self.name = self._get_product_purchase_description(product_lang)
        self.product_qty = 1.0
        self.taxes_id = self.product_id.supplier_taxes_id

from odoo import api, fields, models, tools, SUPERUSER_ID


class OrderProcessing(models.Model):
    _inherit = "order.processing"

    @api.depends('order_line_rfq.price_total')
    def _amount_all_rfq(self):
        for order in self:
            amount_untaxed = amount_tax = 0.0
            for line in order.order_line_rfq:
                line._compute_amount()
                amount_untaxed += line.price_subtotal
                amount_tax += line.price_tax
            order.update({
                'amount_untaxed_rfq': order.currency_id.round(amount_untaxed),
                'amount_tax_rfq': order.currency_id.round(amount_tax),
                'amount_total_rfq': amount_untaxed + amount_tax,
            })

    # RFQ
    order_line_rfq = fields.One2many('order.processing.rfq.line', 'order_id', string='Order Processing RFQ', copy=True)
    amount_untaxed_rfq = fields.Monetary(string='Untaxed Amount', store=True, readonly=True, compute='_amount_all_rfq',
                                         tracking=True)
    amount_tax_rfq = fields.Monetary(string='Taxes', store=True, readonly=True, compute='_amount_all_rfq')
    amount_total_rfq = fields.Monetary(string='Total', store=True, readonly=True, compute='_amount_all_rfq')

    # purchase term
    purchase_term_ids = fields.One2many('purchase.term', 'order_processing_id', string='Purchase term')

    # supplierinfo
    @api.model
    def _get_supplier_info(self):
        return self.env['product.supplierinfo'].search([])

    supplier_info_ids = fields.One2many('product.supplierinfo', 'order_processing_id', default=_get_supplier_info)
    purchase_count = fields.Integer(compute='_compute_purchase_count')

    def _compute_purchase_count(self):
        for record in self:
            record.purchase_count = self.env['purchase.order'].search_count(
                [('order_processing_id', '=', self.id)])

    def action_purchase_count(self):
        """Action smart button Purchase Order"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Purchase',
            'view_mode': 'tree,form',
            'res_model': 'purchase.order',
            'domain': [('order_processing_id', '=', self.id)],
            'context': {}
        }

    def _group_by_supplier_and_currency(self):
        '''
        This function allows you to group the product lines selected in the RFQ page by supplier and currency
        '''
        supplier_list = list(set(self.order_line_rfq.partner_id))
        currency_list = list(set(self.order_line_rfq.currency_id))
        group_by_supplier = []
        group_by_supplier_and_currency = []
        for supplier in supplier_list:
            group_by_supplier.append(self.order_line_rfq.filtered(lambda x: x.partner_id == supplier))
        for currency in currency_list:
            for gbs in group_by_supplier:
                gbs_filtered = gbs.filtered(lambda x: x.currency_id == currency)
                if gbs_filtered:
                    group_by_supplier_and_currency.append(gbs_filtered)
        if group_by_supplier_and_currency:
            return group_by_supplier_and_currency
        return False

    def action_create_rfq(self):
        '''
        This function is an action of the button create purchase order in the RFQ page of the form view of
        'order.processing' which allows to create a purchase order with the lines of the selected products
        '''
        if not self.order_line_rfq:
            return

        # delete the order line which has been deleted since the rfq
        # deleted_order_line = self.env['purchase.order'].search(
        #     [('order_processing_id', '=', self.id), ('state', 'in', ['draft', 'sent'])]).order_line.filtered(
        #     lambda x: x.processing_rfq_line_id.id not in self.order_line_rfq.ids)
        # if deleted_order_line:
        #     deleted_order_line.unlink()

        # Group RFQ lines by supplier and currency
        purchase_list = self._group_by_supplier_and_currency()

        for purchase in purchase_list:
            for p in purchase:
                purchase_id = self.env['purchase.order'].search(
                    [('order_processing_id', '=', self.id), ('partner_id', '=', p.partner_id.id),
                     ('currency_id', '=', p.currency_id.id), ('state', 'in', ['draft', 'sent'])])
                if not purchase_id:
                    purchase_id = self.env['purchase.order'].sudo().create({
                        'partner_id': p.partner_id.id,
                        'currency_id': p.currency_id.id,
                        'order_processing_id': self.id
                    })
                purchase_order_line_id = self.env['purchase.order.line'].search(
                    [('order_id', '=', purchase_id.id), ('processing_rfq_line_id', '=', p.id)])
                vals = {
                    'processing_rfq_line_id': p.id,
                    'sequence': p.sequence,
                    'order_id': purchase_id.id,
                    'product_id': p.product_id.id,
                    'default_code': p.default_code,
                    'name': p.name,
                    'product_qty': p.product_qty,
                    'product_uom': p.product_uom.id,
                    'price_unit': p.price_unit,
                    'price_subtotal': p.price_subtotal,
                    'taxes_id': [(6, 0, p.taxes_id.ids)],
                }
                if purchase_order_line_id:
                    purchase_order_line_id.sudo().write(vals)
                else:
                    self.env['purchase.order.line'].sudo().create(vals)

            # Update purchase_term_ids in purchase.order
            if purchase_id:
                purchase_id.sudo().write({'purchase_term_ids': [(6, 0, self.purchase_term_ids.ids)]})

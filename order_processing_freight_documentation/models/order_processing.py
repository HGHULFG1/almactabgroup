from odoo import api, fields, models, tools, SUPERUSER_ID


class OrderProcessing(models.Model):
    _inherit = "order.processing"

    freight_documentation_ids = fields.One2many('freight.documentation', 'order_id', copy=True)

    amount_untaxed_freight_cost = fields.Monetary(string='Untaxed Amount', store=True, readonly=True, tracking=True)
    amount_tax_freight_cost = fields.Monetary(string='Taxes', store=True, readonly=True)
    amount_total_freight_cost = fields.Monetary(string='Total', store=True, readonly=True)

    amount_untaxed_freight_sale = fields.Monetary(string='Untaxed Amount', store=True, readonly=True,
                                              compute='_amount_all_freight_sale', tracking=5)
    amount_tax_freight_sale = fields.Monetary(string='Taxes', store=True, readonly=True, compute='_amount_all_freight_sale')
    amount_total_freight_sale = fields.Monetary(string='Total', store=True, readonly=True, compute='_amount_all_freight_sale',
                                            tracking=4)

    amount_total_margin = fields.Monetary(string='Total', store=True, readonly=True, compute='_amount_total_margin',
                                          tracking=4)

    @api.depends('freight_documentation_ids.price_total_sale', 'freight_documentation_ids.price_total_cost')
    def _amount_all_freight_sale(self):
        """
        Compute the total amounts of the SO.
        """
        for order in self:
            amount_untaxed_sale = amount_untaxed_cost = amount_tax_sale = amount_tax_cost = 0.0
            for line in order.freight_documentation_ids:
                amount_untaxed_sale += line.price_subtotal_sale
                amount_untaxed_cost += line.price_subtotal_cost
                amount_tax_sale += line.price_tax_sale
                amount_tax_cost += line.price_tax_cost
            order.update({
                'amount_untaxed_freight_sale': amount_untaxed_sale,
                'amount_tax_freight_sale': amount_tax_sale,
                'amount_total_freight_sale': amount_untaxed_sale + amount_tax_sale,
                'amount_untaxed_freight_cost': amount_untaxed_cost,
                'amount_tax_freight_cost': amount_tax_cost,
                'amount_total_freight_cost': amount_untaxed_cost + amount_tax_cost,
            })

    @api.depends('amount_total_freight_cost', 'amount_total_freight_sale')
    def _amount_total_margin(self):
        for record in self:
            record.amount_total_margin = record.amount_total_freight_sale - record.amount_total_freight_cost

    def action_create_rfq_with_freight_documentation(self):
        if not self.freight_documentation_ids:
            return
        for line in self.freight_documentation_ids:

            purchase_id = self.env['purchase.order'].search(
                [('order_processing_id', '=', self.id), ('partner_id', '=', line.partner_id.id),
                 ('currency_id', '=', line.currency_id.id), ('state', 'in', ['draft', 'sent'])])
            vals = {
                'sequence': line.sequence,
                'product_id': line.product_id.id,
                'default_code': line.default_code,
                'name': line.name,
                'product_qty': line.product_uom_qty,
                'product_uom': line.product_uom.id,
                'price_unit': line.price_cost,
                'price_subtotal': line.price_subtotal_cost,
                'currency_id': line.currency_id.id,
                'company_id': line.company_id.id,
                'partner_id': line.partner_id.id,
                'taxes_id': [(6, 0, line.tax_id.ids)],
                'freight_documentation_id': line.id
            }

            if purchase_id:
                vals['order_id'] = purchase_id.id
                purchase_order_line_id = self.env['purchase.order.line'].search(
                    [('order_id', '=', purchase_id.id), ('freight_documentation_id', '=', line.id)])

                if purchase_order_line_id:
                    purchase_order_line_id.sudo().write(vals)
                else:
                    self.env['purchase.order.line'].sudo().create(vals)

                # delete the purchase order line which has been deleted since the rfq
                # deleted_order_line = purchase_id.order_line.filtered(
                #     lambda x: x.freight_documentation_id.id not in self.freight_documentation_ids.ids)
                # if deleted_order_line:
                #     deleted_order_line.unlink()
            else:
                purchase_id = self.env['purchase.order'].sudo().create({
                    'order_processing_id': self.id,
                    'partner_id': line.partner_id.id,
                    'currency_id': line.currency_id.id,
                })
                vals['order_id'] = purchase_id.id
                self.env['purchase.order.line'].sudo().create(vals)

        return True

    def action_create_quotation_with_freight_documentation(self):
        if not self.freight_documentation_ids:
            return

        order_id = self.env['sale.order'].search(
            [('order_processing_id', '=', self.id), ('state', 'in', ['draft', 'sent'])])
        if order_id:
            self._write_quotation_with_freight_documentation(order_id)
        else:
            order_id = self.env['sale.order'].search(
                [('order_processing_id', '=', self.id), ('state', 'not in', ['draft', 'sent'])])
            if order_id:
                return {'type': 'ir.actions.act_window',
                        'name': _('Update sale order'),
                        'res_model': 'order.processing.sale.wizard',
                        'target': 'new',
                        'view_id': self.env.ref('order_processing_sale.view_order_processing_sale_wizard').id,
                        'view_mode': 'form',
                        }
            else:
                order_id = self._create_quotation_with_freight_documentation()
        self._create_sale_order_line_with_freight_documentation(order_id)

        return True

    def _create_quotation_with_freight_documentation(self):
        return self.env['sale.order'].sudo().create({
            'partner_id': self.partner_id.id,
            'pricelist_id': self.pricelist_id.id,
            'team_id': self.team_id.id,
            'currency_id': self.currency_id.id,
            'bank_account_id': self.bank_account_id.id,
            'user_id': self.user_id.id,
            'order_processing_id': self.id
        })

    def _create_sale_order_line_with_freight_documentation(self, order_id):
        line_ids = order_id.order_line_freight_documentation
        for line in self.freight_documentation_ids:
            vals = {
                'is_freight_documentation': True,
                'sequence': line.sequence,
                'product_id': line.product_id.id,
                'default_code': line.default_code,
                'name': line.name,
                'order_partner_id': line.order_partner_id.id,
                'price_subtotal': line.price_subtotal_sale,
                'price_total': line.price_total_sale,
                'price_tax': line.price_tax_sale,
                'price_unit': line.price_unit,
                'tax_id': [(6, 0, line.tax_id.ids)],
                'product_uom': line.product_uom.id,
                'company_id': line.company_id.id,
                'product_uom_qty': line.product_uom_qty,
            }
            if line.sale_order_line_id.id in line_ids.ids:
                self.env['sale.order.line'].browse(line.sale_order_line_id.id).sudo().write(vals)
            else:
                vals['order_id'] = order_id.id
                sale_order_line_id = self.env['sale.order.line'].sudo().create(vals)
                if sale_order_line_id:
                    line.sudo().write({'sale_order_line_id': sale_order_line_id.id})

    def _write_quotation_with_freight_documentation(self, order_id):
        order_id.sudo().write({
            'partner_id': self.partner_id.id,
            'pricelist_id': self.pricelist_id.id,
            'team_id': self.team_id.id,
            'currency_id': self.currency_id.id,
            'bank_account_id': self.bank_account_id.id,
            'user_id': self.user_id.id,
            'order_processing_id': self.id
        })

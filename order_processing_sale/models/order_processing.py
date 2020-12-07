from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.addons.crm.models import crm_stage


class OrderProcessing(models.Model):
    _inherit = "order.processing"

    # sale term
    sale_term_ids = fields.One2many('sale.term', 'order_processing_id', string='Sale term')

    # Sale Order Line
    order_processing_sale_line = fields.One2many('order.processing.sale.line', 'order_id', string='Sale Order Line',
                                                 copy=True)
    pricelist_id = fields.Many2one(
        'product.pricelist', string='Pricelist', check_company=True,  # Unrequired company
        readonly=False,
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]", tracking=1,
        help="If you change the pricelist, only newly added lines will be affected.")

    date_order = fields.Datetime(string='Order Date', required=True, readonly=True, index=True, copy=False,
                                 default=fields.Datetime.now,
                                 help="Creation date of draft/sent orders,\nConfirmation date of confirmed orders.")

    fiscal_position_id = fields.Many2one(
        'account.fiscal.position', string='Fiscal Position',
        domain="[('company_id', '=', company_id)]", check_company=True,
        help="Fiscal positions are used to adapt taxes and accounts for particular customers or sales orders/invoices."
             "The default value comes from the customer.")

    amount_untaxed_sale = fields.Monetary(string='Untaxed Amount', store=True, readonly=True,
                                          compute='_amount_all_sale',
                                          tracking=5)
    amount_tax_sale = fields.Monetary(string='Taxes', store=True, readonly=True, compute='_amount_all_sale')
    amount_total_sale = fields.Monetary(string='Total', store=True, readonly=True, compute='_amount_all_sale',
                                        tracking=4)
    bank_account_id = fields.Many2one(
        'res.partner.bank', 'Bank Account Number',
        domain="[('company_id', '=', company_id)]",
        tracking=True,
        help='Employee bank salary account')

    @api.depends('order_processing_sale_line.price_total')
    def _amount_all_sale(self):
        """
        Compute the total amounts of the SO.
        """
        for order in self:
            amount_untaxed = amount_tax = 0.0
            for line in order.order_processing_sale_line:
                amount_untaxed += line.price_subtotal
                amount_tax += line.price_tax
            order.update({
                'amount_untaxed_sale': amount_untaxed,
                'amount_tax_sale': amount_tax,
                'amount_total_sale': amount_untaxed + amount_tax,
            })

    sale_count = fields.Integer(compute='_compute_sale_count')

    def _compute_sale_count(self):
        for record in self:
            record.sale_count = self.env['sale.order'].search_count(
                [('order_processing_id', '=', self.id)])

    def action_sale_count(self):
        """Action smart button Sale Order"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Quotations',
            'view_mode': 'tree,form',
            'res_model': 'sale.order',
            'domain': [('order_processing_id', '=', self.id)],
            'context': {}
        }

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        """
        Update the following fields when the partner is changed:
        - Pricelist
        """
        if not self.partner_id:
            self.update({
                'fiscal_position_id': False,
            })
            return

        self = self.with_company(self.company_id)

        partner_user = self.partner_id.user_id or self.partner_id.commercial_partner_id.user_id
        values = {
            'pricelist_id': self.partner_id.property_product_pricelist and self.partner_id.property_product_pricelist.id or False,
        }
        user_id = partner_user.id
        if not self.env.context.get('not_self_saleperson'):
            user_id = user_id or self.env.uid
        if user_id and self.user_id.id != user_id:
            values['user_id'] = user_id

        if not self.env.context.get('not_self_saleperson') or not self.team_id:
            values['team_id'] = self.env['crm.team']._get_default_team_id(
                domain=['|', ('company_id', '=', self.company_id.id), ('company_id', '=', False)], user_id=user_id)
        self.update(values)

    def _create_quotation(self):
        return self.env['sale.order'].sudo().create({
            'partner_id': self.partner_id.id,
            'pricelist_id': self.pricelist_id.id,
            'team_id': self.team_id.id,
            'currency_id': self.currency_id.id,
            'bank_account_id': self.bank_account_id.id,
            'user_id': self.user_id.id,
            'order_processing_id': self.id
        })

    def _write_quotation(self, order_id):
        order_id.sudo().write({
            'partner_id': self.partner_id.id,
            'pricelist_id': self.pricelist_id.id,
            'team_id': self.team_id.id,
            'currency_id': self.currency_id.id,
            'bank_account_id': self.bank_account_id.id,
            'user_id': self.user_id.id,
            'order_processing_id': self.id
        })

    def _create_sale_order_line(self, order_id):
        line_ids = order_id.order_line
        sale_order_line_ids = []
        for line in self.order_processing_sale_line:
            vals = {
                'processing_sale_line_id': line.id,
                'sequence': line.sequence,
                'product_id': line.product_id.id,
                'default_code': line.default_code,
                'name': line.name,
                'order_partner_id': line.order_partner_id.id,
                'price_subtotal': line.price_subtotal,
                'price_total': line.price_total,
                'price_tax': line.price_tax,
                'price_unit': line.price_unit,
                'tax_id': [(6, 0, line.tax_id.ids)],
                'product_uom': line.product_uom.id,
                'company_id': line.company_id.id,
                'product_uom_qty': line.product_uom_qty,
            }
            if line.sale_order_line_id.id in line_ids.ids:
                self.env['sale.order.line'].browse(line.sale_order_line_id.id).sudo().write(vals)
                sale_order_line_ids.append(line.sale_order_line_id.id)
            else:
                vals['order_id'] = order_id.id
                sale_order_line_id = self.env['sale.order.line'].sudo().create(vals)
                sale_order_line_ids.append(sale_order_line_id.id)
                if sale_order_line_id:
                    line.sudo().write({'sale_order_line_id': sale_order_line_id.id})

        # drop_ids = [so.id for so in line_ids if so.id not in sale_order_line_ids]
        # if drop_ids:
        #     self.env['sale.order.line'].browse(drop_ids).unlink()

    def action_create_quotation(self):
        if not self.order_processing_sale_line:
            return

        order_id = self.env['sale.order'].search(
            [('order_processing_id', '=', self.id), ('state', 'in', ['draft', 'sent'])])
        if order_id:
            self._write_quotation(order_id)
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
                order_id = self._create_quotation()
        self._create_sale_order_line(order_id)
        if order_id:
            order_id.sudo().write({'sale_term_ids': [(6, 0, self.sale_term_ids.ids)]})

    def update_product_line_rfq_to_sale(self):
        if self.order_line_rfq:
            for line in self.order_line_rfq:
                vals = {'sequence': line.sequence,
                        'product_id': line.product_id.id,
                        'default_code': line.default_code,
                        'name': line.name,
                        'order_partner_id': line.partner_id.id,
                        'product_uom_qty': line.product_qty,
                        'price_unit': line.price_unit,
                        'tax_id': [(6, 0, line.taxes_id.ids)],
                        'price_tax': line.price_tax,
                        'price_subtotal': line.price_subtotal,
                        'price_total': line.price_total,
                        'product_uom': line.product_uom.id,
                        'company_id': line.company_id.id,
                        }
                sale_line = self.env['order.processing.sale.line'].search(
                    [('rfq_line_id', '=', line.id), ('order_id', '=', self.id)])
                if sale_line:
                    self.order_processing_sale_line.sudo().write(vals)
                else:
                    vals['order_id'] = self.id,
                    vals['rfq_line_id'] = line.id
                    self.env['order.processing.sale.line'].sudo().create(vals)

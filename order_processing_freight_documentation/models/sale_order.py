# -*- coding: utf-8 -*-


from odoo import api, fields, models, SUPERUSER_ID, _


class SaleOrder(models.Model):
    _inherit = "sale.order"


    order_line = fields.One2many('sale.order.line', 'order_id', string='Order Lines',
                                 domain=[('is_freight_documentation', '=', False)],
                                 states={'cancel': [('readonly', True)], 'done': [('readonly', True)]}, copy=True,
                                 auto_join=True)

    order_line_freight_documentation = fields.One2many('sale.order.line', 'order_id', string='Order Lines',
                                 domain=[('is_freight_documentation', '=', True)],
                                 readonly=True, copy=True,
                                 auto_join=True)
    amount_untaxed_cost = fields.Monetary(string='Untaxed Amount', store=True, readonly=True, compute='_amount_all_freight_documentation',
                                     tracking=5)
    amount_tax_cost = fields.Monetary(string='Taxes', store=True, readonly=True, compute='_amount_all_freight_documentation')
    amount_total_cost = fields.Monetary(string='Total', store=True, readonly=True, compute='_amount_all_freight_documentation', tracking=4)
    @api.depends('order_line_freight_documentation.price_total')
    def _amount_all_freight_documentation(self):
        """
        Compute the total amounts of the SO.
        """
        for order in self:
            amount_untaxed_cost = amount_tax_cost = 0.0
            for line in order.order_line_freight_documentation:
                amount_untaxed_cost += line.price_subtotal
                amount_tax_cost += line.price_tax
            order.update({
                'amount_untaxed_cost': amount_untaxed_cost,
                'amount_tax_cost': amount_tax_cost,
                'amount_total_cost': amount_untaxed_cost + amount_tax_cost,
            })
    @api.depends('order_line.price_total')
    def _amount_all(self):
        """
        Compute the total amounts of the SO.
        """
        for order in self:
            amount_untaxed = amount_tax = 0.0
            for line in order.order_line:
                amount_untaxed += line.price_subtotal
                amount_tax += line.price_tax
            order.update({
                'amount_untaxed': amount_untaxed,
                'amount_tax': amount_tax,
                'amount_total': amount_untaxed + amount_tax + self.amount_total_cost,
            })

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    is_freight_documentation = fields.Boolean('Is coming from freight and documentation', default=False)

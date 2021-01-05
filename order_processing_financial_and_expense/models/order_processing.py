from odoo import api, fields, models, tools, SUPERUSER_ID


class OrderProcessing(models.Model):
    _inherit = "order.processing"

    expense_line = fields.One2many('expense', 'order_id', copy=True)
    amount_subtotal_expense = fields.Monetary(string='Total', store=True, readonly=True, compute='_amount_all_expense',
                                              tracking=4)
    amount_total_income = fields.Monetary(string='Total', store=True, readonly=True, compute='_amount_total_income',
                                          tracking=4)
    amount_total_expenses = fields.Monetary(string='Total Expenses', store=True, readonly=True,
                                            compute='_amount_total_expenses',
                                            tracking=4)
    amount_total_net_profit = fields.Monetary(string='Total Expenses', store=True, readonly=True,
                                            compute='_amount_total_net_profit',
                                            tracking=4)

    @api.depends('expense_line.price_subtotal')
    def _amount_all_expense(self):
        for order in self:
            amount_subtotal_expense = 0.0
            for line in order.expense_line:
                amount_subtotal_expense += line.price_subtotal

            order.update({
                'amount_subtotal_expense': amount_subtotal_expense,
            })

    @api.depends('amount_total_sale', 'amount_total_freight_sale')
    def _amount_total_income(self):
        for order in self:
            order.update({
                'amount_total_income': order.amount_total_sale + order.amount_total_freight_sale,
            })

    @api.depends('amount_total_rfq', 'amount_total_freight_cost', 'amount_subtotal_expense')
    def _amount_total_expenses(self):
        for order in self:
            order.update({
                'amount_total_expenses': order.amount_total_rfq + order.amount_total_freight_cost + order.amount_subtotal_expense,
            })

    @api.depends('amount_total_income', 'amount_total_expenses')
    def _amount_total_net_profit(self):
        for order in self:
            order.update({
                'amount_total_net_profit': order.amount_total_income - order.amount_total_expenses,
            })

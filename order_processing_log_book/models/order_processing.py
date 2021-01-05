# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class OrderProcessing(models.Model):
    _name = 'order.processing'
    _inherit = 'order.processing'

    log_book_line = fields.One2many('log.book', 'order_id', string='Log Book Line', copy=True)
    log_book_id = fields.Many2one('log.book',string='Last log book status',index=True,compute='_compute_loog_book')

    @api.depends('log_book_line')
    def _compute_loog_book(self):
        for record in self:
            if record.log_book_line:
                record.log_book_id = record.log_book_line[0].id
            else:
                record.log_book_id = None


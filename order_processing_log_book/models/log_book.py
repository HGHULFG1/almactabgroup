from odoo import api, fields, models, _


class LogBookType(models.Model):
    _name = 'log.book.type'

    name = fields.Char('Type Name')

class LogBook(models.Model):
    _name = 'log.book'
    _description = 'Log Book'
    _order = 'date_deadline DESC'

    date_deadline = fields.Date('Due Date', index=True, required=True, default=fields.Date.context_today)
    name = fields.Char('Log Description')
    note = fields.Html('Note', sanitize_style=True)
    user_id = fields.Many2one(
        'res.users', 'Responsible',
        default=lambda self: self.env.user,
        index=True, required=True)
    log_book_type_id = fields.Many2one('log.book.type', string='Type', ondelete='restrict')
    order_id = fields.Many2one('order.processing', string='Order Reference', required=True, ondelete='cascade',
                               index=True, copy=False)

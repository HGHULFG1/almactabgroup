from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.exceptions import ValidationError


class ProductCategory(models.Model):
    _inherit = 'product.category'

    markup = fields.Float('Markup %', default=0, readonly=False, store=True)
    custom_fees = fields.Float('Custom Fees', default=0, readonly=False, store=True)

    @api.constrains('markup')
    def _check_markup_value(self):
        if self.markup > 1.0:
            raise ValidationError(_('You can not set markup bigger than 1.'))

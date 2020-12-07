from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class PackingType(models.Model):
    _name = 'packing.type'

    name = fields.Char('Name', required=True)


class PackingMarks(models.Model):
    _name = 'packing.marks'

    name = fields.Char('Reference', required=True)


class SaleMarketLine(models.Model):
    _name = 'packing'
    _description = 'Packing'
    _order = 'order_id, sequence, id'

    order_id = fields.Many2one('order.processing', string='Order Processing Reference', required=True,
                               ondelete='cascade', index=True,
                               copy=False)
    name = fields.Text('Description')
    sequence = fields.Integer(string='Sequence', default=1)
    sequence_number = fields.Integer(string='#', related='sequence', readonly=False)
    country_id = fields.Many2one('res.country', string='Country', store=True)
    default_code = fields.Char('Part No')
    product_id = fields.Many2one('product.product', string="Product")
    product_uom_qty = fields.Float(string='Quantity', digits='Product Unit of Measure', required=True, default=1.0)
    type_id = fields.Many2one('packing.type', string='Type')
    package_numero = fields.Integer(string="Package No")
    marks_id = fields.Many2one('packing.marks', string='Marks')
    container_id = fields.Many2one('container', string='Container')
    width_pack = fields.Float('Width')
    height_pack = fields.Float('Height')
    length_pack = fields.Float('Length')
    weight_pack = fields.Float('Weight')

    display_type = fields.Selection([
        ('line_section', "Section"),
        ('line_note', "Note")], default=False, help="Technical field for UX purpose.")

    @api.onchange('product_id')
    def product_id_change(self):
        if not self.product_id:
            return
        self.name = self.product_id.display_name
        self.default_code = self.product_id.default_code

    def group_packing_by_container_marks(self):
        res = []
        if self:
            list_marks = list(set(self.marks_id))
            list_container = list(set(self.container_id))
            for c in list_container:
                container = self.filtered(lambda p: p.container_id.id == c.id)
                if container:
                    marks = []
                    for m in list_marks:
                        mar = container.filtered(lambda x: x.marks_id.id == m.id)
                        if mar:
                            marks.append(mar)
                    res.append({'container': c, 'marks': marks})
        return res

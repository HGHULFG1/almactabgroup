from odoo import api, fields, models, tools, SUPERUSER_ID


class OrderProcessingSaleWizard(models.TransientModel):
   _name = 'order.processing.sale.wizard'

   order_processing_id = fields.Many2one('order.processing')


   # Method to mark the mrp orders as done
   def action_done(self):
       active_id = self.env.context.get('active_id')
       active_model = self.env.context.get('active_model')
       order_processing_id = self.env[active_model].search([('id','=',int(active_id))])

       order_id = order_processing_id._create_quotation()

       order_processing_id._create_sale_order_line(order_id)
       if order_id:
           order_id.sudo().write({'sale_term_ids': [(6, 0, order_processing_id.sale_term_ids.ids)]})

       # for line in self.produce_line_ids.mapped('production_id'):
       #     line.button_mark_done()


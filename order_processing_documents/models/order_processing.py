# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class OrderProcessing(models.Model):
    _name = 'order.processing'
    _inherit = ['order.processing', 'documents.mixin']

    document_count = fields.Integer('Document Count', compute='_compute_document_count')
    folder_id = fields.Many2one('documents.folder', string="Workspace", ondelete="restrict", index=True)

    def _compute_document_count(self):
        for record in self:
            documents = self.env['documents.document'].search(
                [('folder_id', '=', record.folder_id.id)])
            record.document_count = len(documents)

    @api.model
    def create(self, vals):
        vals['folder_id'] = self.env['documents.folder'].sudo().create({'name': vals['name'],
                                                                        'parent_folder_id': self.env.ref(
                                                                            'order_processing_documents.documents_order_processing_folder').id}).id
        return super(OrderProcessing, self).create(vals)

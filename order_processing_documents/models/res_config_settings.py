# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    documents_order_processing_settings = fields.Boolean(
        related='company_id.documents_order_processing_settings', readonly=False, string="Order Processing")
    documents_order_processing_folder = fields.Many2one(
        'documents.folder', related='company_id.documents_order_processing_folder', readonly=False, string="order processing default workspace")

    @api.onchange('documents_order_processing_folder')
    def _onchange_documents_order_processing_folder(self):
        # Implemented in other order-processing-documents bridge modules
        pass

# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    def _domain_company(self):
        company = self.env.company
        return ['|', ('company_id', '=', False), ('company_id', '=', company)]

    documents_order_processing_settings = fields.Boolean()
    documents_order_processing_folder = fields.Many2one('documents.folder', string="Order Processing Workspace", domain=_domain_company,
                                          default=lambda self: self.env.ref('order_processing_documents.documents_order_processing_folder',
                                                                            raise_if_not_found=False))

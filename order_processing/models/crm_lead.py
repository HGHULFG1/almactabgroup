# -*- coding: utf-8 -*-
import json
import logging
from odoo import api, fields, models, _
import warnings
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError,Warning

class CrmLead(models.Model):
    _inherit = 'crm.lead'

    def action_create_order_processing(self):
        """This function is an action of the button create order processing in the form view of 'crm.lead' which allows
        to duplicate the lead in model 'order.processing' with all the necessary fields"""
        self.ensure_one()

        vals = {
            'name': self.name,
            'user_id': self.user_id.id,
            'user_email': self.user_email,
            'user_login': self.user_login,
            'company_id': self.company_id.id,
            'referred': self.referred,
            'description': self.description,
            'active': self.active,
            'type': self.type,
            'priority': self.priority,
            'team_id': self.team_id.id,
            'stage_id': self.stage_id.id,
            'probability': self.probability,
            'automated_probability': self.automated_probability,
            'is_automated_probability': self.is_automated_probability,
            'tag_ids': [(6, 0, self.tag_ids.ids)],
            'expected_revenue': self.expected_revenue,
            'company_currency': self.company_currency.id,
            'date_closed': self.date_closed,
            'date_action_last': self.date_action_last,
            'date_open': self.date_open,
            'day_open': self.day_open,
            'day_close': self.day_close,
            'date_last_stage_update': self.date_last_stage_update,
            'date_conversion': self.date_conversion,
            'date_deadline': self.date_deadline,
            'partner_id': self.partner_id.id,
            'partner_is_blacklisted': self.partner_is_blacklisted,
            'contact_name': self.contact_name,
            'partner_name': self.partner_name,
            'function': self.function,
            'title': self.title.id,
            'email_from': self.email_from,
            'phone': self.phone,
            'mobile': self.mobile,
            'phone_mobile_search': self.phone_mobile_search,
            'phone_state': self.phone_state,
            'email_state': self.email_state,
            'website': self.website,
            'lang_id': self.lang_id.id,
            'street': self.street,
            'street2': self.street2,
            'zip': self.zip,
            'city': self.city,
            'state_id': self.state_id.id,
            'country_id': self.country_id.id,
            'meeting_count': self.meeting_count,
            'lost_reason': self.lost_reason.id,
            'ribbon_message': self.ribbon_message,
            'day_open': self.day_open,
            'campaign_id': self.campaign_id.id,
            'medium_id': self.medium_id.id,
            'source_id': self.source_id.id
        }
        if self.env.user.id in self.env.ref('crm.group_use_recurring_revenues').users.ids:
            vals['recurring_revenue'] = self.recurring_revenue
            vals['recurring_plan'] = self.recurring_plan
        order_id = self.env['order.processing'].sudo().create(vals)
        if order_id:
            return {
                'name': self.display_name,
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'order.processing',
                'res_id': order_id.id,
                'target': 'current',
            }
        return False

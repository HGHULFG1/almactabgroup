from odoo import api, fields, models, tools, SUPERUSER_ID
from odoo.addons.crm.models import crm_stage
from datetime import date


class OrderProcessing(models.Model):
    _name = "order.processing"
    _description = "Order Processing"
    _order = "priority desc, id desc"
    _inherit = ['mail.thread.cc',
                'mail.thread.blacklist',
                'mail.thread.phone',
                'mail.activity.mixin',
                'utm.mixin',
                'format.address.mixin',
                'phone.validation.mixin']
    _primary_email = 'email_from'

    name = fields.Char('Name', index=True, required=True, readonly=False, store=True)
    user_id = fields.Many2one('res.users', string='Salesperson', index=True, tracking=True,
                              default=lambda self: self.env.user)
    user_email = fields.Char('User Email', related='user_id.email', readonly=True)
    user_login = fields.Char('User Login', related='user_id.login', readonly=True)
    company_id = fields.Many2one('res.company', string='Company', index=True, default=lambda self: self.env.company.id)
    referred = fields.Char('Referred By')
    description = fields.Text('Notes')
    active = fields.Boolean('Active', default=True, tracking=True)
    type = fields.Selection([('lead', 'Lead'), ('opportunity', 'Opportunity')], index=True, required=True, tracking=15,
                            default=lambda self: 'lead' if self.env['res.users'].has_group(
                                'crm.group_use_lead') else 'opportunity')
    priority = fields.Selection(
        crm_stage.AVAILABLE_PRIORITIES, string='Priority', index=True,
        default=crm_stage.AVAILABLE_PRIORITIES[0][0])
    team_id = fields.Many2one('crm.team', string='Sales Team', index=True, tracking=True, readonly=False, store=True)
    stage_id = fields.Many2one(
        'order.processing.stage', string='Stage', index=True, tracking=True,
        compute='_compute_stage_id', readonly=False, store=True,
        copy=False, group_expand='_read_group_stage_ids', ondelete='restrict',
        domain="['|', ('team_id', '=', False), ('team_id', '=', team_id)]")
    kanban_state = fields.Selection([
        ('grey', 'No next activity planned'),
        ('red', 'Next activity late'),
        ('green', 'Next activity is planned')], string='Kanban State',
        compute='_compute_kanban_state')

    activity_date_deadline_my = fields.Date(
        'My Activities Deadline', compute='_compute_activity_date_deadline_my',
        search='_search_activity_date_deadline_my', compute_sudo=False,
        readonly=True, store=False, groups="base.group_user")
    tag_ids = fields.Many2many(
        'crm.tag', 'order_processing_crm_tag_rel', 'lead_id', 'tag_id', string='Tags',
        help="Classify and analyze your lead/opportunity categories like: Training, Service")
    color = fields.Integer('Color Index', default=0)
    expected_revenue = fields.Monetary('Expected Revenue', currency_field='company_currency', tracking=True)
    recurring_revenue = fields.Monetary('Recurring Revenues', currency_field='company_currency',
                                        groups="crm.group_use_recurring_revenues")
    recurring_plan = fields.Many2one('crm.recurring.plan', string="Recurring Plan",
                                     groups="crm.group_use_recurring_revenues")
    recurring_revenue_monthly = fields.Monetary('Expected MRR', currency_field='company_currency', store=True,
                                                compute="_compute_recurring_revenue_monthly",
                                                groups="crm.group_use_recurring_revenues")
    recurring_revenue_monthly_prorated = fields.Monetary('Prorated MRR', currency_field='company_currency', store=True,
                                                         compute="_compute_recurring_revenue_monthly_prorated",
                                                         groups="crm.group_use_recurring_revenues")
    company_currency = fields.Many2one("res.currency", string='Currency', related='company_id.currency_id',
                                       readonly=True)
    currency_id = fields.Many2one('res.currency', 'Currency', required=True,
                                  default=lambda self: self.env.company.currency_id.id)
    # Dates
    date_closed = fields.Datetime('Closed Date', readonly=True, copy=False)
    date_action_last = fields.Datetime('Last Action', readonly=True)
    date_open = fields.Datetime(
        'Assignment Date', compute='_compute_date_open', readonly=True, store=True)
    day_open = fields.Float('Days to Assign', compute='_compute_day_open', store=True)
    day_close = fields.Float('Days to Close', compute='_compute_day_close', store=True)
    date_last_stage_update = fields.Datetime(
        'Last Stage Update', compute='_compute_date_last_stage_update', index=True, readonly=True, store=True)
    date_conversion = fields.Datetime('Conversion Date', readonly=True)
    date_deadline = fields.Date('Expected Closing', help="Estimate of the date on which the opportunity will be won.")
    # Customer / contact
    partner_id = fields.Many2one('res.partner', string='Customer', index=True, tracking=10,
                                 domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
                                 help="Linked partner (optional). Usually created when converting the lead. You can find a partner by its Name, TIN, Email or Internal Reference.")
    partner_is_blacklisted = fields.Boolean('Partner is blacklisted', related='partner_id.is_blacklisted',
                                            readonly=True)
    contact_name = fields.Char(
        'Contact Name', tracking=30,
        compute='_compute_partner_id_values', readonly=False, store=True)
    partner_name = fields.Char('Company Name', tracking=20, index=True, compute='_compute_partner_id_values',
                               readonly=False, store=True,
                               help='The name of the future partner company that will be created while converting the lead into opportunity')
    function = fields.Char('Job Position', compute='_compute_partner_id_values', readonly=False, store=True)
    title = fields.Many2one('res.partner.title', string='Title', compute='_compute_partner_id_values', readonly=False,
                            store=True)
    email_from = fields.Char('Email', tracking=40, index=True, compute='_compute_email_from',
                             inverse='_inverse_email_from', readonly=False, store=True)
    phone = fields.Char('Phone', tracking=50, compute='_compute_phone', inverse='_inverse_phone', readonly=False,
                        store=True)
    mobile = fields.Char('Mobile', compute='_compute_partner_id_values', readonly=False, store=True)
    phone_mobile_search = fields.Char('Phone/Mobile', store=False, search='_search_phone_mobile_search')
    phone_state = fields.Selection([
        ('correct', 'Correct'),
        ('incorrect', 'Incorrect')], string='Phone Quality', compute="_compute_phone_state", store=True)
    email_state = fields.Selection([
        ('correct', 'Correct'),
        ('incorrect', 'Incorrect')], string='Email Quality', compute="_compute_email_state", store=True)
    website = fields.Char('Website', index=True, help="Website of the contact", compute="_compute_partner_id_values",
                          store=True, readonly=False)
    lang_id = fields.Many2one('res.lang', string='Language')
    # Address fields
    street = fields.Char('Street', compute='_compute_partner_id_values', readonly=False, store=True)
    street2 = fields.Char('Street2', compute='_compute_partner_id_values', readonly=False, store=True)
    zip = fields.Char('Zip', change_default=True, compute='_compute_partner_id_values', readonly=False, store=True)
    city = fields.Char('City', compute='_compute_partner_id_values', readonly=False, store=True)
    state_id = fields.Many2one(
        "res.country.state", string='State',
        compute='_compute_partner_id_values', readonly=False, store=True,
        domain="[('country_id', '=?', country_id)]")
    country_id = fields.Many2one(
        'res.country', string='Country',
        compute='_compute_partner_id_values', readonly=False, store=True)
    probability = fields.Float('Probability', group_operator="avg", copy=False, readonly=False, store=True)
    automated_probability = fields.Float('Automated Probability', readonly=True, store=True)
    is_automated_probability = fields.Boolean('Is automated probability?')
    # External record
    meeting_count = fields.Integer('# Meetings', compute='_compute_meeting_count')
    lost_reason = fields.Many2one(
        'crm.lost.reason', string='Lost Reason',
        index=True, ondelete='restrict', tracking=True)
    ribbon_message = fields.Char('Ribbon message')

    _sql_constraints = [
        ('check_probability', 'check(probability >= 0 and probability <= 100)',
         'The probability of closing the deal should be between 0% and 100%!')
    ]

    @api.depends('activity_date_deadline')
    def _compute_kanban_state(self):
        today = date.today()
        for order in self:
            kanban_state = 'grey'
            if order.activity_date_deadline:
                order_date = fields.Date.from_string(order.activity_date_deadline)
                if order_date >= today:
                    kanban_state = 'green'
                else:
                    kanban_state = 'red'
            order.kanban_state = kanban_state

    def _stage_find(self, team_id=False, domain=None, order='sequence'):
        """ Determine the stage of the current lead with its teams, the given domain and the given team_id
            :param team_id
            :param domain : base search domain for stage
            :returns crm.stage recordset
        """
        # collect all team_ids by adding given one, and the ones related to the current leads
        team_ids = set()
        if team_id:
            team_ids.add(team_id)
        for lead in self:
            if lead.team_id:
                team_ids.add(lead.team_id.id)
        # generate the domain
        if team_ids:
            search_domain = ['|', ('team_id', '=', False), ('team_id', 'in', list(team_ids))]
        else:
            search_domain = [('team_id', '=', False)]
        # AND with the domain in parameter
        if domain:
            search_domain += list(domain)
        # perform search, return the first found
        return self.env['order.processing.stage'].search(search_domain, order=order, limit=1)

    @api.depends('team_id', 'type')
    def _compute_stage_id(self):
        for p in self:
            if not p.stage_id:
                p.stage_id = p._stage_find(domain=[('fold', '=', False)]).id

    @api.depends('activity_ids.date_deadline')
    @api.depends_context('uid')
    def _compute_activity_date_deadline_my(self):
        todo_activities = []
        if self.ids:
            todo_activities = self.env['mail.activity'].search([
                ('user_id', '=', self._uid),
                ('res_model', '=', self._name),
                ('res_id', 'in', self.ids)
            ], order='date_deadline ASC')

        for record in self:
            record.activity_date_deadline_my = next(
                (activity.date_deadline for activity in todo_activities if activity.res_id == record.id),
                False
            )

    def action_set_won_rainbowman(self):
        return True

    def action_set_lost(self):
        return True

    def action_schedule_meeting(self):
        return True

    @api.depends('recurring_revenue', 'recurring_plan.number_of_months')
    def _compute_recurring_revenue_monthly(self):
        for order in self:
            order.recurring_revenue_monthly = (order.recurring_revenue or 0.0) / (
                    order.recurring_plan.number_of_months or 1)

    @api.depends('recurring_revenue_monthly', 'probability')
    def _compute_recurring_revenue_monthly_prorated(self):
        for order in self:
            order.recurring_revenue_monthly_prorated = (order.recurring_revenue_monthly or 0.0) * (
                    order.probability or 0) / 100.0

    def _compute_meeting_count(self):
        for op in self:
            op.meeting_count = 0

    def action_set_automated_probability(self):
        self.write({'probability': self.automated_probability})

    @api.depends('partner_id')
    def _compute_partner_id_values(self):
        """ compute the new values when partner_id has changed """
        for order in self:
            order.update(self.env['crm.lead']._prepare_values_from_partner(order.partner_id))

    def _inverse_email_from(self):
        for order in self:
            if order.partner_id and order.email_from != order.partner_id.email:
                order.partner_id.email = order.email_from

    @api.depends('partner_id.email')
    def _compute_email_from(self):
        for order in self:
            if order.partner_id.email and order.partner_id.email != order.email_from:
                order.email_from = order.partner_id.email

    @api.depends('partner_id.phone')
    def _compute_phone(self):
        for order in self:
            if order.partner_id.phone and order.phone != order.partner_id.phone:
                order.phone = order.partner_id.phone

    def _inverse_phone(self):
        for order in self:
            if order.partner_id and order.phone != order.partner_id.phone:
                order.partner_id.phone = order.phone

    @api.depends('phone', 'country_id.code')
    def _compute_phone_state(self):
        self.env['crm.lead']._compute_phone_state()

    @api.depends('email_from')
    def _compute_email_state(self):
        self.env['crm.lead']._compute_email_state()

    @api.depends('create_date', 'date_open')
    def _compute_day_open(self):
        self.env['crm.lead']._compute_day_open()

    @api.depends('create_date', 'date_closed')
    def _compute_day_close(self):
        self.env['crm.lead']._compute_day_close()

    @api.depends('user_id')
    def _compute_date_open(self):
        self.env['crm.lead']._compute_date_open()

    @api.depends('stage_id')
    def _compute_date_last_stage_update(self):
        self.env['crm.lead']._compute_date_last_stage_update()

    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        # retrieve team_id from the context and write the domain
        # - ('id', 'in', stages.ids): add columns that should be present
        # - OR ('fold', '=', False): add default columns that are not folded
        # - OR ('team_ids', '=', team_id), ('fold', '=', False) if team_id: add team columns that are not folded
        team_id = self._context.get('default_team_id')
        if team_id:
            search_domain = ['|', ('id', 'in', stages.ids), '|', ('team_id', '=', False), ('team_id', '=', team_id)]
        else:
            search_domain = ['|', ('id', 'in', stages.ids), ('team_id', '=', False)]

        # perform search
        stage_ids = stages._search(search_domain, order=order, access_rights_uid=SUPERUSER_ID)
        return stages.browse(stage_ids)

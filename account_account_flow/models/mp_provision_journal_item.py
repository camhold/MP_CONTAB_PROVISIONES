from odoo import fields, models, api, _
from odoo.exceptions import UserError


class MpProvisionJournalItem(models.Model):
    _name = 'mp.provision.journal.item'
    _rec_name = 'account_id'
    _order = "mp_provision_id DESC"

    account_id = fields.Many2one(comodel_name='account.account', string='Cuenta')
    debit = fields.Monetary(string='Debito', currency_field="currency_id")
    currency_company_debit = fields.Monetary(string='Debito CLP', currency_field="company_currency_id",
                                             compute='_compute_currency_company', default=0)
    currency_company_credit = fields.Monetary(string='Credito CLP', currency_field="company_currency_id",
                                              compute='_compute_currency_company', default=0)
    credit = fields.Monetary(string='Credito', currency_field="currency_id")
    mp_provision_account_move_id = fields.Many2one(comodel_name='mp.provision.account.move', string='Provision')
    analytic_tag_ids = fields.Many2many(related='mp_provision_account_move_id.analytic_tag_ids')
    analytic_account_id = fields.Many2one(related='mp_provision_account_move_id.analytic_account_id')
    currency_id = fields.Many2one(comodel_name="res.currency", string="Moneda", required=True)
    state = fields.Selection(related='mp_provision_account_move_id.state')
    date = fields.Date(related='mp_provision_account_move_id.date')
    mp_provision_id = fields.Many2one(related='mp_provision_account_move_id.mp_provision_id', store=True)
    line_mp_provision_id = fields.Many2one(comodel_name='mp.provision')
    company_currency_id = fields.Many2one(
        comodel_name="res.currency",
        string="Currency of the Payment Transaction",
        required=True,
        default=lambda self: self.env.user.company_id.currency_id,
    )

    @api.depends('credit', 'debit')
    def _compute_currency_company(self):
        for line_id in self:
            second_currency_amount = line_id.currency_id._convert(
                line_id.debit if line_id.credit == 0 else line_id.credit, line_id.company_currency_id,
                self.env.user.company_id,
                fields.Date.context_today(self)
            )
            if line_id.debit == 0:
                credit = line_id.credit
                if line_id.currency_id != line_id.company_currency_id:
                    credit = second_currency_amount
                line_id.set_value_at_currency_company_fields(debit=0, credit=credit)
            else:
                debit = line_id.debit
                if line_id.currency_id != line_id.company_currency_id:
                    debit = second_currency_amount
                line_id.set_value_at_currency_company_fields(debit=debit, credit=0)

    def set_value_at_currency_company_fields(self, debit, credit):
        self.currency_company_debit = debit
        self.currency_company_credit = credit

    @api.onchange('account_id')
    def onchange_account_id(self):
        for line_id in self:
            if line_id.account_id.currency_id:
                line_id.currency_id = line_id.account_id.currency_id
            else:
                raise UserError(_(f"La cuienta {line_id.account_id.display_name} no tiene moneda registrada."))

    @api.onchange('debit')
    def onchange_debit(self):
        for item in self:
            if item.debit != 0:
                item.credit = 0

    @api.onchange('credit')
    def onchange_credit(self):
        for item in self:
            if item.credit != 0:
                item.debit = 0

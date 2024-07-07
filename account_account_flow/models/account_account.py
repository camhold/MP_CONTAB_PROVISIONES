from odoo import models, fields, api


class AccountAccount(models.Model):
    _inherit = "account.account"

    group_provision_ids = fields.Many2many(comodel_name='mp.grupo.provision', string='Grupos PROVISION')

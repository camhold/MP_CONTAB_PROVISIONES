from odoo import fields, models, api


class MpProvisionItemLine(models.Model):
    _name = 'mp.provision.item.line'

    account_id = fields.Many2one(comodel_name='account.account', string='Cuenta')
    activo = fields.Boolean(string="Activo", default=False)
    provision_id = fields.Many2one(comodel_name='mp.provision')

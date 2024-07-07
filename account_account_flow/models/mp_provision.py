from odoo import fields, models, _, api
from odoo.exceptions import UserError


class MpProvision(models.Model):
    _name = 'mp.provision'
    _rec_name = "display_name"
    _order = "id DESC"

    codigo = fields.Char(readonly=True, required=True, copy=False, default=lambda self: _('New'))
    decripcion = fields.Text()
    mp_grupo_provision_ids = fields.Many2many(comodel_name="mp.grupo.provision",
                                              string="Grupo Provision", required=True)
    mp_grupo_provision_id = fields.Many2one(comodel_name="mp.grupo.provision")
    display_name = fields.Char(compute='_compute_display_name')
    mp_provision_item_line_ids = fields.One2many(comodel_name='mp.provision.item.line',
                                                 inverse_name='provision_id', required=True)

    def _compute_display_name(self):
        for provision_id in self:
            provision_id.display_name = f'{provision_id.codigo}: {provision_id.decripcion}'

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')):
            vals['codigo'] = self.env['ir.sequence'].sudo().next_by_code('mp.provision')
        return super(MpProvision, self).create(vals)

    @api.onchange('mp_grupo_provision_ids')
    def onchange_mp_group_provision_ids(self):
        for mp_provision_id in self:
            mp_provision_id.sudo().mp_provision_item_line_ids = self.env['mp.provision.item.line']
            account_ids = self.env['account.account'].search([
                ('group_provision_ids', 'in', mp_provision_id.mp_grupo_provision_ids.ids),
            ])
            for account_id in account_ids:
                mp_provision_id.mp_provision_item_line_ids += self.env['mp.provision.item.line'].create({
                    'account_id': account_id.id
                })

    def write(self, vals):
        rec = super(MpProvision, self).write(vals)
        activate_account = 0
        for provision_id in self:
            for line_id in provision_id.mp_provision_item_line_ids:
                if line_id.activo:
                    activate_account += 1
        if activate_account < 2:
            raise UserError(_("Como minimo, deben ser dos cuentas activas."))
        return rec

from odoo import fields, models


class MpGrupoProvision(models.Model):
    _name = 'mp.grupo.provision'
    _rec_name = "nombre"
    _order = "id DESC"

    nombre = fields.Char()
    descripcion = fields.Text()
    account_id = fields.Many2one(comodel_name='account.account')
    mp_provision_ids = fields.One2many(comodel_name="mp.provision", inverse_name="mp_grupo_provision_id",
                                       compute="_compute_mp_provision_ids")

    def _compute_mp_provision_ids(self):
        for grupo_id in self:
            provision_ids = self.env["mp.provision"].search([("mp_grupo_provision_ids", "=", grupo_id.id)])
            if not provision_ids:
                grupo_id.mp_provision_ids = self.env['mp.provision']
            for provision_id in provision_ids:
                grupo_id.mp_provision_ids += provision_id


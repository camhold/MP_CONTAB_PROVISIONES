from odoo import models, fields, api


class AccountMove(models.Model):
    _inherit = "account.move"

    mp_grupo_provision_id = fields.Many2one(comodel_name="mp.grupo.provision]")
    mp_provision_id = fields.Many2one(comodel_name="mp.provision", domain="[('id', 'in', mp_provision_ids)]")
    res_partner_category_id = fields.Many2many(compute='_compute_category_ids',
                                               comodel_name='res.partner.category', string='Etiquetas de proveedor')

    def _compute_category_ids(self):
        for move_id in self:
            move_id.res_partner_category_id = move_id.partner_id.category_id
    # mp_provision_ids = fields.One2many()#related="mp_grupo_provision_id.mp_provision_ids"

    # @api.onchange("mp_grupo_provision_id")
    # def _onchange_mp_provision_id(self):
    #     for move_io in self:
    #         move_io.mp_provision_id = self.env['mp.provision']
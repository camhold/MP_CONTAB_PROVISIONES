from odoo import fields, models, api, _
from odoo.exceptions import UserError


class MpProvisionAccountMove(models.Model):
    _name = 'mp.provision.account.move'
    _order = "name DESC"

    name = fields.Char(readonly=True, required=True, copy=False, default=lambda self: _('New'))
    date = fields.Date(required=True, string='Fecha')
    state = fields.Selection(
        selection=[
            ("draft", "Draft"),
            ("confirmed", "Confirmado"),
        ],
        default="draft",
    )
    mp_grupo_provision_id = fields.Many2one(comodel_name='mp.grupo.provision', string='MP Grupo Provision',
                                            required=True)
    mp_provision_id = fields.Many2one(comodel_name='mp.provision', string='MP Provision',
                                      domain="[('id', 'in', mp_provision_ids)]", required=True)
    mp_provision_ids = fields.One2many(related="mp_grupo_provision_id.mp_provision_ids")
    analytic_account_id = fields.Many2one('account.analytic.account', string='Cuenta Analitica',
                                          index=True, check_company=True, copy=True)
    analytic_tag_ids = fields.Many2many('account.analytic.tag', string='Tags Analiticas',
                                        store=True, readonly=False, check_company=True, copy=True)
    mp_provision_journal_item_ids = fields.One2many(comodel_name='mp.provision.journal.item',
                                                    inverse_name='mp_provision_account_move_id')
    account_move_id = fields.Many2one(comodel_name='account.move', string='Apunte de Diario')
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        required=True,
        default=lambda self: self.env.company,
    )
    currency_id = fields.Many2one(
        comodel_name="res.currency",
        string="Currency of the Payment Transaction",
        required=True,
        default=lambda self: self.env.user.company_id.currency_id,
    )
    
    contact_type = fields.Selection([('employee', 'Empleado'), ('customer', 'Proveedor')], string='Tipo de contacto')
    employee_id = fields.Many2one(comodel_name='hr.employee', string='Empleado')
    partner_id = fields.Many2one(comodel_name='res.partner', string='Proveedor')
    journal_id = fields.Many2one(comodel_name='account.journal', string='Diario', required=True, domain="[('type', '=', 'general')]")

    @api.onchange('contact_type')
    def onchange_contact_type(self):
        if self.contact_type == 'customer':
            self.employee_id = False
        elif self.contact_type == 'employee':
            self.partner_id = False
        else:
            self.employee_id = False
            self.partner_id = False

    def write(self, vals):
        res = super(MpProvisionAccountMove, self).write(vals)
        list_line_ids = []
        sequence = 0
        for line_id in self.mp_provision_journal_item_ids:
            amount_currency = line_id.debit if line_id.credit == 0 else line_id.credit
            amount_currency = amount_currency * -1 if line_id.credit != 0 else amount_currency
            line_id_to_add = (0, 0, {
                'account_id': line_id.account_id.id,
                'account_root_id': line_id.account_id.id,
                'name': line_id.account_id.name,
                'display_type': False,
                'debit': line_id.currency_company_debit,
                'credit': line_id.currency_company_credit,
                'sequence': sequence,
                'amount_currency': amount_currency,
                'currency_id': line_id.currency_id.id,
                'analytic_account_id': self.analytic_account_id.id,
                'analytic_tag_ids': [(6, 0, self.analytic_tag_ids.ids)],
                'company_currency_id': self.currency_id.id,
                'quantity': 1,
                'product_id': False,
            })
            if (line_id.debit != 0 or line_id.credit != 0) and line_id_to_add not in list_line_ids:
                list_line_ids.append(line_id_to_add)
            sequence += 1
        self.account_move_id.line_ids.unlink()
        self.account_move_id.sudo().write({'line_ids': list_line_ids})
        self.account_move_id.sudo().write({'date': self.date})
        ref = self.partner_id.display_name or self.employee_id.display_name
        self.account_move_id.sudo().write({'ref': ref})
        self.account_move_id.sudo().write({'name': self.name})
        return res

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')):
            provision_move_ids = self.env['mp.provision.account.move'].sudo().search([('name', 'ilike', 'PROV%')])
            current_date = fields.Datetime.now()
            if not provision_move_ids:
                vals['name'] = f"PROV/{current_date.year}/{current_date.month}/1"
            else:
                vals['name'] = f"PROV/{current_date.year}/{current_date.month}/{len(provision_move_ids)}"

        rec = super(MpProvisionAccountMove, self).create(vals)

        rec.account_move_id = self.env['account.move'].sudo().create({
            'state': 'draft',
            'date': rec.date,
            'journal_id': self.journal_id.id,
            'name': rec.name,
            'currency_id': rec.currency_id.id
        })
        ref = rec.partner_id.display_name or rec.employee_id.display_name
        rec.account_move_id.sudo().write({'ref': ref})
        sequence = 0
        debit = 0
        credit = 0
        for line_id in rec.mp_provision_journal_item_ids:
            debit += line_id.debit
            credit += line_id.credit
            sequence += 1
        if credit == 0 or debit == 0:
            raise UserError(_("No se puede guardar asientos en 0."))
        return rec

    def action_confirm(self):
        self.state = 'confirmed'
        self.account_move_id.action_post()

    @api.onchange('mp_provision_id')
    def onchange_mp_provision_id(self):
        for provision_id in self:
            provision_id.mp_provision_journal_item_ids = self.env['mp.provision.journal.item']
            for line_id in provision_id.mp_provision_id.mp_provision_item_line_ids:
                if line_id.activo:
                    provision_id.mp_provision_journal_item_ids += self.env['mp.provision.journal.item'].create({
                        'account_id': line_id.account_id.id,
                        'currency_id': line_id.account_id.currency_id.id,
                        'debit': 0,
                        'credit': 0,
                    })

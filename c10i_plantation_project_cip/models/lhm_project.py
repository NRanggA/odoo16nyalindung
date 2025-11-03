from odoo import models, fields, api, _
from odoo.exceptions import UserError

class LhmProject(models.Model):
    _inherit = 'lhm.project'

    amount_cip = fields.Monetary(
        string='Amount CIP',
        compute='_compute_amount_cip',
        store=False,
        currency_field='company_currency_id',
        help='Total Construction In Progress value for this project'
    )
    company_currency_id = fields.Many2one(
        'res.currency',
        string='Company Currency',
        related='company_id.currency_id',
        readonly=True,
    )

    equipment_register_id = fields.Many2one('equipment.register', string='Equipment Register', readonly=True)
    equipment_category_id = fields.Many2one('maintenance.equipment.category', string='Equipment Category')
    product_id = fields.Many2one('product.product',string='Product')


    def action_create_asset(self):
        """Create equipment register based on project data"""
        EquipmentRegister = self.env['equipment.register']
        product = self.env['product.product'].search([('name', '=', 'Product CIP')], limit=1)
        for project in self:
            if project.equipment_register_id:
                raise UserError(_('Equipment register has already been created for this project.'))
            
            if not project.equipment_category_id:
                raise UserError(_('Equipment Category harus diisi.'))

            register_vals = {
                'date': fields.Date.context_today(self),
                'origin': project.code,
                'category_id': project.equipment_category_id.id,
                'company_id': project.company_id.id,
                'register_line_ids': [
                    (0, 0, {
                        'product_id': product.id,
                        'name': project.name,
                        'product_qty': 1,
                        'project_id': project.id,
                    })
                ]
            }

            register = EquipmentRegister.create(register_vals)

            project.equipment_register_id = register.id

        return {
            'type': 'ir.actions.act_window',
            'name': _('Equipment Register'),
            'res_model': 'equipment.register',
            'view_mode': 'form',
            'res_id': register.id,
            'target': 'current',
        }

    def action_open_equipment_register(self):
        self.ensure_one()
        if not self.equipment_register_id:
            raise UserError(_("Belum ada Equipment Register untuk project ini."))

        return {
            'name': _('Equipment Register'),
            'type': 'ir.actions.act_window',
            'res_model': 'equipment.register',
            'view_mode': 'form',
            'res_id': self.equipment_register_id.id,
            'target': 'current',
        }

    @api.depends('activity_ids', 'location_id', 'location_type_id')
    def _compute_amount_cip(self):
        for project in self:
            total = 0.0
            activity = project.activity_ids[:1]

            if not activity or not activity.account_id:
                project.amount_cip = 0.0
                continue

            domain = [
                ('parent_state', '=', 'posted'),
                ('account_id', '=', activity.account_id.id),
            ]
            if project.location_id:
                domain.append(('plantation_location_id', '=', project.location_id.id))
            if project.location_type_id:
                domain.append(('plantation_location_type_id', '=', project.location_type_id.id))

            move_lines = self.env['account.move.line'].search(domain)
            total = sum(move_lines.mapped(lambda l: l.debit - l.credit))
            project.amount_cip = total

    def action_open_project_move_lines(self):
        self.ensure_one()

        # ambil salah satu activity dari project (sesuai instruksi task)
        activity = self.activity_ids[:1]

        # cari semua account.move.line berdasarkan kriteria
        domain = [
            ('plantation_location_id', '=', self.location_id.id),
            ('plantation_location_type_id', '=', self.location_type_id.id),
            ('account_id', '=', activity.account_id.id),
            ('parent_state', '=', 'posted'),
        ]
        move_lines = self.env['account.move.line'].search(domain)

        action = self.env["ir.actions.actions"]._for_xml_id("c10i_plantation_project_cip.project_aml_action")
        action['domain'] = [('id', 'in', move_lines.ids)]
        action['context'] = {'create': False}
        return action
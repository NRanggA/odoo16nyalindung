from odoo import models, fields, api, _
from dateutil.rrule import rrule, YEARLY, MONTHLY, WEEKLY


class EquipmentRegister(models.Model):
    _inherit = 'equipment.register'

    # owner_user_id = fields.Many2one('res.users', string='Owner', tracking=True)
    category_id = fields.Many2one('maintenance.equipment.category', string='Equipment Category', tracking=True,)
    partner_id = fields.Many2one('res.partner', string='Vendor')
    partner_ref = fields.Char('Vendor Reference')
    location = fields.Char('Location')
    model = fields.Char('Model')
    serial_no = fields.Char('Serial Number', copy=False)
    warranty_period = fields.Integer(string="Warranty Period")
    unit_of_time = fields.Selection([
							(str(YEARLY), 'Years'),
							(str(MONTHLY), 'Months'),
							(str(WEEKLY), 'Weeks')], default=lambda x: str(YEARLY))

    employee_id = fields.Many2one('hr.employee', compute='_compute_equipment_assign',
        store=True, readonly=False, string='Assigned Employee', tracking=True)
    department_id = fields.Many2one('hr.department', compute='_compute_equipment_assign',
        store=True, readonly=False, string='Assigned Department', tracking=True)
    equipment_assign_to = fields.Selection(
        [('department', 'Department'), ('employee', 'Employee'), ('other', 'Other')],
        string='Used By',
        required=True,
        default='employee')
    owner_user_id = fields.Many2one(compute='_compute_owner', store=True)
    assign_date = fields.Date(compute='_compute_equipment_assign', store=True, readonly=False, copy=True)

    @api.depends('employee_id', 'department_id', 'equipment_assign_to')
    def _compute_owner(self):
        for equipment in self:
            equipment.owner_user_id = self.env.user.id
            if equipment.equipment_assign_to == 'employee':
                equipment.owner_user_id = equipment.employee_id.user_id.id
            elif equipment.equipment_assign_to == 'department':
                equipment.owner_user_id = equipment.department_id.manager_id.user_id.id

    @api.depends('equipment_assign_to')
    def _compute_equipment_assign(self):
        for equipment in self:
            if equipment.equipment_assign_to == 'employee':
                equipment.department_id = False
                equipment.employee_id = equipment.employee_id
            elif equipment.equipment_assign_to == 'department':
                equipment.employee_id = False
                equipment.department_id = equipment.department_id
            else:
                equipment.department_id = equipment.department_id
                equipment.employee_id = equipment.employee_id
            equipment.assign_date = fields.Date.context_today(self)

    #######################
	#     HELPER METHOD   #
	#######################

	##########################
	#     BUSSINESS METHOD   #
	##########################
    def create_asset_acquisition(self):
        self.ensure_one()
        Acquisition = self.env['account.asset.acquisition']
        AcquisitionLine = self.env['account.asset.acquisition.line']
        
        values = {
			'origin': f"{self.origin}: {self.name}",
			'date': self.date,
			'company_id': self.company_id.id,
		}
        lines = []
        for rline in self.register_line_ids:
            threshold_param = self.env['ir.config_parameter'].sudo().get_param('ny_equipment.threshold', default=0.0)
            threshold = float(threshold_param) if threshold_param else 0.0
            if threshold and rline.purchase_line_id.price_unit > threshold:
                line_vals = {
					'product_id': rline.product_id.id,
					'name': rline.name,
					'product_uom': rline.product_uom.id,
					'product_qty': rline.product_qty,
					'price_unit': rline.purchase_line_id.price_unit,
					'equipment_register_line_id': rline.id,
					'purchase_line_id': rline.purchase_line_id.id,
				}
                lines.append((0,0,line_vals))
        values.update({'line_ids': lines})  
		
        if lines:
            new_acquisition = Acquisition.create(values)
			# new_acquisition.action_submit()
            return new_acquisition
        else:
            return False
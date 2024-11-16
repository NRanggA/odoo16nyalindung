from odoo import fields, models, api, _

class lhmStation(models.Model):
    _name = 'lhm.station'
    _description = 'LHM Station'

    name = fields.Char('Nama', required=True)
    code = fields.Char('Kode', required=True)
    varieties_id = fields.Many2one('plant.varieties', string='ORG')
    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.user.company_id
    )
    plantation = fields.Boolean("Plantation", default=False)
    location_id = fields.Many2one(comodel_name="lhm.location", string="Lokasi")
    location_type_id = fields.Many2one(
        comodel_name="lhm.location.type", 
        string="Type Lokasi", 
        ondelete="restrict", 
        default=lambda self: self._default_location_type()
    )
    group_progress_id = fields.Many2one(comodel_name="plantation.location.reference", string="Grouping LPPH")
    active = fields.Boolean("Active", default=True)
    owner_type = fields.Selection([('inti', 'Inti'), ('plasma', 'Plasma')], 'Tipe Kepemilikan Blok')

    @api.model
    def _default_location_type(self):
        location_type = self.env['lhm.location.type'].search([('mills', '=', True)], limit=1)
        return location_type.id if location_type else False

    @api.model
    def create(self, values):
        location_name = values.get('name', "(NoName)")
        location_code = values.get('code', "(NoCode)")
        location_type_id = values.get('location_type_id', False)
        varieties_id = values.get('varieties_id', False)
        group_progress_id = values.get('group_progress_id', False)
        location_values = {
            'name': location_name,
            'code': location_code,
            'varieties_id': varieties_id,
            'type_id': location_type_id,
            'group_progress_id': group_progress_id,
        }

        location = super(lhmStation, self).create(values)

        if location.plantation:
            new_location = self.env['lhm.location'].create(location_values)
            location.location_id = new_location.id

        return location

    def write(self, values):
        if 'name' in values and self.location_id:
            self.location_id.write({'name': values.get('name')})
        if 'code' in values and self.location_id:
            self.location_id.write({'code': values.get('code')})
        if 'location_type_id' in values and self.location_id:
            self.location_id.write({'type_id': values.get('location_type_id')})
        if 'varieties_id' in values and self.varieties_id:
            self.location_id.write({'varieties_id': values.get('varieties_id')})
        if 'group_progress_id' in values and self.location_id:
            self.location_id.write({'group_progress_id': values.get('group_progress_id')})
        if 'active' in values and self.location_id:
            self.location_id.write({'active': values.get('active')})

        return super(lhmStation, self).write(values)

    def unlink(self):
        for location in self:
            if location.location_id:
                location.location_id.unlink()
        return super(lhmStation, self).unlink()

    def name_get(self):
        result = []
        for record in self:
            name = record.code if record.code else record.name
            if record.name and record.code:
                result.append((record.id, record.code))
            elif record.name:
                result.append((record.id, record.name))
        return result

    def _name_get(self):
        result = []
        for record in self:
            if record.name and record.code:
                result.append((record.id, f"{record.code} - {record.name}"))
            elif record.name:
                result.append((record.id, record.name))
        return result

    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        domain = []
        if name:
            domain = ['|', ('code', 'ilike', name + '%'), ('name', operator, name)]
            if operator in expression.NEGATIVE_TERM_OPERATORS:
                domain = ['&', '!'] + domain[1:]
        lhm_location_type = self.search(domain + args, limit=limit)
        return lhm_location_type._name_get()
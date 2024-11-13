from odoo import models, fields, api, _

class Project(models.Model):
    _inherit = 'lhm.project'

    project_tanaman = fields.Boolean('Project Tanaman')
    plant_block_id = fields.Many2one('lhm.plant.block', string='Blok Tanam')
    varieties_id = fields.Many2one('plant.varieties', string='Varietas')
    harvest_date_schedule = fields.Date('Harvesting Schedule Date')

    def button_progress(self):
        res = super(Project,self).button_progress()
        for project in self:
            if not project.project_tanaman:
                continue
            if project.plant_block_id:
                project.location_id.write({
                    'varieties_id': project.varieties_id.id,
                })
                continue
            block_vals = {
                'name': project.name,
                'code': project.code,
                'location_type_id': project.location_type_id.id,
                'location_id': project.location_id.id,
                'type_of_plant': 'shorterm',
                'is_project': True,
                'varieties_id': project.varieties_id.id,
            }
            new_block = self.env['lhm.plant.block'].sudo().create(block_vals)
            project.write({
                'plant_block_id': new_block.id,
            })
            project.location_id.write({
                'varieties_id': project.varieties_id.id,
            })
        return res

    def button_cancel(self):
        res = super(Project, self).button_cancel()
        for project in self:
            if not project.project_tanaman:
                continue
            if project.plant_block_id:
                project.plant_block_id.active = False
        return res
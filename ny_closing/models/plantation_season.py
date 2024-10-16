from odoo import models, fields, api, Command, _
from odoo.exceptions import UserError, ValidationError

import logging
_logger = logging.getLogger(__name__)

class PlantationSeason(models.Model):
    _name = 'plantation.season'
    _description = 'Plantation Season'
    _order = 'id desc'

    name = fields.Char(compute='_compute_name', readonly=False, precompute=True, store=True)

    date_start = fields.Date('Start Date', required=True)
    date_end = fields.Date('End Date', required=True)

    harvest_date_schedule = fields.Date('Harvest Schedule Date', required=True)

    location_type_id = fields.Many2one('lhm.location.type', string='Type', required=True)
    block_ids = fields.Many2many('lhm.plant.block', 'season_plant_block_rel', 'season_id', 'plant_block_id', string='Blok Tanam', domain="[('location_type_id','=',location_type_id)]")

    active = fields.Boolean(default=True)

    @api.depends('location_type_id', 'date_start', 'date_end')
    def _compute_name(self):
        for season in self:
            season.name = f"{season.location_type_id.name} Season Periode {season.date_start.strftime('%d/%m/%Y')} - {season.date_end.strftime('%d/%m/%Y')}"
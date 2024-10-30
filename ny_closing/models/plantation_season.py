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
    harvest_date_schedule = fields.Date('Harvest Schedule Start Date', required=True)
    date_end = fields.Date('End Date', required=True)

    # location_type_id = fields.Many2one('lhm.location.type', string='Type', required=True)
    varieties_id = fields.Many2one('plant.varieties', string='Varietas', required=True)
    block_ids = fields.Many2many('lhm.plant.block', 'season_plant_block_rel', 'season_id', 'plant_block_id', string='Blok Tanam', domain="[('varieties_id','=',varieties_id)]")

    active = fields.Boolean(default=True)

    @api.constrains('date_start','date_end','harvest_date_start','harvest_date_end')
    def check_date(self):
        for rec in self:
            if rec.date_end <= rec.date_start:
                raise ValidationError(_('End Date tidak dapat lebih kecil atau sama dengan Start Date'))
            if rec.harvest_date_schedule == rec.date_start: 
                raise ValidationError(_('Harvest Schedule Start Date tidak boleh sama dengan Start Date'))
            if rec.harvest_date_schedule >= rec.date_end: 
                raise ValidationError(_('Harvest Schedule Start Date tidak boleh lebih besar atau sama dengan End Date'))

    @api.depends('varieties_id', 'date_start', 'date_end')
    def _compute_name(self):
        for season in self:
            if season.varieties_id and season.date_start and season.date_end:
                season.name = f"{season.varieties_id.name} Season Periode {season.date_start.strftime('%d/%m/%Y')} - {season.date_end.strftime('%d/%m/%Y')}"
            else:
                season.name = ""
            
    def write(self, update_vals):
        self.check_date()
        return super(PlantationSeason, self).write(update_vals)
from odoo import models, fields, api, _

class LhmHanca(models.Model):
    _name = 'lhm.hanca'
    _description = 'LHM Hanca'

    name = fields.Char(string='Blok Hanca', required=True)
    description = fields.Text(string='Keterangan')
    plant_block_id = fields.Many2one('lhm.plant.block', string='Blok Tanaman', required=True)
    active = fields.Boolean(string='Active', default=True)
    geo_map_border = fields.Text(string='Geo Map Border', help='GeoJSON format for the border of the block')
    geo_map_center = fields.Char(string='Geo Map Center', help='Center point of the block in GeoJSON format')

    perimeter = fields.Float(string='Perimeter', help='Perimeter of the block in meters')
    area = fields.Float(string='Area', store=True, help='Area of the block in square meters')
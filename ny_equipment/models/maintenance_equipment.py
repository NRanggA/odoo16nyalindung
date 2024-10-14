from odoo import models, fields

class MaintenanceEquipment(models.Model):
    _inherit = 'maintenance.equipment'

    image = fields.Binary("Equipment Image", attachment=True, help="Upload the image of the equipment")

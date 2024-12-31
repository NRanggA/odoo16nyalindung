from odoo import models, fields

class MaintenanceEquipment(models.Model):
    _inherit = 'maintenance.equipment'

    image = fields.Binary("Equipment Image", attachment=True, help="Upload the image of the equipment")
    no_polisi = fields.Char("No. Polisi")
    no_bpkb = fields.Char("No. BPKB")
    no_mesin = fields.Char("No. Mesin")
    no_rangka = fields.Char("No. Rangka")

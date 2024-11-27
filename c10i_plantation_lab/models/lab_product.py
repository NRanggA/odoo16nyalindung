from odoo import models, fields, api, _

class LabProduct(models.Model):
    _name = 'lab.product'
    _description = 'Lab Product'
    _rec_name = 'product_id'

    product_id = fields.Many2one('product.product', string='Product', required=True)
    code = fields.Char('Code', required=True)
    location_id = fields.Many2one('lhm.location', string='Plantation Location', ondelete='restrict')
    active = fields.Boolean(default=True)
    
    def create_or_update_location(self):
        self.ensure_one()
        location_type = self.env['lhm.location.type'].search([('laboratorium','=',True)], limit=1)
        if not self.location_id:
            new_location = self.env['lhm.location'].create({
                'type_id': location_type.id,
                'name': self.product_id.name,
                'code': self.code,
            })
            self.location_id = new_location.id
        else:
            self.location_id.write({
                'name': self.product_id.name,
                'code': self.code,
            })
    
    @api.model_create_multi
    def create(self, vals_list):
        res = super(LabProduct, self).create(vals_list)
        for product in res:
            product.create_or_update_location()
        return res

    def write(self, update_vals):
        for product in self:
            if update_vals.get('name', False) or update_vals.get('code', False):
                product.create_or_update_location()
        return super(LabProduct, self).write(update_vals)
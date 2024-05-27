from odoo import api, fields, models, _
from odoo.exceptions import UserError

class MaterialRequest(models.Model):
    _inherit = 'material.request'

    purchase_request_count = fields.Integer(compute='_pr_count', string='# Purchase Request', compute_sudo=True)

    def _pr_count(self):
        for request in self:
            request.purchase_request_count = len(request.line_ids.mapped('purchase_request_line_ids.request_id').ids)

    def action_open_purchase_request(self):
        result = self.env["ir.actions.actions"]._for_xml_id('purchase_request.purchase_request_form_action')
        result['context'] = {'default_material_request_id': self.id}
        purchase_requests = self.line_ids.mapped('purchase_request_line_ids.request_id')
        if not purchase_requests or len(purchase_requests)==1:
            result['domain'] = "[('id','=',%s)]" % (purchase_requests.id)
        elif len(purchase_requests)>1:
            result['domain'] = "[('id','in',%s)]" % (purchase_requests.ids)
        return result
    
class MaterialRequestLine(models.Model):
    _inherit = 'material.request.line'

    purchase_request_line_ids = fields.One2many('purchase.request.line', 'material_request_line_id', 'Purchase Request Lines')
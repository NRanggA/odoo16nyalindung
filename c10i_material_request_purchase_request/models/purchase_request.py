from odoo import api, fields, models, _
from odoo.exceptions import UserError

class PurchaseRequest(models.Model):
	_inherit = 'purchase.request'


	@api.model
	def _default_picking_type(self):
		
		return False

		
	material_request_id = fields.Many2one('material.request', 'Material Request')
	warehouse_id = fields.Many2one('stock.warehouse', string='Warehouse', required=1)
	internal_move_ids = fields.One2many('stock.picking', 'purchase_request_move_id',string='Internal Move')
	internal_move_count = fields.Integer(compute='_im_count', string='# Internal Move', compute_sudo=True)
	picking_type_id = fields.Many2one(
		comodel_name="stock.picking.type",
		string="Picking Type",
		required=True,
	)

	def _im_count(self):
		for request in self:
			request.internal_move_count = len(request.internal_move_ids)


	def button_create_im(self):
		Picking = self.env['stock.move']

		return True


	def action_open_internal_move(self):
		result = self.env["ir.actions.actions"]._for_xml_id('stock.stock_picking_action_picking_type')
	  
		if self.internal_move_ids:
			print ('=View==',self.internal_move_ids.id)
			if len(self.internal_move_ids) > 1:
				result['domain'] = f"[('id', 'in', {self.internal_move_ids})]"
			else:
				result['domain'] = f"[('id', '=', {self.internal_move_ids.id})]"
			# result['context'] = {'purchase_request_move_id': self.internal_move_ids.id}
			print ('-----',result)
			return result
		return False


	@api.onchange('material_request_id')
	def onchange_material_request(self):
		if self.material_request_id:
			self.group_id = self.material_request_id.group_id.id
			self.origin = self.material_request_id.name
			request_lines = []
			for line in self.material_request_id.line_ids:
				vals = {
					'product_id': line.product_id.id,
					'product_qty': line.qty_to_issue,
					'name': line.name or line.product_id.name,
					'product_uom_id': line.uom_id.id,
					'date_required': self.material_request_id.date_request,
					'material_request_line_id': line.id,
				}
				request_lines.append((0,0,vals))
			self.line_ids = request_lines

	material_request_count = fields.Integer(compute='_mr_count', string='# Material Request', compute_sudo=True)

	def _mr_count(self):
		for request in self:
			request.material_request_count = len(request.line_ids.mapped('material_request_line_id.mr_id').ids)

	def action_open_material_request(self):
		result = self.env["ir.actions.actions"]._for_xml_id('c10i_material_request.material_request_action')
		material_requests = self.line_ids.mapped('material_request_line_id.mr_id')
		if not material_requests or len(material_requests)==1:
			result['domain'] = "[('id','=',%s)]" % (material_requests.id)
		elif len(purchase_request)>1:
			result['domain'] = "[('id','in',%s)]" % (material_requests.ids)
		return result

class PurchaseRequestLine(models.Model):
	_inherit = 'purchase.request.line'

	material_request_line_id = fields.Many2one('material.request.line', 'Material Request Line')
	qty_im_process = fields.Float('Qty IM Process')


class StockPicking(models.Model):
	_inherit = 'stock.picking'

	purchase_request_move_id = fields.Many2one('purchase.request', string='Purchase Request')





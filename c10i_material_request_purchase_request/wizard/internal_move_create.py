from odoo import models, fields, api,_
from datetime import datetime,date
from odoo.exceptions import UserError, ValidationError

class WizardCreateInternalMove(models.TransientModel):
	_name = "wizard.create.internal.move"

	source_loc_id = fields.Many2one('stock.location', string='Source Location')
	dest_loc_id   = fields.Many2one('stock.location', string='Destination Location')
	lines 			= fields.One2many('wizard.create.internal.move.line', 'create_im_id', string='Lines')


	def default_get(self, fields_list):
		res = super(WizardCreateInternalMove, self).default_get(fields_list)

		context = dict(self._context or {})
		active_model = context.get('active_model', 'undefined')
		active_ids = context.get('active_ids')
		
		if active_ids and active_model == 'purchase.request':
			pr = self.env['purchase.request'].search([('id', '=', active_ids[0])])
			lines = []
			SourceLoc = False
			for line in pr.line_ids:
				StockMove = self.env['stock.move'].search([('purchase_line_id','=',line.purchase_lines.id),('picking_type_id.sequence_code','=','INT')])

				if line.purchase_lines:
					SourceLoc = line.purchase_lines.order_id.picking_type_id.warehouse_id.lot_stock_id.id

				QtyProcess = 0
				# if StockMove:
				if line.qty_done - line.qty_im_process > 0:
					

					prepare_line = {
							'product_id'		: line.product_id.id,
							'unprocessed_qty'	: line.product_qty - line.qty_im_process,
							'product_qty' 		: line.product_qty - line.qty_im_process,
							'pr_line_id'		: line.id,
							}
					lines.append((0,0,prepare_line))


			res.update({
				'source_loc_id': SourceLoc,
				'dest_loc_id':pr.warehouse_id.lot_stock_id.id,
				'lines'		: lines,
			})

		return res


	def action_create_im(self):
		DataLines = []
		
		if self.lines:
			for x in self.lines:
				if x.product_qty > x.unprocessed_qty:
					raise ValidationError(_('Warning ! Qty Max ' + str(x.unprocessed_qty)))
				else:
					DataLines.append((0,0,{
						'name': x.product_id.name,
						'product_id': x.product_id.id,
						'cost_allocation_id':x.pr_line_id.cost_allocation_id.id,
						'cost_center_id': x.pr_line_id.cost_center_id.id,
						'cost_activity_id':x.pr_line_id.cost_activity_id.id,
						'quantity_done': x.product_qty,
						'product_uom':x.pr_line_id.product_uom_id.id,
					}))
			if DataLines:
				IM = self.env['stock.picking'].create({
					'picking_type_id':x.pr_line_id.request_id.warehouse_id.int_type_id.id,
					'location_id':self.source_loc_id.id,
					'location_dest_id': self.dest_loc_id.id,
					'request_pick_ids':False,
					'move_ids_without_package':DataLines,
					'purchase_request_move_id':x.pr_line_id.request_id.id,
					'request_pick_ids':[(6,0,[x.pr_line_id.request_id.id])],
				})

				if IM:
					for i in self.lines:
						i.pr_line_id.update({
							'qty_im_process':  x.product_qty
							})
		else:
			raise ValidationError(_('Warning ! internal Move tidak dapat dibuat '))


		return True


class WizardCreateInternalMoveLine(models.TransientModel):
	_name = "wizard.create.internal.move.line"

	create_im_id 	= fields.Many2one('wizard.create.internal.move', string="Wizard Create SPK", required=True)
	product_id 		= fields.Many2one('product.product')
	unprocessed_qty = fields.Float(string='Unprocessed Qty')
	product_qty 	= fields.Float(string='Qty')
	pr_line_id 		= fields.Many2one('purchase.request.line', string='PR Line')
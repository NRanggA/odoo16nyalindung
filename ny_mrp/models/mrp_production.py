from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime

class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    manual_consume_ids = fields.One2many('mrp.manual.consume', 'component_consume_production_id', string='Manual Consumed')
    product_name = fields.Char('Product Name', related='product_id.name', readonly=True, store=True)
    must_have_source_mo = fields.Boolean(related='bom_id.must_have_source_mo', string='Must Have Source MO', store=True)
    source_mo_id = fields.Many2one('mrp.production', string='Asal MO', readonly=True, help='MO asal dari mana MO ini dibuat melalui proses split atau backorder.')
    wip_date_start = fields.Datetime(related='source_mo_id.date_finished', string='WIP Start Date', help='Tanggal mulai WIP dari MO ini.', readonly=True, store=True)
    finish_mo_ids = fields.One2many('mrp.production', 'source_mo_id', string='Akhir MO', readonly=True)
    state_mo_wip = fields.Selection([
        ('none', 'None'),
        ('inprogress', 'In Progress'),
        ('completed', 'Completed'),
    ], string='State MO WIP', compute='_compute_state_mo_wip', store=True)

    @api.depends('state', 'finish_mo_ids', 'finish_mo_ids.state')
    def _compute_state_mo_wip(self):
        for prod in self:
            if prod.state in ['draft', 'cancel']:
                prod.state_mo_wip = 'none'
            elif any(fin_mo.state != 'done' for fin_mo in prod.finish_mo_ids):
                prod.state_mo_wip = 'inprogress'
            else:
                prod.state_mo_wip = 'completed'
    
    # def action_draft(self):
    #     for production in self:
    #         production.state = 'draft'
    #         # production.reservation_state = False
    #         # production.consumption = 'flexible'

    # @api.model
    # def create(self, vals):
    #     current_date = datetime.today().strftime("%Y-%m-%d")

    #     sequence_count = self.env['mrp.production'].search_count([
    #         ('create_date', '>=', f"{current_date} 00:00:00"),
    #         ('create_date', '<=', f"{current_date} 23:59:59")
    #     ]) + 1

    #     sequence_str = f"{sequence_count:02d}"

    #     vals['name'] = f"MO/{current_date}/{sequence_str}"

    #     return super(MrpProduction, self).create(vals)

    @api.model
    def create(self, vals):
        bom_id = vals.get('bom_id')
        if bom_id:
            bom = self.env['mrp.bom'].browse(bom_id)
            if bom.sequence_id:
                vals['name'] = bom.sequence_id.next_by_id()
            else:
                raise UserError("Product pada Bills of Material tidak memiliki sequence number.")
        else:
            raise UserError("Field 'Bills of Material' wajib diisi untuk membuat nomor MO.")

        return super(MrpProduction, self).create(vals)

    def action_draft(self):
        for production in self:
            for move in production.move_raw_ids | production.move_finished_ids:
                move.state = 'draft'
                move.quantity_done = 0.0
            for workorder in production.workorder_ids:
                workorder.state = 'pending'
            production.state = 'draft'
    
    def get_target_production(self):
        action = self.env["ir.actions.actions"]._for_xml_id("ny_mrp.wizard_mrp_sheet_to_produce_action")
        action['context'] = {'default_mrp_id': self.id,
                             'default_product_latex_id': self.bom_id.bom_line_ids.filtered(lambda x: x.product_id.name=='Lateks').product_id.id,
                             'default_bom_id': self.bom_id.id}
        return action

    def button_mark_done(self):
        for rec in self:
            # Wizard konfirmasi
            if not rec.env.context.get('from_wizard'):
                confirmation_message = f"Anda akan mencatat produksi {rec.qty_producing}/{rec.product_uom_id.name} '{rec.product_id.name}', apakah akan dilanjutkan?"
                return {
                    'type': 'ir.actions.act_window',
                    'res_model': 'wizard.action.validate',
                    'view_mode': 'form',
                    'view_id': self.env.ref('ny_mrp.view_wizard_action_validate_mo').id,
                    'target': 'new',
                    'context': {
                        'active_id': rec.id,
                        'active_model': rec._name,
                        'confirmation_message': confirmation_message
                    },
                }

        # Bagian override Odoo default: salin dari fungsi asli, ubah bagian product_qty
        self._button_mark_done_sanity_checks()

        if not self.env.context.get('button_mark_done_production_ids'):
            self = self.with_context(button_mark_done_production_ids=self.ids)
        res = self._pre_button_mark_done()
        if res is not True:
            return res

        if self.env.context.get('mo_ids_to_backorder'):
            productions_to_backorder = self.browse(self.env.context['mo_ids_to_backorder'])
            productions_not_to_backorder = self - productions_to_backorder
        else:
            productions_not_to_backorder = self
            productions_to_backorder = self.env['mrp.production']

        self.workorder_ids.button_finish()
        backorders = productions_to_backorder and productions_to_backorder._split_productions()
        backorders = backorders - productions_to_backorder

        productions_not_to_backorder._post_inventory(cancel_backorder=True)
        productions_to_backorder._post_inventory(cancel_backorder=True)

        done_move_finished_ids = (productions_to_backorder.move_finished_ids | productions_not_to_backorder.move_finished_ids).filtered(lambda m: m.state == 'done')
        done_move_finished_ids._trigger_assign()

        (productions_not_to_backorder.move_raw_ids | productions_not_to_backorder.move_finished_ids).filtered(lambda x: x.state not in ('done', 'cancel')).write({
            'state': 'done',
            'product_uom_qty': 0.0,
        })

        # Bagian yang diubah: gunakan production.product_qty
        for production in self:
            production.write({
                'date_finished': fields.Datetime.now(),
                'product_qty': production.product_qty,  # ubah dari qty_produced
                'priority': '0',
                'is_locked': True,
                'state': 'done',
            })

        if not backorders:
            if self.env.context.get('from_workorder'):
                return {
                    'type': 'ir.actions.act_window',
                    'res_model': 'mrp.production',
                    'views': [[self.env.ref('mrp.mrp_production_form_view').id, 'form']],
                    'res_id': self.id,
                    'target': 'main',
                }
            if self.user_has_groups('mrp.group_mrp_reception_report') and self.picking_type_id.auto_show_reception_report:
                lines = self.move_finished_ids.filtered(lambda m: m.product_id.type == 'product' and m.state != 'cancel' and m.quantity_done and not m.move_dest_ids)
                if lines:
                    if any(mo.show_allocation for mo in self):
                        return self.action_view_reception_report()
            return True

        context = self.env.context.copy()
        context = {k: v for k, v in context.items() if not k.startswith('default_')}
        for k in context:
            if k.startswith('skip_'):
                context[k] = False

        action = {
            'res_model': 'mrp.production',
            'type': 'ir.actions.act_window',
            'context': dict(context, mo_ids_to_backorder=None, button_mark_done_production_ids=None)
        }
        if len(backorders) == 1:
            action.update({
                'view_mode': 'form',
                'res_id': backorders[0].id,
            })
        else:
            action.update({
                'name': _("Backorder MO"),
                'domain': [('id', 'in', backorders.ids)],
                'view_mode': 'tree,form',
            })
        return action
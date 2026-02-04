from odoo import models, api, fields, Command, _
from odoo.exceptions import ValidationError

from dateutil.relativedelta import relativedelta
from lxml import etree

class ClosingProductionPlantationCost(models.Model):
    _name = 'closing.production.plantation.cost'
    _description = 'Closing Production for Plantation Cost Summary'

    closing_id = fields.Many2one('closing.production', string='Closing Production')
    closing_fg_id = fields.Many2one('closing.production.finishgood', string='Closing FG', ondelete='cascade')
    plantation_location_type_id = fields.Many2one('lhm.location.type', string='Tipe Lokasi', ondelete='restrict')
    plantation_location_id = fields.Many2one('lhm.location', string='Lokasi', ondelete='restrict')
    plantation_activity_id = fields.Many2one('lhm.activity', string='Aktivitas', ondelete='restrict')
    plantation_src_journal_id = fields.Many2one('account.journal', string='Asal Jurnal', ondelete='restrict')
    account_id = fields.Many2one('account.account', string='Account', ondelete='restrict')
    total_cost = fields.Float('Total Cost')
    total_cost_latex = fields.Float(compute='_compute_cost', store=True)
    total_cost_lump = fields.Float(compute='_compute_cost', store=True)
    is_plantation_cost = fields.Boolean()
    is_manufacturing_cost = fields.Boolean()
    is_mrp_sheet_cost = fields.Boolean()
    is_mrp_compound_cost = fields.Boolean()
    is_rm_sheet_cost = fields.Boolean()

    @api.depends('total_cost', 'closing_id', 'closing_fg_id', 
        'is_manufacturing_cost','is_mrp_sheet_cost', 'is_mrp_compound_cost',
        'is_rm_sheet_cost', 'is_plantation_cost',
        'closing_id.pct_cost_for_latex', 'closing_id.pct_cost_for_lump',
        'closing_id.pct_cost_for_sheet', 'closing_id.pct_cost_for_compound',
        )
    def _compute_cost(self):
        for l in self:
            if l.closing_id:
                if l.is_manufacturing_cost:
                    if l.is_mrp_sheet_cost:
                        l.total_cost_latex = l.total_cost
                        l.total_cost_lump = 0.0
                    elif l.is_mrp_compound_cost:
                        l.total_cost_latex = 0.0
                        l.total_cost_lump = l.total_cost
                    else:
                        l.total_cost_latex = l.total_cost * l.closing_id.pct_cost_for_sheet / 100.0
                        l.total_cost_lump = l.total_cost * l.closing_id.pct_cost_for_compound / 100.0
                elif l.is_rm_sheet_cost:
                    l.total_cost_latex = l.total_cost
                    l.total_cost_lump = 0.0
                # elif l.is_plantation_cost:
                else:
                    l.total_cost_latex = l.total_cost * l.closing_id.pct_cost_for_latex / 100.0
                    l.total_cost_lump = l.total_cost * l.closing_id.pct_cost_for_lump / 100.0
            else:
                l.total_cost_latex = 0.0
                l.total_cost_lump = 0.0

class ClosingProductionFinishGood(models.Model):
    _name = 'closing.production.finishgood'
    _description = 'Closing Production Finish Good'

    without_mrp = fields.Boolean()
    closing_process_id = fields.Many2one('closing.process', string='Closing Process')
    parent_state = fields.Selection(related='closing_process_id.state', store=True)
    closing_id = fields.Many2one('closing.production', string='Closing Production')
    prev_closing_fg_id = fields.Many2one('closing.production.finishgood', string='Last Closing Production')
    varieties_id = fields.Many2one('plant.varieties', string='Varitas')
    product_id = fields.Many2one('product.product', string='Product', ondelete='restrict')
    
    inventory_account_id = fields.Many2one('account.account', 'Account Inventory')
    cogs_account_id = fields.Many2one('account.account', 'Account COGS')
    scrap_account_id = fields.Many2one('account.account', 'Scrap Account')
    adjustment_account_id = fields.Many2one('account.account', 'Adjustment Account')

    opening_qty = fields.Float(compute='_compute_opening', inverse='_invrs_opening', readonly=False, store=True, string='Opening Qty')
    opening_qty_manual = fields.Float(string='Opening Qty')
    opening_value = fields.Float(compute='_compute_opening', inverse='_invrs_opening', readonly=False, store=True, string='Opening Value')
    opening_value_manual = fields.Float(string='Opening Value')

    manufacturing_cost = fields.Float(string='Manufacturing Cost')
    plantation_other_cost_account_ids = fields.Many2many('account.account', 'cls_prod_fg_account_karet_rel', string="Other Plantation Cost Account")
    plantation_cost = fields.Float(compute='_compute_plantation_cost', store=True, string='Plantation Cost')
    plantation_cost_ids = fields.One2many('closing.production.plantation.cost', 'closing_fg_id', 'Plantation Cost Summs')
    
    incoming_qty = fields.Float(string='Incoming Qty')
    onhand_qty = fields.Float(compute='_compute_onhand_and_cost_price', store=True, string='Onhand Qty')
    onhand_value = fields.Float(compute='_compute_onhand_and_cost_price', store=True, string='Onhand Value')
    new_cost_price = fields.Float(compute='_compute_onhand_and_cost_price', store=True, string='New Cost Price')
    
    ripening_qty = fields.Float('Ripening Qty')
    ripening_value = fields.Float(compute='_compute_outgoing_value', store=True, string ='Ripening Value')

    outgoing_qty = fields.Float(string='Delivered Qty')
    outgoing_value = fields.Float(compute='_compute_outgoing_value', store=True, string ='Delivered Value')

    outgoing_issue_qty = fields.Float(string='Other Issued Qty')
    outgoing_issue_value = fields.Float(compute='_compute_outgoing_value', store=True, string ='Other Issued Value')
    outgoing_issue_stock_move_ids = fields.Many2many('stock.move', 'closing_prod_fg_stock_move_rel', string='Issued Stock Moves')

    scrap_qty = fields.Float(string='Scrap Qty')
    scrap_value = fields.Float(compute='_compute_outgoing_value', store=True, string ='Scrap Value')

    adjustment_qty = fields.Float(string='Adjustment Qty')
    adjustment_value = fields.Float(compute='_compute_outgoing_value', store=True, string ='Adjustment Value')

    adjustment_closing_qty = fields.Float(string='Adjustment Closing Qty')
    adjustment_closing_value = fields.Float(compute='_compute_outgoing_value', store=True, string ='Adjustment Closing Value')

    adjustment_value_only = fields.Float(string='Adjustment Value only')

    closing_qty = fields.Float(compute='_compute_closing', store=True, string='Closing Qty')
    closing_value = fields.Float(compute='_compute_closing', store=True, string='Closing Value')

    # only for pisang
    inventory_ripening_account_id = fields.Many2one('account.account', 'Account Inventory Ripening')
    ripening_opening_qty = fields.Float(compute='_compute_opening', inverse='_invrs_opening', readonly=False, store=True, string='Opening Ripening Qty')
    ripening_opening_qty_manual = fields.Float(string='Manual Opening Ripening Qty')
    ripening_opening_value = fields.Float(compute='_compute_opening', inverse='_invrs_opening', readonly=False, store=True, string='Opening Ripening Value')
    ripening_opening_value_manual = fields.Float(string='Manual Opening Ripening Value')

    ripening_incoming_qty = fields.Float(compute='_compute_outgoing_value', store=True, string='Ripening Incoming Qty')
    ripening_incoming_value = fields.Float(compute='_compute_outgoing_value', store=True, string='Ripening Incoming Value')
    ripening_cost = fields.Float(compute='_compute_ripening_cost', store=True, string='Ripening Cost')

    ripening_onhand_qty = fields.Float(compute='_compute_ripening_onhand_and_cost_price', store=True, string='Onhand Ripening Qty')
    ripening_onhand_value = fields.Float(compute='_compute_ripening_onhand_and_cost_price', store=True, string='Onhand Ripening Value')
    new_cost_price_ripening = fields.Float(compute='_compute_ripening_onhand_and_cost_price', store=True, string='New Cost Price Ripening')

    ripening_outgoing_qty = fields.Float(string='Delivered Ripening Qty')
    ripening_outgoing_value = fields.Float(compute='_compute_outgoing_ripening_value', store=True, string ='Delivered Value')

    ripening_scrap_qty = fields.Float(string='Scrap Ripening Qty')
    ripening_scrap_value = fields.Float(compute='_compute_outgoing_ripening_value', store=True, string ='Scrap Value')
    
    ripening_closing_qty = fields.Float(compute='_compute_closing_ripening', store=True, string='Closing Ripening Qty')
    ripening_closing_value = fields.Float(compute='_compute_closing_ripening', store=True, string='Closing Ripening Value')

    closing_move_id = fields.Many2one('account.move', string='Journal Entry')

    ############ COMPUTED METHOD ###########
    @api.depends('prev_closing_fg_id')
    def _compute_opening(self):
        for line in self:
            line.opening_qty = line.prev_closing_fg_id.closing_qty if line.prev_closing_fg_id else line.opening_qty_manual
            line.opening_value = line.prev_closing_fg_id.closing_value if line.prev_closing_fg_id else line.opening_value_manual
            line.ripening_opening_qty = line.prev_closing_fg_id.ripening_closing_qty if line.prev_closing_fg_id else line.ripening_opening_qty_manual
            line.ripening_opening_value = line.prev_closing_fg_id.ripening_closing_value if line.prev_closing_fg_id else line.ripening_opening_value_manual

    @api.onchange('opening_qty', 'opening_value', 'ripening_opening_qty', 'ripening_opening_value')
    def _invrs_opening(self):
        for line in self:
            line.opening_qty_manual = line.opening_qty
            line.opening_value_manual = line.opening_value
            line.ripening_opening_qty_manual = line.ripening_opening_qty
            line.ripening_opening_value_manual = line.ripening_opening_value
    
    @api.depends('plantation_cost_ids','plantation_cost_ids.total_cost',
            'closing_id','closing_id.varieties_type','closing_id.plantation_cost',
            'closing_id.pisang_incoming_qty', 'incoming_qty')
    def _compute_plantation_cost(self):
        for line in self:
            if line.plantation_cost_ids:
                line.plantation_cost = sum(line.plantation_cost_ids.mapped('total_cost')) if line.plantation_cost_ids else 0.0
            elif line.closing_id and line.closing_id.varieties_type=='pisang':
                line.plantation_cost = line.incoming_qty * (line.closing_id.plantation_cost / line.closing_id.pisang_incoming_qty) if line.closing_id.pisang_incoming_qty else 0.0
            elif line.closing_id and line.closing_id.varieties_type=='melon':
                # line.plantation_cost = line.incoming_qty * (line.closing_id.plantation_cost / line.closing_id.melon_incoming_qty) if line.closing_id.melon_incoming_qty else 0.0
                qty = sum(line.closing_id.fg_melon_valuation_ids.mapped('opening_qty'))+line.closing_id.melon_incoming_qty
                line.plantation_cost = (line.opening_qty + line.incoming_qty) * (line.closing_id.plantation_cost / qty if qty else 0.0)
            else:
                line.plantation_cost = 0.0

    @api.depends('opening_qty', 'opening_value', 
            'incoming_qty', 'plantation_cost')
    def _compute_onhand_and_cost_price(self):
        for line in self:
            line.onhand_qty = line.opening_qty + line.incoming_qty
            line.onhand_value = line.opening_value + line.plantation_cost + line.manufacturing_cost
            line.new_cost_price = line.onhand_value/line.onhand_qty if line.onhand_qty else 0.0

    @api.depends('new_cost_price', 'outgoing_qty', 'ripening_qty', 'scrap_qty', 'adjustment_qty', 'adjustment_closing_qty')
    def _compute_outgoing_value(self):
        for line in self:
            line.outgoing_value = line.outgoing_qty * line.new_cost_price
            line.outgoing_issue_value = line.outgoing_issue_qty * line.new_cost_price
            line.ripening_value = line.ripening_qty * line.new_cost_price
            line.scrap_value = line.scrap_qty * line.new_cost_price
            line.adjustment_value = line.adjustment_qty * line.new_cost_price
            line.adjustment_closing_value = line.adjustment_closing_qty * line.new_cost_price
            line.ripening_incoming_qty = line.ripening_qty
            line.ripening_incoming_value = line.ripening_value

    @api.depends('onhand_qty', 'onhand_value', 
            'outgoing_qty', 'outgoing_value',
            'ripening_qty', 'ripening_value',
            'scrap_qty', 'scrap_value',
            'adjustment_qty', 'adjustment_value', 'adjustment_value_only'
            )
    def _compute_closing(self):
        for line in self:
            line.closing_qty = line.onhand_qty - line.ripening_qty - line.outgoing_qty - line.outgoing_issue_qty - line.scrap_qty + line.adjustment_qty
            line.closing_value = line.onhand_value - line.ripening_value - line.outgoing_value - line.outgoing_issue_value - line.scrap_value + line.adjustment_value + line.adjustment_value_only 
    
    @api.depends('closing_id', 'closing_id.varieties_type', 
        'ripening_incoming_qty', 'closing_id.pisang_ripening_cost', 
        'closing_id.pisang_ripening_qty')
    def _compute_ripening_cost(self):
        for line in self:
            if line.closing_id and line.closing_id.varieties_type=='pisang':
                line.ripening_cost = line.ripening_incoming_qty * (line.closing_id.pisang_ripening_cost/line.closing_id.pisang_ripening_qty) \
                        if line.closing_id.pisang_ripening_qty else 0.0
            else:
                line.ripening_cost = 0.0
            # print(">>>>>>>>>", line.ripening_cost)

    @api.depends('ripening_opening_qty', 'ripening_opening_value', 
            'ripening_incoming_qty', 'ripening_incoming_value', 'ripening_cost')
    def _compute_ripening_onhand_and_cost_price(self):
        for line in self:
            line.ripening_onhand_qty = line.ripening_opening_qty + line.ripening_incoming_qty
            line.ripening_onhand_value = line.ripening_opening_value + line.ripening_incoming_value + line.ripening_cost
            line.new_cost_price_ripening = line.ripening_onhand_value/line.ripening_onhand_qty if line.ripening_onhand_qty else 0.0

    @api.depends('new_cost_price_ripening', 'ripening_outgoing_qty', 'ripening_scrap_qty')
    def _compute_outgoing_ripening_value(self):
        for line in self:
            line.ripening_outgoing_value = line.ripening_outgoing_qty * line.new_cost_price_ripening
            line.ripening_scrap_value = line.ripening_scrap_qty * line.new_cost_price_ripening

    @api.depends('ripening_onhand_qty', 'ripening_onhand_value', 
            'ripening_outgoing_qty', 'ripening_outgoing_value',
            'ripening_scrap_qty', 'ripening_scrap_value')
    def _compute_closing_ripening(self):
        for line in self:
            line.ripening_closing_qty = line.ripening_onhand_qty - line.ripening_outgoing_qty - line.ripening_scrap_qty
            line.ripening_closing_value = line.ripening_onhand_value - line.ripening_outgoing_value - line.ripening_scrap_value

    def _help_compute_plantation_cost(self):
        self.ensure_one()
        closing_journal = self.env.ref('ny_closing.plantation_closing_plantation')
        # Find Plantation Cost based on Business Unit
        domain_plantation = [('parent_state','=','posted'),
            ('date','>=',self.closing_process_id.date_from),('date','<=',self.closing_process_id.date_to),
            ('plantation_varieties_id','=',self.varieties_id.id),
            ('plantation_location_type_id.plantation','=',True),
            ('plantation_location_id','!=',False),
            ('journal_id','=',closing_journal.id),
            # ('plantation_activity_id','!=',False),
            ]
        activities = self.env['lhm.activity']
        activities |= self.varieties_id.harvest_activity_ids
        activities |= self.varieties_id.upkeep_activity_ids
        # activities |= varieties.general_charges_activity_ids
        # activities |= varieties.indirect_cost_activity_ids
        plantation_cost_account_ids = []
        if activities:
            plantation_cost_account_ids = activities.cost_account_id.ids
        if plantation_cost_account_ids:
            domain_plantation.append(('account_id','in',plantation_cost_account_ids))
        # print(":::::::::::::::::::::::", domain_plantation)
        plantation_cost = self.env['account.move.line'].search(domain_plantation)
        # Grouping by Loc Type, Loc, Activity, Src Journal
        plantation_cost_grouped = {}
        plantation_cost_amt = 0.0
        for aml in plantation_cost:
            key = (aml.plantation_location_type_id.id, aml.plantation_location_id.id, aml.plantation_activity_id.id, aml.plantation_src_journal_id.id, aml.account_id)
            if key not in plantation_cost_grouped.keys():
                plantation_cost_grouped.update({key: {
                        'plantation_location_type_id': aml.plantation_location_type_id.id,
                        'plantation_location_id': aml.plantation_location_id.id,
                        'plantation_activity_id': aml.plantation_activity_id.id,
                        'plantation_src_journal_id': aml.plantation_src_journal_id.id,
                        'account_id': aml.account_id.id,
                        'total_cost': 0.0,
                    }
                })
            plantation_cost_grouped[key]['total_cost'] += aml.balance
            plantation_cost_amt += aml.balance
        plantation_cost_to_add = [(0,0,vals) for vals in plantation_cost_grouped.values()]
        # print(":::::::::::::::::::::::", plantation_cost_to_add)

        # >>>>>>>>>>>>>> Plantation Cost Other Accounts
        # Find Plantation Cost based on Business Unit
        if self.plantation_other_cost_account_ids:
            domain_plantation2 = [('parent_state','=','posted'),
                ('date','>=',self.closing_process_id.date_from),('date','<=',self.closing_process_id.date_to),
                # ('plantation_varieties_id','=',self.varieties_id.id),
                # ('plantation_location_type_id.plantation','=',True),
                # ('plantation_location_id','!=',False),
                ('journal_id','!=',closing_journal.id),
                ]
            if len(self.plantation_other_cost_account_ids.ids)==1:
                domain_plantation2.append(('account_id','=',self.plantation_other_cost_account_ids.id))
            else:
                domain_plantation2.append(('account_id','in',self.plantation_other_cost_account_ids.ids))
            plantation_cost2 = self.env['account.move.line'].search(domain_plantation2)
            # Grouping by Loc Type, Loc, Activity, Src Journal
            plantation_cost_grouped2 = {}
            for aml in plantation_cost2:
                key = (aml.plantation_location_type_id.id, aml.plantation_location_id.id, aml.plantation_activity_id.id, aml.plantation_src_journal_id.id, aml.account_id)
                if key not in plantation_cost_grouped2.keys():
                    plantation_cost_grouped2.update({key: {
                            'plantation_location_type_id': aml.plantation_location_type_id.id,
                            'plantation_location_id': aml.plantation_location_id.id,
                            'plantation_activity_id': aml.plantation_activity_id.id,
                            'plantation_src_journal_id': aml.plantation_src_journal_id.id,
                            'account_id': aml.account_id.id,
                            'total_cost': 0.0,
                        }
                    })
                plantation_cost_grouped2[key]['total_cost'] += aml.balance
                plantation_cost_amt += aml.balance
            plantation_cost_to_add.extend([(0,0,vals) for vals in plantation_cost_grouped2.values()])
        return plantation_cost_amt, plantation_cost_to_add
    #########################################
    #           BUSINESS METHOD             #
    #########################################
    def compute_initial_and_cost_oth_variant(self):
        for line in self:
            if not line.closing_process_id:
                continue
            incoming_naps = self.env['timbangan.pabrik'].search([('product_id','=',line.product_id.id),
                            ('lhm_nap_id.date_nap','>=',line.closing_process_id.date_from),
                            ('lhm_nap_id.date_nap','<=',line.closing_process_id.date_to),
                            ('lhm_nap_id.state','in',['confirmed','done'])])
            line.incoming_qty = sum(incoming_naps.mapped('product_qty')) if incoming_naps else 0.0

            outgoing_moves = self.env['stock.move'].search([('product_id','=',line.product_id.id),('state','=','done'),
                                ('location_id.usage','=','internal'),('location_dest_id.usage','!=','internal'),
                                ('date','>=',line.closing_process_id.date_from.strftime('%Y-%m-%d 00:00:00')),
                                ('date','<=',line.closing_process_id.date_to.strftime('%Y-%m-%d 23:59:59'))
                                ])
            line.outgoing_qty = sum(outgoing_moves.mapped('product_uom_qty')) if outgoing_moves else 0.0
            plantation_cost_amt, plantation_cost_to_add = line._help_compute_plantation_cost()
            if line.plantation_cost_ids:
                line.plantation_cost_ids.unlink()
            line.plantation_cost_ids = plantation_cost_to_add
            line.plantation_cost = plantation_cost_amt
    
    def action_compute_plant_cost(self):
        for line in self:
            plantation_cost_amt, plantation_cost_to_add = line._help_compute_plantation_cost()
            if line.plantation_cost_ids:
                line.plantation_cost_ids.unlink()
            line.plantation_cost_ids = plantation_cost_to_add
            line.plantation_cost = plantation_cost_amt
    
    def create_move_entry_fg(self):
        for line in self:
            move_lines_receiving = []
            move_lines_cogs = []
            if line.incoming_qty:
                vals_dest = {
                    'name': 'Inventory Receipt and Valuation',
                    'plantation_location_type_id': False,
                    'plantation_location_id': False,
                    'plantation_activity_id': False,
                    'plantation_src_journal_id': False,
                    'account_id': self.inventory_account_id.id,
                    'debit': self.plantation_cost if self.plantation_cost>0 else 0.0,
                    'credit': abs(self.plantation_cost) if self.plantation_cost<0 else 0.0,
                }
                move_lines_receiving.append((0,0,vals_dest))

            for pcost in line.plantation_cost_ids:
                vals_src = {
                    'name': 'Cost to Inventory',
                    'plantation_location_type_id': pcost.plantation_location_type_id.id if pcost.plantation_location_type_id else False,
                    'plantation_location_id': pcost.plantation_location_id.id if pcost.plantation_location_id else False,
                    'plantation_activity_id': pcost.plantation_activity_id.id if pcost.plantation_activity_id else False,
                    'plantation_src_journal_id': pcost.plantation_src_journal_id.id if pcost.plantation_src_journal_id else False,
                    'account_id': pcost.account_id.id,
                    'debit': abs(pcost.total_cost) if pcost.total_cost<0 else 0.0,
                    'credit': pcost.total_cost if pcost.total_cost>0 else 0.0,
                }
                move_lines_receiving.append((0,0,vals_src))
            
            if line.outgoing_qty:
                vals_dest2 = {
                    'name': f"Delivery {line.product_id.name}",
                    'plantation_location_type_id': False,
                    'plantation_location_id': False,
                    'plantation_activity_id': False,
                    'plantation_src_journal_id': False,
                    'account_id': self.cogs_account_id.id,
                    'debit': self.outgoing_value if self.outgoing_value>0 else 0.0,
                    'credit': abs(self.outgoing_value) if self.outgoing_value<0 else 0.0,
                }
                move_lines_cogs.append((0,0,vals_dest2))
                vals_src2 = vals_dest2.copy()
                vals_src2.update({
                    'account_id': self.inventory_account_id.id,
                    'debit': self.outgoing_value if self.outgoing_value>0 else 0.0,
                    'credit': abs(self.outgoing_value) if self.outgoing_value<0 else 0.0,
                })
                move_lines_cogs.append((0,0,vals_src2))
            
            if move_lines_receiving or move_lines_cogs:
                misc_journal = self.env.ref('ny_closing.plantation_closing_production')
                values = {
                    'date': line.closing_process_id.date_to,
                    'journal_id': misc_journal.id,
                    'move_type': 'entry',
                    'line_ids': move_lines_receiving+move_lines_cogs,
                }
                new_move = self.env['account.move'].create(values)
                line.closing_move_id = new_move.id
    
    @api.model
    def get_views(self, views, options=None):
        result = super(ClosingProductionFinishGood, self).get_views(views, options=options)
        # if self._context.get('params',{}).get('id',0)>0:
        #     res_active_rec = self.search_read([('id','=',self._context['params']['id'])], ['state'])
        #     if res_active_rec and res_active_rec[0]['state'] not in ('draft','cancel'):
        #         form_arch = etree.fromstring(result['views']['form']['arch'])
        #         page_name_active = res_active_rec[0]['state']
        #         if page_name_active=='done':
        #             page_name_active = 'closing_production'
        #         for node in form_arch.xpath(f"//page[@name='{page_name_active}']"):
        #             node.set("autofocus", "autofocus")
        #         result['views']['form']['arch'] = etree.tostring(form_arch, encoding="unicode").replace('\t', '')
        return result

class ClosingProduction(models.Model):
    _name = 'closing.production'
    _description = 'Closing Production'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    closing_process_id = fields.Many2one('closing.process', string='Closing Process', ondelete='cascade')
    parent_state = fields.Selection(related='closing_process_id.state', store=True)
    prev_closing_id = fields.Many2one('closing.production', string='Last Closing Production')
    varieties_type = fields.Selection([('karet','Karet'),('pisang','Pisang'),('melon','Melon')], string='Varitas')
    date_from = fields.Date()
    date_to = fields.Date()
    state = fields.Selection([('start','Start'),
            ('rm_valuation','Raw Material'),
            ('fg_valuation','Finish Good'),
            ('account_entry','Jurnal Creation'),
            ('done','Done'),
            ('cancel','Cancelled')], string='Status', default='start')

    plantation_other_cost_account_ids = fields.Many2many('account.account', 'cls_prod_account_karet_rel', string="Other Plantation Cost Account")    
    plantation_cost_ids = fields.One2many('closing.production.plantation.cost', 'closing_id', domain=[('is_plantation_cost','=',True)], string='Plantation Cost Summs')
    plantation_cost = fields.Float(compute='_compute_plantation_cost', store=True, string='Total Plantation Cost')

    closing_move_ids = fields.Many2many('account.move', 'closing_prod_acc_move_rel', string='Closing Entries')

    manufacturing_cost_account_ids = fields.Many2many('account.account', 'closing_prod_mrp_cost_account_rel', string='Manufacturing Cost Accounts')
    mrp_sheet_cost_account_ids = fields.Many2many('account.account', 'closing_prod_sheet_cost_account_rel', string='Sheet Cost Accounts')
    mrp_compound_cost_account_ids = fields.Many2many('account.account', 'closing_prod_compound_cost_account_rel', string='Compo Cost Accounts')
    mrp_cost_ids = fields.One2many('closing.production.plantation.cost', 'closing_id', domain=[('is_manufacturing_cost','=',True)], string='Manufacturing Cost Summs')
    manufacturing_cost = fields.Float('Total Manufacturing Cost')
    mrp_sheet_cost = fields.Float('Total Sheet Cost')
    mrp_compound_cost = fields.Float('Total Compound Cost')
    ############################## BEGIN VALUATION RAW MATERIAL ##################################
    # The product are only for Lateks and Lump
    ##############################
    # Lateks
    latex_product_id = fields.Many2one('product.product', string='Product Lateks', ondelete='restrict')
    latex_inventory_account_id = fields.Many2one('account.account', 'Account Inventory Lateks')
    latex_wip_account_id = fields.Many2one('account.account', 'Account WIP Lateks')
    latex_consumption_account_id = fields.Many2one('account.account', 'Account Consumption Lateks')
    latex_adjustment_account_id = fields.Many2one('account.account', 'Account Adjustment Lateks')
    latex_cogs_account_id = fields.Many2one('account.account', 'Account CoGS Lateks')

    latex_opening_qty = fields.Float(compute='_compute_opening_rm', inverse='_invrs_opening_rm', readonly=False, store=True, string='Beginning Qty of Lateks')
    latex_opening_qty_manual = fields.Float()
    latex_opening_value = fields.Float(compute='_compute_opening_rm', inverse='_invrs_opening_rm', readonly=False, store=True, string='Beginning Value of Lateks')
    latex_opening_value_manual = fields.Float()
    latex_incoming_qty = fields.Float(string='Incoming Qty of Lateks')
    
    pct_cost_for_latex = fields.Float('% Cost for Lateks', default=90)
    latex_plantation_cost = fields.Float(compute='_compute_plantation_cost', store=True, string='Plantation Cost of Lateks')
    latex_onhand_qty = fields.Float(compute='_compute_onhand_and_cost_price_rm', store=True, string='Onhand Qty of Lateks')
    latex_onhand_value = fields.Float(compute='_compute_onhand_and_cost_price_rm', store=True, string='Onhand Value of Lateks')
    latex_new_cost_price = fields.Float(compute='_compute_onhand_and_cost_price_rm', store=True, string='New Cost Price of Lateks')
    
    # latex_wip_opening_qty = fields.Float(compute='_compute_opening_rm', inverse='_invrs_opening_rm', readonly=False, store=True, string='Beginning WIP Lateks')
    latex_wip_opening_qty = fields.Float(string='Beginning WIP Lateks')
    latex_wip_opening_qty_manual = fields.Float()
    latex_wip_opening_value = fields.Float(compute='_compute_opening_rm', inverse='_invrs_opening_rm', readonly=False, store=True, string='Beginning Value WIP Lateks')
    latex_wip_opening_value_manual = fields.Float()
    latex_wip_value_manual = fields.Float()
    latex_wip_incoming_qty = fields.Float(string='New Prod. Order Sheet')
    latex_wip_incoming_value = fields.Float(compute='_compute_outgoing_value_rm', store=True, string='New Prod. Order Value Sheet')
    
    pct_cost_for_sheet = fields.Float('% Cost for Sheet', default=90)
    sheet_manufacturing_cost = fields.Float(compute='_compute_mrp_cost_distribution', store=True, string='Manufacturing Cost of Sheet')
    sheet_production_cost = fields.Float(compute='_compute_mrp_cost_distribution', store=True, string='Production Cost of Sheet')
    
    # Asam Semut
    sheet_rm_inventory_account_id = fields.Many2one('account.account', string='Inventory Account Asam Semut')
    sheet_rm_purchase_account_id = fields.Many2one('account.account', string='Purchase Account Asam Semut')
    sheet_rm_consumption_account_id = fields.Many2one('account.account', string='Consumption Account Asam Semut')
    sheet_rm_adjustment_account_id = fields.Many2one('account.account', string='Adjustment Account Asam Semut')
    sheet_rm_opening_qty = fields.Float(compute='_compute_opening_rm', inverse='_invrs_opening_rm', readonly=False, store=True, string='Begining Qty of Asam Semut')
    sheet_rm_opening_qty_manual = fields.Float(string='Begining Qty of Asam Semut')
    sheet_rm_opening_value = fields.Float(compute='_compute_opening_rm', inverse='_invrs_opening_rm', readonly=False, store=True, string='Begining Value of Asam Semut')
    sheet_rm_opening_value_manual = fields.Float(string='Begining Value of Asam Semut')
    
    sheet_rm_opening_adjustment_value_enable = fields.Boolean(string='Enable Adjustment Opening Value')
    sheet_rm_opening_adjustment_value = fields.Float(string='Adjustment Opening Value')
    sheet_rm_opening_adjustment_diff = fields.Float(compute='_compute_opening_adj_value_diff', store=True, string='Adjustment Opening Value Diff')
    # sheet_rm_closing_adjustment_account_id = fields.Many2one('account.account', string='Adjustment Account Asam Semut')
    @api.depends('sheet_rm_opening_value', 'sheet_rm_opening_adjustment_value_enable',
                 'sheet_rm_opening_adjustment_value')
    def _compute_opening_adj_value_diff(self):
        for closing in self:
            if closing.sheet_rm_opening_adjustment_value_enable:
                closing.sheet_rm_opening_adjustment_diff = closing.sheet_rm_opening_adjustment_value - closing.sheet_rm_opening_value
            else:
                closing.sheet_rm_opening_adjustment_diff = 0
    
    sheet_rm_incoming_qty = fields.Float(string='Incoming Qty of Asam Semut')
    sheet_rm_incoming_value = fields.Float(string='Incoming Qty of Asam Semut')
    sheet_rm_onhand_qty = fields.Float(compute='_compute_onhand_asam_semut', store=True, string='Onhand Qty of Asam Semut')
    sheet_rm_onhand_value = fields.Float(compute='_compute_onhand_asam_semut', store=True, string='Onhand Value of Asam Semut')
    sheet_rm_cost_price = fields.Float(compute='_compute_onhand_asam_semut', store=True, string='New Cost Price of Asam Semut')
    sheet_rm_outgoing_qty = fields.Float(string='Consumed Qty of Asam Semut')
    sheet_rm_outgoing_value = fields.Float(compute='_compute_closing_asam_semut', store=True, string='Consumed Qty of Asam Semut')
    sheet_rm_adjustment_qty = fields.Float(string='Adjustment Qty of Asam Semut')
    sheet_rm_adjustment_value = fields.Float(compute='_compute_closing_asam_semut', store=True, string='Adjustment Value of Asam Semut')
    sheet_rm_closing_qty = fields.Float(compute='_compute_closing_asam_semut', store=True, string='Ending Qty of Asam Semut')
    sheet_rm_closing_value = fields.Float(compute='_compute_closing_asam_semut', store=True, string='Ending Value of Asam Semut')
    
    sheet_rm_closing_adjustment_value_enable = fields.Boolean(string='Enable Adjustment Closing Value')
    sheet_rm_closing_adjustment_value = fields.Float(string='Adjustment Closing Value')
    sheet_rm_closing_adjustment_diff = fields.Float(compute='_compute_closing_adj_value_diff', store=True, string='Adjustment Closing Value Diff')
    sheet_rm_closing_value2 = fields.Float(compute='_compute_closing_adj_value_diff', store=True, string='Ending Value of Asam Semut')
    # sheet_rm_closing_adjustment_account_id = fields.Many2one('account.account', string='Adjustment Account Asam Semut')
    @api.depends('sheet_rm_closing_value', 'sheet_rm_closing_adjustment_value_enable', 
                 'sheet_rm_closing_adjustment_value')
    def _compute_closing_adj_value_diff(self):
        for closing in self:
            if closing.sheet_rm_closing_adjustment_value_enable:
                closing.sheet_rm_closing_adjustment_diff = closing.sheet_rm_closing_adjustment_value - closing.sheet_rm_closing_value
                closing.sheet_rm_closing_value2 = closing.sheet_rm_closing_value + closing.sheet_rm_closing_adjustment_diff
            else:
                closing.sheet_rm_closing_adjustment_diff = 0
                closing.sheet_rm_closing_value2 = closing.sheet_rm_closing_value

    sheet_raw_material_cost = fields.Float(compute='_compute_closing_asam_semut', store=True, string='Raw Material Cost of Sheet')

    latex_wip_onhand_qty = fields.Float(compute='_compute_onhand_wip_rm', store=True, string='Current WIP Lateks')
    latex_wip_adjustment_qty = fields.Float(string='Adjustment WIP Lateks')
    latex_wip_onhand_value = fields.Float(compute='_compute_onhand_wip_rm', store=True, string='Current Value WIP Lateks')
    latex_wip_cost_price = fields.Float(compute='_compute_onhand_wip_rm', store=True, string='Cost Price WIP Lateks')
    latex_wip_outgoing_qty = fields.Float(string='Finished Process Sheet')
    
    latex_wip_outgoing_value = fields.Float(compute='_compute_closing_wip_value_rm', store=True, string='Finished Process Value Sheet')
    latex_wip_qty = fields.Float(compute='_compute_closing_wip_value_rm', store=True, string='Closing WIP Lateks')
    latex_wip_value = fields.Float(compute='_compute_closing_wip_value_rm', store=True, string='Lateks Value WIP Lateks')

    # latex_outgoing_qty = fields.Float(string='Consumed Qty of Lateks')
    # # latex_outgoing_value = fields.Float(compute='_compute_outgoing_value_rm', store=True, string='Consumed Value of Lateks')
    latex_delivered_qty = fields.Float(string='Sales Delivered Qty of Lateks')
    latex_adjustment_qty = fields.Float(string='Adjusted Qty of Lateks')
    latex_delivered_value = fields.Float(compute='_compute_outgoing_value_latex_lump', store=True, string='Sales Delivered Value of Lateks')
    latex_adjustment_value = fields.Float(compute='_compute_outgoing_value_latex_lump', store=True, string='Adjusted Value of Lateks')
    latex_closing_qty = fields.Float(compute='_compute_closing_rm', store=True, string='Closing Qty of Lateks')
    latex_closing_value = fields.Float(compute='_compute_closing_rm', store=True, string='Closing Value of Lateks')
    ##############################
    # Lump
    lump_product_id = fields.Many2one('product.product', string='Product Lump', ondelete='restrict')
    lump_inventory_account_id = fields.Many2one('account.account', 'Account Inventory Lump')
    lump_wip_account_id = fields.Many2one('account.account', 'Account WIP Lump')
    lump_consumption_account_id = fields.Many2one('account.account', 'Account Consumption Lump')
    lump_adjustment_account_id = fields.Many2one('account.account', 'Account Adjustment Lump')
    lump_cogs_account_id = fields.Many2one('account.account', 'Account CoGS Lump')
    
    lump_opening_qty = fields.Float(compute='_compute_opening_rm', inverse='_invrs_opening_rm', readonly=False, store=True, string='Beginning Qty of Lump')
    lump_opening_qty_manual = fields.Float(string='Opening Qty of Lump')
    lump_opening_value = fields.Float(compute='_compute_opening_rm', inverse='_invrs_opening_rm', readonly=False, store=True, string='Beginning Value of Lump')
    lump_opening_value_manual = fields.Float(string='Opening Value of Lump')
    lump_incoming_qty = fields.Float(string='Incoming Qty of Lump')
    
    pct_cost_for_lump = fields.Float('% Cost for Lump', default=10)
    lump_plantation_cost = fields.Float(compute='_compute_plantation_cost', store=True, string='Plantation Cost of Lump')
    
    lump_onhand_qty = fields.Float(compute='_compute_onhand_and_cost_price_rm', store=True, string='Onhand Qty of Lump')
    lump_onhand_value = fields.Float(compute='_compute_onhand_and_cost_price_rm', store=True, string='Onhand Value of Lump')
    lump_new_cost_price = fields.Float(compute='_compute_onhand_and_cost_price_rm', store=True, string='New Cost Price of Lump')
    
    lump_wip_opening_qty = fields.Float(string='Beginning WIP Lump')
    # lump_wip_opening_qty = fields.Float(compute='_compute_opening_rm', inverse='_invrs_opening_rm', readonly=False, store=True, string='Beginning WIP Lump')
    lump_wip_opening_qty_manual = fields.Float()
    lump_wip_opening_value = fields.Float(compute='_compute_opening_rm', inverse='_invrs_opening_rm', readonly=False, store=True, string='Beginning Value WIP Lump')
    lump_wip_opening_value_manual = fields.Float()
    lump_wip_value_manual = fields.Float()
    lump_wip_incoming_qty = fields.Float(string='New Prod. Order Compo')
    lump_wip_incoming_value = fields.Float(compute='_compute_outgoing_value_rm', store=True, string='New Prod. Order Value Compo')
    
    pct_cost_for_compound = fields.Float('% Cost for Compo', default=10)
    compound_manufacturing_cost = fields.Float(compute='_compute_mrp_cost_distribution', store=True, string='Manufacturing Cost of Compo')
    # compound_raw_material_cost = fields.Float(string='Raw Material Cost of Compo')
    compound_production_cost = fields.Float(compute='_compute_mrp_cost_distribution', store=True, string='Production Cost of Compo')

    lump_wip_onhand_qty = fields.Float(compute='_compute_onhand_wip_rm', store=True, string='Current WIP Lump')
    lump_wip_onhand_value = fields.Float(compute='_compute_onhand_wip_rm', store=True, string='Current Value WIP Lump')
    lump_wip_cost_price = fields.Float(compute='_compute_onhand_wip_rm', store=True, string='Cost Price WIP Lump')
    lump_wip_outgoing_qty = fields.Float(string='Finished Process Compo')
    lump_wip_outgoing_value = fields.Float(compute='_compute_closing_wip_value_rm', store=True, string='Finished Process Value Compo')
    lump_wip_adjustment_qty = fields.Float(string='Adjustment WIP Lump')
    lump_wip_qty = fields.Float(compute='_compute_closing_wip_value_rm', store=True, string='Closing WIP Lump')
    lump_wip_value = fields.Float(compute='_compute_closing_wip_value_rm', store=True, string='Closing WIP Value Lump')
    
    # lump_outgoing_qty = fields.Float(string='Consumed Qty of Lump')
    # lump_outgoing_value = fields.Float(compute='_compute_outgoing_value_rm', store=True, string ='Consumed Value of Lump')
    lump_delivered_qty = fields.Float(string='Sales Delivered Qty of Lump')
    lump_adjustment_qty = fields.Float(string='Adjusted Qty of Lump')
    lump_delivered_value = fields.Float(compute='_compute_outgoing_value_latex_lump', store=True, string='Sales Delivered Value of Lump')
    lump_adjustment_value = fields.Float(compute='_compute_outgoing_value_latex_lump', store=True, string='Adjusted Value of Lump')
    lump_closing_qty = fields.Float(compute='_compute_closing_rm', store=True, string='Closing Qty of Lump')
    lump_closing_value = fields.Float(compute='_compute_closing_rm', store=True, string='Closing Value of Lump')

    # #################################################################################################
    # # Sheet
    sheet_product_id = fields.Many2one('product.product', string='Product Sheet', ondelete='restrict')
    sheet_wip_account_id = fields.Many2one('account.account', 'Account WIP Sheet')
    sheet_rm_account_id = fields.Many2one('account.account', 'Account Cost Asam Semut')
    # # Compound
    compound_product_id = fields.Many2one('product.product', string='Product Sheet', ondelete='restrict')
    compound_wip_account_id = fields.Many2one('account.account', 'Account WIP Compo')
    
    fg2_valuation_ids = fields.One2many('closing.production.finishgood', 'closing_id', string='Finish Goods Valuation')
    fg_karet_valuation_ids = fields.One2many('closing.production.finishgood', 'closing_id', string='Valuation Product Karet')
    fg_pisang_valuation_ids = fields.One2many('closing.production.finishgood', 'closing_id', string='Valuation Product Pisang')
    fg_melon_valuation_ids = fields.One2many('closing.production.finishgood', 'closing_id', string='Valuation Product Melon')

    ############################# PISANG ###########################
    # Pisang
    pisang_product_id = fields.Many2one('product.product', string='Product Pisang', ondelete='restrict')
    pisang_inventory_account_id = fields.Many2one('account.account', 'Account Inventory Pisang')
    pisang_wip_account_id = fields.Many2one('account.account', 'Account WIP Pisang')
    
    # plantation_cost
    pisang_varieties_id = fields.Many2one('plant.varieties', string='Varitas Pisang')
    pisang_other_product_ids = fields.Many2many(related='pisang_varieties_id.other_product_ids')
    pisang_incoming_qty = fields.Float(compute='_compute_incoming_qty_pisang', store=True, string='Incoming Qty of Pisang')
    pisang_ripening_cost = fields.Float('Pisang Ripening Cost')
    pisang_ripening_qty = fields.Float(compute='_compute_incoming_qty_pisang', store=True, string='Ripening Qty of Pisang')
    pisang_non_grade_ids = fields.Many2many('product.product', 'plant_pisang_non_grade_rel', string='Pisang Non Grade')
    pisang_with_grade_ids = fields.Many2many('product.product', 'plant_pisang_with_grade_rel', string='Pisang with Grade')
    ##############################

    ############################# Melon ###########################
    # Melon
    melon_product_id = fields.Many2one('product.product', string='Product Melon', ondelete='restrict')
    melon_inventory_account_id = fields.Many2one('account.account', 'Account Inventory Melon')
    
    # plantation_cost
    melon_varieties_id = fields.Many2one('plant.varieties', string='Varitas Melon')
    melon_other_product_ids = fields.Many2many(related='melon_varieties_id.other_product_ids')
    melon_incoming_qty = fields.Float(compute='_compute_incoming_qty_melon', store=True, string='Incoming Qty of Melon')
    # melon_ripening_cost = fields.Float('Melon Ripening Cost')
    # melon_ripening_qty = fields.Float(compute='_compute_incoming_qty_pisang', store=True, string='Ripening Qty of Melon')
    ##############################

    ############ COMPUTED METHOD ###########
    @api.depends('prev_closing_id')
    def _compute_opening_rm(self):
        for closing in self:
            closing.latex_opening_qty = closing.prev_closing_id.latex_closing_qty if closing.prev_closing_id else closing.latex_opening_qty_manual
            closing.latex_opening_value = closing.prev_closing_id.latex_closing_value if closing.prev_closing_id else closing.latex_opening_value_manual
            # closing.latex_wip_opening_qty = closing.prev_closing_id.latex_wip_qty if closing.prev_closing_id else closing.latex_wip_opening_qty_manual
            closing.latex_wip_opening_value = closing.prev_closing_id.latex_wip_value if closing.prev_closing_id else closing.latex_wip_opening_value_manual
            
            closing.lump_opening_qty = closing.prev_closing_id.lump_closing_qty if closing.prev_closing_id else closing.lump_opening_qty_manual
            closing.lump_opening_value = closing.prev_closing_id.lump_closing_value if closing.prev_closing_id else closing.lump_opening_value_manual
            # closing.lump_wip_opening_qty = closing.prev_closing_id.lump_wip_qty if closing.prev_closing_id else closing.lump_wip_opening_qty_manual
            closing.lump_wip_opening_value = closing.prev_closing_id.lump_wip_value if closing.prev_closing_id else closing.lump_wip_opening_value_manual

            closing.sheet_rm_opening_qty = closing.prev_closing_id.sheet_rm_closing_qty if closing.prev_closing_id else closing.sheet_rm_closing_qty_manual
            closing.sheet_rm_opening_value = closing.prev_closing_id.sheet_rm_closing_value if closing.prev_closing_id else closing.sheet_rm_closing_value_manual

    @api.onchange('latex_opening_qty', 'latex_opening_value',
            # 'latex_wip_opening_qty', 
            'latex_wip_opening_value',
            'lump_opening_qty', 'lump_opening_value',
            # 'lump_wip_opening_qty', 
            'lump_wip_opening_value')
    def _invrs_opening_rm(self):
        for closing in self:
            closing.latex_opening_qty_manual = closing.latex_opening_qty
            closing.latex_opening_value_manual = closing.latex_opening_value
            # closing.latex_wip_opening_qty_manual = closing.latex_wip_opening_qty
            closing.latex_wip_opening_value_manual = closing.latex_wip_opening_value
            
            closing.lump_opening_qty_manual = closing.lump_opening_qty
            closing.lump_opening_value_manual = closing.lump_opening_value
            # closing.lump_wip_opening_qty_manual = closing.lump_wip_opening_qty
            closing.lump_wip_opening_value_manual = closing.lump_wip_opening_value

    @api.depends('pct_cost_for_latex', 'pct_cost_for_lump', 
        'plantation_cost_ids.total_cost_latex', 'plantation_cost_ids.total_cost_lump')
    def _compute_plantation_cost(self):
        for closing in self:
            closing.latex_plantation_cost = sum(closing.plantation_cost_ids.mapped('total_cost_latex')) if closing.plantation_cost_ids else 0.0
            closing.lump_plantation_cost = sum(closing.plantation_cost_ids.mapped('total_cost_lump')) if closing.plantation_cost_ids else 0.0
    
    @api.depends('sheet_rm_opening_qty', 'sheet_rm_opening_value',
                 'sheet_rm_incoming_qty', 'sheet_rm_incoming_value',
                 'sheet_rm_opening_adjustment_diff')
    def _compute_onhand_asam_semut(self):
        for closing in self:
            closing.sheet_rm_onhand_qty = closing.sheet_rm_opening_qty + closing.sheet_rm_incoming_qty
            closing.sheet_rm_onhand_value = closing.sheet_rm_opening_value + closing.sheet_rm_opening_adjustment_diff + closing.sheet_rm_incoming_value
            closing.sheet_rm_cost_price = closing.sheet_rm_onhand_value/closing.sheet_rm_onhand_qty if closing.sheet_rm_onhand_qty else 0.0
    
    @api.depends('sheet_rm_outgoing_qty', 'sheet_rm_cost_price',
                 'sheet_rm_onhand_qty', 'sheet_rm_onhand_value',
                 'sheet_rm_adjustment_qty', 'sheet_rm_adjustment_value')
    def _compute_closing_asam_semut(self):
        for closing in self:
            closing.sheet_rm_outgoing_value = closing.sheet_rm_cost_price * closing.sheet_rm_outgoing_qty
            closing.sheet_rm_adjustment_value = closing.sheet_rm_cost_price * closing.sheet_rm_adjustment_qty
            closing.sheet_rm_closing_qty = closing.sheet_rm_onhand_qty - closing.sheet_rm_outgoing_qty + closing.sheet_rm_adjustment_qty
            closing.sheet_rm_closing_value = closing.sheet_rm_onhand_value - closing.sheet_rm_outgoing_value + closing.sheet_rm_adjustment_value
            closing.sheet_raw_material_cost = closing.sheet_rm_outgoing_value

    @api.depends('latex_opening_qty', 'latex_opening_value', 
            'latex_incoming_qty', 'latex_plantation_cost',
            'lump_opening_qty', 'lump_opening_value', 
            'lump_incoming_qty', 'lump_plantation_cost')
    def _compute_onhand_and_cost_price_rm(self):
        for closing in self:
            closing.latex_onhand_qty = closing.latex_opening_qty + closing.latex_incoming_qty
            closing.latex_onhand_value = closing.latex_opening_value + closing.latex_plantation_cost
            closing.latex_new_cost_price = closing.latex_onhand_value/closing.latex_onhand_qty if closing.latex_onhand_qty else 0.0
            closing.lump_onhand_qty = closing.lump_opening_qty + closing.lump_incoming_qty
            closing.lump_onhand_value = closing.lump_opening_value + closing.lump_plantation_cost
            closing.lump_new_cost_price = closing.lump_onhand_value/closing.lump_onhand_qty if closing.lump_onhand_qty else 0.0

    @api.depends('latex_new_cost_price', 'latex_wip_incoming_qty',
            'lump_new_cost_price', 'lump_wip_incoming_qty')
    def _compute_outgoing_value_rm(self):
        for closing in self:
            closing.latex_wip_incoming_value = closing.latex_wip_incoming_qty * closing.latex_new_cost_price
            closing.lump_wip_incoming_value = closing.lump_wip_incoming_qty * closing.lump_new_cost_price

    @api.depends('pct_cost_for_sheet', 'pct_cost_for_compound', 
        'mrp_cost_ids.total_cost_latex', 'mrp_cost_ids.total_cost_lump',
        'mrp_sheet_cost','mrp_compound_cost')
    def _compute_mrp_cost_distribution(self):
        for closing in self:
            mrp_cost_only = closing.mrp_cost_ids.filtered(lambda x: x.is_manufacturing_cost and not x.is_mrp_sheet_cost and not x.is_mrp_compound_cost)
            closing.sheet_manufacturing_cost = sum(mrp_cost_only.mapped('total_cost_latex')) if mrp_cost_only else 0.0
            closing.compound_manufacturing_cost = sum(mrp_cost_only.mapped('total_cost_lump')) if mrp_cost_only else 0.0
            closing.sheet_production_cost = closing.sheet_manufacturing_cost + closing.mrp_sheet_cost
            closing.compound_production_cost = closing.compound_manufacturing_cost + closing.mrp_compound_cost

    # @api.depends('manufacturing_cost', 
    #         'pct_cost_for_sheet', 'pct_cost_for_compound')
    # def _compute_mrp_cost_distribution(self):
    #     for closing in self:
    #         closing.sheet_manufacturing_cost = (closing.manufacturing_cost * closing.pct_cost_for_sheet / 100.0)
    #         closing.compound_manufacturing_cost = closing.manufacturing_cost * closing.pct_cost_for_compound / 100.0
    #         # closing.sheet_production_cost = closing.sheet_manufacturing_cost + closing.sheet_raw_material_cost
    #         closing.sheet_production_cost = closing.sheet_manufacturing_cost
    #         # closing.compound_production_cost = closing.compound_manufacturing_cost + closing.compound_raw_material_cost
    #         closing.compound_production_cost = closing.compound_manufacturing_cost

    @api.depends('latex_wip_opening_qty', 'latex_wip_incoming_qty', 
            'latex_wip_opening_value', 'latex_wip_incoming_value',
            'lump_wip_opening_qty', 'lump_wip_incoming_qty', 
            'lump_wip_opening_value', 'lump_wip_incoming_value',
            'sheet_production_cost', 'compound_production_cost',
            'sheet_raw_material_cost')
    def _compute_onhand_wip_rm(self):
        for closing in self:
            closing.latex_wip_onhand_qty = closing.latex_wip_opening_qty + closing.latex_wip_incoming_qty
            # closing.latex_wip_onhand_value = closing.latex_wip_opening_value + closing.latex_wip_incoming_value + closing.sheet_production_cost
            closing.latex_wip_onhand_value = closing.latex_wip_opening_value + closing.latex_wip_incoming_value + closing.sheet_production_cost + closing.sheet_raw_material_cost
            closing.latex_wip_cost_price = closing.latex_wip_onhand_value/closing.latex_wip_onhand_qty if closing.latex_wip_onhand_qty else 0.0
            closing.lump_wip_onhand_qty = closing.lump_wip_opening_qty + closing.lump_wip_incoming_qty
            closing.lump_wip_onhand_value = closing.lump_wip_opening_value + closing.lump_wip_incoming_value + closing.compound_production_cost
            closing.lump_wip_cost_price = closing.lump_wip_onhand_value/closing.lump_wip_onhand_qty if closing.lump_wip_onhand_qty else 0.0

    @api.depends('latex_wip_outgoing_qty', 
                'latex_wip_cost_price', 'latex_wip_onhand_qty',
                'latex_wip_adjustment_qty',
                'lump_wip_outgoing_qty', 'lump_wip_cost_price', 'lump_wip_onhand_qty',
                'lump_wip_adjustment_qty',)
    def _compute_closing_wip_value_rm(self):
        for closing in self:
            closing.latex_wip_outgoing_value = round(closing.latex_wip_outgoing_qty * closing.latex_wip_cost_price, 2)
            closing.latex_wip_qty = closing.latex_wip_onhand_qty - closing.latex_wip_outgoing_qty + closing.latex_wip_adjustment_qty
            closing.latex_wip_value = closing.latex_wip_onhand_value - closing.latex_wip_outgoing_value
            closing.lump_wip_outgoing_value = round(closing.lump_wip_outgoing_qty * closing.lump_wip_cost_price, 2)
            closing.lump_wip_qty = closing.lump_wip_onhand_qty - closing.lump_wip_outgoing_qty + closing.lump_wip_adjustment_qty
            closing.lump_wip_value = closing.lump_wip_onhand_value - closing.lump_wip_outgoing_value

    @api.depends('latex_delivered_qty', 'lump_delivered_qty', 
            'latex_adjustment_qty', 'lump_adjustment_qty',
            'latex_new_cost_price', 'lump_new_cost_price', 
            )
    def _compute_outgoing_value_latex_lump(self):
        for closing in self:
            closing.latex_delivered_value = round(closing.latex_delivered_qty * closing.latex_new_cost_price, 2)
            closing.lump_delivered_value = round(closing.lump_delivered_qty * closing.lump_new_cost_price, 2)
            closing.latex_adjustment_value = round(closing.latex_adjustment_qty * closing.latex_new_cost_price, 2)
            closing.lump_adjustment_value = round(closing.lump_adjustment_qty * closing.lump_new_cost_price, 2)

    @api.depends('latex_onhand_qty', 'latex_onhand_value', 
            'latex_wip_incoming_qty', 'latex_wip_incoming_value',
            'lump_onhand_qty', 'lump_onhand_value', 
            'lump_wip_incoming_qty', 'lump_wip_incoming_value', 
            'latex_delivered_qty','lump_delivered_qty',
            'latex_adjustment_qty','lump_adjustment_qty',
            'latex_delivered_value','lump_delivered_value',
            'latex_adjustment_value','lump_adjustment_value',
            )
    def _compute_closing_rm(self):
        for closing in self:
            closing.latex_closing_qty = closing.latex_onhand_qty - closing.latex_wip_incoming_qty - closing.latex_delivered_qty + closing.latex_adjustment_qty
            closing.latex_closing_value = closing.latex_onhand_value - closing.latex_wip_incoming_value - closing.latex_delivered_value + closing.latex_adjustment_value
            closing.lump_closing_qty = closing.lump_onhand_qty - closing.lump_wip_incoming_qty - closing.lump_delivered_qty + closing.lump_adjustment_qty
            closing.lump_closing_value = closing.lump_onhand_value - closing.lump_wip_incoming_value - closing.lump_delivered_value + closing.lump_adjustment_value

    # PISANG
    @api.depends('varieties_type','fg2_valuation_ids.incoming_qty', 'fg2_valuation_ids.ripening_incoming_qty')
    def _compute_incoming_qty_pisang(self):
        for closing in self:
            if closing.varieties_type=='pisang':
                closing.pisang_incoming_qty = sum(closing.fg2_valuation_ids.mapped('incoming_qty'))
                # closing.pisang_ripening_qty = sum(closing.fg2_valuation_ids.mapped('ripening_qty'))
                closing.pisang_ripening_qty = sum(closing.fg2_valuation_ids.mapped('ripening_incoming_qty'))
            else:
                closing.pisang_incoming_qty = 0.0
                closing.pisang_ripening_qty = 0.0
  
    @api.depends('varieties_type','fg_melon_valuation_ids.incoming_qty')
    def _compute_incoming_qty_melon(self):
        for closing in self:
            if closing.varieties_type=='melon':
                closing.melon_incoming_qty = sum(closing.fg_melon_valuation_ids.mapped('incoming_qty'))
            else:
                closing.melon_incoming_qty = 0.0
  
    def _compute_plantation_cost_karet(self):
        closing_journal = self.env.ref('ny_closing.plantation_closing_plantation')
        self.ensure_one()
        # Get Plantation Cost
        varieties = self.env['plant.varieties'].search([('name','=','Karet')], limit=1)
        domain_plantation = [('parent_state','=','posted'),
            ('date','>=',self.date_from),('date','<=',self.date_to),
            ('plantation_varieties_id.name','=','Karet'),
            ('plantation_location_type_id.plantation','=',True),
            ('plantation_location_id','!=',False),
            ('journal_id','=',closing_journal.id),
            # ('plantation_activity_id','!=',False),
            ]
        if varieties:
            activities = self.env['lhm.activity']
            activities |= varieties.harvest_activity_ids
            activities |= varieties.upkeep_activity_ids
            # activities |= varieties.general_charges_activity_ids
            # activities |= varieties.indirect_cost_activity_ids
            plantation_cost_account_ids = []
            if activities:
                plantation_cost_account_ids = activities.cost_account_id.ids
            if plantation_cost_account_ids:
                domain_plantation.append(('account_id','in',plantation_cost_account_ids))
        plantation_cost = self.env['account.move.line'].search(domain_plantation)

        # Grouping by Loc Type, Loc, Activity, Src Journal
        plantation_cost_grouped = {}
        for aml in plantation_cost:
            key = (aml.plantation_location_type_id.id, aml.plantation_location_id.id, aml.plantation_activity_id.id, aml.plantation_src_journal_id.id, aml.account_id)
            if key not in plantation_cost_grouped.keys():
                plantation_cost_grouped.update({key: {
                        'plantation_location_type_id': aml.plantation_location_type_id.id,
                        'plantation_location_id': aml.plantation_location_id.id,
                        'plantation_activity_id': aml.plantation_activity_id.id,
                        'plantation_src_journal_id': aml.plantation_src_journal_id.id,
                        'account_id': aml.account_id.id,
                        'total_cost': 0.0,
                        'is_plantation_cost': True,
                    }
                })
            plantation_cost_grouped[key]['total_cost'] += aml.balance
        plantation_cost_amt = sum(plantation_cost.mapped('balance')) if plantation_cost else 0.0
        plantation_cost_line_ids = [(0,0,vals) for vals in plantation_cost_grouped.values()]
        # >>>>>>>>>>>>>> Plantation Cost Other Accounts
        # Find Plantation Cost based on Business Unit
        if self.plantation_other_cost_account_ids:
            domain_plantation2 = [('parent_state','=','posted'),
                ('date','>=',self.closing_process_id.date_from),('date','<=',self.closing_process_id.date_to),
                ('plantation_varieties_id.name','=','Karet'),
                # ('plantation_varieties_id','=',self.varieties_id.id),
                # ('plantation_location_type_id.plantation','=',True),
                # ('plantation_location_id','!=',False),
                ('journal_id','!=',closing_journal.id),
                ]
            if len(self.plantation_other_cost_account_ids.ids)==1:
                domain_plantation2.append(('account_id','=',self.plantation_other_cost_account_ids.id))
            else:
                domain_plantation2.append(('account_id','in',self.plantation_other_cost_account_ids.ids))
            plantation_cost2 = self.env['account.move.line'].search(domain_plantation2)
            # Grouping by Loc Type, Loc, Activity, Src Journal
            plantation_cost_grouped2 = {}
            for aml in plantation_cost2:
                key = (aml.plantation_location_type_id.id, aml.plantation_location_id.id, aml.plantation_activity_id.id, aml.plantation_src_journal_id.id, aml.account_id)
                if key not in plantation_cost_grouped2.keys():
                    plantation_cost_grouped2.update({key: {
                            'plantation_location_type_id': aml.plantation_location_type_id.id,
                            'plantation_location_id': aml.plantation_location_id.id,
                            'plantation_activity_id': aml.plantation_activity_id.id,
                            'plantation_src_journal_id': aml.plantation_src_journal_id.id,
                            'account_id': aml.account_id.id,
                            'total_cost': 0.0,
                            'is_plantation_cost': True,
                        }
                    })
                plantation_cost_grouped2[key]['total_cost'] += aml.balance
                plantation_cost_amt += aml.balance
            plantation_cost_line_ids.extend([(0,0,vals) for vals in plantation_cost_grouped2.values()])
        # return sum(plantation_cost.mapped('balance')) if plantation_cost else 0.0, [(0,0,vals) for vals in plantation_cost_grouped.values()]
        return plantation_cost_amt, plantation_cost_line_ids
    
    def _compute_plantation_cost_pisang(self):
        closing_journal = self.env.ref('ny_closing.plantation_closing_plantation')
        self.ensure_one()
        # Get Plantation Cost
        varieties = self.env['plant.varieties'].search([('name','=','Pisang')], limit=1)
        domain_plantation = [('parent_state','=','posted'),
            ('date','>=',self.date_from),('date','<=',self.date_to),
            ('plantation_varieties_id.name','=','Pisang'),
            ('plantation_location_type_id.plantation','=',True),
            ('plantation_location_id','!=',False),
            ('journal_id','=',closing_journal.id),
            # ('plantation_activity_id','!=',False),
            ]
        if varieties:
            activities = self.env['lhm.activity']
            activities |= varieties.harvest_activity_ids
            activities |= varieties.upkeep_activity_ids
            # activities |= varieties.general_charges_activity_ids
            # activities |= varieties.indirect_cost_activity_ids
            plantation_cost_account_ids = []
            if activities:
                plantation_cost_account_ids = activities.cost_account_id.ids
            if plantation_cost_account_ids:
                domain_plantation.append(('account_id','in',plantation_cost_account_ids))
        # print("::::::::::::pisang", domain_plantation)
        plantation_cost = self.env['account.move.line'].search(domain_plantation)

        # Grouping by Loc Type, Loc, Activity, Src Journal
        plantation_cost_grouped = {}
        for aml in plantation_cost:
            key = (aml.plantation_location_type_id.id, aml.plantation_location_id.id, aml.plantation_activity_id.id, aml.plantation_src_journal_id.id, aml.account_id)
            if key not in plantation_cost_grouped.keys():
                plantation_cost_grouped.update({key: {
                        'plantation_location_type_id': aml.plantation_location_type_id.id,
                        'plantation_location_id': aml.plantation_location_id.id,
                        'plantation_activity_id': aml.plantation_activity_id.id,
                        'plantation_src_journal_id': aml.plantation_src_journal_id.id,
                        'account_id': aml.account_id.id,
                        'total_cost': 0.0,
                        'is_plantation_cost': True,
                    }
                })
            plantation_cost_grouped[key]['total_cost'] += aml.balance
        plantation_cost_amt = sum(plantation_cost.mapped('balance')) if plantation_cost else 0.0
        plantation_cost_ids = [(0,0,vals) for vals in plantation_cost_grouped.values()]
        # Hitung Cost diluar Plantation Cost untuk spesific account tertentu
        if self.plantation_other_cost_account_ids:
            domain_plantation2 = [('parent_state','=','posted'),
                ('date','>=',self.date_from),('date','<=',self.date_to),
                ('plantation_varieties_id.name','=','Pisang'),
                # ('plantation_varieties_id','=',self.varieties_id.id),
                ('journal_id','!=',closing_journal.id),
                ]
            if len(self.plantation_other_cost_account_ids.ids)==1:
                domain_plantation2.append(('account_id','=',self.plantation_other_cost_account_ids.id))
            else:
                domain_plantation2.append(('account_id','in',self.plantation_other_cost_account_ids.ids))
            plantation_cost2 = self.env['account.move.line'].search(domain_plantation2)
            # Grouping by Loc Type, Loc, Activity, Src Journal
            plantation_cost_grouped2 = {}
            for aml in plantation_cost2:
                key = (aml.plantation_location_type_id.id, aml.plantation_location_id.id, aml.plantation_activity_id.id, aml.plantation_src_journal_id.id, aml.account_id)
                if key not in plantation_cost_grouped2.keys():
                    plantation_cost_grouped2.update({key: {
                            'plantation_location_type_id': aml.plantation_location_type_id.id,
                            'plantation_location_id': aml.plantation_location_id.id,
                            'plantation_activity_id': aml.plantation_activity_id.id,
                            'plantation_src_journal_id': aml.plantation_src_journal_id.id,
                            'account_id': aml.account_id.id,
                            'total_cost': 0.0,
                            'is_plantation_cost': True,
                        }
                    })
                plantation_cost_grouped2[key]['total_cost'] += aml.balance
                plantation_cost_amt += aml.balance
            plantation_cost_ids.extend([(0,0,vals) for vals in plantation_cost_grouped2.values()])
        
        return plantation_cost_amt, plantation_cost_ids
        # return sum(plantation_cost.mapped('balance')) if plantation_cost else 0.0, [(0,0,vals) for vals in plantation_cost_grouped.values()]

    def _compute_plantation_cost_melon(self):
        closing_journal = self.env.ref('ny_closing.plantation_closing_plantation')
        self.ensure_one()
        # Get Plantation Cost
        varieties = self.env['plant.varieties'].search([('name','=','Melon')], limit=1)
        domain_plantation = [('parent_state','=','posted'),
            ('date','>=',self.date_from),('date','<=',self.date_to),
            ('plantation_varieties_id.name','=','Melon'),
            ('plantation_location_type_id.plantation','=',True),
            ('plantation_location_id','!=',False),
            ('journal_id','=',closing_journal.id),
            # ('plantation_activity_id','!=',False),
            ]
        if varieties:
            activities = self.env['lhm.activity']
            activities |= varieties.harvest_activity_ids
            activities |= varieties.upkeep_activity_ids
            # activities |= varieties.general_charges_activity_ids
            # activities |= varieties.indirect_cost_activity_ids
            plantation_cost_account_ids = []
            if activities:
                plantation_cost_account_ids = activities.cost_account_id.ids
            if plantation_cost_account_ids:
                domain_plantation.append(('account_id','in',plantation_cost_account_ids))
        # print("::::::::::::melon", domain_plantation)
        plantation_cost = self.env['account.move.line'].search(domain_plantation)

        # Grouping by Loc Type, Loc, Activity, Src Journal
        plantation_cost_grouped = {}
        for aml in plantation_cost:
            key = (aml.plantation_location_type_id.id, aml.plantation_location_id.id, aml.plantation_activity_id.id, aml.plantation_src_journal_id.id, aml.account_id)
            if key not in plantation_cost_grouped.keys():
                plantation_cost_grouped.update({key: {
                        'plantation_location_type_id': aml.plantation_location_type_id.id,
                        'plantation_location_id': aml.plantation_location_id.id,
                        'plantation_activity_id': aml.plantation_activity_id.id,
                        'plantation_src_journal_id': aml.plantation_src_journal_id.id,
                        'account_id': aml.account_id.id,
                        'total_cost': 0.0,
                        'is_plantation_cost': True,
                    }
                })
            plantation_cost_grouped[key]['total_cost'] += aml.balance
        plantation_cost_amt = sum(plantation_cost.mapped('balance')) if plantation_cost else 0.0
        plantation_cost_ids = [(0,0,vals) for vals in plantation_cost_grouped.values()]
        
        # Hitung Cost diluar Plantation Cost untuk spesific account tertentu
        if self.plantation_other_cost_account_ids:
            domain_plantation2 = [('parent_state','=','posted'),
                ('date','>=',self.date_from),('date','<=',self.date_to),
                ('plantation_varieties_id.name','=','Melon'),
                ('journal_id','!=',closing_journal.id),
                ]
            if len(self.plantation_other_cost_account_ids.ids)==1:
                domain_plantation2.append(('account_id','=',self.plantation_other_cost_account_ids.id))
            else:
                domain_plantation2.append(('account_id','in',self.plantation_other_cost_account_ids.ids))
            plantation_cost2 = self.env['account.move.line'].search(domain_plantation2)
            # Grouping by Loc Type, Loc, Activity, Src Journal
            plantation_cost_grouped2 = {}
            for aml in plantation_cost2:
                key = (aml.plantation_location_type_id.id, aml.plantation_location_id.id, aml.plantation_activity_id.id, aml.plantation_src_journal_id.id, aml.account_id)
                if key not in plantation_cost_grouped2.keys():
                    plantation_cost_grouped2.update({key: {
                            'plantation_location_type_id': aml.plantation_location_type_id.id,
                            'plantation_location_id': aml.plantation_location_id.id,
                            'plantation_activity_id': aml.plantation_activity_id.id,
                            'plantation_src_journal_id': aml.plantation_src_journal_id.id,
                            'account_id': aml.account_id.id,
                            'total_cost': 0.0,
                            'is_plantation_cost': True,
                        }
                    })
                plantation_cost_grouped2[key]['total_cost'] += aml.balance
                plantation_cost_amt += aml.balance
            plantation_cost_ids.extend([(0,0,vals) for vals in plantation_cost_grouped2.values()])
        
        return plantation_cost_amt, plantation_cost_ids

    def _compute_manufacturing_cost(self):
        closing_journal = self.env.ref('ny_closing.plantation_closing_plantation')
        self.ensure_one()
        # Get Manufacturing Cost
        manufacturing_cost = self.env['account.move.line'].search([('parent_state','=','posted'),
            ('date','>=',self.date_from),('date','<=',self.date_to),
            ('plantation_varieties_id.name','=','Karet'),
            # ('plantation_location_type_id.mill','=',True),
            # ('plantation_location_id','!=',False),
            # ('plantation_activity_id','!=',False),
            ('account_id','in',self.manufacturing_cost_account_ids.ids),
            ('journal_id','!=',closing_journal.id)
            ])
        # Grouping by Loc Type, Loc, Activity, Src Journal
        plantation_cost_grouped = {}
        for aml in manufacturing_cost:
            key = (aml.plantation_location_type_id.id, aml.plantation_location_id.id, aml.plantation_activity_id.id, aml.plantation_src_journal_id.id, aml.account_id)
            if key not in plantation_cost_grouped.keys():
                plantation_cost_grouped.update({key: {
                        'plantation_location_type_id': aml.plantation_location_type_id.id,
                        'plantation_location_id': aml.plantation_location_id.id,
                        'plantation_activity_id': aml.plantation_activity_id.id,
                        'plantation_src_journal_id': aml.plantation_src_journal_id.id,
                        'account_id': aml.account_id.id,
                        'total_cost': 0.0,
                        'is_manufacturing_cost': True,
                    }
                })
            plantation_cost_grouped[key]['total_cost'] += aml.balance
        return sum(manufacturing_cost.mapped('balance')) if manufacturing_cost else 0.0, [(0,0,vals) for vals in plantation_cost_grouped.values()]

    def _compute_mrp_sheet_cost(self):
        self.ensure_one()
        # Get Manufacturing Cost
        manufacturing_cost = self.env['account.move.line'].search([('parent_state','=','posted'),
            ('date','>=',self.date_from),('date','<=',self.date_to),
            # ('plantation_location_type_id.mill','=',True),
            # ('plantation_location_id','!=',False),
            # ('plantation_activity_id','!=',False),
            ('account_id','in',self.mrp_sheet_cost_account_ids.ids),
            # ('journal_id','!=',closing_journal.id)
            ])
        # Grouping by Loc Type, Loc, Activity, Src Journal
        plantation_cost_grouped = {}
        for aml in manufacturing_cost:
            key = (aml.plantation_location_type_id.id, aml.plantation_location_id.id, aml.plantation_activity_id.id, aml.plantation_src_journal_id.id, aml.account_id)
            if key not in plantation_cost_grouped.keys():
                plantation_cost_grouped.update({key: {
                        'plantation_location_type_id': aml.plantation_location_type_id.id,
                        'plantation_location_id': aml.plantation_location_id.id,
                        'plantation_activity_id': aml.plantation_activity_id.id,
                        'plantation_src_journal_id': aml.plantation_src_journal_id.id,
                        'account_id': aml.account_id.id,
                        'total_cost': 0.0,
                        'is_manufacturing_cost': True,
                        'is_mrp_sheet_cost': True,
                    }
                })
            plantation_cost_grouped[key]['total_cost'] += aml.balance
        return sum(manufacturing_cost.mapped('balance')) if manufacturing_cost else 0.0, [(0,0,vals) for vals in plantation_cost_grouped.values()]
    
    def _compute_mrp_compound_cost(self):
        self.ensure_one()
        # Get Manufacturing Cost
        manufacturing_cost = self.env['account.move.line'].search([('parent_state','=','posted'),
            ('date','>=',self.date_from),('date','<=',self.date_to),
            # ('plantation_location_type_id.mill','=',True),
            # ('plantation_location_id','!=',False),
            # ('plantation_activity_id','!=',False),
            ('account_id','in',self.mrp_compound_cost_account_ids.ids),
            # ('journal_id','!=',closing_journal.id)
            ])
        # Grouping by Loc Type, Loc, Activity, Src Journal
        plantation_cost_grouped = {}
        for aml in manufacturing_cost:
            key = (aml.plantation_location_type_id.id, aml.plantation_location_id.id, aml.plantation_activity_id.id, aml.plantation_src_journal_id.id, aml.account_id)
            if key not in plantation_cost_grouped.keys():
                plantation_cost_grouped.update({key: {
                        'plantation_location_type_id': aml.plantation_location_type_id.id,
                        'plantation_location_id': aml.plantation_location_id.id,
                        'plantation_activity_id': aml.plantation_activity_id.id,
                        'plantation_src_journal_id': aml.plantation_src_journal_id.id,
                        'account_id': aml.account_id.id,
                        'total_cost': 0.0,
                        'is_manufacturing_cost': True,
                        'is_mrp_compound_cost': True,
                    }
                })
            plantation_cost_grouped[key]['total_cost'] += aml.balance
        return sum(manufacturing_cost.mapped('balance')) if manufacturing_cost else 0.0, [(0,0,vals) for vals in plantation_cost_grouped.values()]

    def _compute_manufacturing_cost_pisang(self):
        self.ensure_one()
        # Get Manufacturing Cost
        manufacturing_cost = self.env['account.move.line'].search([('parent_state','=','posted'),
            ('date','>=',self.date_from),('date','<=',self.date_to),
            # ('plantation_location_type_id.mill','=',True),
            # ('plantation_location_id','!=',False),
            # ('plantation_activity_id','!=',False),
            ('account_id','in',self.manufacturing_cost_account_ids.ids),
            # ('journal_id','!=',closing_journal.id)
            ])
        # Grouping by Loc Type, Loc, Activity, Src Journal
        plantation_cost_grouped = {}
        for aml in manufacturing_cost:
            key = (aml.plantation_location_type_id.id, aml.plantation_location_id.id, aml.plantation_activity_id.id, aml.plantation_src_journal_id.id, aml.account_id)
            if key not in plantation_cost_grouped.keys():
                plantation_cost_grouped.update({key: {
                        'plantation_location_type_id': aml.plantation_location_type_id.id,
                        'plantation_location_id': aml.plantation_location_id.id,
                        'plantation_activity_id': aml.plantation_activity_id.id,
                        'plantation_src_journal_id': aml.plantation_src_journal_id.id,
                        'account_id': aml.account_id.id,
                        'total_cost': 0.0,
                        'is_manufacturing_cost': True,
                    }
                })
            plantation_cost_grouped[key]['total_cost'] += aml.balance
        return sum(manufacturing_cost.mapped('balance')) if manufacturing_cost else 0.0, [(0,0,vals) for vals in plantation_cost_grouped.values()]

    def _get_mrp_inprogress_prev_month(self, product):
        self.ensure_one()
        inprogress_qty = 0.0
        mrp = self.env['mrp.production'].search([('product_id','=',product.id),('state','=',['progress','done']),
                ('date_start','<', self.date_from.strftime('%Y-%m-%d 00:00:00')),
                '|',
                    ('date_finished','=', False),
                    ('date_finished','>=', self.date_from.strftime('%Y-%m-%d 00:00:00'))])
        return inprogress_qty

    def _get_mrp_done_this_month(self, product):
        self.ensure_one()
        # Old Version
        # mrp = self.env['mrp.production'].search([('product_id','=',product.id),('state','=','done'),
        #         ('date_finished','>=', self.date_from.strftime('%Y-%m-%d 00:00:00')),
        #         ('date_finished','<=', self.date_to.strftime('%Y-%m-%d 23:59:59'))])
        finished_mo = self.env['mrp.production'].search([
                ('source_mo_id.product_id','=',product.id),('state','=','done'),
                ('date_finished','>=', self.date_from.strftime('%Y-%m-%d 00:00:00')),
                ('date_finished','<=', self.date_to.strftime('%Y-%m-%d 23:59:59'))])
        source_mo = finished_mo.mapped('source_mo_id')
        return source_mo

    def _get_mrp_inprogress_this_month(self, product):
        self.ensure_one()
        mrp = self.env['mrp.production'].search([('product_id','=',product.id),
                ('state','in',['progress','done']),
                '|',
                    '&',    
                        ('date_start','>=', self.date_from.strftime('%Y-%m-%d 00:00:00')),
                        ('date_start','<=', self.date_to.strftime('%Y-%m-%d 23:59:59')),
                    '&',    
                        ('date_finished','>=', self.date_from.strftime('%Y-%m-%d 00:00:00')),
                        ('date_finished','<=', self.date_to.strftime('%Y-%m-%d 23:59:59'))])
        return mrp

    def _compute_rm_cost_sheet(self):
        self.ensure_one()
        mrp = self._get_mrp_done_this_month(self.sheet_product_id)
        rm_moves = mrp.move_raw_ids.filtered(lambda s: s.product_id.name not in ('Lateks','Lump'))
        rm_cost = 0.0
        if rm_moves:
            # print(">>>>>>>>>>>>>>", rm_moves)
            if len(rm_moves.ids)>1:
                svl_search = self.env['stock.valuation.layer'].search([('stock_move_id','in',rm_moves.ids)])
            else:
                svl_search = self.env['stock.valuation.layer'].search([('stock_move_id','=',rm_moves.id)])
            # print(">>>>>>>>>>>>>>", svl_search)
            if svl_search:
                rm_cost = -1* sum(svl_search.mapped('value'))
        return rm_cost

    def action_compute_plant_cost(self):
        for closing in self:
            if closing.closing_process_id and closing.parent_state!='closing_production':
                raise ValidationError(f"Tidak dapat mengubah data Closing Plantation yang karena Closing Procedure sudah berstatus {closing.parent_state}")
            if closing.plantation_cost_ids:
                closing.plantation_cost_ids.unlink()
            plantation_cost, summerize_cost = closing._compute_plantation_cost_karet()
            closing.plantation_cost = plantation_cost
            closing.plantation_cost_ids = summerize_cost
    
    def action_compute_sheet_rm_cost(self):
        misc_journal = self.env.ref('ny_closing.plantation_closing_production')
        for closing in self:
            if closing.closing_process_id and closing.parent_state!='closing_production':
                raise ValidationError(f"Tidak dapat mengubah data Closing Plantation yang karena Closing Procedure sudah berstatus {closing.parent_state}")
            purchases_in = self.env['account.move.line'].search([
                        ('account_id','=',closing.sheet_rm_purchase_account_id.id),
                        ('parent_state','=','posted'),('date','>=',closing.date_from),
                        ('date','<=',closing.date_to),('journal_id','!=',misc_journal.id),
                        ('debit','>',0)])
            purchases_out = self.env['account.move.line'].search([
                        ('account_id','=',closing.sheet_rm_purchase_account_id.id),
                        ('parent_state','=','posted'),('date','>=',closing.date_from),
                        ('date','<=',closing.date_to),('journal_id','!=',misc_journal.id),
                        ('credit','>',0)])
            # closing.sheet_rm_incoming_qty = (sum(purchases_in.mapped('quantity')) if purchases_in else 0.0) - (sum(purchases_out.mapped('quantity')) if purchases_out else 0.0)
            closing.sheet_rm_incoming_value = (sum(purchases_in.mapped('balance')) if purchases_in else 0.0) + (sum(purchases_out.mapped('balance')) if purchases_out else 0.0)

    def action_compute_mrp_cost(self):
        for closing in self:
            if closing.closing_process_id and closing.parent_state!='closing_production':
                raise ValidationError(f"Tidak dapat mengubah data Closing Plantation yang karena Closing Procedure sudah berstatus {closing.parent_state}")
            if closing.mrp_cost_ids:
                closing.mrp_cost_ids.unlink()
            if closing.varieties_type=='pisang':
                mrp_cost, summerize_mrp_cost = closing._compute_manufacturing_cost_pisang()
                closing.pisang_ripening_cost = mrp_cost
            else:
                mrp_cost, summerize_mrp_cost = closing._compute_manufacturing_cost()
                sheet_cost, summerize_mrp_cost1 = closing._compute_mrp_sheet_cost()
                compound_cost, summerize_mrp_cost2 = closing._compute_mrp_compound_cost()
                if summerize_mrp_cost1:
                    summerize_mrp_cost.extend(summerize_mrp_cost1)
                if summerize_mrp_cost2:
                    summerize_mrp_cost.extend(summerize_mrp_cost2)
                closing.manufacturing_cost = mrp_cost
                closing.mrp_sheet_cost = sheet_cost
                closing.mrp_compound_cost = compound_cost
            closing.mrp_cost_ids = summerize_mrp_cost
    
    def action_compute_rm_cost_sheet(self):
        for closing in self:
            # closing.sheet_raw_material_cost = closing._compute_rm_cost_sheet()
            pass

    def compute_initial_and_cost_rm_karet(self):
        for closing in self:
            if closing.closing_process_id and closing.parent_state!='closing_production':
                raise ValidationError(f"Tidak dapat mengubah data Closing Plantation yang karena Closing Procedure sudah berstatus {closing.parent_state}")
            sheet_product = self.env['product.product'].search([('name','=','Sheet')], limit=1)
            closing.sheet_product_id = sheet_product.id
            compound_product = self.env['product.product'].search([('name','=','Compo')], limit=1)
            compound_product2 = self.env['product.product'].search([('name','=','WIP Compo')], limit=1)
            closing.compound_product_id = compound_product.id
            
            # Get Plantation Cost
            plantation_cost, summerize_cost = closing._compute_plantation_cost_karet()
            if closing.plantation_cost_ids:
                closing.plantation_cost_ids.unlink()
            closing.plantation_cost = plantation_cost
            closing.plantation_cost_ids = summerize_cost
            
            # Get Manufacturing Cost
            mrp_cost, summerize_mrp_cost = closing._compute_manufacturing_cost()
            mrp_sheet_cost, summerize_mrp_cost1 = closing._compute_mrp_sheet_cost()
            mrp_compound_cost, summerize_mrp_cost2 = closing._compute_mrp_compound_cost()
            if summerize_mrp_cost1:
                summerize_mrp_cost.extend(summerize_mrp_cost1)
            if summerize_mrp_cost2:
                summerize_mrp_cost.extend(summerize_mrp_cost2)
            closing.manufacturing_cost = mrp_cost
            closing.mrp_sheet_cost = mrp_sheet_cost
            closing.mrp_compound_cost = mrp_compound_cost
            if closing.mrp_cost_ids:
                closing.mrp_cost_ids.unlink()
            closing.manufacturing_cost = mrp_cost
            closing.mrp_cost_ids = summerize_mrp_cost
            
            # IN : Get Lateks and Lump Receiving Qty from NAP
            # TODO: Seharusnya ambil dari stock move saja bukan dari timbangan pabrik
            product_latex = self.env['product.product'].search([('name','=','Lateks')], limit=1)
            closing.latex_product_id = product_latex.id
            latex_in = self.env['timbangan.pabrik'].search([('product_id','=',product_latex.id),
                            ('lhm_nap_id.date_nap','>=',closing.date_from),
                            ('lhm_nap_id.date_nap','<=',closing.date_to),
                            ('lhm_nap_id.state','in',['confirmed','done'])])
            closing.latex_incoming_qty = sum(latex_in.mapped('qty_received')) if latex_in else 0.0
            
            product_lump = self.env['product.product'].search([('name','=','Lump')], limit=1)
            closing.lump_product_id = product_lump.id
            compound_in = self.env['timbangan.pabrik'].search([('product_id','=',product_lump.id),
                            ('lhm_nap_id.date_nap','>=',closing.date_from),
                            ('lhm_nap_id.date_nap','<=',closing.date_to),
                            ('lhm_nap_id.state','in',['confirmed','done'])])
            closing.lump_incoming_qty = sum(compound_in.mapped('qty_received')) if compound_in else 0.0
            
            # WIP : GET Beginning WIP
            # GET Work Inprogress Saldo awal WIP atau MO PREV MONTH
            closing.latex_wip_opening_qty = self.prev_closing_id.closing_wip_latex_qty
            closing.lump_wip_opening_qty = self.prev_closing_id.closing_wip_lump_qty
            # mrp_sheet_prev = closing._get_mrp_inprogress_prev_month(sheet_product)
            # if mrp_sheet_prev:
            #     rm_moves = mrp_sheet_prev.move_raw_ids.filtered(lambda s: s.product_id.id==product_latex.id)
            #     closing.latex_wip_opening_qty = sum(rm_moves.mapped('product_qty')) if rm_moves else 0.0
            # mrp_compound_prev = closing._get_mrp_inprogress_prev_month(compound_product)
            # if mrp_compound_prev:
            #     rm_moves = mrp_compound_prev.move_raw_ids.filtered(lambda s: s.product_id.id==product_lump.id)
            #     closing.lump_wip_opening_qty = sum(rm_moves.mapped('product_qty')) if rm_moves else 0.0
            
            # WIP : GET NEW MO THIS MONTH
            mrp_sheet = closing._get_mrp_inprogress_this_month(sheet_product)
            if mrp_sheet:
                rm_moves = mrp_sheet.move_raw_ids.filtered(lambda s: s.product_id.id==product_latex.id)
                closing.latex_wip_incoming_qty = sum(rm_moves.mapped('product_qty')) if rm_moves else 0.0
            mrp_compound = closing._get_mrp_inprogress_this_month(compound_product2)
            if mrp_compound:
                rm_moves = mrp_compound.move_raw_ids.filtered(lambda s: s.product_id.id==product_lump.id)
                closing.lump_wip_incoming_qty = sum(rm_moves.mapped('product_qty')) if rm_moves else 0.0
            
            # WIP : GET MO DONE THIS MONTH
            mrp_sheet_done = closing._get_mrp_done_this_month(sheet_product)
            if mrp_sheet_done:
                rm_moves = mrp_sheet_done.move_raw_ids.filtered(lambda s: s.product_id.id==product_latex.id)
                closing.latex_wip_outgoing_qty = sum(rm_moves.mapped('quantity_done')) if rm_moves else 0.0
            mrp_compound_done = closing._get_mrp_done_this_month(compound_product2)
            if mrp_compound_done:
                rm_moves = mrp_compound_done.move_raw_ids.filtered(lambda s: s.product_id.id==product_lump.id)
                closing.lump_wip_outgoing_qty = sum(rm_moves.mapped('quantity_done')) if rm_moves else 0.0
            
            # WIP : Asam semut hanya untuk SHEET
            # WIP : Get Receiving Asam Semut
            receving_asam_semuts = self.env['stock.move.line'].search([
                        ('product_id.name','=','Asam Semut'),('state','=','done'),
                        ('location_id.usage','not in',('internal','inventory')),
                        ('location_dest_id.usage','=','internal'),
                        ('date','>=',closing.date_from.strftime('%Y-%m-%d 00:00:00')),
                        ('date','<=',closing.date_to.strftime('%Y-%m-%d 23:59:59'))])
            
            # WIP : Get Purchase Amount Asam Semut
            # TODO : harusnya value purchase diambil dari stock valuation layer bukan dari account move line
            closing.sheet_rm_incoming_qty = sum(receving_asam_semuts.mapped('qty_done')) if receving_asam_semuts else 0.0
            closing.action_compute_sheet_rm_cost()
            
            # WIP : Get Consumed Asam Semut
            out_asam_semut = self.env['mrp.manual.consume'].search([('product_id.name','=','Asam Semut'),
                                    ('date','>=',closing.date_from),('date','<=',closing.date_to),
                                    ('is_confirmed','=',True)])
            closing.sheet_rm_outgoing_qty = sum(out_asam_semut.mapped('consumed_qty')) if out_asam_semut else 0.0

            # WIP : Get Adjustment Asam Semut
            asam_semut_adjustment_out_moves = self.env['stock.move.line'].search([('product_id.name','=','Asam Semut'),
                                    ('move_id.picking_id','=',False),('state','=','done'),
                                    ('location_id.usage','=','internal'),
                                    ('location_dest_id.usage','=','inventory'),
                                    ('date','>=',closing.date_from.strftime('%Y-%m-%d 00:00:00')),
                                    ('date','<=',closing.date_to.strftime('%Y-%m-%d 23:59:59'))])
            asam_semut_adjustment_in_moves = self.env['stock.move.line'].search([('product_id.name','=','Asam Semut'),
                                    ('move_id.picking_id','=',False),('state','=','done'),
                                    ('location_dest_id.usage','=','internal'),
                                    ('location_id.usage','=','inventory'),
                                    ('date','>=',closing.date_from.strftime('%Y-%m-%d 00:00:00')),
                                    ('date','<=',closing.date_to.strftime('%Y-%m-%d 23:59:59'))])
            closing.sheet_rm_adjustment_qty = (sum(asam_semut_adjustment_in_moves.mapped('qty_done')) if asam_semut_adjustment_in_moves else 0.0) - (sum(asam_semut_adjustment_out_moves.mapped('qty_done')) if asam_semut_adjustment_out_moves else 0.0)

            # OUT : Get Sales
            latex_delivery_moves = self.env['stock.move.line'].search([('product_id','=',product_latex.id),
                                    ('location_id.usage','=','internal'),('location_dest_id.usage','=','customer'),
                                    ('state','=','done'),('date','>=',closing.date_from.strftime('%Y-%m-%d 00:00:00')),
                                    ('date','<=',closing.date_to.strftime('%Y-%m-%d 23:59:59'))])
            closing.latex_delivered_qty = sum(latex_delivery_moves.mapped('qty_done')) if latex_delivery_moves else 0.0
            lump_delivery_moves = self.env['stock.move.line'].search([('product_id.name','=','Lump'),
                                    ('location_id.usage','=','internal'),('location_dest_id.usage','=','customer'),
                                    ('state','=','done'),('date','>=',closing.date_from.strftime('%Y-%m-%d 00:00:00')),
                                    ('date','<=',closing.date_to.strftime('%Y-%m-%d 23:59:59'))])
            closing.lump_delivered_qty = sum(lump_delivery_moves.mapped('qty_done')) if lump_delivery_moves else 0.0

            # ADJ : Get Adjustment
            latex_adjustment_out_moves = self.env['stock.move.line'].search([('product_id','=',product_latex.id),
                                    ('location_id.usage','=','internal'),('location_dest_id.usage','=','inventory'),
                                    ('state','=','done'),('date','>=',closing.date_from.strftime('%Y-%m-%d 00:00:00')),
                                    ('date','<=',closing.date_to.strftime('%Y-%m-%d 23:59:59'))])
            latex_adjustment_in_moves = self.env['stock.move.line'].search([('product_id','=',product_latex.id),
                                    ('location_dest_id.usage','=','internal'),('location_id.usage','=','inventory'),
                                    ('state','=','done'),('date','>=',closing.date_from.strftime('%Y-%m-%d 00:00:00')),
                                    ('date','<=',closing.date_to.strftime('%Y-%m-%d 23:59:59'))])
            closing.latex_adjustment_qty = (sum(latex_adjustment_in_moves.mapped('qty_done')) if latex_adjustment_in_moves else 0.0) - (sum(latex_adjustment_out_moves.mapped('qty_done')) if latex_adjustment_out_moves else 0.0)
            lump_adjustment_out_moves = self.env['stock.move.line'].search([('product_id.name','=','Lump'),
                                    ('location_id.usage','=','internal'),('location_dest_id.usage','=','inventory'),
                                    ('state','=','done'),('date','>=',closing.date_from.strftime('%Y-%m-%d 00:00:00')),
                                    ('date','<=',closing.date_to.strftime('%Y-%m-%d 23:59:59'))])
            lump_adjustment_in_moves = self.env['stock.move.line'].search([('product_id.name','=','Lump'),
                                    ('location_dest_id.usage','=','internal'),('location_id.usage','=','inventory'),
                                    ('state','=','done'),('date','>=',closing.date_from.strftime('%Y-%m-%d 00:00:00')),
                                    ('date','<=',closing.date_to.strftime('%Y-%m-%d 23:59:59'))])
            closing.lump_adjustment_qty = (sum(lump_adjustment_in_moves.mapped('qty_done')) if lump_adjustment_in_moves else 0.0) - (sum(lump_adjustment_out_moves.mapped('qty_done')) if lump_adjustment_out_moves else 0.0)
        return True
    
    def compute_initial_and_cost_rm_pisang(self):
        for closing in self:
            if closing.closing_process_id and closing.parent_state!='closing_production':
                raise ValidationError(f"Tidak dapat mengubah data Closing Plantation yang karena Closing Procedure sudah berstatus {closing.parent_state}")
            plantation_cost, summerize_cost = closing._compute_plantation_cost_pisang()
            if closing.plantation_cost_ids:
                closing.plantation_cost_ids.unlink()
            closing.plantation_cost = plantation_cost
            closing.plantation_cost_ids = summerize_cost
            
            mrp_cost, summerize_mrp_cost = closing._compute_manufacturing_cost_pisang()
            if closing.mrp_cost_ids:
                closing.mrp_cost_ids.unlink()
            # print(">>>>>>>>>>>>>>>>>>>>mrp_cost", mrp_cost)
            # print(">>>>>>>>>>>>>>>>>>>>", summerize_mrp_cost)
            closing.pisang_ripening_cost = mrp_cost
            closing.mrp_cost_ids = summerize_mrp_cost
            
            # Get Pisang Receiving Qty from NAP
            to_create = []
            total_produced = 0.0
            varietas_pisang = self.env['plant.varieties'].search([('name','=','Pisang')])
            closing.pisang_varieties_id = varietas_pisang.id
            closing.fg2_valuation_ids.unlink()
            for product in varietas_pisang.other_product_ids:
                # Find Previous Valuation
                prev_closing_fg = False
                if closing.prev_closing_id:
                    for line in closing.prev_closing_id.fg2_valuation_ids:
                        if line.product_id.id==product.id:
                            prev_closing_fg = line
                
                pisang_in = self.env['timbangan.pabrik'].search([('product_id','=',product.id),
                                ('lhm_nap_id.date_nap','>=',closing.date_from),
                                ('lhm_nap_id.date_nap','<=',closing.date_to),
                                ('lhm_nap_id.state','in',['confirmed','done'])])
                incoming_qty = sum(pisang_in.mapped('qty_received')) if pisang_in else 0.0
                total_produced += incoming_qty

                ripening_location = self.env.ref('ny_plantation.loc_ripening_loc_1')
                # Find Delivery/Sales
                delivery_moves_out = self.env['stock.move.line'].search([('product_id','=',product.id),
                                ('state','=','done'),
                                ('location_id.usage','=','internal'),
                                ('location_id','!=',ripening_location.id),
                                ('location_dest_id.usage','=','customer'),
                                ('date','>=',closing.date_from.strftime('%Y-%m-%d 00:00:00')),
                                ('date','<=',closing.date_to.strftime('%Y-%m-%d 23:59:59'))
                                ])
                delivery_moves_return = self.env['stock.move.line'].search([('product_id','=',product.id),
                                ('state','=','done'),
                                ('location_dest_id.usage','=','internal'),
                                ('location_dest_id','!=',ripening_location.id),
                                ('location_id.usage','=','customer'),
                                ('date','>=',closing.date_from.strftime('%Y-%m-%d 00:00:00')),
                                ('date','<=',closing.date_to.strftime('%Y-%m-%d 23:59:59'))
                                ])
                outgoing_qty = (sum(delivery_moves_out.mapped('qty_done')) if delivery_moves_out else 0.0) - (sum(delivery_moves_return.mapped('qty_done')) if delivery_moves_return else 0.0)
                
                # Find Scrap
                scrap_moves_out = self.env['stock.move.line'].search([('product_id','=',product.id),('state','=','done'),
                                ('location_id.usage','=','internal'),('location_id','!=',ripening_location.id),
                                ('location_dest_id.scrap_location','=',True),
                                ('date','>=',closing.date_from.strftime('%Y-%m-%d 00:00:00')),
                                ('date','<=',closing.date_to.strftime('%Y-%m-%d 23:59:59'))
                                ])
                scrap_moves_return = self.env['stock.move.line'].search([('product_id','=',product.id),('state','=','done'),
                                ('location_id.scrap_location','=',True),
                                ('location_dest_id.usage','=','internal'),('location_dest_id','!=',ripening_location.id),
                                ('date','>=',closing.date_from.strftime('%Y-%m-%d 00:00:00')),
                                ('date','<=',closing.date_to.strftime('%Y-%m-%d 23:59:59'))
                                ])
                scrap_qty = (sum(scrap_moves_out.mapped('qty_done')) if scrap_moves_out else 0.0) - (sum(scrap_moves_return.mapped('qty_done')) if scrap_moves_return else 0.0)

                # Search Ripening Qty Receive from Internal Transfer
                ripening_int_move_in = self.env['stock.move.line'].search([('product_id','=',product.id),('state','=','done'),
                                ('location_id.usage','=','internal'),
                                ('location_id','!=',ripening_location.id),
                                ('location_dest_id.usage','=','internal'),
                                ('location_dest_id','=',ripening_location.id),
                                ('date','>=',closing.date_from.strftime('%Y-%m-%d 00:00:00')),
                                ('date','<=',closing.date_to.strftime('%Y-%m-%d 23:59:59'))
                                ])
                ripening_int_move_out = self.env['stock.move.line'].search([('product_id','=',product.id),('state','=','done'),
                                ('location_id.usage','=','internal'),
                                ('location_id','=',ripening_location.id),
                                ('location_dest_id.usage','=','internal'),
                                ('location_dest_id','!=',ripening_location.id),
                                ('date','>=',closing.date_from.strftime('%Y-%m-%d 00:00:00')),
                                ('date','<=',closing.date_to.strftime('%Y-%m-%d 23:59:59'))
                                ])
                ripening_qty = (sum(ripening_int_move_in.mapped('qty_done')) if ripening_int_move_in else 0.0) - (sum(ripening_int_move_out.mapped('qty_done')) if ripening_int_move_out else 0.0)

                # Search Delivery from Ripening Location
                out_moves_ripening_loc = self.env['stock.move.line'].search([('product_id','=',product.id),
                                ('state','=','done'),
                                ('location_id.usage','=','internal'),
                                ('location_id','=',ripening_location.id),
                                ('location_dest_id.usage','=','customer'),
                                ('date','>=',closing.date_from.strftime('%Y-%m-%d 00:00:00')),
                                ('date','<=',closing.date_to.strftime('%Y-%m-%d 23:59:59'))
                                ])
                return_moves_ripening_loc = self.env['stock.move.line'].search([('product_id','=',product.id),('state','=','done'),
                                ('location_id.usage','=','customer'),
                                ('location_dest_id.usage','=','internal'),
                                ('location_dest_id','=',ripening_location.id),
                                ('date','>=',closing.date_from.strftime('%Y-%m-%d 00:00:00')),
                                ('date','<=',closing.date_to.strftime('%Y-%m-%d 23:59:59'))
                                ])
                ripening_outgoing_qty = (sum(out_moves_ripening_loc.mapped('qty_done')) if out_moves_ripening_loc else 0.0) - (sum(return_moves_ripening_loc.mapped('qty_done')) if return_moves_ripening_loc else 0.0)

                # Get Adjustment
                adjustment_out_moves = self.env['stock.move.line'].search([
                    ('product_id', '=', product.id),
                    ('location_id.usage', '=', 'internal'),
                    ('location_dest_id.usage', '=', 'inventory'),
                    ('move_id.scrap_ids', '=', False), 
                    ('move_id.picking_id', '=', False),
                    ('state', '=', 'done'),
                    ('date', '>=', closing.date_from.strftime('%Y-%m-%d 00:00:00')),
                    ('date', '<=', closing.date_to.strftime('%Y-%m-%d 23:59:59'))
                ])

                adjustment_in_moves = self.env['stock.move.line'].search([
                    ('product_id', '=', product.id),
                    ('location_dest_id.usage', '=', 'internal'),
                    ('location_id.usage', '=', 'inventory'),
                    ('move_id.scrap_ids', '=', False),
                    ('move_id.picking_id', '=', False),
                    ('state', '=', 'done'),
                    ('date', '>=', closing.date_from.strftime('%Y-%m-%d 00:00:00')),
                    ('date', '<=', closing.date_to.strftime('%Y-%m-%d 23:59:59'))
                ])

                adjustment_qty = (sum(adjustment_in_moves.mapped('qty_done')) if adjustment_in_moves else 0.0) - (sum(adjustment_out_moves.mapped('qty_done')) if adjustment_out_moves else 0.0)

                # for move in adjustment_in_moves:
                #     print(f"==== Adjusment In Move {move.reference} - {move.qty_done}")

                # for move in adjustment_out_moves:
                #     print(f"==== Adjusment Out Move {move.reference} - {move.qty_done}")

                # print(f"==== Adjusment product {product.name} = {adjustment_qty}")
                # Find Material Request Issue
                issued_moves_out = self.env['stock.move.line'].search([('product_id','=',product.id),
                                ('state','=','done'),
                                ('location_id.usage','=','internal'),
                                ('move_id.mr_line_id','!=',False),
                                ('location_dest_id.usage','=','inventory'),
                                ('date','>=',closing.date_from.strftime('%Y-%m-%d 00:00:00')),
                                ('date','<=',closing.date_to.strftime('%Y-%m-%d 23:59:59'))
                                ])
                issued_moves_return = self.env['stock.move.line'].search([('product_id','=',product.id),
                                ('state','=','done'),
                                ('location_dest_id.usage','=','internal'),
                                ('location_id.usage','=','inventory'),
                                ('move_id.mr_line_id','!=',False),
                                ('date','>=',closing.date_from.strftime('%Y-%m-%d 00:00:00')),
                                ('date','<=',closing.date_to.strftime('%Y-%m-%d 23:59:59'))
                                ])
                outgoing_issue_stock_move_ids = [(6, 0, issued_moves_out.move_id.ids + issued_moves_return.move_id.ids)]
                outgoing_issue_qty = (sum(issued_moves_out.mapped('qty_done')) if issued_moves_out else 0.0) - (sum(issued_moves_return.mapped('qty_done')) if issued_moves_return else 0.0)

                values_to_create = {
                    'product_id': product.id,
                    'prev_closing_fg_id': prev_closing_fg.id if prev_closing_fg else False,
                    'opening_qty': prev_closing_fg.closing_qty if prev_closing_fg else 0.0,
                    'opening_value': prev_closing_fg.closing_value if prev_closing_fg else 0.0,
                    'ripening_opening_qty': prev_closing_fg.ripening_closing_qty if prev_closing_fg else 0.0,
                    'ripening_opening_value': prev_closing_fg.ripening_closing_value if prev_closing_fg else 0.0,
                    'incoming_qty': incoming_qty,
                    'scrap_qty': scrap_qty,
                    'ripening_qty': ripening_qty if product.id in closing.pisang_with_grade_ids.ids else 0.0,
                    'outgoing_qty': outgoing_qty,
                    'outgoing_issue_qty': outgoing_issue_qty,
                    'outgoing_issue_stock_move_ids': outgoing_issue_stock_move_ids,
                    'ripening_outgoing_qty': ripening_outgoing_qty if product.id in closing.pisang_with_grade_ids.ids else 0.0,
                    'adjustment_qty': adjustment_qty,
                }
                if prev_closing_fg:
                    values_to_create.update({
                        'inventory_account_id': prev_closing_fg.inventory_account_id.id if prev_closing_fg.inventory_account_id else False,
                        'cogs_account_id': prev_closing_fg.cogs_account_id.id if prev_closing_fg.cogs_account_id else False,
                        'scrap_account_id': prev_closing_fg.scrap_account_id.id if prev_closing_fg.scrap_account_id else False,
                        'adjustment_account_id': prev_closing_fg.adjustment_account_id.id if prev_closing_fg.adjustment_account_id else False,
                        'inventory_ripening_account_id': prev_closing_fg.inventory_ripening_account_id.id if prev_closing_fg.inventory_ripening_account_id else False,
                    })
                to_create.append(values_to_create)
            
            # for exvals in to_create:
            #     exvals['plantation_cost'] = (exvals['incoming_qty'] / total_produced if total_produced else 0.0) * closing.plantation_cost
            # Other Plantation Product
            if to_create:
                closing.fg2_valuation_ids = list(map(lambda x: (0,0,x), to_create))
        return True
    
    def compute_initial_and_cost_rm_melon(self):
        for closing in self:
            if closing.closing_process_id and closing.parent_state!='closing_production':
                raise ValidationError(f"Tidak dapat mengubah data Closing Plantation yang karena Closing Procedure sudah berstatus {closing.parent_state}")
            plantation_cost, summerize_cost = closing._compute_plantation_cost_melon()
            if closing.plantation_cost_ids:
                closing.plantation_cost_ids.unlink()
            closing.plantation_cost = plantation_cost
            closing.plantation_cost_ids = summerize_cost
            
            # mrp_cost, summerize_mrp_cost = closing._compute_manufacturing_cost_melon()
            # if closing.mrp_cost_ids:
            #     closing.mrp_cost_ids.unlink()
            # print(">>>>>>>>>>>>>>>>>>>>mrp_cost", mrp_cost)
            # print(">>>>>>>>>>>>>>>>>>>>", summerize_mrp_cost)
            # closing.melon_ripening_cost = mrp_cost
            # closing.mrp_cost_ids = summerize_mrp_cost
            
            # Get Pisang Receiving Qty from NAP
            to_create = []
            total_produced = total_onhand = 0.0
            varietas_melon = self.env['plant.varieties'].search([('name','=','Melon')])
            closing.melon_varieties_id = varietas_melon.id
            closing.fg2_valuation_ids.unlink()
            for product in varietas_melon.other_product_ids:
                # Find Previous Valuation
                prev_closing_fg = False
                if closing.prev_closing_id:
                    for line in closing.prev_closing_id.fg2_valuation_ids:
                        if line.product_id.id==product.id:
                            prev_closing_fg = line
                
                melon_in = self.env['timbangan.pabrik'].search([('product_id','=',product.id),
                                ('lhm_nap_id.date_nap','>=',closing.date_from),
                                ('lhm_nap_id.date_nap','<=',closing.date_to),
                                ('lhm_nap_id.state','in',['confirmed','done'])])
                incoming_qty = sum(melon_in.mapped('qty_received')) if melon_in else 0.0
                total_produced += incoming_qty

                # ripening_location = self.env.ref('ny_plantation.loc_ripening_loc_1')
                # Find Delivery/Sales
                delivery_moves_out = self.env['stock.move.line'].search([('product_id','=',product.id),
                                ('state','=','done'),
                                ('location_id.usage','=','internal'),
                                # ('location_id','!=',ripening_location.id),
                                ('location_dest_id.usage','=','customer'),
                                ('date','>=',closing.date_from.strftime('%Y-%m-%d 00:00:00')),
                                ('date','<=',closing.date_to.strftime('%Y-%m-%d 23:59:59'))
                                ])
                delivery_moves_return = self.env['stock.move.line'].search([('product_id','=',product.id),
                                ('state','=','done'),
                                ('location_dest_id.usage','=','internal'),
                                # ('location_dest_id','!=',ripening_location.id),
                                ('location_id.usage','=','customer'),
                                ('date','>=',closing.date_from.strftime('%Y-%m-%d 00:00:00')),
                                ('date','<=',closing.date_to.strftime('%Y-%m-%d 23:59:59'))
                                ])
                outgoing_qty = (sum(delivery_moves_out.mapped('qty_done')) if delivery_moves_out else 0.0) - (sum(delivery_moves_return.mapped('qty_done')) if delivery_moves_return else 0.0)
                
                # Find Material Request Issue
                issued_moves_out = self.env['stock.move.line'].search([('product_id','=',product.id),
                                ('state','=','done'),
                                ('location_id.usage','=','internal'),
                                ('move_id.mr_line_id','!=',False),
                                ('location_dest_id.usage','=','inventory'),
                                ('date','>=',closing.date_from.strftime('%Y-%m-%d 00:00:00')),
                                ('date','<=',closing.date_to.strftime('%Y-%m-%d 23:59:59'))
                                ])
                issued_moves_return = self.env['stock.move.line'].search([('product_id','=',product.id),
                                ('state','=','done'),
                                ('location_dest_id.usage','=','internal'),
                                ('location_id.usage','=','inventory'),
                                ('move_id.mr_line_id','!=',False),
                                ('date','>=',closing.date_from.strftime('%Y-%m-%d 00:00:00')),
                                ('date','<=',closing.date_to.strftime('%Y-%m-%d 23:59:59'))
                                ])
                outgoing_issue_stock_move_ids = [(6, 0, issued_moves_out.move_id.ids + issued_moves_return.move_id.ids)]
                outgoing_issue_qty = (sum(issued_moves_out.mapped('qty_done')) if issued_moves_out else 0.0) - (sum(issued_moves_return.mapped('qty_done')) if issued_moves_return else 0.0)

                # Find Scrap
                scrap_moves_out = self.env['stock.move.line'].search([('product_id','=',product.id),('state','=','done'),
                                ('location_id.usage','=','internal'),
                                # ('location_id','!=',ripening_location.id),
                                ('location_dest_id.scrap_location','=',True),
                                ('date','>=',closing.date_from.strftime('%Y-%m-%d 00:00:00')),
                                ('date','<=',closing.date_to.strftime('%Y-%m-%d 23:59:59'))
                                ])
                scrap_moves_return = self.env['stock.move.line'].search([('product_id','=',product.id),('state','=','done'),
                                ('location_id.scrap_location','=',True),
                                ('location_dest_id.usage','=','internal'),
                                # ('location_dest_id','!=',ripening_location.id),
                                ('date','>=',closing.date_from.strftime('%Y-%m-%d 00:00:00')),
                                ('date','<=',closing.date_to.strftime('%Y-%m-%d 23:59:59'))
                                ])
                scrap_qty = (sum(scrap_moves_out.mapped('qty_done')) if scrap_moves_out else 0.0) - (sum(scrap_moves_return.mapped('qty_done')) if scrap_moves_return else 0.0)

                values_to_create = {
                    'product_id': product.id,
                    'prev_closing_fg_id': prev_closing_fg.id if prev_closing_fg else False,
                    'opening_qty': prev_closing_fg.closing_qty if prev_closing_fg else 0.0,
                    'opening_value': prev_closing_fg.closing_value if prev_closing_fg else 0.0,
                    # 'ripening_opening_qty': prev_closing_fg.ripening_closing_qty if prev_closing_fg else 0.0,
                    # 'ripening_opening_value': prev_closing_fg.ripening_closing_value if prev_closing_fg else 0.0,
                    'incoming_qty': incoming_qty,
                    'onhand_qty': (prev_closing_fg.closing_qty if prev_closing_fg else 0.0) + incoming_qty,
                    'scrap_qty': scrap_qty,
                    # 'ripening_qty': ripening_qty if product.id in closing.pisang_with_grade_ids.ids else 0.0,
                    'outgoing_qty': outgoing_qty,
                    'outgoing_issue_qty': outgoing_issue_qty,
                    'outgoing_issue_stock_move_ids': outgoing_issue_stock_move_ids,
                    # 'ripening_outgoing_qty': ripening_outgoing_qty if product.id in closing.pisang_with_grade_ids.ids else 0.0,
                }
                total_onhand += values_to_create['onhand_qty']
                if prev_closing_fg:
                    values_to_create.update({
                        'inventory_account_id': prev_closing_fg.inventory_account_id.id if prev_closing_fg.inventory_account_id else False,
                        'cogs_account_id': prev_closing_fg.cogs_account_id.id if prev_closing_fg.cogs_account_id else False,
                        'scrap_account_id': prev_closing_fg.scrap_account_id.id if prev_closing_fg.scrap_account_id else False,
                        'adjustment_account_id': prev_closing_fg.adjustment_account_id.id if prev_closing_fg.adjustment_account_id else False,
                        # 'inventory_ripening_account_id': prev_closing_fg.inventory_ripening_account_id.id if prev_closing_fg.inventory_ripening_account_id else False,
                    })
                to_create.append(values_to_create)
            
            # for exvals in to_create:
            #     # exvals['plantation_cost'] = (exvals['incoming_qty'] / total_produced if total_produced else 0.0) * closing.plantation_cost
            #     exvals['plantation_cost'] = (exvals['onhand_qty'] / total_onhand if total_onhand else 0.0) * closing.plantation_cost
                
            # Other Plantation Product
            if to_create:
                print(">>>>>>>>>>>>>>", to_create)
                closing.fg2_valuation_ids = list(map(lambda x: (0,0,x), to_create))
        return True
    
    ############################### END VALUATION RAW MATERIAL ###################################

    def compute_initial_and_cost_fg2(self):
        for closing in self:
            if closing.closing_process_id and closing.parent_state!='closing_production':
                raise ValidationError(f"Tidak dapat mengubah data Closing Plantation yang karena Closing Procedure sudah berstatus {closing.parent_state}")
            closing.fg2_valuation_ids.unlink()

            # Manufactured Product : RSS 1, RSS 3, Cutting
            mrp_products = self.env['product.product'].search([('name','in',('RSS I', 'RSS III', 'Cutting'))])
            total_produced = 0.0
            to_create = []
            for product in mrp_products:
                # Find Previous Valuation
                prev_closing_fg = False
                if closing.prev_closing_id:
                    for line in closing.prev_closing_id.fg2_valuation_ids:
                        if line.product_id.id==product.id:
                            prev_closing_fg = line
                # Find Manufacture
                production_moves = self.env['stock.move'].search([('product_id','=',product.id),('state','=','done'),
                                ('location_id.usage','=','production'),('location_dest_id.usage','=','internal'),
                                ('date','>=',closing.date_from.strftime('%Y-%m-%d 00:00:00')),
                                ('date','<=',closing.date_to.strftime('%Y-%m-%d 23:59:59'))
                                ])
                produced_qty = sum(production_moves.mapped('product_uom_qty')) if production_moves else 0.0
                total_produced += produced_qty
                # Find Delivery/Sales
                outgoing_moves = self.env['stock.move'].search([('product_id','=',product.id),('state','=','done'),
                                ('location_id.usage','=','internal'),('location_dest_id.usage','=','customer'),
                                ('date','>=',closing.date_from.strftime('%Y-%m-%d 00:00:00')),
                                ('date','<=',closing.date_to.strftime('%Y-%m-%d 23:59:59'))
                                ])
                outgoing_moves_ret = self.env['stock.move'].search([('product_id','=',product.id),('state','=','done'),
                                ('location_id.usage','=','customer'),('location_dest_id.usage','=','internal'),
                                ('date','>=',closing.date_from.strftime('%Y-%m-%d 00:00:00')),
                                ('date','<=',closing.date_to.strftime('%Y-%m-%d 23:59:59'))
                                ])
                outgoing_qty = sum(outgoing_moves.mapped('product_uom_qty')) if outgoing_moves else 0.0
                outgoing_qty -= sum(outgoing_moves_ret.mapped('product_uom_qty')) if outgoing_moves_ret else 0.0

                # Find Adjustment
                # Punya pak hendra
                # adjustment_out_moves = self.env['stock.move'].search([('product_id','=',product.id),('state','=','done'),
                #                 ('location_id.usage','=','internal'),('location_dest_id.usage','=','inventory'),
                #                 ('date','>=',closing.date_from.strftime('%Y-%m-%d 00:00:00')),
                #                 ('date','<=',closing.date_to.strftime('%Y-%m-%d 23:59:59'))
                #                 ])
                # adjustment_in_moves = self.env['stock.move'].search([('product_id','=',product.id),('state','=','done'),
                #                 ('location_id.usage','=','inventory'),('location_dest_id.usage','=','internal'),
                #                 ('date','>=',closing.date_from.strftime('%Y-%m-%d 00:00:00')),
                #                 ('date','<=',closing.date_to.strftime('%Y-%m-%d 23:59:59'))
                #                 ])
                # adjustment_qty = sum(adjustment_out_moves.mapped('product_uom_qty')) if adjustment_out_moves else 0.0
                # adjustment_qty -= sum(adjustment_in_moves.mapped('product_uom_qty')) if adjustment_in_moves else 0.0

                adjustment_out_moves = self.env['stock.move'].search([
                    ('product_id', '=', product.id),
                    ('state', '=', 'done'),
                    ('scrap_ids', '=', False),
                    ('picking_id', '=', False),
                    ('location_id.usage', '=', 'internal'),
                    ('location_dest_id.usage', '=', 'inventory'),
                    ('date', '>=', closing.date_from.strftime('%Y-%m-%d 00:00:00')),
                    ('date', '<=', closing.date_to.strftime('%Y-%m-%d 23:59:59')),
                ])

                adjustment_in_moves = self.env['stock.move'].search([
                    ('product_id', '=', product.id),
                    ('state', '=', 'done'),
                    ('scrap_ids', '=', False),
                    ('picking_id', '=', False),
                    ('location_id.usage', '=', 'inventory'),
                    ('location_dest_id.usage', '=', 'internal'),
                    ('date', '>=', closing.date_from.strftime('%Y-%m-%d 00:00:00')),
                    ('date', '<=', closing.date_to.strftime('%Y-%m-%d 23:59:59')),
                ])

                # Hitung qty adjustment (in - out)
                adjustment_qty = (
                    sum(adjustment_in_moves.mapped('product_uom_qty')) if adjustment_in_moves else 0.0
                ) - (
                    sum(adjustment_out_moves.mapped('product_uom_qty')) if adjustment_out_moves else 0.0
                )


                values_to_create = {
                    'product_id': product.id,
                    'prev_closing_fg_id': prev_closing_fg.id if prev_closing_fg else False,
                    'opening_qty': prev_closing_fg.closing_qty if prev_closing_fg else 0.0,
                    'opening_value': prev_closing_fg.closing_value if prev_closing_fg else 0.0,
                    'incoming_qty': produced_qty,
                    'manufacturing_cost': 0.0,
                    'outgoing_qty': outgoing_qty,
                    'adjustment_qty': adjustment_qty,
                }
                if prev_closing_fg:
                    values_to_create.update({
                        'inventory_account_id': prev_closing_fg.inventory_account_id.id if prev_closing_fg.inventory_account_id else False,
                        'cogs_account_id': prev_closing_fg.cogs_account_id.id if prev_closing_fg.cogs_account_id else False,
                        'scrap_account_id': prev_closing_fg.scrap_account_id.id if prev_closing_fg.scrap_account_id else False,
                        'adjustment_account_id': prev_closing_fg.adjustment_account_id.id if prev_closing_fg.adjustment_account_id else False,
                    })
                to_create.append(values_to_create)
            # Fill in manufacturing Cost proporsionally
            for exvals in to_create:
                exvals['manufacturing_cost'] = (exvals['incoming_qty'] / total_produced if total_produced else 0.0) * closing.latex_wip_outgoing_value

            # Finish Good : Compo
            # mrp_compound_done = closing._get_mrp_done_this_month(closing.compound_product_id)
            compound_product2 = self.env['product.product'].search([('name','=','WIP Compo')], limit=1)
            mrp_compound_done = closing._get_mrp_done_this_month(compound_product2)
            finished_compo_qty = 0.0
            if mrp_compound_done:
                # rm_moves = mrp_compound_done.move_raw_ids.filtered(lambda s: s.product_id.id==product_lump.id)
                # finished_compo_qty = sum(rm_moves.mapped('product_qty')) if rm_moves else 0.0
                finished_compo_qty = sum(mrp_compound_done.mapped('qty_produced')) if mrp_compound_done else 0.0
                
            prev_closing_fg_compo = False
            if closing.prev_closing_id:
                for line in closing.prev_closing_id.fg2_valuation_ids:
                    if line.product_id.id==closing.compound_product_id.id:
                        prev_closing_fg_compo = line
            # Find Delivery/Sales
            outgoing_moves22_1 = self.env['stock.move'].search([('product_id','=',closing.compound_product_id.id),('state','=','done'),
                            ('location_id.usage','=','internal'),('location_dest_id.usage','=','customer'),
                            ('date','>=',closing.date_from.strftime('%Y-%m-%d 00:00:00')),
                            ('date','<=',closing.date_to.strftime('%Y-%m-%d 23:59:59'))
                            ])
            outgoing_moves22_2 = self.env['stock.move'].search([('product_id','=',closing.compound_product_id.id),('state','=','done'),
                            ('location_id.usage','=','customer'),('location_dest_id.usage','=','internal'),
                            ('date','>=',closing.date_from.strftime('%Y-%m-%d 00:00:00')),
                            ('date','<=',closing.date_to.strftime('%Y-%m-%d 23:59:59'))
                            ])
            outgoing_qty22 = sum(outgoing_moves22_1.mapped('product_uom_qty')) if outgoing_moves22_1 else 0.0
            outgoing_qty22 -= sum(outgoing_moves22_2.mapped('product_uom_qty')) if outgoing_moves22_2 else 0.0
            values_to_create_compo = {
                'product_id': closing.compound_product_id.id,
                'prev_closing_fg_id': prev_closing_fg_compo.id if prev_closing_fg_compo else False,
                'opening_qty': prev_closing_fg_compo.closing_qty if prev_closing_fg_compo else 0.0,
                'opening_value': prev_closing_fg_compo.closing_value if prev_closing_fg_compo else 0.0,
                'incoming_qty': finished_compo_qty,
                'manufacturing_cost': closing.lump_wip_outgoing_value,
                'outgoing_qty': outgoing_qty22,
            }
            if prev_closing_fg_compo:
                values_to_create_compo.update({
                    'inventory_account_id': prev_closing_fg_compo.inventory_account_id.id if prev_closing_fg_compo.inventory_account_id else False,
                    'cogs_account_id': prev_closing_fg_compo.cogs_account_id.id if prev_closing_fg_compo.cogs_account_id else False,
                })
            to_create.append((values_to_create_compo))

            # Other Plantation Product
            if to_create:
                closing.fg2_valuation_ids = list(map(lambda x: (0,0,x), to_create))
        return True
    
    ############################### END VALUATION FINISH GOOD 2 ###################################
    
    ###############################################################################################

    def button_start(self):
        for closing in self:
            #####
            if closing.varieties_type=='karet':
                # Linked to Last Opening Balance
                prev_closing = self.search([('state','=','done'),('date_to','<',closing.date_from),('varieties_type','=','karet')], order='date_from desc', limit=1)
                if prev_closing:
                    closing.prev_closing_id = prev_closing.id
                closing.compute_initial_and_cost_rm_karet()
            elif closing.varieties_type=='pisang':
                # Linked to Last Opening Balance
                prev_closing = self.search([('state','=','done'),('date_to','<',closing.date_from),('varieties_type','=','pisang')], order='date_from desc', limit=1)
                if prev_closing:
                    closing.prev_closing_id = prev_closing.id
                    closing.plantation_other_cost_account_ids = [(6,0,prev_closing.plantation_other_cost_account_ids.ids)] if prev_closing.plantation_other_cost_account_ids else False
                    closing.manufacturing_cost_account_ids = [(6,0,prev_closing.manufacturing_cost_account_ids.ids)] if prev_closing.manufacturing_cost_account_ids else False
                closing.compute_initial_and_cost_rm_pisang()
            closing.write({'state': 'rm_valuation'})
        return True
    
    def button_continue_to_fg(self):
        for closing in self:
            if closing.varieties_type=='karet':
                closing.compute_initial_and_cost_fg2()
                closing.write({'state': 'fg_valuation'})
            else:
                closing.write({'state': 'account_entry'})
        return True

    def button_continue_to_account_entry(self):
        for closing in self:
            closing.write({'state': 'account_entry'})
        return True

    def create_move_entries_rm_karet(self):
        # Output untuk Lateks dan Lump
        # 1. Journal Receiving (Plantation Cost > Inventory) 
        # 2. Journal Addition WIP (Inventory > WIP Lateks/Lump) 
        # 3. Journal Finished Sheet (WIP Lateks > WIP Sheet ) 
        self.ensure_one()
        
        misc_journal = self.env.ref('ny_closing.plantation_closing_production')
        varieties = self.env['plant.varieties'].search([('name','=','Karet')], limit=1)
        
        move_lines_receiving = []
        move_lines_wip = []
        move_lines_outgoing = []
        # BEGIN: Receiving from NAP
        if self.latex_incoming_qty or self.latex_plantation_cost:
            vals_dest = {
                'name': 'Inventory Receipt and Valuation Latex',
                'plantation_varieties_id': varieties.id,
                'plantation_location_type_id': False,
                'plantation_location_id': False,
                'plantation_activity_id': False,
                'plantation_src_journal_id': False,
                'account_id': self.latex_inventory_account_id.id,
                'debit': round(self.latex_plantation_cost if self.latex_plantation_cost>0 else 0.0, 2),
                'credit': round(abs(self.latex_plantation_cost) if self.latex_plantation_cost<0 else 0.0, 2),
            }
            move_lines_receiving.append((0,0,vals_dest))
            
            for ll in self.plantation_cost_ids:
                vals_src = {
                    'name': 'Move Cost to Inventory Lateks',
                    'plantation_varieties_id': varieties.id,
                    'plantation_location_type_id': ll.plantation_location_type_id.id,
                    'plantation_location_id': ll.plantation_location_id.id,
                    'plantation_activity_id': ll.plantation_activity_id.id,
                    'plantation_src_journal_id': ll.plantation_src_journal_id.id,
                    'account_id': ll.account_id.id,
                    'debit': round(abs(ll.total_cost_latex) if ll.total_cost_latex<0 else 0.0, 2),
                    'credit': round(ll.total_cost_latex if ll.total_cost_latex>0 else 0, 2),
                }
                move_lines_receiving.append((0,0,vals_src))
        
        if self.lump_incoming_qty or self.lump_plantation_cost:
            vals_dest = {
                'name': 'Inventory Receipt and Valuation Lump',
                'plantation_location_type_id': False,
                'plantation_varieties_id': varieties.id,
                'plantation_location_id': False,
                'plantation_activity_id': False,
                'plantation_src_journal_id': False,
                'account_id': self.lump_inventory_account_id.id,
                'debit': round(self.lump_plantation_cost if self.lump_plantation_cost>0 else 0.0, 2),
                'credit': round(abs(self.lump_plantation_cost) if self.lump_plantation_cost<0 else 0.0, 2),
            }
            move_lines_receiving.append((0,0,vals_dest))
            for ll in self.plantation_cost_ids:
                vals_src = {
                    'name': 'Move Cost to Inventory Lump',
                    'plantation_varieties_id': varieties.id,
                    'plantation_location_type_id': ll.plantation_location_type_id.id,
                    'plantation_location_id': ll.plantation_location_id.id,
                    'plantation_activity_id': ll.plantation_activity_id.id,
                    'plantation_src_journal_id': ll.plantation_src_journal_id.id,
                    'account_id': ll.account_id.id,
                    'debit': round(abs(ll.total_cost_lump) if ll.total_cost_lump<0 else 0.0, 2),
                    'credit': round(ll.total_cost_lump if ll.total_cost_lump>0 else 0.0, 2),
                }
                move_lines_receiving.append((0,0,vals_src))
        # END: Receiving from NAP
        
        # BEGIN: Inventory Lateks/Lump to WIP  
        if self.latex_wip_incoming_qty or self.latex_wip_incoming_value:
            vals_wip_in = {
                'name': 'Work in Process Lateks',
                'plantation_location_type_id': False,
                'plantation_varieties_id': varieties.id,
                'plantation_location_id': False,
                'plantation_activity_id': False,
                'plantation_src_journal_id': False,
                'account_id': self.latex_wip_account_id.id,
                'product_id': self.latex_product_id.id,
                'debit': round(self.latex_wip_incoming_value if self.latex_wip_incoming_value>0 else 0.0, 2),
                'credit': round(abs(self.latex_wip_incoming_value) if self.latex_wip_incoming_value<0 else 0.0, 2),
            }
            vals_wip_in_src = vals_wip_in.copy()
            vals_wip_in_src.update({
                'account_id': self.latex_inventory_account_id.id,
                'debit': vals_wip_in['credit'],
                'credit': vals_wip_in['debit']
            })
            move_lines_wip.extend([(0,0,vals_wip_in),(0,0,vals_wip_in_src)])
        
        if self.lump_wip_incoming_qty or self.lump_wip_incoming_value:
            vals_wip_in = {
                'name': 'Work in Process Lump',
                'plantation_location_type_id': False,
                'plantation_varieties_id': varieties.id,
                'plantation_location_id': False,
                'plantation_activity_id': False,
                'plantation_src_journal_id': False,
                'account_id': self.lump_wip_account_id.id,
                'product_id': self.lump_product_id.id,
                'debit': round(self.lump_wip_incoming_value if self.lump_wip_incoming_value>0 else 0.0, 2),
                'credit': round(abs(self.lump_wip_incoming_value) if self.lump_wip_incoming_value<0 else 0.0, 2),
            }
            move_lines_wip.append((0,0,vals_wip_in))
            vals_wip_in_src = vals_wip_in.copy()
            vals_wip_in_src.update({
                'account_id': self.lump_inventory_account_id.id,
                'debit': vals_wip_in['credit'],
                'credit': vals_wip_in['debit']
            })
            move_lines_wip.append((0,0,vals_wip_in_src))
        # END: Inventory Lateks/Lum to WIP            
        
        # BEGIN: FOH to WIP Lateks/Lump  
        if self.sheet_production_cost:
            vals_mrp = {
                'name': 'Manufacturing Cost to WIP Lateks',
                'plantation_location_type_id': False,
                'plantation_varieties_id': varieties.id,
                'plantation_location_id': False,
                'plantation_activity_id': False,
                'plantation_src_journal_id': False,
                'account_id': self.latex_wip_account_id.id,
                'product_id': self.latex_product_id.id,
                'debit': round(self.sheet_production_cost if self.sheet_production_cost>0 else 0.0, 2),
                'credit': round(abs(self.sheet_production_cost) if self.sheet_production_cost<0 else 0.0, 2),
            }
            move_lines_wip.append((0,0,vals_mrp))
            for ll in self.mrp_cost_ids:
                vals_wip_src = {
                    'name': 'Move Cost to WIP Lateks',
                    'plantation_varieties_id': varieties.id,
                    # 'plantation_location_type_id': ll.plantation_location_type_id.id,
                    # 'plantation_location_id': ll.plantation_location_id.id,
                    # 'plantation_activity_id': ll.plantation_activity_id.id,
                    # 'plantation_src_journal_id': ll.plantation_src_journal_id.id,
                    'account_id': ll.account_id.id,
                    'debit': round(abs(ll.total_cost_latex) if ll.total_cost_latex<0 else 0.0, 2),
                    'credit': round(ll.total_cost_latex if ll.total_cost_latex>0 else 0.0, 2),
                }
                move_lines_wip.append((0,0,vals_wip_src))
        
        if self.compound_production_cost:
            vals_mrp = {
                'name': 'Manufacturing Cost to WIP Lump',
                'plantation_location_type_id': False,
                'plantation_varieties_id': varieties.id,
                'plantation_location_id': False,
                'plantation_activity_id': False,
                'plantation_src_journal_id': False,
                'account_id': self.lump_wip_account_id.id,
                'product_id': self.lump_product_id.id,
                'debit': round(self.compound_production_cost if self.compound_production_cost>0 else 0.0, 2),
                'credit': round(abs(self.compound_production_cost) if self.compound_production_cost<0 else 0.0, 2),
            }
            move_lines_wip.append((0,0,vals_mrp))
            for ll in self.mrp_cost_ids:
                vals_wip_src = {
                    'name': 'Move Cost to WIP Lump',
                    'plantation_varieties_id': varieties.id,
                    # 'plantation_location_type_id': ll.plantation_location_type_id.id,
                    # 'plantation_location_id': ll.plantation_location_id.id,
                    # 'plantation_activity_id': ll.plantation_activity_id.id,
                    # 'plantation_src_journal_id': ll.plantation_src_journal_id.id,
                    'account_id': ll.account_id.id,
                    'debit': round(abs(ll.total_cost_lump) if ll.total_cost_lump<0 else 0.0, 2),
                    'credit': round(ll.total_cost_lump if ll.total_cost_lump>0 else 0.0, 2),
                }
                move_lines_wip.append((0,0,vals_wip_src))
        # END: FOH to WIP Lateks/Lump
        
        # BEGIN: WIP Lateks to WIP Sheet
        if self.latex_wip_outgoing_qty or self.latex_wip_outgoing_value:
            vals_mrp2 = {
                'name': 'WIP Lateks to WIP Sheet',
                'plantation_location_type_id': False,
                'plantation_varieties_id': varieties.id,
                'plantation_location_id': False,
                'plantation_activity_id': False,
                'plantation_src_journal_id': False,
                'account_id': self.sheet_wip_account_id.id,
                'product_id': self.sheet_product_id.id,
                'debit': round(self.latex_wip_outgoing_value if self.latex_wip_outgoing_value>0 else 0.0, 2),
                'credit': round(abs(self.latex_wip_outgoing_value) if self.latex_wip_outgoing_value<0 else 0.0, 2),
            }
            move_lines_wip.append((0,0,vals_mrp2))
            vals_mrp_src2 = vals_mrp2.copy()
            vals_mrp_src2.update({
                'product_id': self.latex_product_id.id,
                'account_id': self.latex_wip_account_id.id,
                'debit': round(abs(self.latex_wip_outgoing_value) if self.latex_wip_outgoing_value<0.0 else 0.0, 2),
                'credit': round(self.latex_wip_outgoing_value if self.latex_wip_outgoing_value>0.0 else 0.0, 2),
            })
            move_lines_wip.append((0,0,vals_mrp_src2))
        # END: WIP Lateks to WIP Sheet

        # BEGIN: WIP Lump to WIP Compound
        if self.lump_wip_outgoing_qty or self.lump_wip_outgoing_value:
            vals_mrp4 = {
                'name': 'WIP Lump to WIP Compo',
                'plantation_location_type_id': False,
                'plantation_varieties_id': varieties.id,
                'plantation_location_id': False,
                'plantation_activity_id': False,
                'plantation_src_journal_id': False,
                'account_id': self.compound_wip_account_id.id,
                'product_id': self.compound_product_id.id,
                'debit': round(self.lump_wip_outgoing_value if self.lump_wip_outgoing_value>0 else 0.0, 2),
                'credit': round(abs(self.lump_wip_outgoing_value) if self.lump_wip_outgoing_value<0 else 0.0, 2),
            }
            move_lines_wip.append((0,0,vals_mrp4))
            vals_mrp_src4 = vals_mrp4.copy()
            vals_mrp_src4.update({
                'product_id': self.lump_product_id.id,
                'account_id': self.lump_wip_account_id.id,
                'debit': vals_mrp4['credit'],
                'credit': vals_mrp4['debit']
            })
            move_lines_wip.append((0,0,vals_mrp_src4))
        # END: WIP Lump to WIP Compound

        # BEGIN: Sales Latex & Lump
        if self.latex_delivered_qty or self.latex_delivered_value:
            vals_src9 = {
                'name': 'Harga Pokok Penjualan Latex',
                'plantation_location_type_id': False,
                'plantation_varieties_id': varieties.id,
                'plantation_location_id': False,
                'plantation_activity_id': False,
                'plantation_src_journal_id': False,
                'product_id': self.latex_product_id.id,
                'account_id': self.latex_inventory_account_id.id,
                'debit': round(abs(self.latex_delivered_value) if self.latex_delivered_value<0 else 0.0, 2),
                'credit': round(abs(self.latex_delivered_value) if self.latex_delivered_value>0 else 0.0, 2),
            }
            move_lines_outgoing.append((0,0,vals_src9))
            vals_cogs9 = vals_src9.copy()
            vals_cogs9.update({
                'account_id': self.latex_cogs_account_id.id,
                'debit': vals_src9['credit'],
                'credit': vals_src9['debit'],
            })
            move_lines_outgoing.append((0,0,vals_cogs9))
            
        if self.lump_delivered_qty or self.lump_delivered_value:
            vals_src10 = {
                'name': 'Harga Pokok Penjualan Lump',
                'plantation_location_type_id': False,
                'plantation_varieties_id': varieties.id,
                'plantation_location_id': False,
                'plantation_activity_id': False,
                'plantation_src_journal_id': False,
                'product_id': self.lump_product_id.id,
                'account_id': self.lump_inventory_account_id.id,
                'debit': round(abs(self.lump_delivered_value) if self.lump_delivered_value<0 else 0.0, 2),
                'credit': round(abs(self.lump_delivered_value) if self.lump_delivered_value>0 else 0.0, 2),
            }
            move_lines_outgoing.append((0,0,vals_src10))
            vals_cogs10 = vals_src10.copy()
            vals_cogs10.update({
                'account_id': self.lump_cogs_account_id.id,
                'debit': vals_src10['credit'],
                'credit': vals_src10['debit'],
            })
            move_lines_outgoing.append((0,0,vals_cogs10))
        # END: Sales Latex & Lump

        # BEGIN: Adjustment Latex & Lump
        if self.latex_adjustment_qty or self.latex_adjustment_value:
            vals_src11 = {
                'name': 'Penyesuaian Stok Lateks',
                'plantation_location_type_id': False,
                'plantation_varieties_id': varieties.id,
                'plantation_location_id': False,
                'plantation_activity_id': False,
                'plantation_src_journal_id': False,
                'product_id': self.latex_product_id.id,
                'account_id': self.latex_inventory_account_id.id,
                'debit': round(self.latex_adjustment_value if self.latex_adjustment_value>0 else 0.0, 2),
                'credit': round(abs(self.latex_adjustment_value) if self.latex_adjustment_value<0 else 0.0, 2),
            }
            move_lines_outgoing.append((0,0,vals_src11))
            vals_adjs_11 = vals_src11.copy()
            vals_adjs_11.update({
                'account_id': self.latex_adjustment_account_id.id,
                'debit': vals_src11['credit'],
                'credit': vals_src11['debit'],
            })
            move_lines_outgoing.append((0,0,vals_adjs_11))
            
        if self.lump_adjustment_qty or self.lump_adjustment_value:
            vals_src12 = {
                'name': 'Penyesuaian Stok Lump',
                'plantation_location_type_id': False,
                'plantation_varieties_id': varieties.id,
                'plantation_location_id': False,
                'plantation_activity_id': False,
                'plantation_src_journal_id': False,
                'product_id': self.lump_product_id.id,
                'account_id': self.lump_inventory_account_id.id,
                'debit': round(self.lump_adjustment_value if self.lump_adjustment_value>0 else 0.0, 2),
                'credit': round(abs(self.lump_adjustment_value) if self.lump_adjustment_value<0 else 0.0, 2),
            }
            move_lines_outgoing.append((0,0,vals_src12))
            vals_adjs_12 = vals_src12.copy()
            vals_adjs_12.update({
                'account_id': self.lump_adjustment_account_id.id,
                'debit': vals_src12['credit'],
                'credit': vals_src12['debit'],
            })
            move_lines_outgoing.append((0,0,vals_adjs_12))
        # END: Sales Adjustment & Lump

        # BEGIN: Purchase Asam Semut
        if self.sheet_rm_incoming_qty or self.sheet_rm_incoming_value:
            vals_dest31 = {
                'name': 'Pembelian Asam Semut pada Inventory',
                'plantation_varieties_id': varieties.id,
                'product_id': False,
                'account_id': self.sheet_rm_inventory_account_id.id,
                'debit': round(self.sheet_rm_incoming_value if self.sheet_rm_incoming_value>0 else 0.0, 2),
                'credit': round(abs(self.sheet_rm_incoming_value) if self.sheet_rm_incoming_value<0 else 0.0, 2),
            }
            move_lines_receiving.append((0,0,vals_dest31))
            vals_src_31 = vals_dest31.copy()
            vals_src_31.update({
                'account_id': self.sheet_rm_purchase_account_id.id,
                'debit': vals_dest31['credit'],
                'credit': vals_dest31['debit'],
            })
            move_lines_receiving.append((0,0,vals_src_31))
        # END: Purchase Asam Semut

        # BEGIN: Outgoing Asam Semut
        if self.sheet_rm_outgoing_qty or self.sheet_rm_outgoing_value:
            # Persediaan Biaya Asam Semut ke Asam Semut
            vals_dest32 = {
                'name': 'Konsumsi Asam Semut',
                'plantation_varieties_id': varieties.id,
                'product_id': False,
                'account_id': self.sheet_rm_consumption_account_id.id,
                'debit': round(self.sheet_rm_outgoing_value if self.sheet_rm_outgoing_value>0 else 0.0, 2),
                'credit': round(abs(self.sheet_rm_outgoing_value) if self.sheet_rm_outgoing_value<0 else 0.0, 2),
            }
            move_lines_outgoing.append((0,0,vals_dest32))
            vals_src_32 = vals_dest32.copy()
            vals_src_32.update({
                'account_id': self.sheet_rm_inventory_account_id.id,
                'debit': vals_dest32['credit'],
                'credit': vals_dest32['debit'],
            })
            move_lines_outgoing.append((0,0,vals_src_32))
            
            # Asam Semut ke WIP Lates
            vals_dest32 = {
                'name': 'Cost Asam Semut to WIP Lates',
                'plantation_varieties_id': varieties.id,
                'product_id': False,
                'account_id': self.latex_wip_account_id.id,
                'debit': round(self.sheet_rm_outgoing_value if self.sheet_rm_outgoing_value>0 else 0.0, 2),
                'credit': round(abs(self.sheet_rm_outgoing_value) if self.sheet_rm_outgoing_value<0 else 0.0, 2),
            }
            move_lines_wip.append((0,0,vals_dest32))
            vals_src_33 = vals_dest32.copy()
            vals_src_33.update({
                'account_id': self.sheet_rm_consumption_account_id.id,
                'debit': vals_dest32['credit'],
                'credit': vals_dest32['debit'],
            })
            move_lines_wip.append((0,0,vals_src_33))
        # END: Outgoing Asam Semut
        
        # BEGIN: Adjustment Asam Semut
        if self.sheet_rm_opening_adjustment_value_enable and self.sheet_rm_opening_adjustment_diff:
            vals_dest32 = {
                'name': 'Adjustment Selisih Nilai Asam Semut',
                'plantation_varieties_id': varieties.id,
                'product_id': False,
                'account_id': self.sheet_rm_inventory_account_id.id,
                'debit': round(self.sheet_rm_opening_adjustment_diff if self.sheet_rm_opening_adjustment_diff>0 else 0.0, 2),
                'credit': round(abs(self.sheet_rm_opening_adjustment_diff) if self.sheet_rm_opening_adjustment_diff<0 else 0.0, 2),
            }
            move_lines_outgoing.append((0,0,vals_dest32))
            vals_src_32 = vals_dest32.copy()
            vals_src_32.update({
                'account_id': self.sheet_rm_adjustment_account_id.id,
                'debit': vals_dest32['credit'],
                'credit': vals_dest32['debit'],
            })
            move_lines_outgoing.append((0,0,vals_src_32))
        
        if self.sheet_rm_closing_adjustment_value_enable and self.sheet_rm_closing_adjustment_diff:
            vals_dest32 = {
                'name': 'Adjustment Selisih Nilai Asam Semut',
                'plantation_varieties_id': varieties.id,
                'product_id': False,
                'account_id': self.sheet_rm_inventory_account_id.id,
                'debit': round(self.sheet_rm_closing_adjustment_diff if self.sheet_rm_closing_adjustment_diff>0 else 0.0, 2),
                'credit': round(abs(self.sheet_rm_closing_adjustment_diff) if self.sheet_rm_closing_adjustment_diff<0 else 0.0, 2),
            }
            move_lines_outgoing.append((0,0,vals_dest32))
            vals_src_32 = vals_dest32.copy()
            vals_src_32.update({
                'account_id': self.sheet_rm_adjustment_account_id.id,
                'debit': vals_dest32['credit'],
                'credit': vals_dest32['debit'],
            })
            move_lines_outgoing.append((0,0,vals_src_32))
        
        if self.sheet_rm_adjustment_qty and self.sheet_rm_adjustment_value:
            vals_dest32 = {
                'name': 'Adjustment Selisih Nilai Asam Semut',
                'plantation_varieties_id': varieties.id,
                'product_id': False,
                'account_id': self.sheet_rm_inventory_account_id.id,
                'debit': round(self.sheet_rm_adjustment_value if self.sheet_rm_adjustment_value>0 else 0.0, 2),
                'credit': round(abs(self.sheet_rm_adjustment_value) if self.sheet_rm_adjustment_value<0 else 0.0, 2),
            }
            move_lines_wip.append((0,0,vals_dest32))
            vals_src_32 = vals_dest32.copy()
            vals_src_32.update({
                'account_id': self.sheet_rm_adjustment_account_id.id,
                'debit': vals_dest32['credit'],
                'credit': vals_dest32['debit'],
            })
            move_lines_wip.append((0,0,vals_src_32))
        # END: Adjustment Asam Semut
            
        if move_lines_receiving:
            # handling Pembuatan
            first_bal = check_balance = 0.0
            for x,y,val in move_lines_receiving:
                if not first_bal:
                    first_bal = round(val['debit'] - val['credit'], 2)
                check_balance += round(val['debit'] - val['credit'], 2)
            # print("-------------- check balance receiving", first_bal, check_balance)
            if check_balance>0.0 or check_balance<0.0:
                if first_bal>0.0:
                    move_lines_receiving[0][2]['debit'] += (-check_balance if check_balance<0.0 else -check_balance)
                else:
                    move_lines_receiving[0][2]['credit'] += (check_balance if check_balance<0.0 else check_balance)
            # first_bal2 = check_balance2 = 0.0
            # for x,y,val in move_lines_receiving:
            #     if not first_bal2:
            #         first_bal2 = round(val['debit'] - val['credit'], 2)
            #     check_balance2 += round(val['debit'] - val['credit'], 2)
            # print("-------------- check balance receiving after", first_bal2, check_balance2)
            values = {
                'date': self.date_to,
                'journal_id': misc_journal.id,
                'move_type': 'entry',
                'line_ids': move_lines_receiving,
            }
            new_move = self.env['account.move'].create(values)
            self.closing_move_ids = [(4,new_move.id)]
        if move_lines_wip:
            first_bal = check_balance = 0.0
            for x,y,val in move_lines_wip:
                if not first_bal:
                    first_bal = round(val['debit'] - val['credit'],2)
                check_balance += round(val['debit'] - val['credit'], 2)
            # print("-------------- check balance wip", check_balance)
            if check_balance>0.0 or check_balance<0.0:
                if first_bal>0.0:
                    move_lines_wip[0][2]['debit'] += (-check_balance if check_balance<0.0 else -check_balance)
                else:
                    move_lines_wip[0][2]['credit'] += (check_balance if check_balance<0.0 else check_balance)
            values2 = {
                'date': self.date_to,
                'journal_id': misc_journal.id,
                'move_type': 'entry',
                'line_ids': move_lines_wip,
            }
            new_reverse_move = self.env['account.move'].create(values2)
            self.closing_move_ids = [(4,new_reverse_move.id)]
        if move_lines_outgoing:
            first_bal = check_balance = 0.0
            for x,y,val in move_lines_outgoing:
                if not first_bal:
                    first_bal = round(val['debit'] - val['credit'], 2)
                check_balance += round(val['debit'] - val['credit'], 2)
            # print("-------------- check balance outgoing", check_balance)
            if check_balance>0.0 or check_balance<0.0:
                if first_bal>0.0:
                    move_lines_outgoing[0][2]['debit'] += (-check_balance if check_balance<0.0 else -check_balance)
                else:
                    move_lines_outgoing[0][2]['credit'] += (check_balance if check_balance<0.0 else check_balance)
            values2 = {
                'date': self.date_to,
                'journal_id': misc_journal.id,
                'move_type': 'entry',
                'line_ids': move_lines_outgoing,
            }
            new_outgoing_moves = self.env['account.move'].create(values2)
            self.closing_move_ids = [(4,new_outgoing_moves.id)]
        
    def create_move_entries_fg_karet(self):
        self.ensure_one()
        misc_journal = self.env.ref('ny_closing.plantation_closing_production')
        varieties = self.env['plant.varieties'].search([('name','=','Karet')], limit=1)
        
        for line in self.fg2_valuation_ids:
            if (line.incoming_qty or line.outgoing_qty) and not line.inventory_account_id:
                raise ValidationError(f"Silahkan isi akun Inventory valuation untuk Product {line.product_id.name}")
            if (line.outgoing_qty) and not line.cogs_account_id:
                raise ValidationError(f"Silahkan isi akun COGS untuk Product {line.product_id.name}")
            # 1. Journal Receiving (Plantation/Manufacturing Cost > Inventory) 
            # 2. Journal Cost of Goods Sold (COGS > Inventory) 
            move_lines_production = []
            move_lines_cogs = []
            if line.incoming_qty or line.manufacturing_cost:
                vals_dest = {
                    'name': f"{line.product_id.name} Finished Process",
                    'plantation_location_type_id': False,
                    'plantation_varieties_id': varieties.id,
                    'plantation_location_id': False,
                    'plantation_activity_id': False,
                    'plantation_src_journal_id': False,
                    'account_id': line.inventory_account_id.id,
                    'product_id': line.product_id.id,
                    'debit': round(line.manufacturing_cost if line.manufacturing_cost>0 else 0.0, 2),
                    'credit': round(abs(line.manufacturing_cost) if line.manufacturing_cost<0 else 0.0, 2),
                }
                # print('................vals_dest', line.product_id.name, vals_dest['debit'], vals_dest['credit'])
                move_lines_production.append((0,0,vals_dest))
                
                vals_src = vals_dest.copy()
                vals_src.update({
                    'name': f"WIP Sheet Finished",
                    'account_id': line.closing_id.sheet_wip_account_id.id,
                    'debit': vals_dest['credit'],
                    'credit': vals_dest['debit'],
                })
                move_lines_production.append((0,0,vals_src))
            
            if line.outgoing_qty or line.outgoing_value:
                vals_src = {
                    'name': 'Cost of Goods Sold',
                    'plantation_location_type_id': False,
                    'plantation_varieties_id': varieties.id,
                    'plantation_location_id': False,
                    'plantation_activity_id': False,
                    'plantation_src_journal_id': False,
                    'account_id': line.cogs_account_id.id,
                    'product_id': line.product_id.id,
                    'debit': round(line.outgoing_value if line.outgoing_value>0 else 0.0, 2),
                    'credit': round(abs(line.outgoing_value) if line.outgoing_value<0 else 0.0, 2),
                }
                vals_dest = vals_src.copy()
                vals_dest.update({
                    'account_id': line.inventory_account_id.id,
                    'debit': vals_src['credit'],
                    'credit': vals_src['debit'],
                })
                move_lines_production.extend([(0,0,vals_src),(0,0,vals_dest)])
            
            # buat fungsi untuk journal adjustment
            # kalau nilainya minus maka inventory ada di credit, debit nya ada account adjustment
            # Kalau nilainya positif maka inventory ada di debit, credit nya account adjustment
            if line.adjustment_qty or line.adjustment_value:
                adjustment_value = line.adjustment_value or 0.0

                if adjustment_value < 0:
                    debit_account = line.adjustment_account_id.id
                    credit_account = line.inventory_account_id.id
                    debit_val = abs(adjustment_value)
                    credit_val = abs(adjustment_value)
                else:
                    debit_account = line.inventory_account_id.id
                    credit_account = line.adjustment_account_id.id
                    debit_val = adjustment_value
                    credit_val = adjustment_value

                vals_src = {
                    'name': 'Adjustment',
                    'plantation_location_type_id': False,
                    'plantation_varieties_id': varieties.id,
                    'plantation_location_id': False,
                    'plantation_activity_id': False,
                    'plantation_src_journal_id': False,
                    'account_id': debit_account,
                    'product_id': line.product_id.id,
                    'debit': round(debit_val if debit_val > 0 else 0.0, 2),
                    'credit': 0.0,
                }
                vals_dest = vals_src.copy()
                vals_dest.update({
                    'account_id': credit_account,
                    'debit': 0.0,
                    'credit': round(credit_val if credit_val > 0 else 0.0, 2),
                })
                move_lines_production.extend([(0, 0, vals_src), (0, 0, vals_dest)])


            if move_lines_production:
                first_bal = check_balance = 0.0
                for x,y,val in move_lines_production:
                    if not first_bal:
                        first_bal = round(val['debit'] - val['credit'], 2)
                    check_balance += round(val['debit'] - val['credit'], 2)
                if check_balance>0.0 or check_balance<0.0:
                    if first_bal>0.0:
                        move_lines_production[0][2]['debit'] += (-check_balance if check_balance<0.0 else -check_balance)
                    else:
                        move_lines_production[0][2]['credit'] += (check_balance if check_balance<0.0 else check_balance)
                values = {
                    'date': self.date_to,
                    'journal_id': misc_journal.id,
                    'move_type': 'entry',
                    'line_ids': move_lines_production,
                }
                new_move = self.env['account.move'].create(values)    
                line.closing_move_id = new_move.id

    def create_move_entries_fg_pisang(self):
        self.ensure_one()
        misc_journal = self.env.ref('ny_closing.plantation_closing_production')
        varieties = self.env['plant.varieties'].search([('name','=','Pisang')], limit=1)
        
        move_lines_production = []
        move_lines_production2 = []
        move_lines_cogs = []
        check_bal = 0.0
        for line in self.fg2_valuation_ids:
            if any([line.ripening_qty>0,line.outgoing_qty>0,line.scrap_qty>0,line.adjustment_qty>0]) and not line.inventory_account_id:
                raise ValidationError(f"Silahkan isi akun Inventory valuation untuk Product {line.product_id.name}")
            if line.ripening_qty and not line.inventory_ripening_account_id:
                raise ValidationError(f"Silahkan isi akun Inventory valuation untuk proses Ripening Product {line.product_id.name}")
            if (line.ripening_outgoing_qty or line.outgoing_qty) and not line.cogs_account_id:
                raise ValidationError(f"Silahkan isi akun COGS untuk Product {line.product_id.name}")
            if line.scrap_qty and not line.scrap_account_id:
                raise ValidationError(f"Silahkan isi akun Scrap untuk Product {line.product_id.name}")
            if line.adjustment_qty and not line.adjustment_account_id:
                raise ValidationError(f"Silahkan isi akun Susut untuk Product {line.product_id.name}")
            # 1. Journal Receiving (Plantation/Manufacturing Cost > Inventory) 
            vals_dest = {
                'name': f"{line.product_id.name} Received",
                'plantation_location_type_id': False,
                'plantation_varieties_id': varieties.id,
                'plantation_location_id': False,
                'plantation_activity_id': False,
                'plantation_src_journal_id': False,
                'account_id': line.inventory_account_id.id,
                'product_id': line.product_id.id,
                'debit': round(line.plantation_cost, 2) if line.plantation_cost>0 else 0.0,
                'credit': round(abs(line.plantation_cost), 2) if line.plantation_cost<0 else 0.0,
            }
            check_bal += vals_dest['debit'] - vals_dest['credit']
            # print('................vals_dest', line.product_id.name, vals_dest['debit'], vals_dest['credit'])
            move_lines_production.append((0,0,vals_dest))

            # 2. Journal Transfer to Ripening
            if line.ripening_qty or line.ripening_value:
                vals_ripening_tf = {
                    'name': f"{line.product_id.name} transfer to Ripening",
                    'plantation_location_type_id': False,
                    'plantation_varieties_id': varieties.id,
                    'plantation_location_id': False,
                    'plantation_activity_id': False,
                    'plantation_src_journal_id': False,
                    'account_id': line.inventory_ripening_account_id.id,
                    'product_id': line.product_id.id,
                    'debit': round(line.ripening_value, 2) if line.ripening_value>0 else 0.0,
                    'credit': round(abs(line.ripening_value), 2) if line.ripening_value<0 else 0.0,
                }
                move_lines_production2.append((0, 0, vals_ripening_tf))
                vals_src2 = vals_ripening_tf.copy()
                vals_src2.update({
                    'account_id': line.inventory_account_id.id,
                    'debit': vals_ripening_tf['credit'],
                    'credit': vals_ripening_tf['debit'],
                })
                move_lines_production2.append((0, 0, vals_src2))

            # 3. Journal Cost of Goods Sold (COGS > Inventory) from Gudang Mentah
            if line.outgoing_qty or line.outgoing_value:
                vals_cogs = {
                    'name': f"{line.product_id.name} Mentah Delivered",
                    'plantation_location_type_id': False,
                    'plantation_varieties_id': varieties.id,
                    'plantation_location_id': False,
                    'plantation_activity_id': False,
                    'plantation_src_journal_id': False,
                    'account_id': line.cogs_account_id.id,
                    'product_id': line.product_id.id,
                    'debit': round(line.outgoing_value, 2) if line.outgoing_value>0 else 0.0,
                    'credit': round(abs(line.outgoing_value), 2) if line.outgoing_value<0 else 0.0,
                }
                move_lines_cogs.append((0, 0, vals_cogs))
                vals_src3 = vals_cogs.copy()
                vals_src3.update({
                    'name': f"Inventory to Cogs",
                    'account_id': line.inventory_account_id.id,
                    'debit': vals_cogs['credit'],
                    'credit': vals_cogs['debit'],
                })
                move_lines_cogs.append((0, 0, vals_src3))

            # 4. Journal Scrap
            if line.scrap_qty or line.scrap_value:
                vals_cogs = {
                    'name': f"Scrap Cost {line.product_id.name} Mentah",
                    'plantation_location_type_id': False,
                    'plantation_varieties_id': varieties.id,
                    'plantation_location_id': False,
                    'plantation_activity_id': False,
                    'plantation_src_journal_id': False,
                    'account_id': line.scrap_account_id.id,
                    'product_id': line.product_id.id,
                    'debit': round(line.scrap_value, 2) if line.scrap_value>0 else 0.0,
                    'credit': round(abs(line.scrap_value), 2) if line.scrap_value<0 else 0.0,
                }
                move_lines_cogs.append((0, 0, vals_cogs))
                vals_src4 = vals_cogs.copy()
                vals_src4.update({
                    'name': f"Inventory Scrap",
                    'account_id': line.inventory_account_id.id,
                    'debit': vals_cogs['credit'],
                    'credit': vals_cogs['debit'],
                })
                move_lines_cogs.append((0, 0, vals_src4))
            
            # 5. Journal Receiving Ripening Inventory (Transfer Ripening + Ripening Cost)
            # if line.ripening_qty:
            if line.ripening_cost:
                vals_dest2 = vals_dest.copy()
                vals_dest2.update({
                    'name': f"Ripening Cost to Inventory Ripening",
                    'plantation_varieties_id': varieties.id,
                    'account_id': line.inventory_ripening_account_id.id,
                    'debit': round(line.ripening_cost, 2) if line.ripening_cost>0 else 0.0,
                    'credit': round(abs(line.ripening_cost), 2) if line.ripening_cost<0 else 0.0,
                })
                check_bal += vals_dest2['debit'] - vals_dest2['credit']
                # print('................vals_dest2', line.product_id.name, vals_dest2['debit'], vals_dest2['credit'])
                move_lines_production2.append((0,0,vals_dest2))
            
            # 6. Journal Cost of Goods Sold (COGS > Inventory) from Ripening Location
            if line.ripening_outgoing_qty or line.ripening_outgoing_value:
                vals_cogs2 = {
                    'name': f"{line.product_id.name} Delivered",
                    'plantation_location_type_id': False,
                    'plantation_varieties_id': varieties.id,
                    'plantation_location_id': False,
                    'plantation_activity_id': False,
                    'plantation_src_journal_id': False,
                    'account_id': line.cogs_account_id.id,
                    'product_id': line.product_id.id,
                    'debit': round(line.ripening_outgoing_value, 2) if line.ripening_outgoing_value>0 else 0.0,
                    'credit': round(abs(line.ripening_outgoing_value), 2) if line.ripening_outgoing_value<0 else 0.0,
                }
                move_lines_cogs.append((0, 0, vals_cogs2))
                vals_src5 = vals_cogs2.copy()
                vals_src5.update({
                    'name': f"Inventory to Cogs",
                    'account_id': line.inventory_ripening_account_id.id,
                    'debit': vals_cogs2['credit'],
                    'credit': vals_cogs2['debit'],
                })
                move_lines_cogs.append((0, 0, vals_src5))
            
            if line.outgoing_issue_stock_move_ids:
                remaining_issue_value = round(line.outgoing_issue_value, 2)
                for smi in line.outgoing_issue_stock_move_ids:
                    if smi.location_id.usage=='internal' and smi.location_dest_id.usage!='internal':
                        issue_value = round(smi.quantity_done * line.new_cost_price, 2)
                    elif smi.location_id.usage!='internal' and smi.location_dest_id.usage=='internal':
                        issue_value = round(-1 * smi.quantity_done * line.new_cost_price, 2)
                    remaining_issue_value -= issue_value
                    vals_issues = {
                        'name': f"{line.product_id.name} Issued",
                        'plantation_location_type_id': False,
                        'plantation_varieties_id': varieties.id,
                        'plantation_location_id': False,
                        'plantation_activity_id': False,
                        'plantation_src_journal_id': False,
                        'account_id': smi.plantation_activity_id.account_id.id,
                        'product_id': line.product_id.id,
                        'debit': issue_value if issue_value>0 else 0.0,
                        'credit': issue_value if issue_value<0 else 0.0,
                    }
                    move_lines_cogs.append((0, 0, vals_issues))
                vals_src4 = {
                    'name': f"{smi.product_id.name} Issued",
                    'plantation_location_type_id': False,
                    'plantation_varieties_id': False,
                    'plantation_location_id': False,
                    'plantation_activity_id': False,
                    'plantation_src_journal_id': False,
                    'account_id': line.inventory_account_id.id,
                    'product_id': line.product_id.id,
                    # 'debit': round(abs(line.outgoing_issue_value), 2) if line.outgoing_issue_value<0 else 0.0,
                    # 'credit': round(line.outgoing_issue_value, 2) if line.outgoing_issue_value>0 else 0.0,
                    'debit': round(abs(line.outgoing_issue_value-remaining_issue_value), 2) if (line.outgoing_issue_value-remaining_issue_value)<0 else 0.0,
                    'credit': round(line.outgoing_issue_value-remaining_issue_value, 2) if (line.outgoing_issue_value-remaining_issue_value)>0 else 0.0,
                }
                move_lines_cogs.append((0, 0, vals_src4))
            
            # 7. Journal Susut
            if line.adjustment_qty or line.adjustment_value:
                vals_adj = {
                    'name': f"Adjustment Cost {line.product_id.name} Mentah",
                    'plantation_location_type_id': False,
                    'plantation_varieties_id': varieties.id,
                    'plantation_location_id': False,
                    'plantation_activity_id': False,
                    'plantation_src_journal_id': False,
                    'account_id': line.inventory_account_id.id,
                    'product_id': line.product_id.id,
                    'debit': round(line.adjustment_value, 2) if line.adjustment_value>0 else 0.0,
                    'credit': round(abs(line.adjustment_value), 2) if line.adjustment_value<0 else 0.0,
                }
                move_lines_cogs.append((0, 0, vals_adj))
                vals_src5 = vals_adj.copy()
                vals_src5.update({
                    'name': f"Adjustment Cost {line.product_id.name} Mentah",
                    'account_id': line.adjustment_account_id.id,
                    'debit': vals_adj['credit'],
                    'credit': vals_adj['debit'],
                })
                move_lines_cogs.append((0, 0, vals_src5))
            # 7. Journal Susut
            if line.adjustment_closing_qty or line.adjustment_closing_value:
                vals_adj = {
                    'name': f"Adjustment Cost {line.product_id.name} Mentah",
                    'plantation_location_type_id': False,
                    'plantation_varieties_id': varieties.id,
                    'plantation_location_id': False,
                    'plantation_activity_id': False,
                    'plantation_src_journal_id': False,
                    'account_id': line.inventory_account_id.id,
                    'product_id': line.product_id.id,
                    'debit': round(line.adjustment_closing_value, 2) if line.adjustment_closing_value>0 else 0.0,
                    'credit': round(abs(line.adjustment_closing_value), 2) if line.adjustment_closing_value<0 else 0.0,
                }
                move_lines_cogs.append((0, 0, vals_adj))
                vals_src5 = vals_adj.copy()
                vals_src5.update({
                    'name': f"Adjustment Cost {line.product_id.name} Mentah",
                    'account_id': line.adjustment_account_id.id,
                    'debit': vals_adj['credit'],
                    'credit': vals_adj['debit'],
                })
                move_lines_cogs.append((0, 0, vals_src5))

        for plt_cost in self.plantation_cost_ids:
            vals_src = {
                'name': f"Plantation Cost Pisang to Inventory",
                'plantation_varieties_id': varieties.id,
                'plantation_location_type_id': plt_cost.plantation_location_type_id.id if plt_cost.plantation_location_type_id else False,
                'plantation_location_id': plt_cost.plantation_location_id.id if plt_cost.plantation_location_id else False,
                'plantation_activity_id': plt_cost.plantation_activity_id.id if plt_cost.plantation_activity_id else False,
                'plantation_src_journal_id': plt_cost.plantation_src_journal_id.id if plt_cost.plantation_src_journal_id else False,
                'account_id': plt_cost.account_id.id,
                'debit': round(abs(plt_cost.total_cost), 2) if plt_cost.total_cost<0 else 0.0,
                'credit': round(plt_cost.total_cost, 2) if plt_cost.total_cost>0 else 0.0,
            }
            check_bal += vals_src['debit'] - vals_src['credit']
            # print('................vals_src', vals_src['debit'], vals_src['credit'])
            move_lines_production.append((0,0,vals_src))
        
        for ripe_cost in self.mrp_cost_ids:
            vals_src2 = {
                'name': f"Ripening Cost Pisang to Inventory",
                'plantation_varieties_id': varieties.id,
                'plantation_location_type_id': ripe_cost.plantation_location_type_id.id if ripe_cost.plantation_location_type_id else False,
                'plantation_location_id': ripe_cost.plantation_location_id.id if ripe_cost.plantation_location_id else False,
                'plantation_activity_id': ripe_cost.plantation_activity_id.id if ripe_cost.plantation_activity_id else False,
                'plantation_src_journal_id': ripe_cost.plantation_src_journal_id.id if ripe_cost.plantation_src_journal_id else False,
                'account_id': ripe_cost.account_id.id,
                'debit': round(abs(ripe_cost.total_cost), 2) if ripe_cost.total_cost<0 else 0.0,
                'credit': round(ripe_cost.total_cost, 2) if ripe_cost.total_cost>0 else 0.0,
            }
            check_bal += round(vals_src2['debit'] - vals_src2['credit'], 2)
            # print('................vals_src2', vals_src2['debit'], vals_src2['credit'])
            move_lines_production2.append((0,0,vals_src2))

        move_lines_production = [line for line in move_lines_production if line[2].get('account_id')]
        move_lines_production2 = [line for line in move_lines_production2 if line[2].get('account_id')]
        move_lines_cogs = [line for line in move_lines_cogs if line[2].get('account_id')]

        if check_bal and check_bal>=-1.0 and check_bal<=1.0:
            move_lines_production[0][2]['debit'] = move_lines_production[0][2]['debit'] - check_bal

        if move_lines_production or move_lines_production2:
            values = {
                'date': self.date_to,
                'journal_id': misc_journal.id,
                'move_type': 'entry',
                'line_ids': move_lines_production+move_lines_production2,
            }
            new_move = self.env['account.move'].create(values)
            self.closing_move_ids = [(4, new_move.id)]        
        if move_lines_cogs:
            values = {
                'date': self.date_to,
                'journal_id': misc_journal.id,
                'move_type': 'entry',
                'line_ids': move_lines_cogs,
            }
            new_move2 = self.env['account.move'].create(values)
            self.closing_move_ids = [(4, new_move2.id)]
    
    def create_move_entries_fg_melon(self):
        self.ensure_one()
        misc_journal = self.env.ref('ny_closing.plantation_closing_production')
        varieties = self.env['plant.varieties'].search([('name','=','Melon')], limit=1)
        
        move_lines_production = []
        move_lines_production2 = []
        move_lines_cogs = []
        check_bal = 0.0
        for line in self.fg2_valuation_ids:
            if any([line.ripening_qty>0,line.outgoing_qty>0,line.scrap_qty>0,line.adjustment_qty>0]) and not line.inventory_account_id:
                raise ValidationError(f"Silahkan isi akun Inventory valuation untuk Product {line.product_id.name}")
            # if line.ripening_qty and not line.inventory_ripening_account_id:
            #     raise ValidationError(f"Silahkan isi akun Inventory valuation untuk proses Ripening Product {line.product_id.name}")
            # if (line.ripening_outgoing_qty or line.outgoing_qty) and not line.cogs_account_id:
            #     raise ValidationError(f"Silahkan isi akun COGS untuk Product {line.product_id.name}")
            if line.scrap_qty and not line.scrap_account_id:
                raise ValidationError(f"Silahkan isi akun Scrap untuk Product {line.product_id.name}")
            if line.adjustment_qty and not line.adjustment_account_id:
                raise ValidationError(f"Silahkan isi akun Susut untuk Product {line.product_id.name}")
            # 1. Journal Receiving (Plantation/Manufacturing Cost > Inventory) 
            vals_dest = {
                'name': f"{line.product_id.name} Received",
                'plantation_location_type_id': False,
                'plantation_varieties_id': varieties.id,
                'plantation_location_id': False,
                'plantation_activity_id': False,
                'plantation_src_journal_id': False,
                'account_id': line.inventory_account_id.id,
                'product_id': line.product_id.id,
                'debit': round(line.plantation_cost, 2) if line.plantation_cost>0 else 0.0,
                'credit': round(abs(line.plantation_cost), 2) if line.plantation_cost<0 else 0.0,
            }
            check_bal += vals_dest['debit'] - vals_dest['credit']
            # print('................vals_dest', line.product_id.name, vals_dest['debit'], vals_dest['credit'])
            move_lines_production.append((0,0,vals_dest))

            # 3. Journal Cost of Goods Sold (COGS > Inventory) from Gudang Mentah
            if line.outgoing_qty or line.outgoing_value:
                vals_cogs = {
                    'name': f"{line.product_id.name} Delivered",
                    'plantation_location_type_id': False,
                    'plantation_varieties_id': varieties.id,
                    'plantation_location_id': False,
                    'plantation_activity_id': False,
                    'plantation_src_journal_id': False,
                    'account_id': line.cogs_account_id.id,
                    'product_id': line.product_id.id,
                    'debit': round(line.outgoing_value, 2) if line.outgoing_value>0 else 0.0,
                    'credit': round(abs(line.outgoing_value), 2) if line.outgoing_value<0 else 0.0,
                }
                move_lines_cogs.append((0, 0, vals_cogs))
                vals_src3 = vals_cogs.copy()
                vals_src3.update({
                    'name': f"Inventory to Cogs",
                    'account_id': line.inventory_account_id.id,
                    'debit': vals_cogs['credit'],
                    'credit': vals_cogs['debit'],
                })
                move_lines_cogs.append((0, 0, vals_src3))

            if line.outgoing_issue_stock_move_ids:
                remaining_issue_value = round(line.outgoing_issue_value, 2)
                for smi in line.outgoing_issue_stock_move_ids:
                    if smi.location_id.usage=='internal' and smi.location_dest_id.usage!='internal':
                        issue_value = round(smi.quantity_done * line.new_cost_price, 2)
                    elif smi.location_id.usage!='internal' and smi.location_dest_id.usage=='internal':
                        issue_value = round(-1 * smi.quantity_done * line.new_cost_price, 2)
                    remaining_issue_value -= issue_value
                    vals_issues = {
                        'name': f"{line.product_id.name} Issued",
                        'plantation_location_type_id': False,
                        'plantation_varieties_id': varieties.id,
                        'plantation_location_id': False,
                        'plantation_activity_id': False,
                        'plantation_src_journal_id': False,
                        'account_id': smi.plantation_activity_id.account_id.id,
                        'product_id': line.product_id.id,
                        'debit': issue_value if issue_value>0 else 0.0,
                        'credit': issue_value if issue_value<0 else 0.0,
                    }
                    move_lines_cogs.append((0, 0, vals_issues))
                vals_src4 = {
                    'name': f"{smi.product_id.name} Issued",
                    'plantation_location_type_id': False,
                    'plantation_varieties_id': False,
                    'plantation_location_id': False,
                    'plantation_activity_id': False,
                    'plantation_src_journal_id': False,
                    'account_id': line.inventory_account_id.id,
                    'product_id': line.product_id.id,
                    'debit': round(abs(line.outgoing_issue_value), 2) if line.outgoing_issue_value<0 else 0.0,
                    'credit': round(line.outgoing_issue_value, 2) if line.outgoing_issue_value>0 else 0.0,
                }
                move_lines_cogs.append((0, 0, vals_src4))
            
            # 4. Journal Scrap
            if line.scrap_qty or line.scrap_value:
                vals_cogs = {
                    'name': f"Scrap Cost {line.product_id.name} Mentah",
                    'plantation_location_type_id': False,
                    'plantation_varieties_id': varieties.id,
                    'plantation_location_id': False,
                    'plantation_activity_id': False,
                    'plantation_src_journal_id': False,
                    'account_id': line.scrap_account_id.id,
                    'product_id': line.product_id.id,
                    'debit': round(line.scrap_value, 2) if line.scrap_value>0 else 0.0,
                    'credit': round(abs(line.scrap_value), 2) if line.scrap_value<0 else 0.0,
                }
                move_lines_cogs.append((0, 0, vals_cogs))
                vals_src4 = vals_cogs.copy()
                vals_src4.update({
                    'name': f"Inventory Scrap",
                    'account_id': line.inventory_account_id.id,
                    'debit': vals_cogs['credit'],
                    'credit': vals_cogs['debit'],
                })
                move_lines_cogs.append((0, 0, vals_src4))
            
            # 7. Journal Susut
            if line.adjustment_qty or line.adjustment_value or line.adjustment_value_only:
                vals_adj = {
                    'name': f"Adjustment Cost {line.product_id.name} Mentah",
                    'plantation_location_type_id': False,
                    'plantation_varieties_id': varieties.id,
                    'plantation_location_id': False,
                    'plantation_activity_id': False,
                    'plantation_src_journal_id': False,
                    'account_id': line.inventory_account_id.id,
                    'product_id': line.product_id.id,
                    'debit': round(line.adjustment_value + line.adjustment_value_only, 2) if line.adjustment_value or line.adjustment_value_only > 0 else 0.0,
                    'credit': round(abs(line.adjustment_value + line.adjustment_value_only), 2) if line.adjustment_value or line.adjustment_value_only < 0 else 0.0,
                }
                move_lines_cogs.append((0, 0, vals_adj))
                vals_src5 = vals_adj.copy()
                vals_src5.update({
                    'name': f"Inventory Scrap",
                    'account_id': line.adjustment_account_id.id,
                    'debit': vals_adj['credit'],
                    'credit': vals_adj['debit'],
                })
                move_lines_cogs.append((0, 0, vals_src5))

        for plt_cost in self.plantation_cost_ids:
            vals_src = {
                'name': f"Plantation Cost Melon to Inventory",
                'plantation_varieties_id': varieties.id,
                'plantation_location_type_id': plt_cost.plantation_location_type_id.id if plt_cost.plantation_location_type_id else False,
                'plantation_location_id': plt_cost.plantation_location_id.id if plt_cost.plantation_location_id else False,
                'plantation_activity_id': plt_cost.plantation_activity_id.id if plt_cost.plantation_activity_id else False,
                'plantation_src_journal_id': plt_cost.plantation_src_journal_id.id if plt_cost.plantation_src_journal_id else False,
                'account_id': plt_cost.account_id.id,
                'debit': round(abs(plt_cost.total_cost), 2) if plt_cost.total_cost<0 else 0.0,
                'credit': round(plt_cost.total_cost, 2) if plt_cost.total_cost>0 else 0.0,
            }
            check_bal += vals_src['debit'] - vals_src['credit']
            # print('................vals_src', vals_src['debit'], vals_src['credit'])
            move_lines_production.append((0,0,vals_src))
        
        # if check_bal and check_bal>=-1.0 and check_bal<=1.0:
        #     move_lines_production[0][2]['debit'] = move_lines_production[0][2]['debit'] - check_bal
        if move_lines_production or move_lines_production2:
            first_bal = check_balance = 0.0
            move_lines = move_lines_production+move_lines_production2
            for x,y,val in move_lines:
                if not first_bal:
                    first_bal = round(val['debit'] - val['credit'], 2)
                check_balance += round(val['debit'] - val['credit'], 2)
            # print("-------------- check balance receiving", first_bal, check_balance)
            if check_balance>0.0 or check_balance<0.0:
                if first_bal>0.0:
                    move_lines[0][2]['debit'] += (-check_balance if check_balance<0.0 else -check_balance)
                else:
                    move_lines[0][2]['credit'] += (check_balance if check_balance<0.0 else check_balance)
            values = {
                'date': self.date_to,
                'journal_id': misc_journal.id,
                'move_type': 'entry',
                'line_ids': move_lines,
            }
            new_move = self.env['account.move'].create(values)
            self.closing_move_ids = [(4, new_move.id)]
        if move_lines_cogs:
            first_bal = check_balance = 0.0
            for x,y,val in move_lines_cogs:
                if not first_bal:
                    first_bal = round(val['debit'] - val['credit'], 2)
                check_balance += round(val['debit'] - val['credit'], 2)
            # print("-------------- check balance receiving", first_bal, check_balance)
            if check_balance>0.0 or check_balance<0.0:
                if first_bal>0.0:
                    move_lines_cogs[0][2]['debit'] += (-check_balance if check_balance<0.0 else -check_balance)
                else:
                    move_lines_cogs[0][2]['credit'] += (check_balance if check_balance<0.0 else check_balance)
            values = {
                'date': self.date_to,
                'journal_id': misc_journal.id,
                'move_type': 'entry',
                'line_ids': move_lines_cogs,
            }
            new_move2 = self.env['account.move'].create(values)
            self.closing_move_ids = [(4, new_move2.id)]
    
    def create_move_entries(self):
        for closing in self:
            if closing.closing_process_id and closing.parent_state!='closing_production':
                raise ValidationError(f"Tidak dapat mengubah data Closing Plantation yang karena Closing Procedure sudah berstatus {closing.parent_state}")
            if closing.closing_move_ids:
                for exmove in closing.closing_move_ids:
                    if exmove.state=='posted':
                        exmove.button_draft()
                        exmove.write({'name': ''})
                closing.closing_move_ids.unlink()

            if closing.fg2_valuation_ids.closing_move_id:
                for exmove in closing.fg2_valuation_ids.closing_move_id:
                    if exmove.state=='posted':
                        exmove.button_draft()
                        exmove.write({'name': ''})
                closing.fg2_valuation_ids.closing_move_id.unlink()

            if closing.varieties_type=='karet':
                closing.create_move_entries_rm_karet()
                closing.create_move_entries_fg_karet()
            elif closing.varieties_type=='pisang':
                closing.create_move_entries_fg_pisang()
            elif closing.varieties_type=='melon':
                closing.create_move_entries_fg_melon()
        return True

    def action_done(self):
        for closing in self:
            closing.create_move_entries()
            closing.closing_move_ids._post(soft=False)
            closing.fg2_valuation_ids.mapped('closing_move_id')._post(soft=False)
            closing.write({'state': 'done'})
        return True

    def button_back(self):
        for closing in self:
            if closing.state=='account_entry':
                closing.state='fg_valuation'
            # elif closing.state=='fg2_valuation':
            #     closing.state='fg1_valuation'
            # elif closing.state=='fg1_valuation':
            #     closing.state='rm_valuation'
            elif closing.state=='fg_valuation':
                closing.state='rm_valuation'
            elif closing.state=='rm_valuation':
                closing.state='start'
        return True
    
    def button_cancel(self):
        for closing in self:
            if closing.state=='done':
                raise ValidationError("Tidak bisa cancel data yang sudah di posting. Silahkan Cancel Manual terlebih dahulu")
            
        self.filtered(lambda x: x.state in ('start','rm_valuation','fg1_valuation','fg2_valuation')).write({'state':'cancel'})
        return True
    
    def button_cancel_done(self):
        for closing in self:
            if closing.varieties_type=='karet':
                closing.closing_move_ids.button_cancel()
                closing.closing_move_ids.button_draft()
                closing.closing_move_ids.write({'name': ''})
                closing.closing_move_ids.unlink()
                for line in closing.fg2_valuation_ids:
                    line.closing_move_id.button_cancel()
                    line.closing_move_id.button_draft()
                    line.closing_move_id.write({'name': ''})
                    line.closing_move_id.unlink()
            elif closing.varieties_type in ('pisang','melon'):
                closing.closing_move_ids.button_cancel()
                closing.closing_move_ids.button_draft()
                closing.closing_move_ids.write({'name': ''})
                closing.closing_move_ids.unlink()
            closing.write({'state': 'account_entry'})
        return True

    def button_set_new(self):
        self.filtered(lambda x: x.state=='cancel').write({'state':'start'})
        return True

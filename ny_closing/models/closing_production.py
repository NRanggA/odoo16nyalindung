from odoo import models, api, fields, Command, _
from odoo.exceptions import ValidationError

from dateutil.relativedelta import relativedelta

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

    @api.depends('total_cost', 'closing_id.pct_cost_for_latex', 'closing_id.pct_cost_for_lump')
    def _compute_cost(self):
        for l in self:
            l.total_cost_latex = l.total_cost * l.closing_id.pct_cost_for_latex / 100.0
            l.total_cost_lump = l.total_cost * l.closing_id.pct_cost_for_lump / 100.0

class ClosingProductionFinishGood(models.Model):
    _name = 'closing.production.finishgood'
    _description = 'Closing Production Finish Good'

    closing_id = fields.Many2one('closing.production', string='Closing Production')
    prev_closing_fg_id = fields.Many2one('closing.production.finishgood', string='Last Closing Production')
    product_id = fields.Many2one('product.product', string='Product', ondelete='restrict')
    
    inventory_account_id = fields.Many2one('account.account', 'Account Inventory')
    cogs_account_id = fields.Many2one('account.account', 'Account COGS')

    opening_qty = fields.Float(compute='_compute_opening', inverse='_invrs_opening', readonly=False, store=True, string='Opening Qty')
    opening_qty_manual = fields.Float(string='Opening Qty')
    opening_value = fields.Float(compute='_compute_opening', inverse='_invrs_opening', readonly=False, store=True, string='Opening Value')
    opening_value_manual = fields.Float(string='Opening Value')
    
    manufacturing_cost = fields.Float(string='Manufacturing Cost')
    plantation_cost = fields.Float(compute='_compute_plantation_cost', store=True, string='Plantation Cost')
    plantation_cost_ids = fields.One2many('closing.production.plantation.cost', 'closing_fg_id', 'Plantation Cost Summs')
    
    incoming_qty = fields.Float(string='Incoming Qty')
    onhand_qty = fields.Float(compute='_compute_onhand_and_cost_price', store=True, string='Onhand Qty')
    onhand_value = fields.Float(compute='_compute_onhand_and_cost_price', store=True, string='Onhand Value')
    new_cost_price = fields.Float(compute='_compute_onhand_and_cost_price', store=True, string='New Cost Price')
    
    outgoing_qty = fields.Float(string='Delivered Qty')
    outgoing_value = fields.Float(compute='_compute_outgoing_value', store=True, string ='Delivered Value')
    
    closing_qty = fields.Float(compute='_compute_closing', store=True, string='Closing Qty')
    closing_value = fields.Float(compute='_compute_closing', store=True, string='Closing Value')

    closing_move_id = fields.Many2one('account.move', string='Journal Entry')

    ############ COMPUTED METHOD ###########
    @api.depends('prev_closing_fg_id')
    def _compute_opening(self):
        for line in self:
            line.opening_qty = line.prev_closing_fg_id.closing_qty if line.prev_closing_fg_id else line.opening_qty_manual
            line.opening_value = line.prev_closing_fg_id.closing_value if line.prev_closing_fg_id else line.opening_value_manual

    @api.onchange('opening_qty', 'opening_value')
    def _invrs_opening(self):
        for line in self:
            line.opening_qty_manual = line.opening_qty
            line.opening_qty_manual = line.opening_value
    
    @api.depends('plantation_cost_ids','plantation_cost_ids.total_cost')
    def _compute_plantation_cost(self):
        for line in self:
            line.plantation_cost = sum(line.plantation_cost_ids.mapped('total_cost')) if line.plantation_cost_ids else 0.0

    @api.depends('opening_qty', 'opening_value', 
            'incoming_qty', 'plantation_cost')
    def _compute_onhand_and_cost_price(self):
        for line in self:
            line.onhand_qty = line.opening_qty + line.incoming_qty
            line.onhand_value = line.opening_value + line.plantation_cost + line.manufacturing_cost
            line.new_cost_price = line.onhand_value/line.onhand_qty if line.onhand_qty else 0.0

    @api.depends('new_cost_price', 'outgoing_qty')
    def _compute_outgoing_value(self):
        for line in self:
            line.outgoing_value = line.outgoing_qty * line.new_cost_price

    @api.depends('onhand_qty', 'onhand_value', 
            'outgoing_qty', 'outgoing_value')
    def _compute_closing(self):
        for line in self:
            line.closing_qty = line.onhand_qty - line.outgoing_qty
            line.closing_value = line.onhand_value - line.outgoing_value

class ClosingProduction(models.Model):
    _name = 'closing.production'
    _description = 'Closing Production'

    closing_process_id = fields.Many2one('closing.process', string='Closing Process', ondelete='cascade')

    prev_closing_id = fields.Many2one('closing.production', string='Last Closing Production')
    date_from = fields.Date()
    date_to = fields.Date()
    state = fields.Selection([('start','Start'),
            ('rm_valuation','Raw Material'),
            ('fg1_valuation','Semi-Finish Good'),
            ('fg2_valuation','Finish Good'),
            ('account_entry','Jurnal Creation'),
            ('done','Done'),
            ('cancel','Cancelled')], string='Status', default='start')
    
    plantation_cost_ids = fields.One2many('closing.production.plantation.cost', 'closing_id', 'Plantation Cost Summs')
    plantation_cost = fields.Float(compute='_compute_plantation_cost', store=True, string='Total Plantation Cost')

    closing_move_ids = fields.Many2many('account.move', 'closing_prod_acc_move_rel', string='Closing Entries')

    manufacturing_cost_account_ids = fields.Many2many('account.account', 'closing_prod_mrp_cost_account_rel', string='Manufacturing Cost Accounts')
    manufacturing_cost = fields.Float('Total Manufacturing Cost')
    ############################## BEGIN VALUATION RAW MATERIAL ##################################
    # The product are only for Latex and Lump
    # Latex
    latex_product_id = fields.Many2one('product.product', string='Product Latex', ondelete='restrict')
    latex_inventory_account_id = fields.Many2one('account.account', 'Account Inventory Latex')
    latex_wip_account_id = fields.Many2one('account.account', 'Account WIP Latex')
    latex_consumption_account_id = fields.Many2one('account.account', 'Account Consumption Latex')
    latex_opening_qty = fields.Float(compute='_compute_opening_rm', inverse='_invrs_opening_rm', readonly=False, store=True, string='Opening Qty of Latex')
    latex_opening_qty_manual = fields.Float()
    latex_opening_value = fields.Float(compute='_compute_opening_rm', inverse='_invrs_opening_rm', readonly=False, store=True, string='Opening Value of Latex')
    latex_opening_value_manual = fields.Float()
    latex_incoming_qty = fields.Float(string='Incoming Qty of Latex')
    pct_cost_for_latex = fields.Float('% Cost for Latex', default=90)
    latex_plantation_cost = fields.Float(compute='_compute_plantation_cost', store=True, string='Plantation Cost of Latex')
    latex_onhand_qty = fields.Float(compute='_compute_onhand_and_cost_price_rm', store=True, string='Onhand Qty of Latex')
    latex_onhand_value = fields.Float(compute='_compute_onhand_and_cost_price_rm', store=True, string='Onhand Value of Latex')
    latex_new_cost_price = fields.Float(compute='_compute_onhand_and_cost_price_rm', store=True, string='New Cost Price of Latex')
    latex_wip_qty = fields.Float(string='Latex on Work in Process')
    latex_wip_value = fields.Float(compute='_compute_outgoing_value_rm', store=True, string='Latex Value on Work in Process')
    latex_outgoing_qty = fields.Float(string='Consumed Qty of Latex')
    latex_outgoing_value = fields.Float(compute='_compute_outgoing_value_rm', store=True, string='Consumed Value of Latex')
    latex_closing_qty = fields.Float(compute='_compute_closing_rm', store=True, string='Closing Qty of Latex')
    latex_closing_value = fields.Float(compute='_compute_closing_rm', store=True, string='Closing Value of Latex')
    # Lump
    lump_product_id = fields.Many2one('product.product', string='Product Lump', ondelete='restrict')
    lump_inventory_account_id = fields.Many2one('account.account', 'Account Inventory Lump')
    lump_wip_account_id = fields.Many2one('account.account', 'Account WIP Lump')
    lump_consumption_account_id = fields.Many2one('account.account', 'Account Consumption Lump')
    lump_opening_qty = fields.Float(compute='_compute_opening_rm', inverse='_invrs_opening_rm', readonly=False, store=True, string='Opening Qty of Lump')
    lump_opening_qty_manual = fields.Float(string='Opening Qty of Lump')
    lump_opening_value = fields.Float(compute='_compute_opening_rm', inverse='_invrs_opening_rm', readonly=False, store=True, string='Opening Value of Lump')
    lump_opening_value_manual = fields.Float(string='Opening Value of Lump')
    pct_cost_for_lump = fields.Float('% Cost for Lump', default=10)
    lump_plantation_cost = fields.Float(compute='_compute_plantation_cost', store=True, string='Plantation Cost of Lump')
    lump_incoming_qty = fields.Float(string='Incoming Qty of Lump')
    lump_onhand_qty = fields.Float(compute='_compute_onhand_and_cost_price_rm', store=True, string='Onhand Qty of Lump')
    lump_onhand_value = fields.Float(compute='_compute_onhand_and_cost_price_rm', store=True, string='Onhand Value of Lump')
    lump_new_cost_price = fields.Float(compute='_compute_onhand_and_cost_price_rm', store=True, string='New Cost Price of Lump')
    lump_wip_qty = fields.Float(string='Lump on Work in Process')
    lump_wip_value = fields.Float(compute='_compute_outgoing_value_rm', store=True, string='Lump Value on Work in Process')
    lump_outgoing_qty = fields.Float(string='Consumed Qty of Lump')
    lump_outgoing_value = fields.Float(compute='_compute_outgoing_value_rm', store=True, string ='Consumed Value of Lump')
    lump_closing_qty = fields.Float(compute='_compute_closing_rm', store=True, string='Closing Qty of Lump')
    lump_closing_value = fields.Float(compute='_compute_closing_rm', store=True, string='Closing Value of Lump')

    ############ COMPUTED METHOD ###########
    @api.depends('prev_closing_id')
    def _compute_opening_rm(self):
        for closing in self:
            closing.latex_opening_qty = closing.prev_closing_id.latex_closing_qty if closing.prev_closing_id else closing.latex_opening_qty_manual
            closing.latex_opening_value = closing.prev_closing_id.latex_closing_value if closing.prev_closing_id else closing.latex_opening_value_manual
            closing.lump_opening_qty = closing.prev_closing_id.lump_closing_qty if closing.prev_closing_id else closing.lump_opening_qty_manual
            closing.lump_opening_value = closing.prev_closing_id.lump_closing_value if closing.prev_closing_id else closing.lump_opening_value_manual

    @api.onchange('latex_opening_qty', 'latex_opening_value',
            'lump_opening_qty', 'lump_opening_value')
    def _invrs_opening_rm(self):
        for closing in self:
            closing.latex_opening_qty_manual = closing.latex_opening_qty
            closing.latex_opening_qty_manual = closing.latex_opening_value
            closing.lump_opening_qty_manual = closing.lump_opening_qty
            closing.lump_opening_qty_manual = closing.lump_opening_value

    @api.depends('pct_cost_for_latex', 'pct_cost_for_lump', 'plantation_cost_ids.total_cost_latex', 'plantation_cost_ids.total_cost_lump')
    def _compute_plantation_cost(self):
        for closing in self:
            # closing.latex_plantation_cost = closing.plantation_cost * closing.pct_cost_for_latex / 100.0
            # closing.lump_plantation_cost = closing.plantation_cost * closing.pct_cost_for_lump / 100.0
            closing.latex_plantation_cost = sum(closing.plantation_cost_ids.mapped('total_cost_latex')) if closing.plantation_cost_ids else 0.0
            closing.lump_plantation_cost = sum(closing.plantation_cost_ids.mapped('total_cost_lump')) if closing.plantation_cost_ids else 0.0
    
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

    @api.depends('latex_new_cost_price', 'latex_wip_qty', 'latex_outgoing_qty',
            'lump_new_cost_price', 'lump_wip_qty', 'lump_outgoing_qty')
    def _compute_outgoing_value_rm(self):
        for closing in self:
            closing.latex_wip_value = closing.latex_wip_qty * closing.latex_new_cost_price
            closing.latex_outgoing_value = closing.latex_outgoing_qty * closing.latex_new_cost_price
            closing.lump_wip_value = closing.lump_wip_qty * closing.lump_new_cost_price
            closing.lump_outgoing_value = closing.lump_outgoing_qty * closing.lump_new_cost_price

    @api.depends('latex_onhand_qty', 'latex_onhand_value', 
            'latex_wip_qty', 'latex_wip_value', 
            'latex_outgoing_qty', 'latex_outgoing_value',
            'lump_onhand_qty', 'lump_onhand_value', 
            'lump_wip_qty', 'lump_wip_value', 
            'lump_outgoing_qty', 'lump_outgoing_value')
    def _compute_closing_rm(self):
        for closing in self:
            closing.latex_closing_qty = closing.latex_onhand_qty - closing.latex_wip_qty - closing.latex_outgoing_qty
            closing.latex_closing_value = closing.latex_onhand_value - closing.latex_wip_value - closing.latex_outgoing_value
            closing.lump_closing_qty = closing.lump_onhand_qty - closing.lump_wip_qty - closing.lump_outgoing_qty
            closing.lump_closing_value = closing.lump_onhand_value - closing.lump_wip_value - closing.lump_outgoing_value    

    def compute_initial_and_cost_rm(self):
        closing_journal = self.env.ref('ny_closing.plantation_closing_plantation')
        for closing in self:
            # Get All Incoming Qty from NAP
            product_latex = self.env['product.product'].search([('name','=','Latex')], limit=1)
            closing.latex_product_id = product_latex.id
            latex_in = self.env['lhm.nap.line'].search([('product_id','=',product_latex.id),
                            ('lhm_nap_id.date_nap','>=',closing.date_from),
                            ('lhm_nap_id.date_nap','<=',closing.date_to),
                            ('lhm_nap_id.state','in',['confirmed','done'])])
            closing.latex_incoming_qty = sum(latex_in.mapped('qty_nap')) if latex_in else 0.0  
            # lhm_transaction_nap_id
            product_lump = self.env['product.product'].search([('name','=','Lump')], limit=1)
            closing.lump_product_id = product_latex.id
            lump_in = self.env['lhm.nap.line'].search([('product_id','=',product_lump.id),
                            ('lhm_nap_id.date_nap','>=',closing.date_from),
                            ('lhm_nap_id.date_nap','<=',closing.date_to),
                            ('lhm_nap_id.state','in',['confirmed','done'])])
            closing.lump_incoming_qty = sum(lump_in.mapped('qty_nap')) if latex_in else 0.0  
            
            # Get Plantation Cost
            varieties = self.env['plant.varieties'].search([('name','=','Karet')], limit=1)
            domain_plantation = [('parent_state','=','posted'),
                ('date','>=',closing.date_from),('date','<=',closing.date_to),
                ('plantation_varieties_id.name','=','Karet'),
                ('plantation_location_type_id.plantation','=',True),
                ('plantation_location_id','!=',False),
                ('journal_id','=',closing_journal.id),
                # ('plantation_activity_id','!=',False),
                ]
            if varieties:
                activities = self.env['lhm.activity']
                activities |= varieties.harvest_activity_id
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
                        }
                    })
                plantation_cost_grouped[key]['total_cost'] += aml.balance
            # closing.plantation_cost = sum(plantation_cost.mapped('balance')) if plantation_cost else 0.0
            closing.plantation_cost_ids = [(0,0,vals) for vals in plantation_cost_grouped.values()]
            # Get All WIP Qty from Manufacture Order
            latex_wip = self.env['stock.move'].search([('product_id','=',product_latex.id),
                                ('workorder_id.state','in',['progress','done']),
                                ('workorder_id.production_id.state','=','progress')])
            lump_wip = self.env['stock.move'].search([('product_id','=',product_lump.id),
                                ('workorder_id.state','in',['progress','done']),
                                ('workorder_id.production_id.state','=','progress')])
            closing.latex_wip_qty = sum(latex_wip.mapped('product_uom_qty')) if latex_wip else 0.0
            closing.lump_wip_qty = sum(lump_wip.mapped('product_uom_qty')) if lump_wip else 0.0
            
            # Get All Outgoing QTy from Manufacture Order
            latex_out = self.env['stock.move'].search([('product_id','=',product_latex.id),
                                ('state','=','done'),
                                ('location_id.usage','=','internal'),
                                ('location_dest_id.usage','!=','internal'),
                                ('date','>=',closing.date_from.strftime('%Y-%m-%d 00:00:00')),
                                ('date','<=',closing.date_to.strftime('%Y-%m-%d 00:00:00'))])
            lump_out = self.env['stock.move'].search([('product_id','=',product_lump.id),
                                ('state','=','done'),
                                ('location_id.usage','=','internal'),
                                ('location_dest_id.usage','!=','internal'),
                                ('date','>=',closing.date_from.strftime('%Y-%m-%d 00:00:00')),
                                ('date','<=',closing.date_to.strftime('%Y-%m-%d 00:00:00'))])
            closing.latex_outgoing_qty = sum(latex_out.mapped('product_uom_qty')) if latex_out else 0.0
            closing.lump_outgoing_qty = sum(lump_out.mapped('product_uom_qty')) if lump_out else 0.0
        return True
    ############################### END VALUATION RAW MATERIAL ###################################

    #################################################################################################
    # Valuation of Finish Good 1 : Sheet and Compound
    # The product are only for Latex and Lump
    # Sheet
    sheet_product_id = fields.Many2one('product.product', string='Product Sheet', ondelete='restrict')
    sheet_inventory_account_id = fields.Many2one('account.account', 'Account Inventory Sheet')
    sheet_wip_account_id = fields.Many2one('account.account', 'Account WIP Sheet')
    sheet_consumption_account_id = fields.Many2one('account.account', 'Account Consumption Sheet')
    sheet_opening_qty = fields.Float(compute='_compute_opening_fg1', inverse='_invrs_opening_fg1', readonly=False, store=True, string='Opening Qty of Sheet')
    sheet_opening_qty_manual = fields.Float()
    sheet_opening_value = fields.Float(compute='_compute_opening_fg1', inverse='_invrs_opening_fg1', readonly=False, store=True, string='Opening Value of Sheet')
    sheet_opening_value_manual = fields.Float()
    sheet_incoming_qty = fields.Float(string='Incoming Qty of Sheet')
    pct_cost_for_sheet = fields.Float('% Cost for Sheet', default=90)
    sheet_manufacturing_cost = fields.Float(compute='_compute_mrp_cost_distribution', store=True, string='Manufacturing Cost of Sheet')
    sheet_raw_material_cost = fields.Float(string='Raw Material Cost of Sheet')
    sheet_production_cost = fields.Float(compute='_compute_mrp_cost_distribution', store=True, string='Production Cost of Sheet')
    sheet_onhand_qty = fields.Float(compute='_compute_onhand_and_cost_price_fg1', store=True, string='Onhand Qty of Sheet')
    sheet_onhand_value = fields.Float(compute='_compute_onhand_and_cost_price_fg1', store=True, string='Onhand Value of Sheet')
    sheet_new_cost_price = fields.Float(compute='_compute_onhand_and_cost_price_fg1', store=True, string='New Cost Price of Sheet')
    sheet_wip_qty = fields.Float(string='Sheet on Work in Process')
    sheet_wip_value = fields.Float(compute='_compute_outgoing_value_fg1', store=True, string='Sheet Value on Work in Process')
    sheet_outgoing_qty = fields.Float(string='Consumed Qty of Sheet')
    sheet_outgoing_value = fields.Float(compute='_compute_outgoing_value_fg1', store=True, string='Consumed Value of Sheet')
    sheet_closing_qty = fields.Float(compute='_compute_closing_fg1', store=True, string='Closing Qty of Sheet')
    sheet_closing_value = fields.Float(compute='_compute_closing_fg1', store=True, string='Closing Value of Sheet')
    # Compound
    compound_product_id = fields.Many2one('product.product', string='Product Compound', ondelete='restrict')
    compound_opening_qty = fields.Float(compute='_compute_opening_fg1', inverse='_invrs_opening_fg1', readonly=False, store=True, string='Opening Qty of Compound')
    compound_opening_qty_manual = fields.Float(string='Opening Qty of Compound')
    compound_opening_value = fields.Float(compute='_compute_opening_fg1', inverse='_invrs_opening_fg1', readonly=False, store=True, string='Opening Value of Compound')
    compound_opening_value_manual = fields.Float(string='Opening Value of Compound')
    pct_cost_for_compound = fields.Float('% Cost for Compound', default=10)
    compound_manufacturing_cost = fields.Float(compute='_compute_mrp_cost_distribution', store=True, string='Manufacturing Cost of Compound')
    compound_raw_material_cost = fields.Float(string='Raw Material Cost of Compound')
    compound_production_cost = fields.Float(compute='_compute_mrp_cost_distribution', store=True, string='Production Cost of Compound')
    compound_incoming_qty = fields.Float(string='Incoming Qty of Compound')
    compound_onhand_qty = fields.Float(compute='_compute_onhand_and_cost_price_fg1', store=True, string='Onhand Qty of Compound')
    compound_onhand_value = fields.Float(compute='_compute_onhand_and_cost_price_fg1', store=True, string='Onhand Value of Compound')
    compound_new_cost_price = fields.Float(compute='_compute_onhand_and_cost_price_fg1', store=True, string='New Cost Price of Compound')
    # compound_wip_qty = fields.Float(string='Compound on Work in Process')
    # compound_wip_value = fields.Float(compute='_compute_outgoing_value_fg1', store=True, string='Compound Value on Work in Process')
    compound_outgoing_qty = fields.Float(string='Delivered Qty of Compound')
    compound_outgoing_value = fields.Float(compute='_compute_outgoing_value_fg1', store=True, string ='Consumed Value of Compound')
    compound_closing_qty = fields.Float(compute='_compute_closing_fg1', store=True, string='Closing Qty of Compound')
    compound_closing_value = fields.Float(compute='_compute_closing_fg1', store=True, string='Closing Value of Compound')

    ############ COMPUTED METHOD ###########
    @api.depends('prev_closing_id')
    def _compute_opening_fg1(self):
        for closing in self:
            closing.sheet_opening_qty = closing.prev_closing_id.sheet_closing_qty if closing.prev_closing_id else closing.sheet_opening_qty_manual
            closing.sheet_opening_value = closing.prev_closing_id.sheet_closing_value if closing.prev_closing_id else closing.sheet_opening_value_manual
            closing.compound_opening_qty = closing.prev_closing_id.compound_closing_qty if closing.prev_closing_id else closing.compound_opening_qty_manual
            closing.compound_opening_value = closing.prev_closing_id.compound_closing_value if closing.prev_closing_id else closing.compound_opening_value_manual

    @api.onchange('sheet_opening_qty', 'sheet_opening_value',
            'compound_opening_qty', 'compound_opening_value')
    def _invrs_opening_fg1(self):
        for closing in self:
            closing.sheet_opening_qty_manual = closing.sheet_opening_qty
            closing.sheet_opening_qty_manual = closing.sheet_opening_value
            closing.compound_opening_qty_manual = closing.compound_opening_qty
            closing.compound_opening_qty_manual = closing.compound_opening_value

    @api.depends('manufacturing_cost', 'pct_cost_for_sheet', 'pct_cost_for_compound',
            'sheet_raw_material_cost',)
    def _compute_mrp_cost_distribution(self):
        for closing in self:
            closing.sheet_manufacturing_cost = (closing.manufacturing_cost * closing.pct_cost_for_sheet / 100.0)
            closing.compound_manufacturing_cost = closing.manufacturing_cost * closing.pct_cost_for_compound / 100.0
            closing.sheet_production_cost = closing.sheet_manufacturing_cost + closing.sheet_raw_material_cost
            closing.compound_production_cost = closing.compound_manufacturing_cost + closing.compound_raw_material_cost
    
    @api.depends('sheet_opening_qty', 'sheet_opening_value', 
            'sheet_incoming_qty', 'sheet_production_cost',
            'compound_opening_qty', 'compound_opening_value', 
            'compound_incoming_qty', 'compound_production_cost')
    def _compute_onhand_and_cost_price_fg1(self):
        for closing in self:
            closing.sheet_onhand_qty = closing.sheet_opening_qty + closing.sheet_incoming_qty
            closing.sheet_onhand_value = closing.sheet_opening_value + closing.sheet_production_cost
            closing.sheet_new_cost_price = closing.sheet_onhand_value/closing.sheet_onhand_qty if closing.sheet_onhand_qty else 0.0
            closing.compound_onhand_qty = closing.compound_opening_qty + closing.compound_incoming_qty
            closing.compound_onhand_value = closing.compound_opening_value + closing.compound_production_cost
            closing.compound_new_cost_price = closing.compound_onhand_value/closing.compound_onhand_qty if closing.compound_onhand_qty else 0.0

    # 'compound_wip_qty', 
    @api.depends('sheet_new_cost_price', 'sheet_wip_qty', 'sheet_outgoing_qty',
            'compound_new_cost_price', 'compound_outgoing_qty')
    def _compute_outgoing_value_fg1(self):
        for closing in self:
            closing.sheet_wip_value = closing.sheet_wip_qty * closing.sheet_new_cost_price
            closing.sheet_outgoing_value = closing.sheet_outgoing_qty * closing.sheet_new_cost_price
            # closing.compound_wip_value = closing.compound_wip_qty * closing.compound_new_cost_price
            closing.compound_outgoing_value = closing.compound_outgoing_qty * closing.compound_new_cost_price

    # 'compound_wip_qty', 'compound_wip_value', 
    @api.depends('sheet_onhand_qty', 'sheet_onhand_value', 
            'sheet_wip_qty', 'sheet_wip_value', 
            'sheet_outgoing_qty', 'sheet_outgoing_value',
            'compound_onhand_qty', 'compound_onhand_value', 
            'compound_outgoing_qty', 'compound_outgoing_value')
    def _compute_closing_fg1(self):
        for closing in self:
            closing.sheet_closing_qty = closing.sheet_onhand_qty - closing.sheet_wip_qty - closing.sheet_outgoing_qty
            closing.sheet_closing_value = closing.sheet_onhand_value - closing.sheet_wip_value - closing.sheet_outgoing_value
            # closing.compound_closing_qty = closing.compound_onhand_qty - closing.compound_wip_qty - closing.compound_outgoing_qty
            closing.compound_closing_qty = closing.compound_onhand_qty - closing.compound_outgoing_qty
            # closing.compound_closing_value = closing.compound_onhand_value - closing.compound_wip_value - closing.compound_outgoing_value
            closing.compound_closing_value = closing.compound_onhand_value - closing.compound_outgoing_value
    
    def compute_initial_and_cost_fg1(self):
        for closing in self:
            # Get All Incoming Qty from Stock Move
            product_sheet = self.env['product.product'].search([('name','=','Sheet')], limit=1)
            closing.sheet_product_id = product_sheet.id
            sheet_in = self.env['stock.move'].search([('product_id','=',product_sheet.id),
                            ('state','=','done'),
                            ('location_id.usage','!=','internal'),
                            ('location_dest_id.usage','=','internal'),
                            ('date','>=',closing.date_from.strftime('%Y-%m-%d 00:00:00')),
                            ('date','<=',closing.date_to.strftime('%Y-%m-%d 00:00:00'))])
            closing.sheet_incoming_qty = sum(sheet_in.mapped('product_uom_qty')) if sheet_in else 0.0  
            
            product_compound = self.env['product.product'].search([('name','=','Compound')], limit=1)
            closing.compound_product_id = product_compound.id
            compound_in = self.env['stock.move'].search([('product_id','=',product_compound.id),
                            ('state','=','done'),
                            ('location_id.usage','!=','internal'),
                            ('location_dest_id.usage','=','internal'),
                            ('date','>=',closing.date_from.strftime('%Y-%m-%d 00:00:00')),
                            ('date','<=',closing.date_to.strftime('%Y-%m-%d 00:00:00'))])
            closing.compound_incoming_qty = sum(compound_in.mapped('product_uom_qty')) if compound_in else 0.0  
            
            # Get Manufacturing Cost
            # manufacturing_cost_account_ids = []
            # mill_cost
            # raw_mat_cost
            closing_journal = self.env.ref('ny_closing.plantation_closing_production')
            manufacturing_cost = self.env['account.move.line'].search([('parent_state','=','posted'),
                ('date','>=',closing.date_from),('date','<=',closing.date_to),
                # ('plantation_location_type_id.station','=',True),
                # ('plantation_location_id','!=',False),
                # ('plantation_activity_id','!=',False),
                ('account_id','in',closing.manufacturing_cost_account_ids.ids),
                ('journal_id','!=',closing_journal.id)
                ])
            closing.manufacturing_cost = sum(manufacturing_cost.mapped('balance')) if manufacturing_cost else 0.0
            closing.sheet_raw_material_cost = closing.latex_outgoing_value
            closing.compound_raw_material_cost = closing.lump_outgoing_value

            # Get All WIP Qty from Manufacture Order
            sheet_wip = self.env['stock.move'].search([('product_id','=',product_sheet.id),
                            ('workorder_id.state','in',['progress','done']),
                            ('workorder_id.production_id.state','=','progress')])
            closing.sheet_wip_qty = sum(sheet_wip.mapped('product_uom_qty')) if sheet_wip else 0.0
            
            # Get All Outgoing Qty from Stock Move
            sheet_out = self.env['stock.move'].search([('product_id','=',product_sheet.id),
                            ('state','=','done'),
                            ('location_id.usage','=','internal'),
                            ('location_dest_id.usage','!=','internal'),
                            ('date','>=',closing.date_from.strftime('%Y-%m-%d 00:00:00')),
                            ('date','<=',closing.date_to.strftime('%Y-%m-%d 00:00:00'))])
            closing.sheet_outgoing_qty = sum(sheet_out.mapped('product_uom_qty')) if sheet_out else 0.0
            compound_out = self.env['stock.move'].search([('product_id','=',product_compound.id),
                            ('state','=','done'),
                            ('location_id.usage','=','internal'),
                            ('location_dest_id.usage','=','customer'),
                            ('date','>=',closing.date_from.strftime('%Y-%m-%d 00:00:00')),
                            ('date','<=',closing.date_to.strftime('%Y-%m-%d 00:00:00'))])
            closing.compound_outgoing_qty = sum(compound_out.mapped('product_uom_qty')) if compound_out else 0.0
        return True
    ############################### END VALUATION FINISH GOOD 1 ###################################
    
    ############################# BEGIN VALUATION FINISH GOOD 2 ###################################
    # Valuation of Finish Good 2 : RSS1, RSS3, Cutting, Compo
    
    fg2_valuation_ids = fields.One2many('closing.production.finishgood', 'closing_id', string='Finish Goods Valuation')

    def compute_initial_and_cost_fg2(self):
        for closing in self:
            closing.fg2_valuation_ids.unlink()

            # Manufactured Product : RSS 1, RSS 3, Cutting
            mrp_products = self.env['product.product'].search([('name','in',('RSS 1', 'RSS 3', 'Cutting'))])
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
                                ('date','<=',closing.date_to.strftime('%Y-%m-%d 00:00:00'))
                                ])
                produced_qty = sum(production_moves.mapped('product_uom_qty')) if production_moves else 0.0
                total_produced += produced_qty
                # Find Delivery/Sales
                outgoing_moves = self.env['stock.move'].search([('product_id','=',product.id),('state','=','done'),
                                ('location_id.usage','=','internal'),('location_dest_id.usage','!=','internal'),
                                ('date','>=',closing.date_from.strftime('%Y-%m-%d 00:00:00')),
                                ('date','<=',closing.date_to.strftime('%Y-%m-%d 00:00:00'))
                                ])
                outgoing_qty = sum(outgoing_moves.mapped('product_uom_qty')) if outgoing_moves else 0.0
                values_to_create = {
                    'product_id': product.id,
                    'prev_closing_fg_id': prev_closing_fg.id if prev_closing_fg else False,
                    'opening_qty': prev_closing_fg.closing_qty if prev_closing_fg else 0.0,
                    'opening_value': prev_closing_fg.closing_value if prev_closing_fg else 0.0,
                    'incoming_qty': produced_qty,
                    'manufacturing_cost': 0.0,
                    'outgoing_qty': outgoing_qty,
                }
                if prev_closing_fg:
                    values_to_create.update({
                        'inventory_account_id': prev_closing_fg.inventory_account_id.id if prev_closing_fg.inventory_account_id else False,
                        'cogs_account_id': prev_closing_fg.cogs_account_id.id if prev_closing_fg.cogs_account_id else False,
                    })
                to_create.append(values_to_create)
            # Fill in manufacturing Cost proporsionally
            for exvals in to_create:
                exvals['manufacturing_cost'] = (exvals['incoming_qty'] / total_produced if total_produced else 0.0) * closing.sheet_outgoing_value

            # Finish Good : Compound
            prev_closing_fg_compo = False
            if closing.prev_closing_id:
                for line in closing.prev_closing_id.fg2_valuation_ids:
                    if line.product_id.id==closing.compound_product_id.id:
                        prev_closing_fg_compo = line
            values_to_create_compo = {
                'product_id': closing.compound_product_id.id,
                'prev_closing_fg_id': prev_closing_fg_compo.id if prev_closing_fg_compo else False,
                'opening_qty': closing.compound_opening_qty,
                'opening_qty_manual': closing.compound_opening_qty,
                'opening_value': closing.compound_opening_value,
                'opening_value_manual': closing.compound_opening_value,
                'incoming_qty': closing.compound_incoming_qty,
                'manufacturing_cost': closing.compound_manufacturing_cost,
                'outgoing_qty': closing.compound_outgoing_qty,
            }
            if prev_closing_fg_compo:
                values_to_create_compo.update({
                    'inventory_account_id': prev_closing_fg_compo.inventory_account_id.id if prev_closing_fg_compo.inventory_account_id else False,
                    'cogs_account_id': prev_closing_fg_compo.cogs_account_id.id if prev_closing_fg_compo.cogs_account_id else False,
                })
                to_create.append(values_to_create_compo)
            to_create.append(values_to_create_compo)

            # Other Plantation Product
            varieties = self.env['plant.varieties'].search([('name','!=','Karet')])
            closing_journal = self.env.ref('ny_closing.plantation_closing_plantation')
            for varietas in varieties:
                product = varietas.product_id
                if not product:
                    continue
                # Find Previous Valuation
                prev_closing_fg_plant = False
                if closing.prev_closing_id:
                    for line in closing.prev_closing_id.fg2_valuation_ids:
                        if line.product_id.id==product.id:
                            prev_closing_fg_plant = line
                # Find Plantation Cost based on Business Unit
                domain_plantation = [('parent_state','=','posted'),
                    ('date','>=',closing.date_from),('date','<=',closing.date_to),
                    ('plantation_varieties_id','=',varietas.id),
                    ('plantation_location_type_id.plantation','=',True),
                    ('plantation_location_id','!=',False),
                    ('journal_id','=',closing_journal.id),
                    # ('plantation_activity_id','!=',False),
                    ]
                activities = self.env['lhm.activity']
                activities |= varietas.harvest_activity_id
                activities |= varietas.upkeep_activity_ids
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
                            }
                        })
                    plantation_cost_grouped[key]['total_cost'] += aml.balance
                # closing.plantation_cost = sum(plantation_cost.mapped('balance')) if plantation_cost else 0.0
                plantation_cost_to_add = [(0,0,vals) for vals in plantation_cost_grouped.values()]

                # From NAP
                incoming_naps = self.env['lhm.nap.line'].search([('product_id','=',product.id),
                            ('lhm_nap_id.date_nap','>=',closing.date_from),
                            ('lhm_nap_id.date_nap','<=',closing.date_to),
                            ('lhm_nap_id.state','in',['confirmed','done'])])
                incoming_qty = sum(incoming_naps.mapped('qty_nap')) if incoming_naps else 0.0
                # Find Delivery/Sales
                outgoing_moves = self.env['stock.move'].search([('product_id','=',product.id),('state','=','done'),
                                ('location_id.usage','=','internal'),('location_dest_id.usage','!=','internal'),
                                ('date','>=',closing.date_from.strftime('%Y-%m-%d 00:00:00')),
                                ('date','<=',closing.date_to.strftime('%Y-%m-%d 00:00:00'))
                                ])
                outgoing_qty = sum(outgoing_moves.mapped('product_uom_qty')) if outgoing_moves else 0.0
                values_to_create = {
                    'product_id': product.id,
                    'prev_closing_fg_id': prev_closing_fg_plant.id if prev_closing_fg_plant else False,
                    'opening_qty': prev_closing_fg_plant.closing_qty if prev_closing_fg_plant else 0.0,
                    'opening_value': prev_closing_fg_plant.closing_value if prev_closing_fg_plant else 0.0,
                    'incoming_qty': incoming_qty,
                    'outgoing_qty': outgoing_qty,
                    'plantation_cost_ids': plantation_cost_to_add,
                }
                if prev_closing_fg_plant:
                    values_to_create.update({
                        'inventory_account_id': prev_closing_fg_plant.inventory_account_id.id if prev_closing_fg_plant.inventory_account_id else False,
                        'cogs_account_id': prev_closing_fg_plant.cogs_account_id.id if prev_closing_fg_plant.cogs_account_id else False,
                    })
                to_create.append(values_to_create)

            if to_create:
                closing.fg2_valuation_ids = list(map(lambda x: (0,0,x), to_create))
        return True
    ############################### END VALUATION FINISH GOOD 2 ###################################
    
    ###############################################################################################

    def button_start(self):
        for closing in self:
            # Linked to Last Opening Balance
            prev_closing = self.search([('state','=','done'),('date_to','<',closing.date_from)], order='date_from desc', limit=1)
            if prev_closing:
                closing.prev_closing_id = prev_closing.id
            #####
            closing.compute_initial_and_cost_rm()
            closing.write({'state': 'rm_valuation'})
        return True
    
    def button_continue_to_fg1(self):
        for closing in self:
            closing.compute_initial_and_cost_fg1()
            closing.write({'state': 'fg1_valuation'})
        return True
    
    def button_continue_to_fg2(self):
        for closing in self:
            closing.compute_initial_and_cost_fg2()
            closing.write({'state': 'fg2_valuation'})
        return True

    def button_continue_to_account_entry(self):
        for closing in self:
            closing.write({'state': 'account_entry'})
        return True

    def create_move_entries_rm(self):
        # Output untuk Latex dan Lump
        # 1. Journal Receiving (Plantation Cost > Inventory) 
        # 2. Journal Outgoing WIP (WIP > Inventory) 
        # 3. Journal Consumed (Raw Material Cost > Inventory) 
        # 4. Reverse Journal WIP diawal periode bulan depan (Inventory > WIP)
        self.ensure_one()
        misc_journal = self.env['account.journal'].search([('type','=','general')], limit=1)

        move_lines = []
        move_lines_reverse_wip = []
        # Latex
        if self.latex_wip_qty:
            vals_wip = {
                'name': 'Work in Progress Latex',
                'plantation_location_type_id': False,
                'plantation_location_id': False,
                'plantation_activity_id': False,
                'plantation_src_journal_id': False,
                'account_id': self.latex_wip_account_id.id,
                'product_id': self.latex_product_id.id,
                'debit': self.latex_wip_value if self.latex_wip_value>0 else 0.0,
                'credit': abs(self.latex_wip_value) if self.latex_wip_value<0 else 0.0,
            }
            vals_wip_src = vals_wip.copy()
            vals_wip_src.update({
                'account_id': self.latex_inventory_account_id.id,
                'debit': vals_wip['credit'],
                'credit': vals_wip['debit']
            })
            
            
            move_lines.extend([(0,0,vals_wip),(0,0,vals_wip_src)])
            
            vals_reverse_wip = vals_wip.copy()
            vals_reverse_wip.update({
                'name': f"Reverse: {vals_wip['name']}",
                'account_id': self.latex_inventory_account_id.id,
            })
            vals_reverse_wip_dest = vals_wip_src.copy()
            vals_reverse_wip_dest.update({
                'name': f"Reverse: {vals_wip_src['name']}",
                'account_id': self.latex_wip_account_id.id,
            })
            move_lines_reverse_wip.extend([(0,0,vals_reverse_wip_dest),(0,0,vals_reverse_wip)])
        
        if self.latex_incoming_qty:
            vals_dest = {
                'name': 'Inventory Receipt and Revaluation',
                'plantation_location_type_id': False,
                'plantation_location_id': False,
                'plantation_activity_id': False,
                'plantation_src_journal_id': False,
                'account_id': self.latex_inventory_account_id.id,
                'debit': self.latex_plantation_cost if self.latex_plantation_cost>0 else 0.0,
                'credit': abs(self.latex_plantation_cost) if self.latex_plantation_cost<0 else 0.0,
            }
            move_lines.append((0,0,vals_dest))
            
            for ll in self.plantation_cost_ids:
                vals_src = {
                    'name': 'Move Cost to Inventory Latex',
                    'plantation_location_type_id': ll.plantation_location_type_id.id,
                    'plantation_location_id': ll.plantation_location_id.id,
                    'plantation_activity_id': ll.plantation_activity_id.id,
                    'plantation_src_journal_id': ll.plantation_src_journal_id.id,
                    'account_id': ll.account_id.id,
                    'debit': abs(ll.total_cost_latex) if ll.total_cost_latex<0 else 0.0,
                    'credit': ll.total_cost_latex if ll.total_cost_latex>0 else 0.0,
                }
                
                move_lines.append((0,0,vals_src))
        
        if self.latex_outgoing_qty:
            vals_src = {
                'name': 'Consumption Latex',
                'plantation_location_type_id': False,
                'plantation_location_id': False,
                'plantation_activity_id': False,
                'plantation_src_journal_id': False,
                'account_id': self.latex_consumption_account_id.id,
                'product_id': self.latex_product_id.id,
                'debit': self.latex_outgoing_value if self.latex_outgoing_value>0 else 0.0,
                'credit': abs(self.latex_outgoing_value) if self.latex_outgoing_value<0 else 0.0,
            }
            vals_dest = vals_src.copy()
            vals_dest.update({
                'account_id': self.latex_inventory_account_id.id,
                'debit': vals_src['credit'],
                'credit': vals_src['debit'],
            })
            
            
            move_lines.extend([(0,0,vals_src),(0,0,vals_dest)])
        
        # Lump
        if self.lump_wip_qty:
            vals_wip = {
                'name': 'Work in Progress Latex',
                'plantation_location_type_id': False,
                'plantation_location_id': False,
                'plantation_activity_id': False,
                'plantation_src_journal_id': False,
                'account_id': self.lump_wip_account_id.id,
                'product_id': self.lump_product_id.id,
                'debit': self.lump_wip_value if self.lump_wip_value>0 else 0.0,
                'credit': abs(self.lump_wip_value) if self.lump_wip_value<0 else 0.0,
            }
            vals_wip_src = vals_wip.copy()
            vals_wip_src.update({
                'account_id': self.lump_inventory_account_id.id,
                'debit': vals_wip['credit'],
                'credit': vals_wip['debit']
            })
            move_lines.extend([(0,0,vals_wip),(0,0,vals_wip_src)])
            
            vals_reverse_wip = vals_wip.copy()
            vals_reverse_wip.update({
                'name': f"Reverse: {vals_wip['name']}",
                'account_id': self.lump_inventory_account_id.id,
            })
            vals_reverse_wip_dest = vals_wip_src.copy()
            vals_reverse_wip_dest.update({
                'name': f"Reverse: {vals_wip_src['name']}",
                'account_id': self.lump_wip_account_id.id,
            })
            move_lines_reverse_wip.extend([(0,0,vals_reverse_wip_dest),(0,0,vals_reverse_wip)])
        
        if self.lump_incoming_qty:
            vals_dest = {
                'name': 'Inventory Receipt and Revaluation',
                'plantation_location_type_id': False,
                'plantation_location_id': False,
                'plantation_activity_id': False,
                'plantation_src_journal_id': False,
                'account_id': self.lump_inventory_account_id.id,
                'debit': self.lump_plantation_cost if self.lump_plantation_cost>0 else 0.0,
                'credit': abs(self.lump_plantation_cost) if self.lump_plantation_cost<0 else 0.0,
            }
            move_lines.append((0,0,vals_dest))
            for ll in self.plantation_cost_ids:
                vals_src = {
                    'name': 'Move Cost to Inventory Lump',
                    'plantation_location_type_id': ll.plantation_location_type_id.id,
                    'plantation_location_id': ll.plantation_location_id.id,
                    'plantation_activity_id': ll.plantation_activity_id.id,
                    'plantation_src_journal_id': ll.plantation_src_journal_id.id,
                    'account_id': ll.account_id.id,
                    'debit': abs(ll.total_cost_lump) if ll.total_cost_lump<0 else 0.0,
                    'credit': ll.total_cost_lump if ll.total_cost_lump>0 else 0.0,
                }
                move_lines.append((0,0,vals_src))
        
        if self.lump_outgoing_qty:
            vals_src = {
                'name': 'Consumption Latex',
                'plantation_location_type_id': False,
                'plantation_location_id': False,
                'plantation_activity_id': False,
                'plantation_src_journal_id': False,
                'account_id': self.lump_consumption_account_id.id,
                'product_id': self.lump_product_id.id,
                'debit': self.lump_outgoing_value if self.lump_outgoing_value>0 else 0.0,
                'credit': abs(self.lump_outgoing_value) if self.lump_outgoing_value<0 else 0.0,
            }
            vals_dest = vals_src.copy()
            vals_dest.update({
                'account_id': self.lump_inventory_account_id.id,
                'debit': vals_src['credit'],
                'credit': vals_src['debit'],
            })
            move_lines.extend([(0,0,vals_src),(0,0,vals_dest)])
        
        if move_lines:
            values = {
                'date': self.date_to,
                'journal_id': misc_journal.id,
                'move_type': 'entry',
                'line_ids': move_lines,
            }
            new_move = self.env['account.move'].create(values)
            self.closing_move_ids = [(4,new_move.id)]
        if move_lines_reverse_wip:
            values2 = {
                'date': self.date_from + relativedelta(months=1),
                'journal_id': misc_journal.id,
                'move_type': 'entry',
                'line_ids': move_lines_reverse_wip,
            }
            new_reverse_move = self.env['account.move'].create(values2)
            self.closing_move_ids = [(4,new_reverse_move.id)]

    def create_move_entries_fg1(self):
        # 1. Journal Receiving (Plantation Cost > Inventory) 
        # 2. Journal Outgoing WIP (WIP > Inventory) 
        # 3. Journal Consumed (Raw Material Cost > Inventory) 
        # 4. Reverse Journal WIP diawal periode bulan depan (Inventory > WIP)
        self.ensure_one()
        misc_journal = self.env['account.journal'].search([('type','=','general')], limit=1)

        move_lines = []
        move_lines_reverse_wip = []
        # Latex
        if self.sheet_wip_qty:
            vals_wip = {
                'name': 'Work in Progress Latex',
                'plantation_location_type_id': False,
                'plantation_location_id': False,
                'plantation_activity_id': False,
                'plantation_src_journal_id': False,
                'account_id': self.sheet_wip_account_id.id,
                'product_id': self.sheet_product_id.id,
                'debit': self.sheet_wip_value if self.sheet_wip_value>0 else 0.0,
                'credit': abs(self.sheet_wip_value) if self.sheet_wip_value<0 else 0.0,
            }
            
            vals_wip_src = vals_wip.copy()
            vals_wip_src.update({
                'account_id': self.sheet_inventory_account_id.id,
                'debit': vals_wip['credit'],
                'credit': vals_wip['debit']
            })
            
            move_lines.extend([(0,0,vals_wip),(0,0,vals_wip_src)])
            
            vals_reverse_wip = vals_wip.copy()
            vals_reverse_wip.update({
                'name': f"Reverse: {vals_wip['name']}",
                'account_id': self.sheet_inventory_account_id.id,
            })
            vals_reverse_wip_dest = vals_wip_src.copy()
            vals_reverse_wip_dest.update({
                'name': f"Reverse: {vals_wip_src['name']}",
                'account_id': self.sheet_wip_account_id.id,
            })
            move_lines_reverse_wip.extend([(0,0,vals_reverse_wip_dest),(0,0,vals_reverse_wip)])
        
        if self.sheet_incoming_qty:
            vals_dest = {
                'name': 'Sheet Produced',
                'plantation_location_type_id': False,
                'plantation_location_id': False,
                'plantation_activity_id': False,
                'plantation_src_journal_id': False,
                'account_id': self.sheet_inventory_account_id.id,
                'product_id': self.sheet_product_id.id,
                'debit': self.sheet_manufacturing_cost if self.sheet_manufacturing_cost>0 else 0.0,
                'credit': abs(self.sheet_manufacturing_cost) if self.sheet_manufacturing_cost<0 else 0.0,
            }
            move_lines.append((0,0,vals_dest))
            
            closing_journal = self.env.ref('ny_closing.plantation_closing_production')
            manufacturing_cost_moves = self.env['account.move.line'].search([('parent_state','=','posted'),
                ('date','>=',self.date_from),('date','<=',self.date_to),
                # ('plantation_location_type_id.station','=',True),
                # ('plantation_location_id','!=',False),
                # ('plantation_activity_id','!=',False),
                ('account_id','in',self.manufacturing_cost_account_ids.ids),
                ('journal_id','!=',closing_journal.id)
                ])
            grouped_cost = {}
            for aml in manufacturing_cost_moves:
                key = aml.account_id.id
                if key not in grouped_cost.keys():
                    grouped_cost.update({aml.account_id.id: {
                        'name': 'Cost for Sheet Production',
                        'account_id': aml.account_id.id,
                        'debit': 0.0,
                        'credit': 0.0,
                    }})
                grouped_cost[aml.account_id.id]['debit'] += (abs(aml.balance) if aml.balance<0 else 0.0)*self.pct_cost_for_sheet/100.0
                grouped_cost[aml.account_id.id]['credit'] += (aml.balance if aml.balance>0 else 0.0)*self.pct_cost_for_sheet/100.0
            for vals_src in grouped_cost.values():
                
                move_lines.append((0,0,vals_src))
        
        if self.sheet_outgoing_qty:
            vals_src = {
                'name': 'Consumption Sheet',
                'plantation_location_type_id': False,
                'plantation_location_id': False,
                'plantation_activity_id': False,
                'plantation_src_journal_id': False,
                'account_id': self.sheet_consumption_account_id.id,
                'product_id': self.sheet_product_id.id,
                'debit': self.sheet_outgoing_value if self.sheet_outgoing_value>0 else 0.0,
                'credit': abs(self.sheet_outgoing_value) if self.sheet_outgoing_value<0 else 0.0,
            }
            
            vals_dest = vals_src.copy()
            vals_dest.update({
                'account_id': self.sheet_inventory_account_id.id,
                'debit': vals_src['credit'],
                'credit': vals_src['debit'],
            })
            
            move_lines.extend([(0,0,vals_src),(0,0,vals_dest)])
        
        if move_lines:
            values = {
                'date': self.date_to,
                'journal_id': misc_journal.id,
                'move_type': 'entry',
                'line_ids': move_lines,
            }
            new_move = self.env['account.move'].create(values)
            self.closing_move_ids = [(4,new_move.id)]
        
        if move_lines_reverse_wip:
            values2 = {
                'date': self.date_from + relativedelta(months=1),
                'journal_id': misc_journal.id,
                'move_type': 'entry',
                'line_ids': move_lines_reverse_wip,
            }
            new_reverse_move = self.env['account.move'].create(values2)
            self.closing_move_ids = [(4,new_reverse_move.id)]
    
    def create_move_entries_fg2(self):
        self.ensure_one()
        misc_journal = self.env['account.journal'].search([('type','=','general')], limit=1)
        
        for line in self.fg2_valuation_ids:
            if not line.inventory_account_id:
                raise ValidationError(f"Silahkan isi akun Inventory valuation untuk Product {line.product_id.name}")
            if not line.cogs_account_id:
                raise ValidationError(f"Silahkan isi akun COGS untuk Product {line.product_id.name}")
            # 1. Journal Receiving (Plantation/Manufacturing Cost > Inventory) 
            # 2. Journal Cost of Goods Sold (COGS > Inventory) 
            move_lines = []
            move_lines_reverse_wip = []
            # Latex
            if line.incoming_qty:
                vals_dest = {
                    'name': f"{line.product_id.name} Produced",
                    'plantation_location_type_id': False,
                    'plantation_location_id': False,
                    'plantation_activity_id': False,
                    'plantation_src_journal_id': False,
                    'account_id': line.inventory_account_id.id,
                    'product_id': line.product_id.id,
                    'debit': (line.manufacturing_cost + line.plantation_cost) if (line.manufacturing_cost + line.plantation_cost)>0 else 0.0,
                    'credit': abs(line.manufacturing_cost + line.plantation_cost) if (line.manufacturing_cost + line.plantation_cost)<0 else 0.0,
                }
                print('................vals_dest', line.product_id.name, vals_dest['debit'], vals_dest['credit'])
                move_lines.append((0,0,vals_dest))
                
                # Konsumsi Raw Material. Jika produknya adalah barang plantation, 
                # idealnya journalnya adalah dari proses Closing Plantation
                if line.plantation_cost_ids:
                    for ll in line.plantation_cost_ids:
                        vals_src = {
                            'name': 'Move Cost to Inventory {line.product_id.name}',
                            'plantation_location_type_id': ll.plantation_location_type_id.id,
                            'plantation_location_id': ll.plantation_location_id.id,
                            'plantation_activity_id': ll.plantation_activity_id.id,
                            'plantation_src_journal_id': ll.plantation_src_journal_id.id,
                            'account_id': ll.account_id.id,
                            'debit': abs(ll.total_cost) if ll.total_cost<0 else 0.0,
                            'credit': ll.total_cost if ll.total_cost>0 else 0.0,
                        }
                        print('................vals_src', line.product_id.name, vals_src['debit'], vals_src['credit'])
                        move_lines.append((0,0,vals_src))
                elif line.product_id.name=='Compound':
                    closing_journal = self.env.ref('ny_closing.plantation_closing_production')
                    manufacturing_cost_moves = self.env['account.move.line'].search([('parent_state','=','posted'),
                        ('date','>=',line.closing_id.date_from),('date','<=',line.closing_id.date_to),
                        # ('plantation_location_type_id.station','=',True),
                        # ('plantation_location_id','!=',False),
                        # ('plantation_activity_id','!=',False),
                        ('account_id','in',line.closing_id.manufacturing_cost_account_ids.ids),
                        ('journal_id','!=',closing_journal.id)
                        ])
                    grouped_cost = {}
                    for aml in manufacturing_cost_moves:
                        key = aml.account_id.id
                        if key not in grouped_cost.keys():
                            grouped_cost.update({aml.account_id.id: {
                                'name': 'Cost for Sheet Production',
                                'account_id': aml.account_id.id,
                                'debit': 0.0,
                                'credit': 0.0,
                            }})
                        grouped_cost[aml.account_id.id]['debit'] += (abs(aml.balance) if aml.balance<0 else 0.0)*line.closing_id.pct_cost_for_compound/100.0
                        grouped_cost[aml.account_id.id]['credit'] += (aml.balance if aml.balance>0 else 0.0)*line.closing_id.pct_cost_for_compound/100.0
                    for vals_src in grouped_cost.values():
                        print('................vals_src', line.product_id.name, vals_src['debit'], vals_src['credit'])
                        move_lines.append((0,0,vals_src))
                else:
                    vals_src = vals_dest.copy()
                    vals_src.update({
                        'name': f"Raw Material Consumed",
                        'account_id': line.closing_id.sheet_consumption_account_id.id,
                        'debit': vals_dest['credit'],
                        'credit': vals_dest['debit'],
                    })
                    move_lines.append((0,0,vals_src))
            
            if line.outgoing_qty:
                vals_src = {
                    'name': 'Cost of Goods Sold',
                    'plantation_location_type_id': False,
                    'plantation_location_id': False,
                    'plantation_activity_id': False,
                    'plantation_src_journal_id': False,
                    'account_id': line.cogs_account_id.id,
                    'product_id': line.product_id.id,
                    'debit': line.outgoing_value if line.outgoing_value>0 else 0.0,
                    'credit': abs(line.outgoing_value) if line.outgoing_value<0 else 0.0,
                }
                vals_dest = vals_src.copy()
                vals_dest.update({
                    'account_id': line.inventory_account_id.id,
                    'debit': vals_src['credit'],
                    'credit': vals_src['debit'],
                })
                move_lines.extend([(0,0,vals_src),(0,0,vals_dest)])
            
            if move_lines:
                values = {
                    'date': self.date_to,
                    'journal_id': misc_journal.id,
                    'move_type': 'entry',
                    'line_ids': move_lines,
                }
                new_move = self.env['account.move'].create(values)    
                line.closing_move_id = new_move.id

    def create_move_entries(self):
        for closing in self:
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

            closing.create_move_entries_rm()
            closing.create_move_entries_fg1()
            closing.create_move_entries_fg2()
        return True

    def action_done(self):
        for closing in self:
            closing.create_move_entries()
            closing.write({'state': 'done'})
        return True

    def button_back(self):
        for closing in self:
            if closing.state=='account_entry':
                closing.state='fg2_valuation'
            elif closing.state=='fg2_valuation':
                closing.state='fg1_valuation'
            elif closing.state=='fg1_valuation':
                closing.state='rm_valuation'
            elif closing.state=='rm_valuation':
                closing.state='start'
        return True
    
    def button_cancel(self):
        self.filtered(lambda x: x.state in ('start','rm_valuation','fg1_valuation','fg2_valuation')).write({'state':'cancel'})
        return True
    
    def button_set_new(self):
        self.filtered(lambda x: x.state=='cancel').write({'state':'start'})
        return True
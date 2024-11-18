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
    is_plantation_cost = fields.Boolean()
    is_manufacturing_cost = fields.Boolean()
    is_rm_sheet_cost = fields.Boolean()

    @api.depends('total_cost', 'closing_id', 'closing_fg_id', 
        'is_manufacturing_cost', 'is_rm_sheet_cost', 'is_plantation_cost',
        'closing_id.pct_cost_for_latex', 'closing_id.pct_cost_for_lump',
        'closing_id.pct_cost_for_sheet', 'closing_id.pct_cost_for_compound',
        )
    def _compute_cost(self):
        for l in self:
            if l.closing_id:
                if l.is_manufacturing_cost:
                    l.total_cost_latex = l.total_cost * l.closing_id.pct_cost_for_latex / 100.0
                    l.total_cost_lump = l.total_cost * l.closing_id.pct_cost_for_lump / 100.0
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
    varieties_type = fields.Selection([('karet','Karet'),('pisang','Pisang')], string='Varitas')
    date_from = fields.Date()
    date_to = fields.Date()
    state = fields.Selection([('start','Start'),
            ('rm_valuation','Raw Material'),
            ('fg_valuation','Finish Good'),
            ('account_entry','Jurnal Creation'),
            ('done','Done'),
            ('cancel','Cancelled')], string='Status', default='start')
    
    plantation_cost_ids = fields.One2many('closing.production.plantation.cost', 'closing_id', domain=[('is_plantation_cost','=',True)], string='Plantation Cost Summs')
    plantation_cost = fields.Float(compute='_compute_plantation_cost', store=True, string='Total Plantation Cost')

    closing_move_ids = fields.Many2many('account.move', 'closing_prod_acc_move_rel', string='Closing Entries')

    manufacturing_cost_account_ids = fields.Many2many('account.account', 'closing_prod_mrp_cost_account_rel', string='Manufacturing Cost Accounts')
    mrp_cost_ids = fields.One2many('closing.production.plantation.cost', 'closing_id', domain=[('is_manufacturing_cost','=',True)], string='Plantation Cost Summs')
    manufacturing_cost = fields.Float('Total Manufacturing Cost')
    ############################## BEGIN VALUATION RAW MATERIAL ##################################
    # The product are only for Latex and Lump
    ##############################
    # Latex
    latex_product_id = fields.Many2one('product.product', string='Product Latex', ondelete='restrict')
    latex_inventory_account_id = fields.Many2one('account.account', 'Account Inventory Latex')
    latex_wip_account_id = fields.Many2one('account.account', 'Account WIP Latex')
    latex_consumption_account_id = fields.Many2one('account.account', 'Account Consumption Latex')
    
    latex_opening_qty = fields.Float(compute='_compute_opening_rm', inverse='_invrs_opening_rm', readonly=False, store=True, string='Beginning Qty of Latex')
    latex_opening_qty_manual = fields.Float()
    latex_opening_value = fields.Float(compute='_compute_opening_rm', inverse='_invrs_opening_rm', readonly=False, store=True, string='Beginning Value of Latex')
    latex_opening_value_manual = fields.Float()
    latex_incoming_qty = fields.Float(string='Incoming Qty of Latex')
    
    pct_cost_for_latex = fields.Float('% Cost for Latex', default=90)
    latex_plantation_cost = fields.Float(compute='_compute_plantation_cost', store=True, string='Plantation Cost of Latex')
    latex_onhand_qty = fields.Float(compute='_compute_onhand_and_cost_price_rm', store=True, string='Onhand Qty of Latex')
    latex_onhand_value = fields.Float(compute='_compute_onhand_and_cost_price_rm', store=True, string='Onhand Value of Latex')
    latex_new_cost_price = fields.Float(compute='_compute_onhand_and_cost_price_rm', store=True, string='New Cost Price of Latex')
    
    # latex_wip_opening_qty = fields.Float(compute='_compute_opening_rm', inverse='_invrs_opening_rm', readonly=False, store=True, string='Beginning WIP Latex')
    latex_wip_opening_qty = fields.Float(string='Beginning WIP Latex')
    latex_wip_opening_qty_manual = fields.Float()
    latex_wip_opening_value = fields.Float(compute='_compute_opening_rm', inverse='_invrs_opening_rm', readonly=False, store=True, string='Beginning Value WIP Latex')
    latex_wip_opening_value_manual = fields.Float()
    latex_wip_value_manual = fields.Float()
    latex_wip_incoming_qty = fields.Float(string='New Prod. Order Sheet')
    latex_wip_incoming_value = fields.Float(compute='_compute_outgoing_value_rm', store=True, string='New Prod. Order Value Sheet')
    
    pct_cost_for_sheet = fields.Float('% Cost for Sheet', default=90)
    sheet_manufacturing_cost = fields.Float(compute='_compute_mrp_cost_distribution', store=True, string='Manufacturing Cost of Sheet')
    sheet_production_cost = fields.Float(compute='_compute_mrp_cost_distribution', store=True, string='Production Cost of Sheet')

    latex_wip_onhand_qty = fields.Float(compute='_compute_onhand_wip_rm', store=True, string='Current WIP Latex')
    latex_wip_onhand_value = fields.Float(compute='_compute_onhand_wip_rm', store=True, string='Current Value WIP Latex')
    latex_wip_cost_price = fields.Float(compute='_compute_onhand_wip_rm', store=True, string='Cost Price WIP Latex')
    latex_wip_outgoing_qty = fields.Float(string='Finished Process Sheet')
    sheet_raw_material_cost = fields.Float(string='Raw Material Cost of Sheet')
    
    latex_wip_outgoing_value = fields.Float(compute='_compute_closing_wip_value_rm', store=True, string='Finished Process Value Sheet')
    latex_wip_qty = fields.Float(compute='_compute_closing_wip_value_rm', store=True, string='Closing WIP Latex')
    latex_wip_value = fields.Float(compute='_compute_closing_wip_value_rm', store=True, string='Latex Value WIP Latex')

    # latex_outgoing_qty = fields.Float(string='Consumed Qty of Latex')
    # # latex_outgoing_value = fields.Float(compute='_compute_outgoing_value_rm', store=True, string='Consumed Value of Latex')
    latex_closing_qty = fields.Float(compute='_compute_closing_rm', store=True, string='Closing Qty of Latex')
    latex_closing_value = fields.Float(compute='_compute_closing_rm', store=True, string='Closing Value of Latex')
    ##############################
    # Lump
    lump_product_id = fields.Many2one('product.product', string='Product Lump', ondelete='restrict')
    lump_inventory_account_id = fields.Many2one('account.account', 'Account Inventory Lump')
    lump_wip_account_id = fields.Many2one('account.account', 'Account WIP Lump')
    lump_consumption_account_id = fields.Many2one('account.account', 'Account Consumption Lump')
    
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
    lump_wip_qty = fields.Float(compute='_compute_closing_wip_value_rm', store=True, string='Closing WIP Lump')
    lump_wip_value = fields.Float(compute='_compute_closing_wip_value_rm', store=True, string='Closing WIP Value Lump')
    
    # lump_outgoing_qty = fields.Float(string='Consumed Qty of Lump')
    # lump_outgoing_value = fields.Float(compute='_compute_outgoing_value_rm', store=True, string ='Consumed Value of Lump')
    
    lump_closing_qty = fields.Float(compute='_compute_closing_rm', store=True, string='Closing Qty of Lump')
    lump_closing_value = fields.Float(compute='_compute_closing_rm', store=True, string='Closing Value of Lump')

    # #################################################################################################
    # # Sheet
    sheet_product_id = fields.Many2one('product.product', string='Product Sheet', ondelete='restrict')
    sheet_wip_account_id = fields.Many2one('account.account', 'Account WIP Sheet')
    # # Compound
    compound_product_id = fields.Many2one('product.product', string='Product Sheet', ondelete='restrict')
    compound_wip_account_id = fields.Many2one('account.account', 'Account WIP Compo')
    
    fg2_valuation_ids = fields.One2many('closing.production.finishgood', 'closing_id', string='Finish Goods Valuation')

    ############################# PISANG ###########################
    # Pisang
    pisang_product_id = fields.Many2one('product.product', string='Product Pisang', ondelete='restrict')
    pisang_inventory_account_id = fields.Many2one('account.account', 'Account Inventory Pisang')
    pisang_wip_account_id = fields.Many2one('account.account', 'Account WIP Pisang')
    
    pisang_opening_qty = fields.Float(compute='_compute_opening_rm_pisang', inverse='_invrs_opening_rm_pisang', readonly=False, store=True, string='Beginning Qty of Pisang')
    pisang_opening_qty_manual = fields.Float()
    pisang_opening_value = fields.Float(compute='_compute_opening_rm_pisang', inverse='_invrs_opening_rm_pisang', readonly=False, store=True, string='Beginning Value of Pisang')
    pisang_opening_value_manual = fields.Float()
    pisang_incoming_qty = fields.Float(string='Incoming Qty of Pisang')
    # pisang_plantation_cost = fields.Float(compute='_compute_plantation_cost', store=True, string='Plantation Cost of Pisang')
    pisang_onhand_qty = fields.Float(compute='_compute_onhand_and_cost_price_rm_pisang', store=True, string='Onhand Qty of Pisang')
    pisang_onhand_value = fields.Float(compute='_compute_onhand_and_cost_price_rm_pisang', store=True, string='Onhand Value of Pisang')
    pisang_new_cost_price = fields.Float(compute='_compute_onhand_and_cost_price_rm_pisang', store=True, string='New Cost Price of Pisang')
    pisang_wip_opening_qty = fields.Float(string='Beginning WIP Pisang')
    pisang_wip_opening_qty_manual = fields.Float()
    pisang_wip_opening_value = fields.Float(compute='_compute_opening_rm_pisang', inverse='_invrs_opening_rm_pisang', readonly=False, store=True, string='Beginning Value WIP Pisang')
    pisang_wip_opening_value_manual = fields.Float()
    pisang_wip_value_manual = fields.Float()
    pisang_wip_incoming_qty = fields.Float(string='New Prod. Order Pisang')
    pisang_wip_incoming_value = fields.Float(compute='_compute_outgoing_value_rm_pisang', store=True, string='New Prod. Order Value Pisang')
    pisang_wip_onhand_qty = fields.Float(compute='_compute_onhand_wip_rm_pisang', store=True, string='Current WIP Pisang')
    pisang_wip_onhand_value = fields.Float(compute='_compute_onhand_wip_rm_pisang', store=True, string='Current Value WIP Pisang')
    pisang_wip_cost_price = fields.Float(compute='_compute_onhand_wip_rm_pisang', store=True, string='Cost Price WIP Pisang')
    pisang_wip_outgoing_qty = fields.Float(string='Finished Process Pisang')
    pisang_wip_outgoing_value = fields.Float(compute='_compute_closing_wip_value_rm_pisang', store=True, string='Finished Process Value Pisang')
    pisang_wip_qty = fields.Float(compute='_compute_closing_wip_value_rm_pisang', store=True, string='Closing WIP Pisang')
    pisang_wip_value = fields.Float(compute='_compute_closing_wip_value_rm_pisang', store=True, string='Pisang Value WIP Pisang')
    pisang_closing_qty = fields.Float(compute='_compute_closing_rm_pisang', store=True, string='Closing Qty of Pisang')
    pisang_closing_value = fields.Float(compute='_compute_closing_rm_pisang', store=True, string='Closing Value of Pisang')
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
        'mrp_cost_ids.total_cost_latex', 'mrp_cost_ids.total_cost_lump')
    def _compute_mrp_cost_distribution(self):
        for closing in self:
            closing.sheet_manufacturing_cost = sum(closing.mrp_cost_ids.mapped('total_cost_latex')) if closing.mrp_cost_ids else 0.0
            closing.compound_manufacturing_cost = sum(closing.mrp_cost_ids.mapped('total_cost_lump')) if closing.mrp_cost_ids else 0.0
            closing.sheet_production_cost = closing.sheet_manufacturing_cost
            closing.compound_production_cost = closing.compound_manufacturing_cost

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
            'sheet_production_cost', 'compound_production_cost')
    def _compute_onhand_wip_rm(self):
        for closing in self:
            closing.latex_wip_onhand_qty = closing.latex_wip_opening_qty + closing.latex_wip_incoming_qty
            closing.latex_wip_onhand_value = closing.latex_wip_opening_value + closing.latex_wip_incoming_value + closing.sheet_production_cost
            closing.latex_wip_cost_price = closing.latex_wip_onhand_value/closing.latex_wip_onhand_qty if closing.latex_wip_onhand_qty else 0.0
            closing.lump_wip_onhand_qty = closing.lump_wip_opening_qty + closing.lump_wip_incoming_qty
            closing.lump_wip_onhand_value = closing.lump_wip_opening_value + closing.lump_wip_incoming_value + closing.compound_production_cost
            closing.lump_wip_cost_price = closing.lump_wip_onhand_value/closing.lump_wip_onhand_qty if closing.lump_wip_onhand_qty else 0.0

    @api.depends('latex_wip_outgoing_qty', 'sheet_raw_material_cost', 
                'latex_wip_cost_price', 'latex_wip_onhand_qty',
                 'lump_wip_outgoing_qty', 'lump_wip_cost_price', 'lump_wip_onhand_qty')
    def _compute_closing_wip_value_rm(self):
        for closing in self:
            closing.latex_wip_outgoing_value = closing.latex_wip_outgoing_qty * closing.latex_wip_cost_price
            closing.latex_wip_qty = closing.latex_wip_onhand_qty - closing.latex_wip_outgoing_qty
            closing.latex_wip_value = closing.latex_wip_onhand_value - closing.latex_wip_outgoing_value
            closing.lump_wip_outgoing_value = closing.lump_wip_outgoing_qty * closing.lump_wip_cost_price
            closing.lump_wip_qty = closing.lump_wip_onhand_qty - closing.lump_wip_outgoing_qty
            closing.lump_wip_value = closing.lump_wip_onhand_value - closing.lump_wip_outgoing_value

    @api.depends('latex_onhand_qty', 'latex_onhand_value', 
            'latex_wip_incoming_qty', 'latex_wip_incoming_value',
            'lump_onhand_qty', 'lump_onhand_value', 
            'lump_wip_incoming_qty', 'lump_wip_incoming_value', 
            )
    def _compute_closing_rm(self):
        for closing in self:
            closing.latex_closing_qty = closing.latex_onhand_qty - closing.latex_wip_incoming_qty
            closing.latex_closing_value = closing.latex_onhand_value - closing.latex_wip_incoming_value
            closing.lump_closing_qty = closing.lump_onhand_qty - closing.lump_wip_incoming_qty
            closing.lump_closing_value = closing.lump_onhand_value - closing.lump_wip_incoming_value

    # PISANG
    @api.depends('prev_closing_id')
    def _compute_opening_rm_pisang(self):
        for closing in self:
            closing.pisang_opening_qty = closing.prev_closing_id.pisang_closing_qty if closing.prev_closing_id else closing.pisang_opening_qty_manual
            closing.pisang_opening_value = closing.prev_closing_id.pisang_closing_value if closing.prev_closing_id else closing.pisang_opening_value_manual
            closing.pisang_wip_opening_value = closing.prev_closing_id.pisang_wip_value if closing.prev_closing_id else closing.pisang_wip_opening_value_manual
    
    @api.onchange('pisang_opening_qty', 'pisang_opening_value',
            'pisang_wip_opening_value')
    def _invrs_opening_rm_pisang(self):
        for closing in self:
            closing.pisang_opening_qty_manual = closing.pisang_opening_qty
            closing.pisang_opening_value_manual = closing.pisang_opening_value
            closing.pisang_wip_opening_value_manual = closing.pisang_wip_opening_value
    
    @api.depends('pisang_opening_qty', 'pisang_opening_value', 
            'pisang_incoming_qty', 'plantation_cost')
    def _compute_onhand_and_cost_price_rm_pisang(self):
        for closing in self:
            closing.pisang_onhand_qty = closing.pisang_opening_qty + closing.pisang_incoming_qty
            closing.pisang_onhand_value = closing.pisang_opening_value + closing.plantation_cost
            closing.pisang_new_cost_price = closing.pisang_onhand_value/closing.pisang_onhand_qty if closing.pisang_onhand_qty else 0.0
    
    @api.depends('pisang_new_cost_price', 'pisang_wip_incoming_qty')
    def _compute_outgoing_value_rm_pisang(self):
        for closing in self:
            closing.pisang_wip_incoming_value = closing.pisang_wip_incoming_qty * closing.pisang_new_cost_price
    
    @api.depends('pisang_wip_opening_qty', 'pisang_wip_incoming_qty', 
            'pisang_wip_opening_value', 'pisang_wip_incoming_value',
            'manufacturing_cost')
    def _compute_onhand_wip_rm_pisang(self):
        for closing in self:
            closing.pisang_wip_onhand_qty = closing.pisang_wip_opening_qty + closing.pisang_wip_incoming_qty
            closing.pisang_wip_onhand_value = closing.pisang_wip_opening_value + closing.pisang_wip_incoming_value + closing.manufacturing_cost
            closing.pisang_wip_cost_price = closing.pisang_wip_onhand_value/closing.pisang_wip_onhand_qty if closing.pisang_wip_onhand_qty else 0.0
    
    @api.depends('pisang_wip_outgoing_qty', 'pisang_wip_cost_price', 
                 'pisang_wip_onhand_qty')
    def _compute_closing_wip_value_rm_pisang(self):
        for closing in self:
            closing.pisang_wip_outgoing_value = closing.pisang_wip_outgoing_qty * closing.pisang_wip_cost_price
            closing.pisang_wip_qty = closing.pisang_wip_onhand_qty - closing.pisang_wip_outgoing_qty
            closing.pisang_wip_value = closing.pisang_wip_onhand_value - closing.pisang_wip_outgoing_value

    @api.depends('pisang_onhand_qty', 'pisang_onhand_value', 
            'pisang_wip_incoming_qty', 'pisang_wip_incoming_value')
    def _compute_closing_rm_pisang(self):
        for closing in self:
            closing.pisang_closing_qty = closing.pisang_onhand_qty - closing.pisang_wip_incoming_qty
            closing.pisang_closing_value = closing.pisang_onhand_value - closing.pisang_wip_incoming_value
        
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
                        'is_plantation_cost': True,
                    }
                })
            plantation_cost_grouped[key]['total_cost'] += aml.balance
        return sum(plantation_cost.mapped('balance')) if plantation_cost else 0.0, [(0,0,vals) for vals in plantation_cost_grouped.values()]
    
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
            activities |= varieties.harvest_activity_id
            activities |= varieties.upkeep_activity_ids
            # activities |= varieties.general_charges_activity_ids
            # activities |= varieties.indirect_cost_activity_ids
            plantation_cost_account_ids = []
            if activities:
                plantation_cost_account_ids = activities.cost_account_id.ids
            if plantation_cost_account_ids:
                domain_plantation.append(('account_id','in',plantation_cost_account_ids))
        print("::::::::::::pisang", domain_plantation)
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
        return sum(plantation_cost.mapped('balance')) if plantation_cost else 0.0, [(0,0,vals) for vals in plantation_cost_grouped.values()]

    def _compute_manufacturing_cost(self):
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
        mrp = self.env['mrp.production'].search([('product_id','=',product.id),('state','=',['progress','done']),
                ('date_start','<', self.date_from.strftime('%Y-%m-%d 00:00:00')),
                '|',
                    ('date_finished','=', False),
                    ('date_finished','>=', self.date_from.strftime('%Y-%m-%d 00:00:00'))])
        return mrp

    def _get_mrp_done_this_month(self, product):
        self.ensure_one()
        mrp = self.env['mrp.production'].search([('product_id','=',product.id),('state','=','done'),
                ('date_finished','>=', self.date_from.strftime('%Y-%m-%d 00:00:00')),
                ('date_finished','<=', self.date_to.strftime('%Y-%m-%d 23:59:59'))])
        return mrp

    def _get_mrp_inprogress_this_month(self, product):
        self.ensure_one()
        mrp = self.env['mrp.production'].search([('product_id','=',product.id),('state','in',['progress','done']),
                ('date_start','>=', self.date_from.strftime('%Y-%m-%d 00:00:00'))])
        return mrp

    def _compute_rm_cost_sheet(self):
        self.ensure_one()
        mrp = self._get_mrp_done_this_month(self.sheet_product_id)
        rm_moves = mrp.move_raw_ids.filtered(lambda s: s.product_id.name not in ('Latex','Lump'))
        rm_cost = 0.0
        if rm_moves:
            print(">>>>>>>>>>>>>>", rm_moves)
            if len(rm_moves.ids)>1:
                svl_search = self.env['stock.valuation.layer'].search([('stock_move_id','in',rm_moves.ids)])
            else:
                svl_search = self.env['stock.valuation.layer'].search([('stock_move_id','=',rm_moves.id)])
            print(">>>>>>>>>>>>>>", svl_search)
            if svl_search:
                rm_cost = -1* sum(svl_search.mapped('value'))
        return rm_cost

    def action_compute_mrp_cost(self):
        for closing in self:
            if closing.mrp_cost_ids:
                closing.mrp_cost_ids.unlink()
            mrp_cost, summerize_mrp_cost = closing._compute_manufacturing_cost()
            closing.manufacturing_cost = mrp_cost
            closing.mrp_cost_ids = summerize_mrp_cost
    
    def action_compute_rm_cost_sheet(self):
        for closing in self:
            closing.sheet_raw_material_cost = closing._compute_rm_cost_sheet()

    def compute_initial_and_cost_rm_karet(self):
        for closing in self:
            sheet_product = self.env['product.product'].search([('name','=','Sheet')], limit=1)
            closing.sheet_product_id = sheet_product.id
            compound_product = self.env['product.product'].search([('name','=','Compo')], limit=1)
            closing.compound_product_id = compound_product.id
            
            plantation_cost, summerize_cost = closing._compute_plantation_cost_karet()
            print(">>>>>>>>>>>>>>>>>>>>plantation_cost", closing.plantation_cost_ids)
            if closing.plantation_cost_ids:
                closing.plantation_cost_ids.unlink()
            print(">>>>>>>>>>>>>>>>>>>>plantation_cost", plantation_cost)
            print(">>>>>>>>>>>>>>>>>>>>", summerize_cost)
            closing.plantation_cost = plantation_cost
            closing.plantation_cost_ids = summerize_cost
            mrp_cost, summerize_mrp_cost = closing._compute_manufacturing_cost()
            if closing.mrp_cost_ids:
                closing.mrp_cost_ids.unlink()
            print(">>>>>>>>>>>>>>>>>>>>mrp_cost", mrp_cost)
            print(">>>>>>>>>>>>>>>>>>>>", summerize_mrp_cost)
            closing.manufacturing_cost = mrp_cost
            closing.mrp_cost_ids = summerize_mrp_cost
            
            # Get Latex and Lump Receiving Qty from NAP
            product_latex = self.env['product.product'].search([('name','=','Latex')], limit=1)
            closing.latex_product_id = product_latex.id
            # latex_in = self.env['lhm.nap.line'].search([('product_id','=',product_latex.id),
            #                 ('lhm_nap_id.date_nap','>=',closing.date_from),
            #                 ('lhm_nap_id.date_nap','<=',closing.date_to),
            #                 ('lhm_nap_id.state','in',['confirmed','done'])])
            latex_in = self.env['timbangan.pabrik'].search([('product_id','=',product_latex.id),
                            ('lhm_nap_id.date_nap','>=',closing.date_from),
                            ('lhm_nap_id.date_nap','<=',closing.date_to),
                            ('lhm_nap_id.state','in',['confirmed','done'])])
            print(">>>>>>>>>>>>>>>>>>>>latex_in", sum(latex_in.mapped('product_qty')) if latex_in else 0.0)
            closing.latex_incoming_qty = sum(latex_in.mapped('product_qty')) if latex_in else 0.0
            
            product_lump = self.env['product.product'].search([('name','=','Lump')], limit=1)
            closing.lump_product_id = product_lump.id
            compound_in = self.env['timbangan.pabrik'].search([('product_id','=',product_lump.id),
                            ('lhm_nap_id.date_nap','>=',closing.date_from),
                            ('lhm_nap_id.date_nap','<=',closing.date_to),
                            ('lhm_nap_id.state','in',['confirmed','done'])])
            print(">>>>>>>>>>>>>>>>>>>>compound_in", sum(compound_in.mapped('product_qty')) if compound_in else 0.0)
            closing.lump_incoming_qty = sum(compound_in.mapped('product_qty')) if compound_in else 0.0
            
            # GET PENDING MO PREV MONTH
            mrp_sheet_prev = closing._get_mrp_inprogress_prev_month(sheet_product)
            print(">>>>>>>>>>>>>>>>>>>>mrp_sheet_prev", mrp_sheet_prev)
            if mrp_sheet_prev:
                rm_moves = mrp_sheet_prev.move_raw_ids.filtered(lambda s: s.product_id.id==product_latex.id)
                closing.latex_wip_opening_qty = sum(rm_moves.mapped('product_qty')) if rm_moves else 0.0
            mrp_compound_prev = closing._get_mrp_inprogress_prev_month(compound_product)
            print(">>>>>>>>>>>>>>>>>>>>mrp_compound_prev", mrp_compound_prev)
            if mrp_compound_prev:
                rm_moves = mrp_compound_prev.move_raw_ids.filtered(lambda s: s.product_id.id==product_lump.id)
                closing.lump_wip_opening_qty = sum(rm_moves.mapped('product_qty')) if rm_moves else 0.0
            
            # GET NEW MO THIS MONTH
            mrp_sheet = closing._get_mrp_inprogress_this_month(sheet_product)
            print(">>>>>>>>>>>>>>>>>>>>mrp_sheet", mrp_sheet)
            if mrp_sheet:
                rm_moves = mrp_sheet.move_raw_ids.filtered(lambda s: s.product_id.id==product_latex.id)
                closing.latex_wip_incoming_qty = sum(rm_moves.mapped('product_qty')) if rm_moves else 0.0
            mrp_compound = closing._get_mrp_inprogress_this_month(compound_product)
            print(">>>>>>>>>>>>>>>>>>>>mrp_compound", mrp_compound)
            if mrp_compound:
                rm_moves = mrp_compound.move_raw_ids.filtered(lambda s: s.product_id.id==product_lump.id)
                closing.lump_wip_incoming_qty = sum(rm_moves.mapped('product_qty')) if rm_moves else 0.0
            
            # GET MO DONE THIS MONTH
            mrp_sheet_done = closing._get_mrp_done_this_month(sheet_product)
            print(">>>>>>>>>>>>>>>>>>>>mrp_sheet_done", mrp_sheet_done)
            if mrp_sheet_done:
                rm_moves = mrp_sheet_done.move_raw_ids.filtered(lambda s: s.product_id.id==product_latex.id)
                closing.latex_wip_outgoing_qty = sum(rm_moves.mapped('product_qty')) if rm_moves else 0.0
            mrp_compound_done = closing._get_mrp_done_this_month(compound_product)
            print(">>>>>>>>>>>>>>>>>>>>mrp_compound_done", mrp_compound_done)
            if mrp_compound_done:
                rm_moves = mrp_compound_done.move_raw_ids.filtered(lambda s: s.product_id.id==product_lump.id)
                closing.lump_wip_outgoing_qty = sum(rm_moves.mapped('product_qty')) if rm_moves else 0.0
            
            closing.sheet_raw_material_cost = closing._compute_rm_cost_sheet()
        return True
    
    def compute_initial_and_cost_rm_pisang(self):
        for closing in self:
            plantation_cost, summerize_cost = closing._compute_plantation_cost_pisang()
            print(">>>>>>>>>>>>>>>>>>>>plantation_cost", closing.plantation_cost_ids)
            if closing.plantation_cost_ids:
                closing.plantation_cost_ids.unlink()
            print(">>>>>>>>>>>>>>>>>>>>plantation_cost", plantation_cost)
            print(">>>>>>>>>>>>>>>>>>>>", summerize_cost)
            closing.plantation_cost = plantation_cost
            closing.plantation_cost_ids = summerize_cost
            mrp_cost, summerize_mrp_cost = closing._compute_manufacturing_cost()
            if closing.mrp_cost_ids:
                closing.mrp_cost_ids.unlink()
            print(">>>>>>>>>>>>>>>>>>>>mrp_cost", mrp_cost)
            print(">>>>>>>>>>>>>>>>>>>>", summerize_mrp_cost)
            closing.manufacturing_cost = mrp_cost
            self.mrp_cost_ids = summerize_mrp_cost
            
            # Get Pisang Receiving Qty from NAP
            product_pisang = self.env['product.product'].search([('name','=','Pisang')], limit=1)
            closing.pisang_product_id = product_pisang.id
            pisang_in = self.env['timbangan.pabrik'].search([('product_id','=',product_pisang.id),
                            ('lhm_nap_id.date_nap','>=',closing.date_from),
                            ('lhm_nap_id.date_nap','<=',closing.date_to),
                            ('lhm_nap_id.state','in',['confirmed','done'])])
            print(">>>>>>>>>>>>>>>>>>>>pisang_in", sum(pisang_in.mapped('product_qty')) if pisang_in else 0.0)
            closing.pisang_incoming_qty = sum(pisang_in.mapped('product_qty')) if pisang_in else 0.0
            
            fg_pisang_product = self.env['product.product'].search([('name','=','Pisang X')], limit=1)
            # GET PENDING MO PREV MONTH
            mrp_pisang_prev = closing._get_mrp_inprogress_prev_month(fg_pisang_product)
            print(">>>>>>>>>>>>>>>>>>>>mrp_pisang_prev", mrp_pisang_prev)
            if mrp_pisang_prev:
                rm_moves = mrp_pisang_prev.move_raw_ids.filtered(lambda s: s.product_id.id==product_pisang.id)
                closing.pisang_wip_opening_qty = sum(rm_moves.mapped('product_qty')) if rm_moves else 0.0
            
            # GET NEW MO THIS MONTH
            mrp_pisang = closing._get_mrp_inprogress_this_month(fg_pisang_product)
            print(">>>>>>>>>>>>>>>>>>>>mrp_pisang", mrp_pisang)
            if mrp_pisang:
                rm_moves = mrp_pisang.move_raw_ids.filtered(lambda s: s.product_id.id==product_pisang.id)
                closing.pisang_wip_incoming_qty = sum(rm_moves.mapped('product_qty')) if rm_moves else 0.0
            
            # GET MO DONE THIS MONTH
            mrp_pisang_done = closing._get_mrp_done_this_month(fg_pisang_product)
            print(">>>>>>>>>>>>>>>>>>>>mrp_pisang_done", mrp_pisang_done)
            if mrp_pisang_done:
                rm_moves = mrp_pisang_done.move_raw_ids.filtered(lambda s: s.product_id.id==product_pisang.id)
                closing.pisang_wip_outgoing_qty = sum(rm_moves.mapped('product_qty')) if rm_moves else 0.0
            
            closing.sheet_raw_material_cost = closing._compute_rm_cost_sheet()
        return True
    
    ############################### END VALUATION RAW MATERIAL ###################################

    def compute_initial_and_cost_fg2(self):
        for closing in self:
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
                                ('location_id.usage','=','internal'),('location_dest_id.usage','!=','internal'),
                                ('date','>=',closing.date_from.strftime('%Y-%m-%d 00:00:00')),
                                ('date','<=',closing.date_to.strftime('%Y-%m-%d 23:59:59'))
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
                exvals['manufacturing_cost'] = (exvals['incoming_qty'] / total_produced if total_produced else 0.0) * (closing.latex_wip_outgoing_value + closing.sheet_raw_material_cost)

            # Finish Good : Compo
            # compound_product_id = self.env['product.product'].search([('name','=','Compo')])
            prev_closing_fg_compo = False
            if closing.prev_closing_id:
                for line in closing.prev_closing_id.fg2_valuation_ids:
                    if line.product_id.id==closing.compound_product_id.id:
                        prev_closing_fg_compo = line
            # Find Delivery/Sales
            outgoing_moves22 = self.env['stock.move'].search([('product_id','=',closing.compound_product_id.id),('state','=','done'),
                            ('location_id.usage','=','internal'),('location_dest_id.usage','!=','internal'),
                            ('date','>=',closing.date_from.strftime('%Y-%m-%d 00:00:00')),
                            ('date','<=',closing.date_to.strftime('%Y-%m-%d 23:59:59'))
                            ])
            outgoing_qty22 = sum(outgoing_moves22.mapped('product_uom_qty')) if outgoing_moves22 else 0.0
            values_to_create_compo = {
                'product_id': closing.compound_product_id.id,
                'prev_closing_fg_id': prev_closing_fg_compo.id if prev_closing_fg_compo else False,
                'opening_qty': prev_closing_fg_compo.closing_qty if prev_closing_fg_compo else 0.0,
                'opening_value': prev_closing_fg_compo.closing_value if prev_closing_fg_compo else 0.0,
                'incoming_qty': closing.lump_wip_outgoing_qty,
                'manufacturing_cost': closing.lump_wip_outgoing_value,
                'outgoing_qty': outgoing_qty22,
            }
            if prev_closing_fg_compo:
                values_to_create_compo.update({
                    'inventory_account_id': prev_closing_fg_compo.inventory_account_id.id if prev_closing_fg_compo.inventory_account_id else False,
                    'cogs_account_id': prev_closing_fg_compo.cogs_account_id.id if prev_closing_fg_compo.cogs_account_id else False,
                })
                to_create.append(values_to_create_compo)
            to_create.append(values_to_create_compo)

            # Other Plantation Product
            if to_create:
                closing.fg2_valuation_ids = list(map(lambda x: (0,0,x), to_create))
        return True
    
    def compute_initial_and_cost_fg_pisang(self):
        for closing in self:
            closing.fg2_valuation_ids.unlink()

            # Manufactured Product : RSS 1, RSS 3, Cutting
            mrp_products = self.env['product.product'].search([('name','like','Pisang')])
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
                                ('location_id.usage','=','internal'),('location_dest_id.usage','!=','internal'),
                                ('date','>=',closing.date_from.strftime('%Y-%m-%d 00:00:00')),
                                ('date','<=',closing.date_to.strftime('%Y-%m-%d 23:59:59'))
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
                exvals['manufacturing_cost'] = (exvals['incoming_qty'] / total_produced if total_produced else 0.0) * closing.pisang_wip_outgoing_value

            # Other Plantation Product
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
            if closing.varieties_type=='karet':
                closing.compute_initial_and_cost_rm_karet()
            elif closing.varieties_type=='pisang':
                closing.compute_initial_and_cost_rm_pisang()
            closing.write({'state': 'rm_valuation'})
        return True
    
    def button_continue_to_fg(self):
        for closing in self:
            if closing.varieties_type=='karet':
                closing.compute_initial_and_cost_fg2()
            elif closing.varieties_type=='pisang':
                closing.compute_initial_and_cost_fg_pisang()
            closing.write({'state': 'fg_valuation'})
        return True

    def button_continue_to_account_entry(self):
        for closing in self:
            closing.write({'state': 'account_entry'})
        return True

    def create_move_entries_rm(self):
        # Output untuk Latex dan Lump
        # 1. Journal Receiving (Plantation Cost > Inventory) 
        # 2. Journal Addition WIP (Inventory > WIP Latex/Lump) 
        # 3. Journal Finished Sheet (WIP Latex > WIP Sheet ) 
        self.ensure_one()
        misc_journal = self.env['account.journal'].search([('type','=','general')], limit=1)

        move_lines_receiving = []
        move_lines_wip = []
        # BEGIN: Receiving from NAP
        if self.latex_incoming_qty:
            vals_dest = {
                'name': 'Inventory Receipt and Valuation',
                'plantation_location_type_id': False,
                'plantation_location_id': False,
                'plantation_activity_id': False,
                'plantation_src_journal_id': False,
                'account_id': self.latex_inventory_account_id.id,
                'debit': self.latex_plantation_cost if self.latex_plantation_cost>0 else 0.0,
                'credit': abs(self.latex_plantation_cost) if self.latex_plantation_cost<0 else 0.0,
            }
            move_lines_receiving.append((0,0,vals_dest))
            
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
                move_lines_receiving.append((0,0,vals_src))
        
        if self.lump_incoming_qty:
            vals_dest = {
                'name': 'Inventory Receipt and Valuation',
                'plantation_location_type_id': False,
                'plantation_location_id': False,
                'plantation_activity_id': False,
                'plantation_src_journal_id': False,
                'account_id': self.lump_inventory_account_id.id,
                'debit': self.lump_plantation_cost if self.lump_plantation_cost>0 else 0.0,
                'credit': abs(self.lump_plantation_cost) if self.lump_plantation_cost<0 else 0.0,
            }
            move_lines_receiving.append((0,0,vals_dest))
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
                move_lines_receiving.append((0,0,vals_src))
        # END: Receiving from NAP
        
        # BEGIN: Inventory Latex/Lump to WIP  
        if self.latex_wip_incoming_qty:
            vals_wip_in = {
                'name': 'Work in Process Latex',
                'plantation_location_type_id': False,
                'plantation_location_id': False,
                'plantation_activity_id': False,
                'plantation_src_journal_id': False,
                'account_id': self.latex_wip_account_id.id,
                'product_id': self.latex_product_id.id,
                'debit': self.latex_wip_incoming_value if self.latex_wip_incoming_value>0 else 0.0,
                'credit': abs(self.latex_wip_incoming_value) if self.latex_wip_incoming_value<0 else 0.0,
            }
            vals_wip_in_src = vals_wip_in.copy()
            vals_wip_in_src.update({
                'account_id': self.latex_inventory_account_id.id,
                'debit': vals_wip_in['credit'],
                'credit': vals_wip_in['debit']
            })
            move_lines_wip.extend([(0,0,vals_wip_in),(0,0,vals_wip_in_src)])
        
        if self.lump_wip_incoming_qty:
            vals_wip_in = {
                'name': 'Work in Process Lump',
                'plantation_location_type_id': False,
                'plantation_location_id': False,
                'plantation_activity_id': False,
                'plantation_src_journal_id': False,
                'account_id': self.lump_wip_account_id.id,
                'product_id': self.lump_product_id.id,
                'debit': self.lump_wip_incoming_value if self.lump_wip_incoming_value>0 else 0.0,
                'credit': abs(self.lump_wip_incoming_value) if self.lump_wip_incoming_value<0 else 0.0,
            }
            move_lines_wip.append((0,0,vals_wip_in))
            vals_wip_in_src = vals_wip_in.copy()
            vals_wip_in_src.update({
                'account_id': self.lump_inventory_account_id.id,
                'debit': vals_wip_in['credit'],
                'credit': vals_wip_in['debit']
            })
            move_lines_wip.append((0,0,vals_wip_in_src))
        # END: Inventory Latex/Lum to WIP            
        
        # BEGIN: FOH to WIP Latex/Lump  
        if self.sheet_production_cost:
            vals_mrp = {
                'name': 'Manufacturing Cost to WIP Latex',
                'plantation_location_type_id': False,
                'plantation_location_id': False,
                'plantation_activity_id': False,
                'plantation_src_journal_id': False,
                'account_id': self.latex_wip_account_id.id,
                'product_id': self.latex_product_id.id,
                'debit': self.sheet_production_cost if self.sheet_production_cost>0 else 0.0,
                'credit': abs(self.sheet_production_cost) if self.sheet_production_cost<0 else 0.0,
            }
            move_lines_wip.append((0,0,vals_mrp))
            for ll in self.mrp_cost_ids:
                vals_wip_src = {
                    'name': 'Move Cost to WIP Latex',
                    # 'plantation_location_type_id': ll.plantation_location_type_id.id,
                    # 'plantation_location_id': ll.plantation_location_id.id,
                    # 'plantation_activity_id': ll.plantation_activity_id.id,
                    # 'plantation_src_journal_id': ll.plantation_src_journal_id.id,
                    'account_id': ll.account_id.id,
                    'debit': abs(ll.total_cost_latex) if ll.total_cost_latex<0 else 0.0,
                    'credit': ll.total_cost_latex if ll.total_cost_latex>0 else 0.0,
                }
                move_lines_wip.append((0,0,vals_wip_src))
        
        if self.compound_production_cost:
            vals_mrp = {
                'name': 'Manufacturing Cost to WIP Latex',
                'plantation_location_type_id': False,
                'plantation_location_id': False,
                'plantation_activity_id': False,
                'plantation_src_journal_id': False,
                'account_id': self.lump_wip_account_id.id,
                'product_id': self.lump_product_id.id,
                'debit': self.compound_production_cost if self.compound_production_cost>0 else 0.0,
                'credit': abs(self.compound_production_cost) if self.compound_production_cost<0 else 0.0,
            }
            move_lines_wip.append((0,0,vals_mrp))
            for ll in self.mrp_cost_ids:
                vals_wip_src = {
                    'name': 'Move Cost to WIP Lump',
                    # 'plantation_location_type_id': ll.plantation_location_type_id.id,
                    # 'plantation_location_id': ll.plantation_location_id.id,
                    # 'plantation_activity_id': ll.plantation_activity_id.id,
                    # 'plantation_src_journal_id': ll.plantation_src_journal_id.id,
                    'account_id': ll.account_id.id,
                    'debit': abs(ll.total_cost_lump) if ll.total_cost_lump<0 else 0.0,
                    'credit': ll.total_cost_lump if ll.total_cost_lump>0 else 0.0,
                }
                move_lines_wip.append((0,0,vals_wip_src))
        # END: FOH to WIP Latex/Lump
        
        # BEGIN: WIP Latex to WIP Sheet
        if self.latex_wip_outgoing_qty:
            vals_mrp2 = {
                'name': 'WIP Latex to WIP Sheet',
                'plantation_location_type_id': False,
                'plantation_location_id': False,
                'plantation_activity_id': False,
                'plantation_src_journal_id': False,
                'account_id': self.sheet_wip_account_id.id,
                'product_id': self.sheet_product_id.id,
                'debit': (self.latex_wip_outgoing_value+self.sheet_raw_material_cost) if (self.latex_wip_outgoing_value+self.sheet_raw_material_cost)>0 else 0.0,
                'credit': abs(self.latex_wip_outgoing_value+self.sheet_raw_material_cost) if (self.latex_wip_outgoing_value+self.sheet_raw_material_cost)<0 else 0.0,
            }
            move_lines_wip.append((0,0,vals_mrp2))
            if self.sheet_raw_material_cost:
                mrp_sheet = self._get_mrp_done_this_month(self.sheet_product_id)
                rm_moves = mrp_sheet.move_raw_ids.filtered(lambda s: s.product_id.name not in ('Latex','Lump'))
                rm_cost_grouped = {}
                if rm_moves:
                    if len(rm_moves.ids)>1:
                        svl_search = self.env['stock.valuation.layer'].search([('stock_move_id','in',rm_moves.ids)])
                    else:
                        svl_search = self.env['stock.valuation.layer'].search([('stock_move_id','=',rm_moves.id)])
                    for rm_svl in svl_search:
                        if rm_svl.product_id.categ_id.property_valuation!='real_time':
                            continue
                        if not rm_svl.account_move_id:
                            continue
                        for aml in rm_svl.account_move_id.line_ids:
                            if aml.account_id.id==rm_svl.product_id.categ_id.property_stock_valuation_account_id.id:
                                continue
                            if aml.account_id.id not in rm_cost_grouped.keys():
                                rm_cost_grouped.update({aml.account_id.id: 0.0})
                            rm_cost_grouped[aml.account_id.id] += aml.balance
                for rm_acc_id, rm_cost in rm_cost_grouped.items():
                    vals_mrp2_rm = vals_mrp2.copy()
                    vals_mrp2_rm.update({
                        # 'product_id': False,
                        'account_id': rm_acc_id,
                        'debit': abs(rm_cost) if rm_cost<0 else 0.0,
                        'credit': rm_cost if rm_cost>0 else 0.0,
                    })
                    move_lines_wip.append((0,0,vals_mrp2_rm))
            
            vals_mrp_src2 = vals_mrp2.copy()
            vals_mrp_src2.update({
                'product_id': self.latex_product_id.id,
                'account_id': self.latex_wip_account_id.id,
                'debit': abs(self.latex_wip_outgoing_value) if self.latex_wip_outgoing_value<0.0 else 0.0,
                'credit': self.latex_wip_outgoing_value if self.latex_wip_outgoing_value>0.0 else 0.0,
            })
            move_lines_wip.append((0,0,vals_mrp_src2))
        # END: WIP Latex to WIP Sheet

        if move_lines_receiving:
            values = {
                'date': self.date_to,
                'journal_id': misc_journal.id,
                'move_type': 'entry',
                'line_ids': move_lines_receiving,
            }
            new_move = self.env['account.move'].create(values)
            self.closing_move_ids = [(4,new_move.id)]
        if move_lines_wip:
            values2 = {
                'date': self.date_from + relativedelta(months=1),
                'journal_id': misc_journal.id,
                'move_type': 'entry',
                'line_ids': move_lines_wip,
            }
            new_reverse_move = self.env['account.move'].create(values2)
            self.closing_move_ids = [(4,new_reverse_move.id)]

    def create_move_entries_fg(self):
        self.ensure_one()
        misc_journal = self.env['account.journal'].search([('type','=','general')], limit=1)
        
        for line in self.fg2_valuation_ids:
            if not line.inventory_account_id:
                raise ValidationError(f"Silahkan isi akun Inventory valuation untuk Product {line.product_id.name}")
            if not line.cogs_account_id:
                raise ValidationError(f"Silahkan isi akun COGS untuk Product {line.product_id.name}")
            # 1. Journal Receiving (Plantation/Manufacturing Cost > Inventory) 
            # 2. Journal Cost of Goods Sold (COGS > Inventory) 
            move_lines_production = []
            move_lines_cogs = []
            if line.incoming_qty:
                vals_dest = {
                    'name': f"{line.product_id.name} Finished Process",
                    'plantation_location_type_id': False,
                    'plantation_location_id': False,
                    'plantation_activity_id': False,
                    'plantation_src_journal_id': False,
                    'account_id': line.inventory_account_id.id,
                    'product_id': line.product_id.id,
                    'debit': line.manufacturing_cost if line.manufacturing_cost>0 else 0.0,
                    'credit': abs(line.manufacturing_cost) if line.manufacturing_cost<0 else 0.0,
                }
                print('................vals_dest', line.product_id.name, vals_dest['debit'], vals_dest['credit'])
                move_lines_production.append((0,0,vals_dest))
                
                vals_src = vals_dest.copy()
                vals_src.update({
                    'name': f"WIP Sheet Finished",
                    'account_id': line.closing_id.sheet_wip_account_id.id,
                    'debit': vals_dest['credit'],
                    'credit': vals_dest['debit'],
                })
                move_lines_production.append((0,0,vals_src))
            
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
                move_lines_production.extend([(0,0,vals_src),(0,0,vals_dest)])
            
            if move_lines_production:
                values = {
                    'date': self.date_to,
                    'journal_id': misc_journal.id,
                    'move_type': 'entry',
                    'line_ids': move_lines_production,
                }
                new_move = self.env['account.move'].create(values)    
                line.closing_move_id = new_move.id

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
            # move_lines_reverse_wip = []
            if line.incoming_qty:
                vals_dest = {
                    'name': f"{line.product_id.name} Finished Process",
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
                elif line.product_id.name=='Compo':
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

    def create_move_entries_rm_pisang(self):
        self.ensure_one()
        misc_journal = self.env['account.journal'].search([('type','=','general')], limit=1)

        move_lines_receiving = []
        move_lines_wip = []
        # BEGIN: Receiving from NAP
        if self.pisang_incoming_qty:
            vals_dest = {
                'name': 'Inventory Receipt and Valuation',
                'plantation_location_type_id': False,
                'plantation_location_id': False,
                'plantation_activity_id': False,
                'plantation_src_journal_id': False,
                'account_id': self.pisang_inventory_account_id.id,
                'debit': self.plantation_cost if self.plantation_cost>0 else 0.0,
                'credit': abs(self.plantation_cost) if self.plantation_cost<0 else 0.0,
            }
            move_lines_receiving.append((0,0,vals_dest))
            
            for ll in self.plantation_cost_ids:
                vals_src = {
                    'name': 'Move Cost to Inventory Pisang',
                    'plantation_location_type_id': ll.plantation_location_type_id.id,
                    'plantation_location_id': ll.plantation_location_id.id,
                    'plantation_activity_id': ll.plantation_activity_id.id,
                    'plantation_src_journal_id': ll.plantation_src_journal_id.id,
                    'account_id': ll.account_id.id,
                    'debit': abs(ll.total_cost) if ll.total_cost<0 else 0.0,
                    'credit': ll.total_cost if ll.total_cost>0 else 0.0,
                }
                move_lines_receiving.append((0,0,vals_src))
        # END: Receiving from NAP
        
        # BEGIN: Inventory Pisang to WIP  
        if self.pisang_wip_incoming_qty:
            vals_wip_in = {
                'name': 'Work in Process Pisang',
                'plantation_location_type_id': False,
                'plantation_location_id': False,
                'plantation_activity_id': False,
                'plantation_src_journal_id': False,
                'account_id': self.pisang_wip_account_id.id,
                'product_id': self.pisang_product_id.id,
                'debit': self.pisang_wip_incoming_value if self.pisang_wip_incoming_value>0 else 0.0,
                'credit': abs(self.pisang_wip_incoming_value) if self.pisang_wip_incoming_value<0 else 0.0,
            }
            vals_wip_in_src = vals_wip_in.copy()
            vals_wip_in_src.update({
                'account_id': self.pisang_inventory_account_id.id,
                'debit': vals_wip_in['credit'],
                'credit': vals_wip_in['debit']
            })
            move_lines_wip.extend([(0,0,vals_wip_in),(0,0,vals_wip_in_src)])
        # END: Inventory Latex/Lum to WIP            
        
        # BEGIN: FOH to WIP Latex/Lump  
        if self.manufacturing_cost:
            vals_mrp = {
                'name': 'Manufacturing Cost to WIP Pisang',
                'plantation_location_type_id': False,
                'plantation_location_id': False,
                'plantation_activity_id': False,
                'plantation_src_journal_id': False,
                'account_id': self.pisang_wip_account_id.id,
                'product_id': self.pisang_product_id.id,
                'debit': self.manufacturing_cost if self.manufacturing_cost>0 else 0.0,
                'credit': abs(self.manufacturing_cost) if self.manufacturing_cost<0 else 0.0,
            }
            move_lines_wip.append((0,0,vals_mrp))
            for ll in self.mrp_cost_ids:
                vals_wip_src = {
                    'name': 'Move Cost to WIP Pisang',
                    # 'plantation_location_type_id': ll.plantation_location_type_id.id,
                    # 'plantation_location_id': ll.plantation_location_id.id,
                    # 'plantation_activity_id': ll.plantation_activity_id.id,
                    # 'plantation_src_journal_id': ll.plantation_src_journal_id.id,
                    'account_id': ll.account_id.id,
                    'debit': abs(ll.total_cost) if ll.total_cost<0 else 0.0,
                    'credit': ll.total_cost if ll.total_cost>0 else 0.0,
                }
                move_lines_wip.append((0,0,vals_wip_src))
        # END: FOH to WIP Latex/Lump
        
        if move_lines_receiving:
            values = {
                'date': self.date_to,
                'journal_id': misc_journal.id,
                'move_type': 'entry',
                'line_ids': move_lines_receiving,
            }
            new_move = self.env['account.move'].create(values)
            self.closing_move_ids = [(4,new_move.id)]
        if move_lines_wip:
            values2 = {
                'date': self.date_from + relativedelta(months=1),
                'journal_id': misc_journal.id,
                'move_type': 'entry',
                'line_ids': move_lines_wip,
            }
            new_reverse_move = self.env['account.move'].create(values2)
            self.closing_move_ids = [(4,new_reverse_move.id)]

    def create_move_entries_fg_pisang(self):
        self.ensure_one()
        misc_journal = self.env['account.journal'].search([('type','=','general')], limit=1)
        
        for line in self.fg2_valuation_ids:
            if not line.inventory_account_id:
                raise ValidationError(f"Silahkan isi akun Inventory valuation untuk Product {line.product_id.name}")
            if not line.cogs_account_id:
                raise ValidationError(f"Silahkan isi akun COGS untuk Product {line.product_id.name}")
            # 1. Journal Receiving (Plantation/Manufacturing Cost > Inventory) 
            # 2. Journal Cost of Goods Sold (COGS > Inventory) 
            move_lines_production = []
            move_lines_cogs = []
            if line.incoming_qty:
                vals_dest = {
                    'name': f"{line.product_id.name} Finished Process",
                    'plantation_location_type_id': False,
                    'plantation_location_id': False,
                    'plantation_activity_id': False,
                    'plantation_src_journal_id': False,
                    'account_id': line.inventory_account_id.id,
                    'product_id': line.product_id.id,
                    'debit': line.manufacturing_cost if line.manufacturing_cost>0 else 0.0,
                    'credit': abs(line.manufacturing_cost) if line.manufacturing_cost<0 else 0.0,
                }
                print('................vals_dest', line.product_id.name, vals_dest['debit'], vals_dest['credit'])
                move_lines_production.append((0,0,vals_dest))
                
                vals_src = vals_dest.copy()
                vals_src.update({
                    'name': f"WIP Sheet Finished",
                    'account_id': line.closing_id.pisang_wip_account_id.id,
                    'debit': vals_dest['credit'],
                    'credit': vals_dest['debit'],
                })
                move_lines_production.append((0,0,vals_src))
            
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
                move_lines_production.extend([(0,0,vals_src),(0,0,vals_dest)])
            
            if move_lines_production:
                values = {
                    'date': self.date_to,
                    'journal_id': misc_journal.id,
                    'move_type': 'entry',
                    'line_ids': move_lines_production,
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

            if closing.varieties_type=='karet':
                closing.create_move_entries_rm()
                closing.create_move_entries_fg()
            elif closing.varieties_type=='pisang':
                closing.create_move_entries_rm_pisang()
                closing.create_move_entries_fg_pisang()
        return True

    def action_done(self):
        for closing in self:
            closing.create_move_entries()
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
        self.filtered(lambda x: x.state in ('start','rm_valuation','fg1_valuation','fg2_valuation')).write({'state':'cancel'})
        return True
    
    def button_set_new(self):
        self.filtered(lambda x: x.state=='cancel').write({'state':'start'})
        return True

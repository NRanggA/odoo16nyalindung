from odoo import models, api, tools

class IrUiMenu(models.Model):
    _inherit = 'ir.ui.menu'

    @api.model
    @tools.ormcache('frozenset(self.env.user.groups_id.ids)', 'debug')
    def _visible_menu_ids(self, debug=False):
        visible_ids = super()._visible_menu_ids(debug)
        viewer_group = self.env.ref('ny_management_viewer.group_management_viewer', raise_if_not_found=False)
        is_admin = self.env.user.has_group('base.group_system')
        if viewer_group and viewer_group in self.env.user.groups_id and not is_admin:
            allowed_roots = [
                'stock.menu_stock_root',
                'c10i_lhm_v16.main_menu_lhm',
                'mrp.menu_mrp_root',
                'purchase.menu_purchase_root',
                'purchase_request.parent_menu_purchase_request',
                'sale.sale_menu_root',
                'account.menu_finance',
            ]
            allowed_root_ids = [self.env.ref(x).id for x in allowed_roots if self.env.ref(x, raise_if_not_found=False)]
            if allowed_root_ids:
                self.env.cr.execute("""
                    WITH RECURSIVE menu_tree AS (
                        SELECT id FROM ir_ui_menu WHERE id = ANY(%s)
                        UNION ALL
                        SELECT m.id FROM ir_ui_menu m JOIN menu_tree t ON m.parent_id = t.id
                    ) SELECT id FROM menu_tree
                """, (allowed_root_ids,))
                allowed_all = {r[0] for r in self.env.cr.fetchall()}
                visible_ids = visible_ids & allowed_all

        return visible_ids

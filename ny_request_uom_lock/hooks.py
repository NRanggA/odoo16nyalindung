from odoo import _
from odoo.exceptions import UserError


def pre_init_hook(cr):
    # The local combined addon defines the same fields and overrides. A database
    # using it needs a coordinated migration rather than two competing owners.
    cr.execute(
        "SELECT state FROM ir_module_module "
        "WHERE name = 'ny_mom_fixes' AND state IN ('installed', 'to install', 'to upgrade')"
    )
    legacy = cr.fetchone()
    if not legacy:
        return
    cr.execute("""
        SELECT 1
          FROM ir_model_data d
          LEFT JOIN ir_ui_view v ON d.model = 'ir.ui.view' AND v.id = d.res_id
         WHERE d.module = 'ny_mom_fixes'
           AND (
               (d.model = 'ir.model.fields' AND d.name IN (
                   'field_purchase_request__mom_enforce_uom',
                   'field_material_request__mom_enforce_uom',
                   'field_purchase_request_line__mom_enforce_uom',
                   'field_material_request_line__mom_enforce_uom',
                   'field_purchase_order_line__mom_pr_uom_locked'
               ))
               OR (d.model = 'ir.ui.view' AND v.active AND d.name IN (
                   'pr_form', 'mr_form', 'purchase_pr_uom_form', 'pr_line_uom_form'
               ))
           )
         LIMIT 1
    """)
    if legacy[0] == 'to install' or cr.fetchone():
        raise UserError(_(
            "Database ini masih memakai aturan poin 17 dari ny_mom_fixes. "
            "Pindahkan kepemilikan field dan view serta lepaskan kode poin 17 "
            "dari addon tersebut sebelum memasang Nyalindung Request UoM Lock."
        ))

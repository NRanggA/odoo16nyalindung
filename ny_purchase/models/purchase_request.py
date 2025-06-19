from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
from odoo.tools.translate import _

class PurchaseRequest(models.Model):
    _inherit = "purchase.request"

    po_status = fields.Char(string="PO Status",compute="_compute_po_status",store=True)

    # @api.onchange('requested_by')
    # def _onchange_requested_by(self):
    #     self.assigned_to = False

    #     if self.requested_by and self.requested_by.employee_id:
    #         approver_employee = self.requested_by.employee_id.approver_pr_id
    #         if approver_employee and approver_employee.user_id:
    #             self.assigned_to = approver_employee.user_id

    assigned_to = fields.Many2one(
        comodel_name="res.users",
        string="Approver",
        compute="_compute_assigned_to",
        store=True,
        tracking=True,
        index=True,
    )

    @api.depends('create_uid')
    def _compute_assigned_to(self):
        for record in self:
            employee = record.create_uid.employee_id
            record.assigned_to = (
                employee.approver_pr_id.user_id if employee and employee.approver_pr_id else False
            )

    def button_approved(self):
        for rec in self:
            assigned_user = rec.assigned_to  

            if self.env.user != assigned_user and not self.env.user.has_group('purchase_request.group_purchase_request_approver'):
                raise ValidationError(_('You are not allowed to approve this request.'))

            rec.write({'state': 'approved'})


    @api.depends('line_ids.purchase_lines')
    def _compute_po_status(self):
        for record in self:
            if any(line.purchase_lines for line in record.line_ids):
                record.po_status = "Purchase Order"
            else:
                record.po_status = "Not Yet"
from odoo import api, fields, models, _
from odoo.exceptions import AccessError, ValidationError


def check_policy_access(records, values):
    if (
        "mom_enforce_uom" in values
        and not records.env.su
        and not records.env.user.has_group("base.group_system")
    ):
        raise AccessError(_("Kebijakan satuan hanya dapat diubah administrator."))


class PurchaseRequest(models.Model):
    _inherit = "purchase.request"

    # False is intentional: Odoo uses field.default to initialize existing rows
    # when adding this column. The form and create() enable only new documents.
    mom_enforce_uom = fields.Boolean("Kebijakan UOM produk", copy=False, default=False)

    @api.model
    def default_get(self, field_names):
        values = super().default_get(field_names)
        if "mom_enforce_uom" in field_names:
            values["mom_enforce_uom"] = True
        return values

    @api.model_create_multi
    def create(self, values_list):
        return super().create([dict(values, mom_enforce_uom=True) for values in values_list])

    def write(self, values):
        check_policy_access(self, values)
        result = super().write(values)
        if values.get("mom_enforce_uom"):
            self.line_ids._mom_check_uom()
            self.line_ids.purchase_lines._check_mom_pr_uom()
        return result

    def copy_data(self, default=None):
        copied_values = super().copy_data(default=default)
        # A new PR always uses product UoM. Convert the copied quantity as well
        # so copying a historical 0.01 km request produces 10 m, not 0.01 m.
        for values in copied_values:
            commands = []
            for command in values.get("line_ids", []):
                if command[0] == 0:
                    line_values = dict(command[2])
                    product = self.env["product.product"].browse(line_values.get("product_id"))
                    unit = self.env["uom.uom"].browse(line_values.get("product_uom_id"))
                    if product and unit and unit != product.uom_id:
                        line_values["product_qty"] = unit._compute_quantity(
                            line_values.get("product_qty", 0), product.uom_id, round=False
                        )
                        line_values["product_uom_id"] = product.uom_id.id
                    command = (0, 0, line_values)
                commands.append(command)
            if "line_ids" in values:
                values["line_ids"] = commands
        return copied_values


class MaterialRequest(models.Model):
    _inherit = "material.request"

    mom_enforce_uom = fields.Boolean("Kebijakan UOM produk", copy=False, default=False)

    @api.model
    def default_get(self, field_names):
        values = super().default_get(field_names)
        if "mom_enforce_uom" in field_names:
            values["mom_enforce_uom"] = True
        return values

    @api.model_create_multi
    def create(self, values_list):
        return super().create([dict(values, mom_enforce_uom=True) for values in values_list])

    def write(self, values):
        check_policy_access(self, values)
        result = super().write(values)
        if values.get("mom_enforce_uom"):
            self.line_ids._mom_check_uom()
        return result


class PurchaseRequestLine(models.Model):
    _inherit = "purchase.request.line"

    mom_enforce_uom = fields.Boolean(related="request_id.mom_enforce_uom")

    def _mom_check_uom(self):
        for line in self:
            if line.mom_enforce_uom and line.product_id and line.product_uom_id != line.product_id.uom_id:
                raise ValidationError(_("Satuan PR baru harus mengikuti satuan produk."))

    @api.model_create_multi
    def create(self, values_list):
        prepared = []
        for values in values_list:
            values = dict(values)
            request = self.env["purchase.request"].browse(
                values.get("request_id") or self.env.context.get("default_request_id")
            )
            if values.get("product_id") and request.mom_enforce_uom:
                product = self.env["product.product"].browse(values["product_id"])
                values.setdefault("product_uom_id", product.uom_id.id)
            prepared.append(values)
        lines = super().create(prepared)
        lines._mom_check_uom()
        lines.purchase_lines._check_mom_pr_uom()
        return lines

    def write(self, values):
        if values.get("product_id") and "product_uom_id" not in values:
            enforced = self.filtered("mom_enforce_uom")
            legacy = self - enforced
            if enforced:
                product = self.env["product.product"].browse(values["product_id"])
                super(PurchaseRequestLine, enforced).write(dict(values, product_uom_id=product.uom_id.id))
            if legacy:
                super(PurchaseRequestLine, legacy).write(values)
            result = True
        else:
            result = super().write(values)
        if {"product_id", "product_uom_id", "request_id", "purchase_lines"} & set(values):
            self._mom_check_uom()
            # A constraint on PO lines alone is not triggered by editing a PR.
            self.purchase_lines._check_mom_pr_uom()
        return result


class MaterialRequestLine(models.Model):
    _inherit = "material.request.line"

    mom_enforce_uom = fields.Boolean(related="mr_id.mom_enforce_uom")

    def _mom_check_uom(self):
        for line in self:
            if line.mom_enforce_uom and line.product_id and line.uom_id != line.product_id.uom_id:
                raise ValidationError(_("Satuan MR baru harus mengikuti satuan produk."))

    @api.model_create_multi
    def create(self, values_list):
        prepared = []
        for values in values_list:
            values = dict(values)
            request = self.env["material.request"].browse(
                values.get("mr_id") or self.env.context.get("default_mr_id")
            )
            if values.get("product_id") and request.mom_enforce_uom:
                product = self.env["product.product"].browse(values["product_id"])
                values.setdefault("uom_id", product.uom_id.id)
            prepared.append(values)
        lines = super().create(prepared)
        lines._mom_check_uom()
        return lines

    def write(self, values):
        if values.get("product_id") and "uom_id" not in values:
            enforced = self.filtered("mom_enforce_uom")
            legacy = self - enforced
            if enforced:
                product = self.env["product.product"].browse(values["product_id"])
                super(MaterialRequestLine, enforced).write(dict(values, uom_id=product.uom_id.id))
            if legacy:
                super(MaterialRequestLine, legacy).write(values)
            result = True
        else:
            result = super().write(values)
        if {"product_id", "uom_id", "mr_id"} & set(values):
            self._mom_check_uom()
        return result

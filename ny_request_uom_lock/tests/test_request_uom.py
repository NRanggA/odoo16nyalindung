import json

from lxml import etree
from types import SimpleNamespace

from odoo import fields
from odoo.exceptions import UserError, ValidationError
from odoo.tests import Form, TransactionCase, tagged



@tagged("post_install", "-at_install")
class TestRequestUomLock(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.meter = cls.env.ref("uom.product_uom_meter")
        cls.km = cls.env.ref("uom.product_uom_km")
        cls.litre = cls.env.ref("uom.product_uom_litre")
        cls.env.ref("base.user_admin").write({
            "groups_id": [(4, cls.env.ref("uom.group_uom").id)],
        })
        cls.vendor = cls.env["res.partner"].create({"name": "Task 17 Test Vendor", "supplier_rank": 1})
        cls.cable = cls.env["product.product"].create({
            "name": "Task 17 Cable", "default_code": "TASK17-TEST-CABLE",
            "uom_id": cls.meter.id, "uom_po_id": cls.km.id, "purchase_ok": True,
        })
        cls.liquid = cls.env["product.product"].create({
            "name": "Task 17 Liquid", "default_code": "TASK17-TEST-LIQUID",
            "uom_id": cls.litre.id, "uom_po_id": cls.litre.id, "purchase_ok": True,
        })

    def make_pr(self, quantity=10):
        values = {"name": "TASK17-TEST-PR"}
        if "warehouse_id" in self.env["purchase.request"]._fields:
            warehouse = self.env["stock.warehouse"].search([
                ("company_id", "=", self.env.company.id)
            ], limit=1)
            values.update(warehouse_id=warehouse.id, picking_type_id=warehouse.in_type_id.id)
        request = self.env["purchase.request"].create(values)
        line = self.env["purchase.request.line"].create({
            "request_id": request.id, "product_id": self.cable.id,
            "name": self.cable.name, "product_qty": quantity,
            "date_required": fields.Date.today(),
        })
        return request, line

    def make_mr(self):
        request = self.env["material.request"].create({"name": "TASK17-TEST-MR"})
        line = self.env["material.request.line"].create({
            "mr_id": request.id, "product_id": self.cable.id,
            "name": self.cable.name, "product_qty": 10,
        })
        return request, line

    def make_wizard(self, request, order=None):
        values = {"supplier_id": self.vendor.id}
        if "supplier_ids" in self.env["purchase.request.line.make.purchase.order"]._fields:
            values["supplier_ids"] = [(6, 0, self.vendor.ids)]
        if order:
            values["purchase_order_id"] = order.id
        return self.env["purchase.request.line.make.purchase.order"].with_context(
            active_model="purchase.request", active_ids=request.ids
        ).create(values)

    def test_new_documents_and_pr_mr_validation(self):
        for model in ["purchase.request", "material.request"]:
            self.assertTrue(self.env[model].default_get(["mom_enforce_uom"])["mom_enforce_uom"])
        for request, line, unit in [(*self.make_pr(), "product_uom_id"), (*self.make_mr(), "uom_id")]:
            self.assertTrue(request.mom_enforce_uom)
            self.assertEqual(line[unit], self.meter)
            with self.assertRaises(ValidationError), self.cr.savepoint():
                line.write({unit: self.km.id})
            values = {"product_id": self.cable.id, "product_qty": 1, unit: self.km.id}
            values["request_id" if unit == "product_uom_id" else "mr_id"] = request.id
            with self.assertRaises(ValidationError), self.cr.savepoint():
                self.env[line._name].create(values)
            line.write({"product_id": self.liquid.id})
            self.assertEqual(line[unit], self.litre)

    def test_new_forms_enable_policy_before_save(self):
        for model in ["purchase.request", "material.request"]:
            form = Form(self.env[model])
            self.assertTrue(form.mom_enforce_uom)

    def test_schema_initialization_keeps_historical_rows_unlocked(self):
        self.cr.execute("CREATE TEMP TABLE task17_historical_rows (mom_enforce_uom boolean) ON COMMIT DROP")
        self.cr.execute("INSERT INTO task17_historical_rows VALUES (NULL)")
        for model_name in ["purchase.request", "material.request"]:
            model = self.env[model_name]
            proxy = SimpleNamespace(_fields=model._fields, _cr=self.cr, _table="task17_historical_rows")
            type(model)._init_column(proxy, "mom_enforce_uom")
            self.cr.execute("SELECT mom_enforce_uom FROM task17_historical_rows")
            self.assertFalse(self.cr.fetchone()[0])

    def test_legacy_copy_converts_quantity_and_preserves_original(self):
        request, line = self.make_pr()
        request.write({"mom_enforce_uom": False})
        line.write({"product_uom_id": self.km.id, "product_qty": .01, "estimated_cost": 250})
        copied = request.copy({"name": "TASK17-TEST-COPY"})
        self.assertTrue(copied.mom_enforce_uom)
        self.assertEqual(copied.line_ids.product_uom_id, self.meter)
        self.assertAlmostEqual(copied.line_ids.product_qty, 10)
        self.assertEqual(copied.line_ids.estimated_cost, 250)
        self.assertEqual(line.product_uom_id, self.km)
        self.assertAlmostEqual(line.product_qty, .01)
        self.assertFalse(request.mom_enforce_uom)

    def test_activating_policy_validates_existing_lines(self):
        for request, line, unit in [(*self.make_pr(), "product_uom_id"), (*self.make_mr(), "uom_id")]:
            request.write({"mom_enforce_uom": False})
            line.write({unit: self.km.id})
            with self.assertRaises(ValidationError), self.cr.savepoint():
                request.write({"mom_enforce_uom": True})

    def test_linked_pr_and_rfq_reject_inconsistent_changes(self):
        request, source = self.make_pr()
        order = self.env["purchase.order"].create({"partner_id": self.vendor.id})
        line = self.env["purchase.order.line"].create({
            "order_id": order.id, "product_id": self.cable.id,
            "name": self.cable.name, "product_qty": 10, "product_uom": self.meter.id,
            "price_unit": 0, "date_planned": fields.Datetime.now(),
            "purchase_request_lines": [(4, source.id)],
        })
        self.assertTrue(line.mom_pr_uom_locked)
        with self.assertRaises(ValidationError), self.cr.savepoint():
            line.write({"product_uom": self.km.id})
        with self.assertRaises(ValidationError), self.cr.savepoint():
            source.write({"product_id": self.liquid.id})
        self.assertEqual(source.product_id, self.cable)
        self.assertEqual(line.product_uom, source.product_uom_id)

    def test_direct_rfq_remains_editable(self):
        order = self.env["purchase.order"].create({"partner_id": self.vendor.id})
        line = self.env["purchase.order.line"].create({
            "order_id": order.id, "product_id": self.cable.id,
            "name": self.cable.name, "product_qty": 10, "product_uom": self.meter.id,
            "price_unit": 0, "date_planned": fields.Datetime.now(),
        })
        self.assertFalse(line.mom_pr_uom_locked)
        line.write({"product_uom": self.km.id, "product_qty": .01})
        self.assertEqual(line.product_uom, self.km)

    def test_wizard_vendor_minimum_and_price(self):
        self.env["product.supplierinfo"].create({
            "partner_id": self.vendor.id, "product_tmpl_id": self.cable.product_tmpl_id.id,
            "min_qty": 2, "price": 100000, "currency_id": self.env.company.currency_id.id,
        })
        request, source = self.make_pr()
        request.write({"state": "approved"})
        wizard = self.make_wizard(request)
        wizard.make_purchase_order()
        line = source.purchase_lines
        self.assertEqual(len(line), 1)
        self.assertEqual(line.product_uom, self.meter)
        self.assertAlmostEqual(line.product_qty, 2000)
        self.assertAlmostEqual(line.price_unit, 100)
        self.assertTrue(line.mom_pr_uom_locked)

    def test_wizard_merges_same_product_and_uom(self):
        first, source = self.make_pr(10)
        second, another = self.make_pr(7)
        (first | second).write({"state": "approved"})
        wizard = self.make_wizard(first)
        wizard.make_purchase_order()
        order = source.purchase_lines.order_id
        next_wizard = self.make_wizard(second, order)
        source.purchase_lines.write({"name": next_wizard._get_purchase_line_name(order, next_wizard.item_ids)})
        next_wizard.make_purchase_order()
        self.assertEqual(len(order.order_line), 1)
        self.assertAlmostEqual(order.order_line.product_qty, 17)
        self.assertEqual(order.order_line.purchase_request_lines, source | another)

    def test_views_contain_uom_lock_in_all_supported_editors(self):
        for model, unit, marker, expected in [
            ("purchase.request", "product_uom_id", "mom_enforce_uom", 1),
            ("purchase.request.line", "product_uom_id", "mom_enforce_uom", 1),
            ("material.request", "uom_id", "mom_enforce_uom", 2),
            ("purchase.order", "product_uom", "mom_pr_uom_locked", 3),
        ]:
            view = self.env[model].with_user(self.env.ref("base.user_admin")).get_view(view_type="form")
            root = etree.fromstring(view["arch"].encode())
            nodes = root.xpath("//field[@name='%s']" % unit)
            locked = [node for node in nodes if marker in node.get("modifiers", "")]
            self.assertGreaterEqual(len(locked), expected)

    def test_create_rfq_wizard_locks_uom_and_allows_quantity_edit(self):
        request, source = self.make_pr(100)
        request.write({"state": "approved"})
        wizard = self.make_wizard(request)
        item = wizard.item_ids.ensure_one()
        self.assertEqual(item.product_uom_id, self.meter)
        self.assertTrue(item.mom_source_uom_locked)

        view = wizard.with_user(self.env.ref("base.user_admin")).get_view(
            view_id=self.env.ref("purchase_request.view_purchase_request_line_make_purchase_order").id,
            view_type="form",
        )
        tree, = etree.fromstring(view["arch"].encode()).xpath("//field[@name='item_ids']/tree")
        uom, = tree.xpath("./field[@name='product_uom_id']")
        qty, = tree.xpath("./field[@name='product_qty']")
        self.assertEqual(json.loads(uom.get("modifiers", "{}"))["readonly"],
                         [["mom_source_uom_locked", "=", True]])
        self.assertFalse(json.loads(qty.get("modifiers", "{}")).get("readonly"))

        with self.assertRaisesRegex(ValidationError, "Satuan pada Create RFQ"), self.cr.savepoint():
            item.write({"product_uom_id": self.km.id})
        item.write({"product_qty": 25})
        wizard.make_purchase_order()
        self.assertEqual(source.purchase_lines.product_qty, 25)
        self.assertEqual(source.purchase_lines.product_uom, self.meter)

    def test_create_rfq_wizard_preserves_legacy_uom_selection(self):
        request, _source = self.make_pr()
        request.write({"state": "approved", "mom_enforce_uom": False})
        item = self.make_wizard(request).item_ids.ensure_one()
        self.assertFalse(item.mom_source_uom_locked)
        item.write({"product_uom_id": self.km.id})
        self.assertEqual(item.product_uom_id, self.km)

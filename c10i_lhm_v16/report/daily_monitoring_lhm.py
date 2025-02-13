from odoo import models, fields

class LhmTransactionMonitoring(models.Model):
    _name = "lhm.transaction.monitoring"
    _description = "LHM Transaction Monitoring"
    _auto = False

    date = fields.Date(string="Date")
    lhm_name = fields.Char(string="LHM Name")
    location_type_id = fields.Many2one("lhm.location.type", string="Tipe")
    varieties_id = fields.Many2one("plant.varieties", string="ORG")
    location_id = fields.Many2one("lhm.location", string="Lokasi")
    activity_id = fields.Many2one("lhm.activity", string="Aktivitas")
    lhm_state = fields.Selection([
        ("draft", "Draft"),
        ("confirmed", "Confirmed"),
        ("done", "Done"),
        ("cancel", "Cancelled"),
    ], string="State")

    def init(self):
        self.env.cr.execute("""
            CREATE OR REPLACE VIEW lhm_transaction_monitoring AS (
                SELECT 
                    row_number() OVER () AS id,
                    lt.date,
                    lt.name AS lhm_name,
                    ltl.location_type_id,
                    ltl.varieties_id,
                    ltl.location_id,
                    ltl.activity_id,
                    lt.state AS lhm_state
                FROM lhm_transaction_line ltl
                JOIN lhm_transaction lt ON ltl.lhm_id = lt.id
                WHERE 
                    ltl.location_type_id IS NULL OR
                    ltl.varieties_id IS NULL OR
                    ltl.location_id IS NULL OR
                    ltl.activity_id IS NULL
                GROUP BY 
                    lt.date,
                    lt.name,
                    ltl.location_type_id,
                    ltl.varieties_id,
                    ltl.location_id,
                    ltl.activity_id,
                    lt.state
                ORDER BY lt.date DESC
            );
        """)

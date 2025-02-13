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
            DROP VIEW IF EXISTS lhm_transaction_monitoring CASCADE;
            CREATE OR REPLACE VIEW lhm_transaction_monitoring AS (
                SELECT
                    row_number() OVER () AS id,
                    lt.name AS lhm_name,
                    ltl.location_type_id,
                    ltl.varieties_id,
                    ltl.location_id,
                    ltl.activity_id,
                    lt.state AS lhm_state
                FROM lhm_transaction_line ltl
                JOIN lhm_transaction lt ON ltl.lhm_id = lt.id
                LEFT JOIN lhm_location_type llt ON ltl.location_type_id = llt.id
                LEFT JOIN lhm_location ll ON ltl.location_id = ll.id
                LEFT JOIN lhm_project_line lp ON ltl.activity_id = lp.activity_id
                LEFT JOIN lhm_project p ON lp.project_id = p.id
                LEFT JOIN lhm_activity la ON ltl.activity_id::varchar = la.code
                WHERE 
                    (
                        (llt.code IN ('FC', 'GC', 'IDC', 'PJ') AND ltl.varieties_id IS NULL) OR
                        (ltl.location_id IS NOT NULL AND ll.type_id IS NOT NULL AND ltl.location_type_id <> ll.type_id) OR
                        (ltl.location_id IS NOT NULL AND ll.varieties_id IS NOT NULL AND ltl.varieties_id <> ll.varieties_id) OR
                        (llt.code = 'PJ' AND ltl.activity_id IS NOT NULL 
                        AND NOT EXISTS (
                            SELECT 1 FROM lhm_project_line WHERE lhm_project_line.activity_id = ltl.activity_id
                        )) OR
                        (llt.code IN ('WS','VH','MA','NS','LB') AND ltl.activity_id IS NOT NULL 
                        AND NOT EXISTS (
                            SELECT 1 FROM lhm_activity WHERE lhm_activity.code = ltl.activity_id::varchar
                        ))
                    )
                    AND NOT (
                        (ltl.activity_id IS NOT NULL AND ll.type_id IS NOT NULL AND ltl.location_type_id = ll.type_id)
                        AND (ltl.location_id IS NOT NULL AND ll.type_id IS NOT NULL AND ltl.location_type_id = ll.type_id)
                        AND (ltl.location_id IS NOT NULL AND ll.varieties_id IS NULL AND ltl.varieties_id IS NULL)
                        AND (ltl.location_type_id IS NOT NULL AND llt.varieties_id IS NULL AND ltl.varieties_id IS NULL)
                    )
                GROUP BY
                    lt.name, ltl.location_type_id, ltl.varieties_id, 
                    ltl.location_id, ltl.activity_id, lt.state
                ORDER BY lt.name DESC
            );
        """)

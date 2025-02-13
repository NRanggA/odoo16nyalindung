from odoo import models, fields

class LhmContractorMonitoring(models.Model):
    _name = "lhm.contractor.monitoring"
    _description = "LHM Contractor Monitoring"
    _auto = False

    bk_name = fields.Char(string="Buku Kontraktor Name")
    location_type_id = fields.Many2one("lhm.location.type", string="Tipe")
    varieties_id = fields.Many2one("plant.varieties", string="ORG")
    location_id = fields.Many2one("lhm.location", string="Lokasi")
    activity_id = fields.Many2one("lhm.activity", string="Aktivitas")
    bk_state = fields.Selection([
        ("draft", "Draft"),
        ("confirmed", "Confirmed"),
        ("done", "Done"),
        ("cancel", "Cancelled"),
    ], string="State")

    def init(self):
        self.env.cr.execute("""
            DROP VIEW IF EXISTS lhm_contractor_monitoring CASCADE;
            CREATE OR REPLACE VIEW lhm_contractor_monitoring AS (
                SELECT
                    row_number() OVER () AS id,
                    lc.name AS bk_name,
                    lcl.location_type_id,
                    lcl.varieties_id,
                    lcl.location_id,
                    lcl.activity_id,
                    lc.state AS bk_state
                FROM lhm_contractor_line lcl
                JOIN lhm_contractor lc ON lcl.contractor_id = lc.id
                LEFT JOIN lhm_location_type llt ON lcl.location_type_id = llt.id
                LEFT JOIN lhm_location ll ON lcl.location_id = ll.id
                LEFT JOIN lhm_project_line lp ON lcl.activity_id = lp.activity_id
                LEFT JOIN lhm_project p ON lp.project_id = p.id
                LEFT JOIN lhm_activity la ON lcl.activity_id::varchar = la.code
                WHERE 
                    (llt.code IN ('FC', 'GC', 'IDC', 'PJ') AND lcl.varieties_id IS NULL) OR
                    (lcl.location_id IS NOT NULL AND ll.type_id IS NOT NULL AND lcl.location_type_id <> ll.type_id) OR
                    (lcl.location_id IS NOT NULL AND ll.varieties_id IS NOT NULL AND lcl.varieties_id <> ll.varieties_id) OR
                    (llt.code = 'PJ' AND lcl.activity_id IS NOT NULL 
                    AND NOT EXISTS (
                        SELECT 1 FROM lhm_project_line WHERE lhm_project_line.activity_id = lcl.activity_id
                    )) OR
                    (llt.code IN ('WS','VH','MA','NS','LB') AND lcl.activity_id IS NOT NULL 
                    AND NOT EXISTS (
                        SELECT 1 FROM lhm_activity WHERE lhm_activity.code = lcl.activity_id::varchar
                    ))
                GROUP BY
                    lc.name, lcl.location_type_id, lcl.varieties_id, 
                    lcl.location_id, lcl.activity_id, lc.state
                ORDER BY lc.name DESC
            );
        """)

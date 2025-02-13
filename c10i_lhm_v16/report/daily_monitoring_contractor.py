from odoo import models, fields

class LhmContractorMonitoring(models.Model):
    _name = "lhm.contractor.monitoring"
    _description = "LHM Contractor Monitoring"
    _auto = False

    # date = fields.Date(string="Date")
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
                WHERE 
                    lcl.location_type_id IS NULL OR
                    lcl.varieties_id IS NULL OR
                    lcl.location_id IS NULL OR
                    lcl.activity_id IS NULL
                GROUP BY 
                    lc.name,
                    lcl.location_type_id,
                    lcl.varieties_id,
                    lcl.location_id,
                    lcl.activity_id,
                    lc.state
                ORDER BY lc.name ASC
            );
        """)

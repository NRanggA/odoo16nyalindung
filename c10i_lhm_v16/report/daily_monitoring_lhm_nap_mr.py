from odoo import models, fields, api

class LhmNapPisangMonitoringWizard(models.TransientModel):
    _name = 'lhm.nap.pisang.monitoring.wizard'
    _description = 'Wizard Monitoring LHM NAP Pisang'

    plant_varieties_id = fields.Many2one('plant.varieties', string="Varietas", default=lambda self: self.env['plant.varieties'].browse(20))
    harvest_activity_ids = fields.Many2many(
        'lhm.activity',
        string="Aktivitas",
        domain="[('id', 'in', available_activity_ids)]"
    )
    available_activity_ids = fields.Many2many(
        'lhm.activity',
        compute='_compute_available_activity_ids',
        store=False
    )

    from_month = fields.Selection(
        selection=lambda self: self._get_available_months(),
        string='Dari Bulan'
    )
    to_month = fields.Selection(
        selection=lambda self: self._get_available_months(),
        string='Sampai Bulan'
    )

    @api.model
    def _get_available_months(self):
        self.env.cr.execute("""
            SELECT DISTINCT TO_CHAR(date, 'YYYY-MM') AS bulan
            FROM lhm_transaction
            ORDER BY bulan
        """)
        rows = self.env.cr.fetchall()
        return [(r[0], r[0]) for r in rows]

    @api.depends('plant_varieties_id')
    def _compute_available_activity_ids(self):
        for wizard in self:
            wizard.available_activity_ids = wizard.plant_varieties_id.harvest_activity_ids

    # def action_view_report(self):
    #     activity_ids = self.harvest_activity_ids.ids or [375]

    #     context = {
    #         'default_activity_ids': activity_ids,
    #         'from_month': self.from_month,
    #         'to_month': self.to_month,
    #     }

    #     return {
    #         'type': 'ir.actions.act_window',
    #         'name': 'Cek Total Qty Pisang LHM vs NAP',
    #         'res_model': 'lhm.nap.pisang.monitoring',
    #         'view_mode': 'tree',
    #         'target': 'current',
    #         'context': context
    #     }

    def action_view_report(self):
        activity_ids = self.harvest_activity_ids.ids or [375]
        from_month = self.from_month or '2025-01'
        to_month = self.to_month or '2025-12'

        # Bangun view ulang sebelum buka window
        self.env['lhm.nap.pisang.monitoring']._rebuild_view(activity_ids, from_month, to_month)

        return {
            'type': 'ir.actions.act_window',
            'name': 'Cek Total Qty Pisang LHM vs NAP',
            'res_model': 'lhm.nap.pisang.monitoring',
            'view_mode': 'tree',
            'target': 'current',
        }

class LhmNapPisangMonitoring(models.Model):
    _name = "lhm.nap.pisang.monitoring"
    _description = "LHM NAP Pisang Monitoring"
    _auto = False

    id = fields.Integer(string="ID", readonly=True)
    bulan = fields.Char(string="Bulan")
    jumlah_lhm_per_bulan = fields.Integer(string="Jumlah Dokumen LHM")
    total_hasil_1 = fields.Float(string="LHM Qty (Kg)")
    total_product_qty = fields.Float(string="NAP Qty (Kg)")
    nap_mr = fields.Float(string="Material Receipt Qty (Kg)")
    nap_mr_return = fields.Float(string="Material Receipt - Return Qty (Kg)")
    nett = fields.Float(string="Material Receipt Nett")
    lhm_names = fields.Text(string="Dokumen LHM")
    nap_names = fields.Text(string="Dokumen NAP")

    # def init(self):
    #     activity_ids = self.env.context.get('default_activity_ids') or [375]
    #     from_month = self.env.context.get('from_month') or '2025-01'
    #     to_month = self.env.context.get('to_month') or '2025-12'
    #     activity_ids_str = ','.join(map(str, activity_ids))
    #     self.env.cr.execute(f"""
    #         DROP VIEW IF EXISTS lhm_nap_pisang_monitoring CASCADE;
    #         CREATE OR REPLACE VIEW lhm_nap_pisang_monitoring AS (
    #             WITH lhm_data AS (
    #                 SELECT
    #                     TO_CHAR(lhm.date, 'YYYY-MM') AS bulan,
    #                     lhm.id AS lhm_id,
    #                     lhm.name AS lhm_name,
    #                     line.activity_id,
    #                     line.hasil_1,
    #                     line.location_id
    #                 FROM
    #                     lhm_transaction lhm
    #                 JOIN
    #                     lhm_transaction_line line ON line.lhm_id = lhm.id
    #                 WHERE
    #                     line.varieties_id = 20
    #                     AND line.activity_id IN ({activity_ids_str})
    #                     AND lhm.kemandoran_id = 192
    #                     AND TO_CHAR(lhm.date, 'YYYY-MM') BETWEEN '{from_month}' AND '{to_month}'
    #             ),
    #             lhm_locations_per_bulan AS (
    #                 SELECT
    #                     TO_CHAR(lhm.date, 'YYYY-MM') AS bulan,
    #                     lhm.date::date AS tanggal,
    #                     ARRAY_AGG(DISTINCT line.location_id ORDER BY line.location_id) AS lhm_locations
    #                 FROM
    #                     lhm_transaction lhm
    #                 JOIN
    #                     lhm_transaction_line line ON line.lhm_id = lhm.id
    #                 WHERE
    #                     line.varieties_id = 20
    #                     AND line.activity_id IN ({activity_ids_str})
    #                     AND lhm.kemandoran_id = 192
    #                     AND TO_CHAR(lhm.date, 'YYYY-MM') BETWEEN '{from_month}' AND '{to_month}'
    #                 GROUP BY
    #                     TO_CHAR(lhm.date, 'YYYY-MM'), lhm.date
    #             ),
    #             nap_data_raw_all AS (
    #                 SELECT
    #                     TO_CHAR(tp.tgl_panen, 'YYYY-MM') AS bulan,
    #                     tp.tgl_panen,
    #                     nap.name AS nap_name,
    #                     nap.id AS nap_id,
    #                     block.location_id AS location_id,
    #                     tp.product_qty,
    #                     tp.id AS tp_id
    #                 FROM
    #                     timbangan_pabrik tp
    #                 JOIN
    #                     lhm_nap nap ON tp.lhm_nap_id = nap.id
    #                 JOIN
    #                     lhm_plant_block block ON block.id = tp.block_id
    #                 JOIN
    #                     product_product pp ON tp.product_id = pp.id
    #                 JOIN
    #                     varitas_product_rel rel ON rel.product_product_id = pp.id
    #                 JOIN
    #                     plant_varieties pv ON pv.id = rel.plant_varieties_id
    #                 WHERE
    #                     nap.state = 'done'
    #                     AND nap.afdeling_id = 37
    #                     AND TO_CHAR(tp.tgl_panen, 'YYYY-MM') BETWEEN '{from_month}' AND '{to_month}'
    #             ),
    #             valid_nap AS (
    #                 SELECT DISTINCT
    #                     r.nap_id,
    #                     r.nap_name,
    #                     r.bulan
    #                 FROM
    #                     nap_data_raw_all r
    #                 JOIN (
    #                     SELECT
    #                         nap_id,
    #                         tgl_panen,
    #                         bulan,
    #                         ARRAY_AGG(DISTINCT location_id ORDER BY location_id) AS nap_locations
    #                     FROM
    #                         nap_data_raw_all
    #                     GROUP BY nap_id, bulan, tgl_panen
    #                 ) agg ON agg.nap_id = r.nap_id AND agg.bulan = r.bulan
    #                 JOIN lhm_locations_per_bulan lhm ON lhm.bulan = agg.bulan AND lhm.tanggal = agg.tgl_panen
    #                 WHERE
    #                     lhm.lhm_locations <@ agg.nap_locations
    #             ),
    #             nap_data_raw AS (
    #                 SELECT
    #                     r.*
    #                 FROM
    #                     nap_data_raw_all r
    #                 JOIN
    #                     valid_nap v ON r.nap_id = v.nap_id
    #             ),
    #             nap_data AS (
    #                 SELECT
    #                     bulan,
    #                     location_id,
    #                     STRING_AGG(DISTINCT nap_name, ', ') AS nap_names,
    #                     SUM(product_qty) AS total_product_qty
    #                 FROM
    #                     nap_data_raw
    #                 WHERE
    #                     product_qty IS NOT NULL
    #                 GROUP BY
    #                     bulan, location_id
    #             ),
    #             stock_move_summary AS (
    #                 SELECT
    #                     TO_CHAR(tp.tgl_panen, 'YYYY-MM') AS bulan,
    #                     block.location_id,
    #                     SUM(CASE WHEN sm.picking_type_id = 12 THEN sm.product_qty ELSE 0 END) AS nap_mr,
    #                     SUM(CASE WHEN sm.picking_type_id = 14 THEN sm.product_qty ELSE 0 END) AS nap_mr_return
    #                 FROM
    #                     stock_move sm
    #                 JOIN
    #                     timbangan_pabrik tp ON tp.id = sm.nap_tim_pabrik_id
    #                 JOIN
    #                     lhm_plant_block block ON tp.block_id = block.id
    #                 JOIN
    #                     valid_nap vn ON tp.lhm_nap_id = vn.nap_id
    #                 WHERE
    #                     sm.state = 'done'
    #                     AND TO_CHAR(tp.tgl_panen, 'YYYY-MM') BETWEEN '{from_month}' AND '{to_month}'
    #                 GROUP BY
    #                     TO_CHAR(tp.tgl_panen, 'YYYY-MM'),
    #                     block.location_id
    #             )
    #             SELECT
    #                 row_number() OVER () AS id,
    #                 lhm.bulan,
    #                 STRING_AGG(DISTINCT lhm.lhm_name, ', ') AS lhm_names,
    #                 COUNT(DISTINCT lhm.lhm_id) AS jumlah_lhm_per_bulan,
    #                 SUM(lhm.hasil_1) AS total_hasil_1,
    #                 COALESCE(SUM(DISTINCT pq.total_product_qty), 0) AS total_product_qty,
    #                 COALESCE(STRING_AGG(DISTINCT pq.nap_names, ', '), '') AS nap_names,
    #                 COALESCE(SUM(DISTINCT sm.nap_mr), 0) AS nap_mr,
    #                 COALESCE(SUM(DISTINCT sm.nap_mr_return), 0) AS nap_mr_return,
    #                 COALESCE(SUM(DISTINCT sm.nap_mr), 0) - COALESCE(SUM(DISTINCT sm.nap_mr_return), 0) AS nett
    #             FROM
    #                 lhm_data lhm
    #             LEFT JOIN
    #                 nap_data pq ON pq.bulan = lhm.bulan AND pq.location_id = lhm.location_id
    #             LEFT JOIN 
    #                 stock_move_summary sm ON sm.bulan = lhm.bulan AND sm.location_id = lhm.location_id
    #             GROUP BY
    #                 lhm.bulan
    #             ORDER BY
    #                 lhm.bulan
    #         );
    #     """)

    def _rebuild_view(self, activity_ids, from_month, to_month):
        activity_ids_str = ','.join(map(str, activity_ids))
        self.env.cr.execute(f"""
            DROP VIEW IF EXISTS lhm_nap_pisang_monitoring CASCADE;
            CREATE OR REPLACE VIEW lhm_nap_pisang_monitoring AS (
                WITH lhm_data AS (
                    SELECT
                        TO_CHAR(lhm.date, 'YYYY-MM') AS bulan,
                        lhm.id AS lhm_id,
                        lhm.name AS lhm_name,
                        line.activity_id,
                        line.hasil_1,
                        line.location_id
                    FROM
                        lhm_transaction lhm
                    JOIN
                        lhm_transaction_line line ON line.lhm_id = lhm.id
                    WHERE
                        line.varieties_id = 20
                        AND line.activity_id IN ({activity_ids_str})
                        AND lhm.kemandoran_id = 192
                        AND TO_CHAR(lhm.date, 'YYYY-MM') BETWEEN '{from_month}' AND '{to_month}'
                ),
                lhm_locations_per_bulan AS (
                    SELECT
                        TO_CHAR(lhm.date, 'YYYY-MM') AS bulan,
                        lhm.date::date AS tanggal,
                        ARRAY_AGG(DISTINCT line.location_id ORDER BY line.location_id) AS lhm_locations
                    FROM
                        lhm_transaction lhm
                    JOIN
                        lhm_transaction_line line ON line.lhm_id = lhm.id
                    WHERE
                        line.varieties_id = 20
                        AND line.activity_id IN ({activity_ids_str})
                        AND lhm.kemandoran_id = 192
                        AND TO_CHAR(lhm.date, 'YYYY-MM') BETWEEN '{from_month}' AND '{to_month}'
                    GROUP BY
                        TO_CHAR(lhm.date, 'YYYY-MM'), lhm.date
                ),
                nap_data_raw_all AS (
                    SELECT
                        TO_CHAR(tp.tgl_panen, 'YYYY-MM') AS bulan,
                        tp.tgl_panen,
                        nap.name AS nap_name,
                        nap.id AS nap_id,
                        block.location_id AS location_id,
                        tp.product_qty,
                        tp.id AS tp_id
                    FROM
                        timbangan_pabrik tp
                    JOIN
                        lhm_nap nap ON tp.lhm_nap_id = nap.id
                    JOIN
                        lhm_plant_block block ON block.id = tp.block_id
                    JOIN
                        product_product pp ON tp.product_id = pp.id
                    JOIN
                        varitas_product_rel rel ON rel.product_product_id = pp.id
                    JOIN
                        plant_varieties pv ON pv.id = rel.plant_varieties_id
                    WHERE
                        nap.state = 'done'
                        AND nap.afdeling_id = 37
                        AND TO_CHAR(tp.tgl_panen, 'YYYY-MM') BETWEEN '{from_month}' AND '{to_month}'
                ),
                valid_nap AS (
                    SELECT DISTINCT
                        r.nap_id,
                        r.nap_name,
                        r.bulan
                    FROM
                        nap_data_raw_all r
                    JOIN (
                        SELECT
                            nap_id,
                            tgl_panen,
                            bulan,
                            ARRAY_AGG(DISTINCT location_id ORDER BY location_id) AS nap_locations
                        FROM
                            nap_data_raw_all
                        GROUP BY nap_id, bulan, tgl_panen
                    ) agg ON agg.nap_id = r.nap_id AND agg.bulan = r.bulan
                    JOIN lhm_locations_per_bulan lhm ON lhm.bulan = agg.bulan AND lhm.tanggal = agg.tgl_panen
                    WHERE
                        lhm.lhm_locations <@ agg.nap_locations
                ),
                nap_data_raw AS (
                    SELECT
                        r.*
                    FROM
                        nap_data_raw_all r
                    JOIN
                        valid_nap v ON r.nap_id = v.nap_id
                ),
                nap_data AS (
                    SELECT
                        bulan,
                        location_id,
                        STRING_AGG(DISTINCT nap_name, ', ') AS nap_names,
                        SUM(product_qty) AS total_product_qty
                    FROM
                        nap_data_raw
                    WHERE
                        product_qty IS NOT NULL
                    GROUP BY
                        bulan, location_id
                ),
                stock_move_summary AS (
                    SELECT
                        TO_CHAR(tp.tgl_panen, 'YYYY-MM') AS bulan,
                        block.location_id,
                        SUM(CASE WHEN sm.picking_type_id = 12 THEN sm.product_qty ELSE 0 END) AS nap_mr,
                        SUM(CASE WHEN sm.picking_type_id = 14 THEN sm.product_qty ELSE 0 END) AS nap_mr_return
                    FROM
                        stock_move sm
                    JOIN
                        timbangan_pabrik tp ON tp.id = sm.nap_tim_pabrik_id
                    JOIN
                        lhm_plant_block block ON tp.block_id = block.id
                    JOIN
                        valid_nap vn ON tp.lhm_nap_id = vn.nap_id
                    WHERE
                        sm.state = 'done'
                        AND TO_CHAR(tp.tgl_panen, 'YYYY-MM') BETWEEN '{from_month}' AND '{to_month}'
                    GROUP BY
                        TO_CHAR(tp.tgl_panen, 'YYYY-MM'),
                        block.location_id
                )
                SELECT
                    row_number() OVER () AS id,
                    lhm.bulan,
                    STRING_AGG(DISTINCT lhm.lhm_name, ', ') AS lhm_names,
                    COUNT(DISTINCT lhm.lhm_id) AS jumlah_lhm_per_bulan,
                    SUM(lhm.hasil_1) AS total_hasil_1,
                    COALESCE(SUM(DISTINCT pq.total_product_qty), 0) AS total_product_qty,
                    COALESCE(STRING_AGG(DISTINCT pq.nap_names, ', '), '') AS nap_names,
                    COALESCE(SUM(DISTINCT sm.nap_mr), 0) AS nap_mr,
                    COALESCE(SUM(DISTINCT sm.nap_mr_return), 0) AS nap_mr_return,
                    COALESCE(SUM(DISTINCT sm.nap_mr), 0) - COALESCE(SUM(DISTINCT sm.nap_mr_return), 0) AS nett
                FROM
                    lhm_data lhm
                LEFT JOIN
                    nap_data pq ON pq.bulan = lhm.bulan AND pq.location_id = lhm.location_id
                LEFT JOIN 
                    stock_move_summary sm ON sm.bulan = lhm.bulan AND sm.location_id = lhm.location_id
                GROUP BY
                    lhm.bulan
                ORDER BY
                    lhm.bulan
            );
        """)


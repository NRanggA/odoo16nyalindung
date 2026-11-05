# -*- coding: utf-8 -*-
# [FIX 05/11/2026 - Alfi (KSI)] Field baru tm_date (Tanggal Menjadi TM). Sebelum modul dimuat, kolom dibuat dan diisi
# 1 Januari dari Tahun Menjadi TM yang sudah ada, supaya tm_year (sekarang dihitung dari tm_date) tidak
# berubah. Tanggal pastinya dikoreksi kebun sesudahnya. Blok TM yang Tahun TM-nya kosong tidak diisi
# (harus dilengkapi data kebun).
import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    cr.execute("ALTER TABLE lhm_plant_block ADD COLUMN IF NOT EXISTS tm_date date")
    cr.execute("""
        UPDATE lhm_plant_block
           SET tm_date = make_date(tm_year, 1, 1)
         WHERE tm_date IS NULL AND COALESCE(tm_year, 0) > 0
    """)
    _logger.info("Migrasi c10i_lhm_v16 0.2: tm_date diisi untuk %s blok dari tm_year.", cr.rowcount)
# [FIX 05/11/2026] END

# CHANGELOG ny_closing

Catatan perubahan modul `ny_closing` di luar developer utama.
Setiap perubahan ditandai di kode dengan komentar `# [FIX <tanggal> - <nama>] ... # [FIX <tanggal>] END`
(cari dengan `grep -rn "FIX <tanggal>"`). Kode asli yang diubah/dipindah disimpan di bawah.

---

## [FIX 05/11/2026 - Alfi (KSI)] Compo adjustment ikut dihitung di Closing Production

**File:** `models/closing_production.py` (model `closing.production`)
**Fungsi:** `compute_initial_and_cost_fg2` (tab Finish Good Valuation, varietas karet), method baru `_get_fg_adjustment_qty`
**Perlu upgrade modul:** tidak (hanya Python, cukup restart Odoo). Field, view dan jurnal tidak berubah.

### Masalah
Stock adjustment (Physical Inventory / Product Quantity Updated) untuk produk Compo tidak pernah masuk kolom
Adjustment di Closing Production, sedangkan RSS I, RSS III dan Cutting masuk.

### Penyebab
Query adjustment hanya ada di dalam loop `for product in mrp_products`, dan `mrp_products` hanya berisi
RSS I, RSS III, Cutting. Compo dihitung terpisah (`closing.compound_product_id`) tanpa query adjustment,
dan `values_to_create_compo` tidak berisi `adjustment_qty`, sehingga selalu 0.

### Perubahan
1. Query adjustment dipindah dari loop `mrp_products` ke method `_get_fg_adjustment_qty(product)`.
   Filter dan rumus **sama persis** dengan kode asli (lihat di bawah): stock move `done`, tanpa scrap,
   tanpa picking, lokasi internal <-> inventory, `stock.move.date` dalam periode closing; qty = in - out.
2. Loop `mrp_products` memanggil `closing._get_fg_adjustment_qty(product)` (hasil RSS I/RSS III/Cutting tidak berubah).
3. Bagian Compo memanggil method yang sama, lalu mengisi `'adjustment_qty'` di `values_to_create_compo`.
4. `adjustment_account_id` Compo dibawa dari closing sebelumnya, sama seperti RSS I/RSS III/Cutting.

Jurnal adjustment Compo dibuat oleh `create_move_entries_fg_karet` yang sudah ada (berlaku untuk semua baris
Finish Good), selama Adjustment Account baris Compo terisi. Closing pertama setelah perubahan ini: isi
Adjustment Account Compo sekali (sebelumnya kosong); bulan berikutnya terbawa otomatis.

### Kode asli (sebelum diubah), di loop `mrp_products` fungsi `compute_initial_and_cost_fg2`

```python
adjustment_out_moves = self.env['stock.move'].search([
    ('product_id', '=', product.id),
    ('state', '=', 'done'),
    ('scrap_ids', '=', False),
    ('picking_id', '=', False),
    ('location_id.usage', '=', 'internal'),
    ('location_dest_id.usage', '=', 'inventory'),
    ('date', '>=', closing.date_from.strftime('%Y-%m-%d 00:00:00')),
    ('date', '<=', closing.date_to.strftime('%Y-%m-%d 23:59:59')),
])

adjustment_in_moves = self.env['stock.move'].search([
    ('product_id', '=', product.id),
    ('state', '=', 'done'),
    ('scrap_ids', '=', False),
    ('picking_id', '=', False),
    ('location_id.usage', '=', 'inventory'),
    ('location_dest_id.usage', '=', 'internal'),
    ('date', '>=', closing.date_from.strftime('%Y-%m-%d 00:00:00')),
    ('date', '<=', closing.date_to.strftime('%Y-%m-%d 23:59:59')),
])

# Hitung qty adjustment (in - out)
adjustment_qty = (
    sum(adjustment_in_moves.mapped('product_uom_qty')) if adjustment_in_moves else 0.0
) - (
    sum(adjustment_out_moves.mapped('product_uom_qty')) if adjustment_out_moves else 0.0
)
```

### Uji
- Sebelum perubahan: 3 adjustment uji (Compo, RSS I, RSS III) dibuat bersamaan di dalam periode closing ->
  RSS I dan RSS III ketarik, Compo 0.
- Setelah perubahan: Compo adjustment ketarik.
- Uji regresi: closing yang sama dihitung dengan kode sebelum dan sesudah perubahan; semua angka Finish Good
  dan bahan baku harus sama kecuali Adjustment Compo dan turunannya.

---

## [FIX 05/11/2026 - Alfi (KSI)] Tanggal Menjadi TM, status closing plantation dibekukan, perubahan TM tersimpan, dilindungi dan tercatat

**File:** `models/closing_plantation.py`
**Perlu upgrade modul:** ya, `-u c10i_lhm_v16,ny_closing` (versi `c10i_lhm_v16` naik ke 0.2; migrasi mengisi Tanggal Menjadi TM dari Tahun Menjadi TM). **Prasyarat:** perbaikan *Field GAE Distribution di form Journal Item lewat kode* (ny_closing_gae) dan reset view `account.move.line.form`, kalau tidak upgrade `c10i_lhm_v16` gagal.

### Masalah
Blok tanam yang sudah di-TM-kan kembali menjadi TBM (contoh Pisang Cavendish Blok B), dan perubahan status blok hari ini ikut mengubah closing plantation bulan-bulan sebelumnya. Tahun Menjadi TM bisa diubah siapa saja tanpa riwayat. Selain itu Tahun Menjadi TM yang baru diisi di form tidak tersimpan: status langsung berubah TM di layar, tetapi setelah Save lalu refresh/buka lagi kembali TBM.

### Penyebab
`lhm.plant.block.status` dihitung dari Tahun Menjadi TM (`tm_year`); bila `tm_year` kosong/berubah, status kembali TBM. `closing.plantation.status` adalah field *related* (store) ke status blok, sehingga setiap perubahan status blok ikut mengubah closing lama. Tidak ada pembatasan hak ubah maupun riwayat perubahan. Di form, field Tahun Menjadi TM dibuat readonly begitu status TM (`attrs readonly status = tm`). Karena status langsung dihitung TM saat tahun diisi, field berubah readonly sebelum Save, dan Odoo tidak mengirim nilai field readonly (tanpa `force_save`), sehingga nilai tidak tersimpan dan status kembali TBM.

### Perubahan
- `lhm.plant.block`: field baru `tm_date` (Tanggal Menjadi TM, tracking); `tm_year` menjadi compute store dari `tm_date`. Tombol *Tanaman Menghasilkan* mengisi tanggal hari ini.
- Versi `c10i_lhm_v16` naik ke 0.2; `migrations/0.2/pre-migrate.py` mengisi `tm_date` = 1 Januari dari `tm_year` yang sudah ada (tanggal pastinya dikoreksi kebun).
- `lhm.plant.block`: `mail.thread`, `tracking` pada status, chatter di form.
- Form blok tanam: field Tanggal Menjadi TM bisa diubah Plantation Manager kapan saja (user lain readonly) dan memakai `force_save`; dulu readonly begitu status TM sehingga nilai tidak tersimpan. Field bantu `can_edit_tm` (compute, tidak disimpan).
- `_check_tm_change` (dipanggil dari `write`): hanya Plantation Manager; tidak boleh melebihi hari ini/tahun berjalan; blok TBM yang menjadi TM tidak boleh sebelum awal period Open paling awal (`_get_tm_min_date`; tanpa period Open: awal bulan berjalan). Koreksi blok yang sudah TM tetap boleh dan tercatat di chatter.
- `closing.plantation.status`: dari related menjadi compute store dari blok saat closing dibuat (dibekukan).

### Kode asli (sebelum diubah)

`models/closing_plantation.py` (baris 100):

```python
status = fields.Selection(related='plant_block_id.status', store=True)
```

### Uji
- Migrasi: blok yang punya Tahun Menjadi TM terisi Tanggal Menjadi TM 1 Januari tahun itu; blok TM tanpa Tahun TM tetap kosong (dilengkapi kebun).
- Plantation Manager mengisi Tanggal Menjadi TM blok TBM (tanggal di period Open), Save, refresh: status tetap TM dan Tahun Menjadi TM terisi.
- Blok TBM yang diisi tanggal/tahun sebelum awal period Open paling awal: ditolak (pesan menyebut tanggal batasnya).
- Tanggal/tahun yang akan datang: ditolak.
- Blok yang sudah TM dikoreksi Plantation Manager (termasuk blok TM yang Tahun TM-nya kosong dilengkapi tahun lama): berhasil, tercatat di chatter.
- User non Plantation Manager: field readonly di form; perubahan lewat kode/import ditolak. Save form tanpa mengubah field ini tetap berhasil.
- Mengubah status blok: closing plantation bulan lalu tidak ikut berubah.

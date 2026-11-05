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

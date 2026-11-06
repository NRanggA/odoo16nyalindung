# CHANGELOG c10i_stock

Catatan perubahan modul `c10i_stock` di luar developer utama.
Setiap perubahan ditandai di kode dengan komentar `# [FIX <tanggal> - <nama>] ... # [FIX <tanggal>] END`
(di XML: `<!-- [FIX ...] -->`; cari dengan `grep -rn "FIX <tanggal>"`). Kode asli yang diubah/dipindah disimpan di bawah.

---

## [FIX 06/11/2026 - Alfi (KSI)] Kolom Asal / Tujuan di Stock Card

**File:** `report/report_stock_card.py`
**Perlu upgrade modul:** tidak, cukup restart Odoo (hanya kode laporan).

### Masalah
Stock Card hanya menampilkan nomor dokumen, sehingga tujuan barang keluar (customer DO) dan asal barang masuk harus dicari manual dari data lain.

### Penyebab
Laporan Stock Card tidak menampilkan pihak atau tujuan transaksi.

### Perubahan
- Kolom baru "Asal / Tujuan" setelah Transaction; kolom Penerimaan, Pengeluaran, Satuan, Balance bergeser satu (D–G).
- `_get_asal_tujuan`: customer (retur dari customer diberi keterangan), vendor, Store Issue = lokasi kebun / aktivitas / karyawan, bahan atau hasil produksi, Scrap, Penyesuaian stok, nama tipe transaksi (misalnya retur NAP), atau lokasi lawan untuk pindah antar lokasi.
- Field plantation, MRP, dan karyawan dibaca hanya bila ada (c10i_stock tidak bergantung pada modul itu).
- Perhitungan saldo tidak diubah.

### Kode asli (sebelum diubah)

`report/report_stock_card.py` (baris 249):

```python
sheet.set_column('C:C', 10)
```

`report/report_stock_card.py` (baris 252):

```python
sheet.set_column('F:F', 20)
```

`report/report_stock_card.py` (baris 280–283):

```python
sheet.write(row, 2, 'Penerimaan', wbf['header'])
sheet.write(row, 3, 'Pengeluaran', wbf['header'])
sheet.write(row, 4, 'Satuan', wbf['header'])
sheet.write(row, 5, 'Balance', wbf['header'])
```

`report/report_stock_card.py` (baris 293):

```python
sheet.write(row, 5, opening, wbf['total_float'])
```

`report/report_stock_card.py` (baris 328–329):

```python
sheet.write(row, 2, '', wbf['negative'])
sheet.write(row, 3, qty, wbf['negative'])
```

`report/report_stock_card.py` (baris 331–332):

```python
sheet.write(row, 2, qty, wbf['positive'])
sheet.write(row, 3, '', wbf['positive'])
```

`report/report_stock_card.py` (baris 334):

```python
sheet.write(row, 4, move.product_id.uom_id.name, wbf['content'])
```

`report/report_stock_card.py` (baris 338):

```python
sheet.write(row, 5, balance, wbf['total_float'])
```

`report/report_stock_card.py` (baris 343–344):

```python
sheet.merge_range(row, 0, row, 4, 'Saldo Akhir', wbf['header'])
sheet.write(row, 5, balance, wbf['total_float'])
```

### Uji
- Stock Card produk yang dijual (Compo, WH/Stock/Pabrik): DO berisi nama customer, retur customer bertanda (retur), hasil MO berisi Hasil produksi.
- Stock Card bahan (Meroke Kalnit, WH/Stock): penerimaan berisi nama vendor, Store Issue berisi lokasi / aktivitas / karyawan.
- Saldo awal, Penerimaan, Pengeluaran, Balance, Saldo Akhir sama dengan sebelum perubahan (hanya bergeser satu kolom).

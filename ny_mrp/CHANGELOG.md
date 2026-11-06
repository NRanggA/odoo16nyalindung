# CHANGELOG ny_mrp

Catatan perubahan modul `ny_mrp` di luar developer utama.
Setiap perubahan ditandai di kode dengan komentar `# [FIX <tanggal> - <nama>] ... # [FIX <tanggal>] END`
(di XML: `<!-- [FIX ...] -->`; cari dengan `grep -rn "FIX <tanggal>"`). Kode asli yang diubah/dipindah disimpan di bawah.

---

## [FIX 06/11/2026 - Alfi (KSI)] Jumlah Lembar WIP Compo di Manufacturing Order dan Laporan Produksi

**File:** `models/mrp_production.py`, `views/mrp_production_view.xml`, `report/report_production_order_xlsx.py`
**Perlu upgrade modul:** ya, `-u ny_mrp` (field baru).

### Masalah
Pabrik perlu mencatat jumlah lembar Compo saat WIP Compo dibuat untuk kontrol fisik, dan melihatnya di Laporan Produksi. Belum ada tempat untuk mengisinya.

### Penyebab
Fitur belum ada: MO hanya mencatat berat (Kg). Selain itu rumus DRC di sheet Olahan Lump menunjuk nomor kolom yang ditulis tetap (7 dan 3), sehingga akan salah bila ada kolom baru.

### Perubahan
- `mrp.production.qty_lembar` (Jumlah Lembar, bilangan bulat, tracking): tampil di form MO hanya untuk produk WIP Compo.
- `_check_qty_lembar_before_done` dipanggil di awal `button_mark_done`: MO WIP Compo dengan Jumlah Lembar kosong/0 ditolak sebelum wizard konfirmasi. Sesudah Done tetap bisa dikoreksi user MRP (tercatat di riwayat).
- Laporan Produksi, sheet Olahan Lump: kolom Lembar setelah Asam Semut + total; rumus DRC memakai posisi kolom Compo/Lump dari header.
- MO lama tetap kosong (tidak ada migrasi data).

### Kode asli (sebelum diubah)

`models/mrp_production.py`: hanya tambahan, tidak ada baris asli yang diubah.

`views/mrp_production_view.xml`: hanya tambahan, tidak ada baris asli yang diubah.

`report/report_production_order_xlsx.py` (baris 450):

```python
f"={xl_rowcol_to_cell(next_row, 7)}/{xl_rowcol_to_cell(next_row, 3)}",
```

`report/report_production_order_xlsx.py` (baris 490):

```python
f"={xl_rowcol_to_cell(next_row, 7)}/{xl_rowcol_to_cell(next_row, 3)}",
```

### Uji
- MO WIP Compo Draft disimpan tanpa Jumlah Lembar: boleh.
- Mark as Done dengan Jumlah Lembar kosong/0: ditolak dengan pesan.
- Mark as Done dengan Jumlah Lembar terisi: berhasil; field tetap bisa diubah setelah Done, perubahan tercatat di chatter.
- MO selain WIP Compo (Sheet, Compo, RSS): field tidak tampil, Mark as Done tidak terpengaruh.
- Laporan Produksi (Olah Bahan Baku dan Barang Jadi): kolom Lembar dan totalnya tampil; DRC sama dengan sebelum perubahan (Compo / Lump).

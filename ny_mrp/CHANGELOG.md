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

---

## [FIX 10/11/2026 - Alfi (KSI)] Jumlah Lembar juga di MO Compo, dengan Selisih Lembar di Laporan Produksi

**File:** `models/mrp_production.py`, `views/mrp_production_view.xml`, `report/report_production_order_xlsx.py`
**Perlu upgrade modul:** ya, `-u ny_mrp` (view form MO).

### Masalah
Jumlah lembar hanya dicatat di MO WIP Compo. Berat Compo selalu lebih kecil dari WIP karena pengeringan, jadi lembar yang hilang atau rusak selama pengeringan tidak terlihat tanpa jumlah lembar di sisi Compo.

### Penyebab
Jumlah Lembar sebelumnya sengaja dibatasi untuk MO WIP Compo saja. Diperluas ke MO Compo sesuai keputusan review 10/11/2026.

### Perubahan
- MO Compo: field Jumlah Lembar tampil di bawah Quantity, terisi otomatis dari MO WIP Compo asal saat Asal MO dipilih (atau saat MO dibuat dengan Asal MO), dan bisa diubah. Bila satu WIP dipecah ke beberapa MO Compo, yang terisi adalah sisa lembar yang belum dipakai.
- MO Compo wajib berisi Jumlah Lembar sebelum Mark as Done (aturan yang sama dengan MO WIP Compo).
- Laporan Produksi, sheet Olahan Lump: kolom Lembar Compo (jumlah lembar MO Compo selesai) dan Selisih Lembar (rumus Lembar - Lembar Compo, kosong bila salah satu belum diisi) setelah kolom Compo, berikut totalnya. Rumus DRC tetap memakai posisi kolom dari header.

### Kode asli (sebelum diubah)

`models/mrp_production.py` (baris 14–15):

```python
# [FIX 06/11/2026 - Alfi (KSI)] Jumlah lembar WIP Compo untuk kontrol fisik di pabrik. Hanya untuk MO WIP Compo
# (MO Compo / barang jadi tidak diisi). Wajib sebelum Mark as Done, sesudahnya tetap bisa dikoreksi
```

`models/mrp_production.py` (baris 68):

```python
return super(MrpProduction, self).create(vals)
```

`models/mrp_production.py` (baris 89):

```python
return self.product_id.name == 'WIP Compo'
```

`models/mrp_production.py` (baris 94):

```python
raise UserError(_("Isi Jumlah Lembar dulu sebelum Mark as Done (MO WIP Compo %s).") % rec.name)
```

`views/mrp_production_view.xml` (baris 35):

```xml
<!-- [FIX 06/11/2026 - Alfi (KSI)] Jumlah Lembar hanya tampil di MO WIP Compo -->
```

`views/mrp_production_view.xml` (baris 37):

```xml
<field name="qty_lembar" attrs="{'invisible': [('product_name', '!=', 'WIP Compo')]}"/>
```

`report/report_production_order_xlsx.py`: hanya tambahan, tidak ada baris asli yang diubah.

### Uji
- MO Compo baru, Asal MO = MO WIP Compo berlembar 52 → Jumlah Lembar terisi 52; diubah 50 → tersimpan, tercatat di chatter.
- Jumlah Lembar 0 → Mark as Done ditolak.
- Laporan Produksi: baris WIP itu Lembar 52, Lembar Compo 50, Selisih 2; MO lama kolom baru kosong; total dan DRC benar.
- MO lain (Sheet, RSS) tidak berubah, field tidak tampil.

---

## [FIX 10/11/2026 - Alfi (KSI)] Laporan Produksi: angka rumus tampil tanpa Enable Editing; Selisih Lembar menunggu semua MO Compo selesai

**File:** `report/report_production_order_xlsx.py`
**Perlu upgrade modul:** ya, `-u ny_mrp` (kode laporan; cukup restart, upgrade aman).

### Masalah
File Excel Laporan Produksi yang baru di-download (Protected View) menampilkan 0 untuk semua rumus (DRC, TOTAL, Selisih Lembar) sampai user klik Enable Editing. Selain itu Selisih Lembar terlihat besar bila satu WIP dipecah ke beberapa MO Compo dan baru sebagian yang selesai.

### Penyebab
xlsxwriter menulis rumus tanpa nilai hasil (tersimpan 0); Excel baru menghitung ulang setelah file boleh diedit. Selisih dihitung dari MO Compo yang sudah Done saja.

### Perubahan
- Kelas `_SheetDenganNilai` membungkus worksheet Olahan Lateks dan Olahan Lump: mencatat angka yang ditulis, lalu setiap `write_formula` diberi nilai hasil (SUM, AVERAGE, + - * /; pembagian nol atau AVERAGE kosong = #DIV/0! seperti Excel). Rumus tetap ada.
- Selisih Lembar hanya diisi bila semua MO Compo dari WIP itu sudah Done atau Cancel.

### Kode asli (sebelum diubah)

`report/report_production_order_xlsx.py` (baris 201):

```python
worksheet = workbook.add_worksheet("Olahan Lateks")
```

`report/report_production_order_xlsx.py` (baris 367):

```python
worksheet2 = workbook.add_worksheet("Olahan Lump")
```

`report/report_production_order_xlsx.py` (baris 479):

```python
if mo.qty_lembar and lembar_compo:
```

### Uji
- Download laporan, buka tanpa Enable Editing: DRC, TOTAL, Lembar Compo, Selisih tampil dengan angka benar; setelah Enable Editing angka sama.
- WIP dengan satu MO Compo Done dan satu masih proses: Selisih kosong; setelah semua Done: Selisih terisi.

---

## [FIX 23/11/2026 - Alfi (KSI)] Jumlah Lembar MO Compo diisi manual dari hasil hitung

**File:** `models/mrp_production.py`, `views/mrp_production_view.xml`
**Perlu upgrade modul:** ya, `-u ny_mrp` (kode Python dan komentar view; tidak ada perubahan database).

### Masalah
Jumlah Lembar MO Compo terisi otomatis dari sisa lembar MO WIP Compo asal. Bila operator langsung menerima angka itu tanpa menghitung, Lembar Compo selalu sama dengan Lembar WIP dan Selisih Lembar di Laporan Produksi selalu 0, sehingga lembar yang hilang atau rusak saat pengeringan tidak pernah terlihat.

### Penyebab
Isian otomatis saat Asal MO dipilih (onchange) dan saat MO Compo dibuat dengan Asal MO (create).

### Perubahan
- Isian otomatis Jumlah Lembar MO Compo dihapus (onchange `source_mo_id`, isian di `create`, dan fungsi `_get_sisa_lembar_asal`). `create` kembali seperti kode asli.
- Jumlah Lembar MO Compo kosong sampai diisi operator dari hasil hitung; Mark as Done tetap ditolak bila Jumlah Lembar kosong/0.
- Laporan Produksi tidak berubah: Lembar Compo dan Selisih Lembar tetap dihitung dari angka yang diisi.

### Kode asli (sebelum diubah)

`models/mrp_production.py` (baris 17–18):

```python
# [FIX 10/11/2026 - Alfi (KSI)] juga untuk MO Compo (barang jadi): terisi dari lembar MO WIP Compo asal
# dan bisa diubah, supaya jumlah lembar masuk dan keluar pengeringan bisa dibandingkan.
```

`models/mrp_production.py` (baris 71–76):

```python
# [FIX 10/11/2026 - Alfi (KSI)] MO Compo yang dibuat dengan Asal MO langsung terisi Jumlah Lembar dari WIP asal
res = super(MrpProduction, self).create(vals)
if res.product_id.name == 'Compo' and res.source_mo_id and not res.qty_lembar:
    res.qty_lembar = res._get_sisa_lembar_asal()
return res
# [FIX 10/11/2026] END
```

`models/mrp_production.py` (baris 105–120):

```python

# [FIX 10/11/2026 - Alfi (KSI)] Jumlah Lembar MO Compo diisi dari MO WIP Compo asal. Bila satu WIP dipecah ke
# beberapa MO Compo, yang diisi adalah sisa lembar yang belum dipakai MO Compo lain.
def _get_sisa_lembar_asal(self):
    self.ensure_one()
    src = self.source_mo_id
    if not src or not src.qty_lembar:
        return 0
    lain = src.finish_mo_ids.filtered(lambda m: m.id != self._origin.id and m.state != 'cancel')
    return max(src.qty_lembar - sum(lain.mapped('qty_lembar')), 0)

@api.onchange('source_mo_id')
def _onchange_source_mo_qty_lembar(self):
    if self.product_id.name == 'Compo' and self.state in ('draft', 'confirmed', 'progress', 'to_close'):
        self.qty_lembar = self._get_sisa_lembar_asal()
# [FIX 10/11/2026] END
```

`views/mrp_production_view.xml` (baris 36):

```xml
<!-- [FIX 10/11/2026 - Alfi (KSI)] juga di MO Compo (terisi dari WIP asal) -->
```

### Uji
- MO Compo baru dengan Asal MO = MO WIP Compo berlembar: Jumlah Lembar kosong (0), baik lewat form maupun saat dibuat dengan Asal MO.
- Mark as Done dengan Jumlah Lembar 0: ditolak dengan pesan.
- Jumlah Lembar diisi lebih kecil dari lembar WIP, lalu Done: Laporan Produksi menampilkan Selisih Lembar sesuai.
- MO WIP Compo tidak berubah (tetap wajib diisi).

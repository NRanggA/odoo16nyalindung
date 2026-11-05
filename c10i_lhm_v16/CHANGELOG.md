# CHANGELOG c10i_lhm_v16

Catatan perubahan modul `c10i_lhm_v16` di luar developer utama.
Setiap perubahan ditandai di kode dengan komentar `# [FIX <tanggal> - <nama>] ... # [FIX <tanggal>] END`
(di XML: `<!-- [FIX ...] -->`; cari dengan `grep -rn "FIX <tanggal>"`). Kode asli yang diubah/dipindah disimpan di bawah.

---

## [FIX 05/11/2026 - Alfi (KSI)] Tanggal Menjadi TM, status closing plantation dibekukan, perubahan TM tersimpan, dilindungi dan tercatat

**File:** `__manifest__.py`, `migrations/0.2/pre-migrate.py`, `models/lhm_plant_block.py`, `views/lhm_views.xml`
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

`__manifest__.py` (baris 20):

```python
'version': '0.1',
```

`migrations/0.2/pre-migrate.py`: file baru (tidak ada kode asli).

`models/lhm_plant_block.py` (baris 82):

```python
status              = fields.Selection(selection=[('tbm','Tanaman Belum Menghasilkan'),('tm','Tanaman Menghasilkan')],string="Status", compute="_compute_time_plant", store=True)
```

`models/lhm_plant_block.py` (baris 84):

```python
tm_year             = fields.Integer(string='Tahun Menjadi TM')
```

`models/lhm_plant_block.py` (baris 133–134):

```python
self.status = 'tm'
self.tm_year = int(time.strftime('%Y'))
```

`views/lhm_views.xml` (baris 1124):

```xml
<field name="tm_year" attrs="{'readonly': [('status','=','tm')]}"/>
```

### Uji
- Migrasi: blok yang punya Tahun Menjadi TM terisi Tanggal Menjadi TM 1 Januari tahun itu; blok TM tanpa Tahun TM tetap kosong (dilengkapi kebun).
- Plantation Manager mengisi Tanggal Menjadi TM blok TBM (tanggal di period Open), Save, refresh: status tetap TM dan Tahun Menjadi TM terisi.
- Blok TBM yang diisi tanggal/tahun sebelum awal period Open paling awal: ditolak (pesan menyebut tanggal batasnya).
- Tanggal/tahun yang akan datang: ditolak.
- Blok yang sudah TM dikoreksi Plantation Manager (termasuk blok TM yang Tahun TM-nya kosong dilengkapi tahun lama): berhasil, tercatat di chatter.
- User non Plantation Manager: field readonly di form; perubahan lewat kode/import ditolak. Save form tanpa mengubah field ini tetap berhasil.
- Mengubah status blok: closing plantation bulan lalu tidak ikut berubah.

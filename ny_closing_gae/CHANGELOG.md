# CHANGELOG ny_closing_gae

Catatan perubahan modul `ny_closing_gae` di luar developer utama.
Setiap perubahan ditandai di kode dengan komentar `# [FIX <tanggal> - <nama>] ... # [FIX <tanggal>] END`
(di XML: `<!-- [FIX ...] -->`; cari dengan `grep -rn "FIX <tanggal>"`). Kode asli yang diubah/dipindah disimpan di bawah.

---

## [FIX 05/11/2026 - Alfi (KSI)] Field GAE Distribution di form Journal Item lewat kode (prasyarat upgrade modul)

**File:** `views/account_move_line_view.xml`
**Perlu upgrade modul:** ya, `-u ny_closing_gae`. **Sebelum upgrade**, edit manual di view standar harus di-reset: Settings > Technical > Views > `account.move.line.form` > Reset View Architecture (hard).

### Masalah
Upgrade modul yang memvalidasi view Journal Item (misalnya `c10i_lhm_v16`) gagal dengan pesan "Field gae_distribution_id does not exist".

### Penyebab
Field GAE Distribution ditambahkan ke view standar `account.view_move_line_form` dengan mengedit view langsung dari UI (arch_updated, 04/06/2026). View standar divalidasi sebelum `ny_closing_gae` dimuat, sehingga field itu belum dikenal.

### Perubahan
- View baru `view_move_line_form_gae` (inherit `account.view_move_line_form`) menambahkan `gae_distribution_id` sesudah `quantity`.
- Edit manual di view standar harus di-reset sekali sebelum upgrade.

### Kode asli (sebelum diubah)

`views/account_move_line_view.xml`: hanya tambahan, tidak ada baris asli yang diubah.

### Uji
- Sesudah reset view dan upgrade `ny_closing_gae`, field GAE Distribution tetap tampil di form Journal Item.
- Upgrade `c10i_lhm_v16` berhasil (sebelumnya gagal).

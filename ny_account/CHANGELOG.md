# CHANGELOG ny_account

Catatan perubahan modul `ny_account` di luar developer utama.
Setiap perubahan ditandai di kode dengan komentar `# [FIX <tanggal> - <nama>] ... # [FIX <tanggal>] END`
(di XML: `<!-- [FIX ...] -->`; cari dengan `grep -rn "FIX <tanggal>"`). Kode asli yang diubah/dipindah disimpan di bawah.

---

## [FIX 24/11/2026 - Task 20] Confirm Payment beberapa pembayaran dalam satu transaksi

**File:** `models/account_payment.py`, `wizard/action_confirm_payment.py`, `models/account_move.py`.
**Perlu upgrade modul:** tidak (perubahan Python, restart Odoo setelah deployment).

### Masalah dan penyebab
Confirm Payment untuk beberapa pembayaran memakai `self.id`/`active_id`, sehingga terjadi Expected singleton atau hanya satu pembayaran yang diproses. Jalur posting juga mengembalikan hasil dari dalam loop dan memanggil parent pada seluruh recordset. Commit manual di `account.move.action_post` dapat memotong transaksi sebelum seluruh proses selesai.

### Perubahan
- Wizard menerima `active_ids`, tetap mendukung `active_id` tunggal, dan mempertahankan context pengguna.
- Validasi dokumen tersedia, status Draft, hak akses tulis, serta larangan memilih kedua pasangan Internal Transfer; diperiksa kembali saat konfirmasi.
- Parent posting dipanggil untuk satu pembayaran per iterasi. Penomoran, rekonsiliasi, pasangan transfer, dan biaya administrasi tetap memakai jalur yang sudah ada.
- Hapus commit manual agar kegagalan request membatalkan seluruh batch. Sequence PostgreSQL dapat tetap memiliki nomor terlewat setelah rollback.
- Hanya memindahkan task 20 dari `ny_mom_fixes` port 8071; tidak menambahkan dependency addon tersebut atau mengubah task lain.

### Hasil validasi 24/11/2026

11 skenario lulus pada database lokal pengujian `odoo_mom_test`: satu pembayaran; tiga pembayaran; rollback kegagalan pembayaran kedua; status berubah sesudah wizard dibuka; pilihan hilang/kosong/model salah; kompatibilitas `active_id` dan penolakan posting ulang; ID duplikat; penolakan hak akses tulis; penolakan kedua pasangan transfer; jurnal biaya administrasi; serta tidak ada commit terlalu awal.

Metode dari file yang disiapkan dimuat ke proses Odoo shell terpisah; override task 20 dari `ny_mom_fixes` dilewati agar tidak menutupi hasil. Semua skenario diakhiri rollback, commit manual diblokir, dan penomoran menggunakan sequence sementara. Ini pengujian backend; belum merupakan deployment atau uji antarmuka produksi.

### Kode asli yang diganti

Awal `models/account_payment.py:action_post`:

```python
    def action_post(self):
        for rec in self:
            # if rec.env.context.get('from_wizard'):
            #     continue
            if not rec.env.context.get('from_wizard'):
                if rec.is_internal_transfer:
                    confirmation_message = f"Apakah anda yakin ingin memproses dari rekening {rec.journal_id.name} ke {rec.destination_journal_id.name} ?"
                else:
                    confirmation_message = "Apakah anda yakin ingin memproses dari rekening: %s ?" % rec.journal_id.name
                return {
                    'type'      : 'ir.actions.act_window',
                    'res_model' : 'wizard.action.confirm.payment',
                    'view_mode' : 'form',
                    'view_id'   : self.env.ref('ny_account.view_wizard_action_confirm_payment').id,
                    'target'    : 'new',
                    'context': {
                        'active_id'             : self.id,
                        'active_model'          : self._name,
                        'confirmation_message'  : confirmation_message
                    },
                }

            res = super().action_post()
```

`return res` sebelumnya berada di dalam loop pembayaran; sekarang setelah loop.

`wizard/action_confirm_payment.py:action_confirm`:

```python
    def action_confirm(self):
        active_model = self.env.context.get('active_model')
        active_id = self.env.context.get('active_id')
        if active_model == 'account.payment':
            payment_record = self.env[active_model].browse(active_id)
            # if payment_record.employee_expense_id:
            payment_record.with_context(from_wizard=True).action_post()

        return {'type': 'ir.actions.act_window_close'}
```

`models/account_move.py:action_post` menghapus baris:

```python
        self.env.cr.commit()
```

---

## [FIX 13/11/2026 - Alfi (KSI)] Report Customer Invoice ikut menampilkan credit note sebagai baris minus

**File:** `report/report_customer_excel.py`
**Perlu upgrade modul:** tidak (hanya Python, cukup restart Odoo).

### Masalah
Invoice yang dibatalkan atau dikurangi lewat credit note (Add Credit Note) tetap tampil penuh di Report Customer Invoice (menu Sales dan Accounting), sehingga penjualan di laporan lebih besar dari yang sebenarnya.

### Penyebab
Query laporan hanya membaca dokumen `out_invoice` yang Posted. Invoice yang di-reverse tetap Posted, sedangkan credit note (`out_refund`) yang menolkannya tidak pernah dibaca.

### Perubahan
- `get_query`: membaca `out_invoice` dan `out_refund`. Untuk credit note, Quantity, Total Harga, dan Net AR ditampilkan minus. Harga satuan tetap.
- Kolom baru di paling kanan: **Jenis Dokumen** (Invoice / Credit Note) dan **Referensi** (untuk credit note: invoice yang dibalik; untuk invoice: credit note yang membaliknya, bila ada).
- Kolom lama tidak bergeser.

### Kode asli (sebelum diubah)

`report/report_customer_excel.py` (baris 209):

```python
ail.quantity,
```

`report/report_customer_excel.py` (baris 211):

```python
ail.price_subtotal,
```

`report/report_customer_excel.py` (baris 217):

```python
(ail.price_subtotal -
```

`report/report_customer_excel.py` (baris 222):

```python
) AS outstanding_amount
```

`report/report_customer_excel.py` (baris 228):

```python
WHERE ai.move_type = 'out_invoice'
```

`report/report_customer_excel.py` (baris 274):

```python
'Harga', 'Total Harga', 'Term of Payment', 'Down Payment', 'Net AR']
```

`report/report_customer_excel.py` (baris 285):

```python
for invoice_date, invoice_name, partner_id, plantation_location_type_id, plantation_varieties_id, plantation_location_id, plantation_activity_id, product_id, description, quantity, price_unit, price_subtotal, term_of_payment, down_payment, outstanding_amount in results:
```

### Uji
- Periode dengan invoice yang dibatalkan penuh lewat credit note: kedua dokumen tampil, jumlah Total Harga keduanya 0.
- Invoice tanpa credit note tampil seperti sebelumnya, kolom Referensi berisi `-`.
- Credit note yang tanggalnya di luar periode tidak ikut tampil, tetapi nomornya terlihat di kolom Referensi invoice.

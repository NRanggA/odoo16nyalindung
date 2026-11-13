# CHANGELOG ny_account

Catatan perubahan modul `ny_account` di luar developer utama.
Setiap perubahan ditandai di kode dengan komentar `# [FIX <tanggal> - <nama>] ... # [FIX <tanggal>] END`
(di XML: `<!-- [FIX ...] -->`; cari dengan `grep -rn "FIX <tanggal>"`). Kode asli yang diubah/dipindah disimpan di bawah.

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

Nyalindung Request UoM Lock
===========================

Addon Odoo 16 untuk task 17. PR/MR baru memakai satuan dasar produk. RFQ/PO dari PR dengan kebijakan aktif mengikuti satuan PR sumber, termasuk konversi satuan pembelian dan minimum vendor. Konfigurasi dokumen lama dipertahankan.

Instalasi baru membutuhkan purchase_request dan c10i_material_request. Untuk database yang sudah memakai task 17 dari ny_mom_fixes, pindahkan XML ID field dan view sebelum meng-upgrade ny_mom_fixes dan memasang addon ini dalam satu proses upgrade Odoo.

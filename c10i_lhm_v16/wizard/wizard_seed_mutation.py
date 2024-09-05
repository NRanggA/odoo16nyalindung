from odoo import models, fields, api, _


class WizardSeedMutation(models.TransientModel):
    _name           = 'wizard.seed.mutation'
    _description    = 'Wizard Mutasi Bibit'

    period_id       = fields.Many2one("account.period", string="Periode", ondelete="restrict")
    date_start      = fields.Date('Date Start')
    date_end        = fields.Date('Date End')
    date_type       = fields.Selection([
                        ('period', 'Periode'),
                        ('custom', 'Custom'),
                    ], string='Date Type')
    product_id      = fields.Many2one('product.product', string='Product')
    location_ids    = fields.Many2many('lhm.location', string='Lokasi')


    def action_get_products(self):
        date_start  = self.date_start if self.date_type == 'custom' else self.period_id.date_start
        date_end    = self.date_end if self.date_type == 'custom' else self.period_id.date_stop

        semai_lines = self.env['seed.semai.line'].search([
            ('seed_semai_id.date', '>=', date_start),
            ('seed_semai_id.date', '<=', date_end),
            ('product_id', '=', self.product_id.id),
            ('location_id', 'in', self.location_ids.ids)
        ])

        release_lines = self.env['seed.release.line'].search([
            ('seed_release_id.date', '>=', date_start),
            ('seed_release_id.date', '<=', date_end),
            ('product_id', '=', self.product_id.id),
            ('location_id', 'in', self.location_ids.ids)
        ])

        # Hapus data lama di SeedMutation 
        self.env['seed.mutation'].search([]).unlink()

        balance = 0

        # Simpan data SeedSemai dan hitung saldo
        for line in semai_lines:
            qty = line.qty
            mutation_type = line.mutation_type_id.mutation

            # Jika jenis mutasi adalah tambah, tambahkan qty ke balance
            if mutation_type == 'tambah':
                balance += qty
            elif mutation_type == 'kurang':  # Jika jenis mutasi adalah kurang, kurangkan qty dari balance
                balance -= qty

            self.env['seed.mutation'].create({
                'product_id'        : line.product_id.id,
                'date'              : line.seed_semai_id.date,
                'mutation_type_id'  : line.mutation_type_id.id,
                'location_id'       : line.location_id.id,
                'qty'               : line.qty,
                'satuan_id'         : line.satuan_id.id,
                'balance'           : balance
            })

        # Simpan data SeedRelease dan hitung saldo
        for line in release_lines:
            qty = line.qty
            mutation_type = line.mutation_type_id.mutation

            # Jika jenis mutasi adalah tambah, tambahkan qty ke balance
            if mutation_type == 'tambah':
                balance += qty
            elif mutation_type == 'kurang':  
                balance -= qty

            self.env['seed.mutation'].create({
                'product_id'        : line.product_id.id,
                'date'              : line.seed_release_id.date,
                'mutation_type_id'  : line.mutation_type_id.id,
                'location_id'       : line.location_id.id,
                'qty'               : line.qty,
                'satuan_id'         : line.satuan_id.id,
                'balance'           : balance
            })

        return {
            'type'      : 'ir.actions.act_window',
            'name'      : 'Mutasi Bibitan',
            'res_model' : 'seed.mutation',
            'view_mode' : 'tree',
            'target'    : 'current',
            'context'   : {'create': False},
            'domain'    : [],
        }
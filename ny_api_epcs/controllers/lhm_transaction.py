from odoo import http, fields
from odoo.http import request, Response
from odoo.exceptions import MissingError, ValidationError
import json
from datetime import datetime, time
from pytz import timezone, utc

from odoo.addons.c10i_base_api.controllers.main import ApiBase, HEADERS, DateEncoder, BASE_ROUTE

ROUTES = f"{BASE_ROUTE}/plantationai/lhm"

class ProfileApi(ApiBase):
    @http.route(ROUTES, auth='public', website=False, csrf=False, type='http', methods=['POST'])
    def submit_new_lhm(self):
        # check token
        check_user, message = self._verify_auth()
        if not check_user:
            return Response(json.dumps({'message': message}), headers=HEADERS, status=400)
        
        datas = self._get_payload() or {}
        existing_block_mapped = {}
        try:
            raw_list_to_create = datas.get('data', [])
            if not raw_list_to_create:
                raise ValidationError("Empty Data: Nothing to create")
            # Validate Mandatory Field
            mandatory_fields = ['date','kemandoran_id']
            for line_to_check in raw_list_to_create:
                to_check_keys = line_to_check.keys()
                if any([(x not in to_check_keys) for x in mandatory_fields]):
                    raise ValidationError(f"This field are mandatory. ({','.join(mandatory_fields)})")
                for key in to_check_keys:
                    if key in mandatory_fields and not line_to_check.get(key, False):
                        raise ValidationError(f"Field '{key}' are a mandatory Field)")
                if not line_to_check.get('lhm_line_ids', []):
                    raise ValidationError("Field 'lhm_line_ids' are mandatory field and must be filled.")

            lhm_list_to_create = [] # lhm.transaction
            lhm_contractor_lines = []
            data_validation_error = []
            line_validation_error = []
            for vals in raw_list_to_create:
                ############# LHM
                lhm_lines = []
                is_lhm = None
                is_lhm_contractor = None
                for line_vals in vals.get('lhm_line_ids',[]):
                    # {
                    #     "employee_id": 2370,
                    #     "supplier_id": null, # For Contractor
                    #     "spk_number": null, # For Contractor
                    #     "attendance_type_id": 1,
                    #     "work_day": 1.0,
                    #     "is_borong": false,
                    #     "plant_block_id": 323,
                    #     "activity_id": 4892,
                    #     "product_id_1": null, >> "product_id"
                    #     "hasil_1": 20.0,
                    #     "uom_id_1": 28, >> "satuan_1"
                    #     "product_id_2": null,
                    #     "hasil_2": 0.0,
                    #     "uom_id_2": null >> "satuan_2"
                    # },
                    if is_lhm_contractor is None:
                        is_lhm_contractor = bool(line_vals.get('supplier_id', False) and line_vals.get('spk_number', False))
                    if is_lhm is None:
                        is_lhm = bool(line_vals.get('employee_id', False))

                    if not is_lhm and not is_lhm_contractor:
                        line_validation_error.append("Either 'employee_id' or 'supplier_id' and 'spk_number' must be provided in lhm_line_ids")
                        continue

                    employee = supplier = False
                    if is_lhm:
                        # Validate Employee Contract
                        employee = request.env['hr.employee'].sudo().browse(line_vals['employee_id'])
                        if not employee.contract_id:
                            line_validation_error.append("Karyawan {employee.name} ({employee.no_induk or ''}) tidak memiliki Kontrak Aktif")
                            continue
                    else:
                        supplier = request.env['res.partner'].sudo().browse(line_vals['supplier_id'])

                    if not line_vals.get('plant_block_id', False):
                        line_validation_error.append("Field 'plant_block_id' is mandatory in lhm_line_ids")
                        continue
                    
                    location_id = varieties_id = location_type_id = False
                    if line_vals['plant_block_id'] in existing_block_mapped:
                        location_id = existing_block_mapped[line_vals['plant_block_id']][0]
                        varieties_id = existing_block_mapped[line_vals['plant_block_id']][1]
                        location_type_id = existing_block_mapped[line_vals['plant_block_id']][2]
                    else:
                        plant_block = request.env['lhm.plant.block'].sudo().browse(line_vals['plant_block_id'])
                        if not plant_block:
                            line_validation_error.append(f"Plant Block dengan ID {line_vals['plant_block_id']} tidak ditemukan")
                            continue
                        location_id = plant_block.location_id.id
                        varieties_id = plant_block.varieties_id.id
                        location_type_id = plant_block.location_id.type_id.id
                        existing_block_mapped[line_vals['plant_block_id']] = (location_id, varieties_id, location_type_id)

                    if not line_vals.get('activity_id', False):
                        line_validation_error.append("Field 'activity_id' is mandatory in lhm_line_ids")
                        continue

                    if is_lhm:
                        lhm_lines.append({
                            'date': vals['date'],
                            'employee_id': line_vals.get('employee_id', False),
                            'work_day': line_vals.get('work_day', 0.0),
                            'attendance_id': line_vals.get('attendance_type_id', False),
                            # 'non_work_day': line_vals.get(' 'non_work_day', False),
                            'varieties_id': varieties_id,
                            'location_type_id': location_type_id,
                            'location_id': location_id,
                            'activity_id': line_vals.get('activity_id', False),
                            # 'work_result': line_vals.get(' 'work_result', False),
                            # 'satuan_id': line_vals.get(' 'satuan_id', False),
                            'product_id': line_vals.get('product_id_id', False),
                            'hasil_1': line_vals.get('hasil_1', 0.0),
                            'satuan_1': line_vals.get('uom_id_1', False),
                            'product_id_2': line_vals.get('product_id_2', False),
                            'hasil_2': line_vals.get('hasil_2', 0.0),
                            'satuan_2': line_vals.get('uom_id_2', False),
                            # 'is_hasil_2': line_vals.get(' 'is_hasil_2', False),
                            # 'unit_price': line_vals.get('unit_price', 0.0),
                            # 'premi': line_vals.get('premi', 0.0),
                            # 'overtime_hour': line_vals.get('overtime_hour', 0),
                            # 'penalty': line_vals.get('penalty', 0.0),
                            'contract_id': employee.contract_id.id,
                            # 'contract_wage_value': round(contract.wage / contract.wage_day, 2)
                            'contract_wage_value': round(employee.contract_id.wage / employee.contract_id.wage_day, 2)
                        })
                    else:
                        lhm_contractor_lines.append({
                            'supplier_id': line_vals.get('supplier_id', False),
                            'date': vals['date'],
                            'origin': vals.get('origin', False),
                            'spk_number': line_vals.get('spk_number', False),
                            'varieties_id': varieties_id,
                            'location_type_id': location_type_id,
                            'location_id': location_id,
                            'activity_id': line_vals.get('activity_id', False),
                            'product_id': line_vals.get('product_id_id', False),
                            'nilai': line_vals.get('hasil_1', 0.0),
                            'uom_id': line_vals.get('uom_id_1', False),
                            'product_id_2': line_vals.get('product_id_2', False),
                            'nilai2': line_vals.get('hasil_2', 0.0),
                            'uom2_id': line_vals.get('uom_id_2', False),
                        })
                
                # material_lines = []
                # for material_vals in vals.get('material_line_ids',[]):
                #     # Find material request line based on product_id, activity_id, and plant_block_id
                #     location_id = varieties_id = location_type_id = False
                #     if material_vals['plant_block_id'] in existing_block_mapped:
                #         location_id = existing_block_mapped[material_vals['plant_block_id']][0]
                #     else:
                #         plant_block = request.env['lhm.plant.block'].sudo().browse(material_vals['plant_block_id'])
                #         if not plant_block:
                #             line_validation_error.append(f"Plant Block dengan ID {material_vals['plant_block_id']} tidak ditemukan")
                #             continue
                #         location_id = plant_block.location_id.id
                #         varieties_id = plant_block.varieties_id.id
                #         location_type_id = plant_block.location_id.type_id.id
                #         existing_block_mapped[material_vals['plant_block_id']] = (location_id, varieties_id, location_type_id)
                #     if not material_vals.get('mr_id', False):
                #         line_validation_error.append("Field 'mr_id' is mandatory in material_line_ids")
                #         continue
                #     if not material_vals.get('product_id', False):
                #         line_validation_error.append("Field 'product_id' is mandatory in material_line_ids")
                #     if not material_vals.get('activity_id', False):
                #         line_validation_error.append("Field 'activity_id' is mandatory in material_line_ids")
                #     mr_lines = request.env['material.request.line'].sudo().search([
                #         ('mr_id','=', material_vals.get('mr_id', False)),
                #         ('product_id', '=', material_vals.get('product_id', False)),
                #         ('location_id', '=', location_id),
                #         ('activity_id', '=', material_vals.get('activity_id', False)),
                #     ])
                #     if mr_lines:
                #         stock_moves = mr_lines.move_ids.filtered(lambda m: m.state == 'done')
                #         if stock_moves:
                #             material_lines.append((0,0,{
                #                 'date': vals['date'],
                #                 'from_mobile_apps': True,
                #                 'move_id': stock_moves[0].id,
                #                 'picking_id': stock_moves[0].picking_id.id,
                #                 'product_id': material_vals.get('product_id', False),
                #                 'activity_id': material_vals.get('activity_id', False),
                #                 'location_id': location_id,
                #                 'product_uom_id': material_vals.get('uom_id', False),
                #                 'realization': material_vals.get('product_qty', 0.0)
                #             }))
                        # else:
                        #     line_validation_error.append(f"Material Request Line dengan Product ID {material_vals.get('product_id', False)}, Blok Tanam {material_vals.get('plant_block_id', False)}, dan Activity ID {material_vals.get('activity_id', False)} tidak memiliki Stock Move yang sudah valid.")
                
                if lhm_lines:
                    lhm_transaction = {
                        'date': vals['date'],
                        'origin': vals.get('origin', False),
                        'kemandoran_id': vals['kemandoran_id'],
                        'lhm_line_ids': list(map(lambda x: (0, 0, x), lhm_lines)),
                        # 'material_line_ids': material_lines,
                        # 'note': vals['note'],
                    }
                    lhm_list_to_create.append(lhm_transaction)
            
            if line_validation_error:
                raise ValidationError("\n".join(line_validation_error))

            if data_validation_error:
                raise ValidationError("\n".join(data_validation_error))

            created_lhm = False
            if lhm_list_to_create:
                created_lhm = request.env['lhm.transaction'].with_user(check_user).create(lhm_list_to_create)

            grouping_by_supplier_per_month = {}
            lhm_contractor_list_to_create = [] # lhm.contractor
            for line in lhm_contractor_lines:
                supplier_id = line.get('supplier_id')
                if not supplier_id:
                    continue
                month_year = fields.Date.from_string(vals['date']).strftime('%Y-%m')
                key = (supplier_id, month_year)
                if key not in grouping_by_supplier_per_month:
                    grouping_by_supplier_per_month[key] = []
                del line['supplier_id']  # Remove supplier_id from line data
                grouping_by_supplier_per_month[key].append(line)
            updated_lhm_contractor_list = [] # lhm.contractor
            for supplier_id, month_year in grouping_by_supplier_per_month.keys():
                existing_lhm_contractor = request.env['lhm.contractor'].with_user(check_user).search([
                    ('supplier_id', '=', supplier_id),
                    ('date_start', '>=', f"{month_year}-01"),
                    ('date_end', '<=', f"{month_year}-31")
                ], limit=1)
                lhm_contractor_lines1 = grouping_by_supplier_per_month[(supplier_id, month_year)]
                if existing_lhm_contractor:
                    # Update existing LHM Contractor
                    existing_lhm_contractor.write({
                        'line_ids': [(0, 0, line) for line in lhm_contractor_lines1]
                    })
                    updated_lhm_contractor_list.append(existing_lhm_contractor)
                else:
                    # Create new LHM Contractor
                    lhm_contractor_transaction = {
                        'type': 'vendor',
                        # 'afdeling_id': vals['kemandoran_id'],
                        'payment_type': 'payment0',
                        'date_start': f"{month_year}-01",
                        'date_end': f"{month_year}-31",
                        'origin': vals.get('origin', False),
                        'supplier_id': supplier_id,
                        'line_ids': list(map(lambda x: (0, 0, x), lhm_contractor_lines1)),
                        # 'note': vals['note'],
                    }
                    lhm_contractor_list_to_create.append(lhm_contractor_transaction)
            created_lhm_contractor = False
            if lhm_contractor_list_to_create:
                created_lhm_contractor = request.env['lhm.contractor'].with_user(check_user).create(lhm_contractor_list_to_create)

            result = {'data': [], 'count': 0}
            if created_lhm or created_lhm_contractor or updated_lhm_contractor_list:
                if created_lhm:
                    result = {'data': list(map(lambda x: {'id': x.id, 'name': x.name}, created_lhm)), 'count': len(created_lhm.ids)}
                if created_lhm_contractor:
                    result = {'data': list(map(lambda x: {'id': x.id, 'name': x.name}, created_lhm_contractor)), 'count': len(created_lhm_contractor.ids)}
                if updated_lhm_contractor_list:
                    result = {'data': list(map(lambda x: {'id': x.id, 'name': x.name}, updated_lhm_contractor_list)), 'count': len(updated_lhm_contractor_list)}
                return Response(json.dumps({
                        'message': f"Successfully create a new Laporan Harian Mandor (LHM)",
                        'data': result
                    }, cls=DateEncoder), headers=HEADERS, status=201)
            else:
                raise MissingError("Failed to create Laporan Harian Mandor")
        except Exception as error:
            return self._handle_exception(error)
    
    @http.route([ROUTES, f"{ROUTES}/<lhm_id>"], auth='public', website=False, csrf=False, type='http', methods=['GET'])
    def get_lhm(self, lhm_id=None):
        # check token
        check_user, message = self._verify_auth()
        if not check_user:
            return Response(json.dumps({'message': message}), headers=HEADERS, status=400)
        
        datas = self._get_payload() or {}
        try:
            result = {'data': [], 'count': 0}
            conditions = []
            params = []
            if lhm_id:
                conditions.append("lt.id = %s")
                params.append(int(lhm_id))
            elif datas.get('date_from') and datas.get('date_to'):
                conditions.append("lt.date >= %s AND lt.date <= %s")
                params.extend([datas['date_from'], datas['date_to']])
            limit = datas.get('limit', 10)
            offset = datas.get('offset', 0)
            where_clause = ("WHERE " + " AND ".join(conditions)) if conditions else ""
            params.extend([limit, offset])
            cr = request.env.cr
            cr.execute(f"""
                SELECT lt.id, lt.name, lt.kemandoran_id, hf.afdeling_id, lt.date, lt.origin, lt.state
                FROM lhm_transaction lt
                       INNER JOIN hr_foreman hf ON hf.id = lt.kemandoran_id
                {where_clause}
                ORDER BY lt.date DESC
                LIMIT %s OFFSET %s
            """, params)
            lhm_records = cr.dictfetchall()
            if not lhm_records:
                raise MissingError("Data LHM not found")
            # This is for Material Line in LHM

            for lhm in lhm_records:
                # lhm_line_records = request.env['lhm.transaction.line'].with_user(check_user).search_read(domain=[('lhm_id','=',lhm['id'])], fields=fields2)
                
                # lhm_line.date,
                query_line = """SELECT 
                        lhm_line.id,
                        lhm_line.employee_id,
                        lhm_line.attendance_id as attendance_type_id,
                        lhm_line.work_day,
                        lhm_line.is_borong,
                        block.id as plant_block_id,
                        lhm_line.activity_id,
                        lhm_line.product_id as product_id_1,
                        lhm_line.hasil_1,
                        lhm_line.satuan_1 as uom_id_1,
                        lhm_line.product_id_2,
                        lhm_line.hasil_2,
                        lhm_line.satuan_2 as uom_id_2
                    FROM lhm_transaction_line lhm_line
                        left join lhm_plant_block block on block.location_id = lhm_line.location_id
                    WHERE lhm_line.lhm_id = %s
                    """
                request.env.cr.execute(query_line, (lhm['id'],))
                lhm_line_records = request.env.cr.dictfetchall()
                
                # material_line_records = request.env['lhm.transaction.material.line'].with_user(check_user).search_read(domain=[('lhm_id','=',lhm['id'])], fields=fields3)
                query_material_line = """SELECT
                        material_line.id,
                        mrl.mr_id,
                        material_line.product_id,
                        block.id as plant_block_id,
                        material_line.activity_id,
                        material_line.product_uom_id as uom_id,
                        coalesce(material_line.realization,0) as product_qty
                    FROM lhm_transaction_material_line material_line
                        left join lhm_plant_block block on block.location_id = material_line.location_id
                        left join stock_move sm ON sm.id = material_line.move_id
                        left join material_request_line mrl ON mrl.id = sm.mr_line_id
                    WHERE material_line.lhm_id = %s
                """
                request.env.cr.execute(query_material_line, (lhm['id'],))
                material_line_records = request.env.cr.dictfetchall()
                lhm.update({
                    'lhm_line_ids': lhm_line_records,
                    'material_line_ids': material_line_records
                })
            
            result['data'] = lhm_records
            result['count'] = len(lhm_records)
            return Response(json.dumps({
                    'message': f"Successfully get data Laporan Harian Mandor (LHM)",
                    'data': result
                }, cls=DateEncoder), headers=HEADERS, status=201)
        except Exception as error:
            return self._handle_exception(error)
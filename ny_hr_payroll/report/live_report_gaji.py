from odoo import models, fields

class EmployeeContractReport(models.Model):
    _name = 'employee.contract.report'
    _description = 'Employee Contract Report'
    _auto = False

    tanggal = fields.Date(string="Tanggal")
    employee_id = fields.Many2one('hr.employee', string="Employee")
    identification_id = fields.Char(string="Identification No")
    contract_id = fields.Many2one('hr.contract', string="Current Contract")
    employee_type_id = fields.Many2one('hr.contract', string="Employee Type")
    wage_type_id = fields.Many2one('hr.contract', string="Wage Type")
    wage_type_name = fields.Char(string="Wage Type", readonly=True)
    wage = fields.Float(string="Wage")
    wage_day = fields.Integer(string="Wage Daily")
    is_lhm = fields.Boolean(string="Is LHM")
    total_work_day = fields.Integer(string="HK")
    total_contract_wage_value = fields.Float(string="Borong")
    kemandoran_id = fields.Many2one('hr.foreman', string="Kemandoran")
    kemandoran_name = fields.Char(string="Kemandoran", readonly=True)

    def init(self):
        self._cr.execute("""
            DROP VIEW IF EXISTS employee_contract_report;
            CREATE OR REPLACE VIEW employee_contract_report AS (
                SELECT 
                    ROW_NUMBER() OVER() AS id,
                    e.id AS employee_id,
                    e.identification_id AS identification_id,
                    e.contract_id AS contract_id,
                    c.employee_type_id AS employee_type_id,
                    c.wage_type_id AS wage_type_id,
                    wt.name AS wage_type_name,
                    c.wage AS wage,
                    c.wage_day AS wage_day,
                    c.is_lhm AS is_lhm,
                    e.kemandoran_id AS kemandoran_id,
                    f.name AS kemandoran_name,
                    l.date AS tanggal,
                    SUM(l.work_day) AS total_work_day,
                    SUM(
                        CASE 
                            WHEN l.is_borong = true THEN l.contract_wage_value
                            ELSE 0
                        END
                    ) AS total_contract_wage_value
                FROM 
                    hr_employee e
                INNER JOIN 
                    hr_contract c 
                ON 
                    e.contract_id = c.id
                LEFT JOIN 
                    lhm_transaction_line l 
                ON 
                    l.employee_id = e.id
                LEFT JOIN 
                    hr_contract_wage_type wt
                ON 
                    c.wage_type_id = wt.id
                LEFT JOIN 
                    hr_foreman f 
                ON 
                    e.kemandoran_id = f.id
                WHERE 
                    l.date IS NOT NULL
                GROUP BY 
                    e.id, e.contract_id, e.identification_id, 
                    c.employee_type_id, c.wage_type_id, wt.name,
                    c.wage, c.wage_day, c.is_lhm, e.kemandoran_id, f.name,
                    l.date
            )
        """)

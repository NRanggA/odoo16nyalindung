# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
import ast
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    @api.model
    def _query_get(self, domain=None):
        self.check_access_rights('read')

        context = dict(self._context or {})
        domain = domain or []

        if not isinstance(domain, (list, tuple)):
            domain = ast.literal_eval(domain)

        # Determine the date field based on context
        date_field = 'date_maturity' if context.get('aged_balance') else 'date'

        # Filter by date range
        if context.get('date_to'):
            domain += [(date_field, '<=', context['date_to'])]

        if context.get('date_from'):
            if not context.get('strict_range'):
                domain += [
                    '|', 
                    (date_field, '>=', context['date_from']),
                    ('account_id.include_initial_balance', '=', True)
                ]
            elif context.get('initial_bal'):
                domain += [(date_field, '<', context['date_from'])]
            else:
                domain += [(date_field, '>=', context['date_from'])]

        # Filter by journal
        if context.get('journal_ids'):
            domain += [('journal_id', 'in', context['journal_ids'])]

        # Filter by state
        state = context.get('state')
        if state and state.lower() != 'all':
            domain += [('parent_state', '=', state)]

        # Filter by company
        if context.get('company_id'):
            domain += [('company_id', '=', context['company_id'])]
        elif context.get('allowed_company_ids'):
            domain += [('company_id', 'in', self.env.companies.ids)]
        else:
            domain += [('company_id', '=', self.env.company.id)]

        # Reconcile date filtering
        if context.get('reconcile_date'):
            domain += [
                '|', ('reconciled', '=', False),
                '|', ('matched_debit_ids.max_date', '>', context['reconcile_date']),
                ('matched_credit_ids.max_date', '>', context['reconcile_date'])
            ]

        # Additional filters based on context
        filters = [
            ('account_tag_ids', 'account_id.tag_ids'),
            ('account_ids', 'account_id'),
            ('analytic_tag_ids', 'analytic_tag_ids'),
            ('analytic_account_ids', 'analytic_account_id'),
            ('partner_ids', 'partner_id'),
            ('partner_categories', 'partner_id.category_id')
        ]

        for ctx_key, field in filters:
            if context.get(ctx_key):
                domain += [(field, 'in', context[ctx_key].ids)]

        # Add mandatory filters
        domain += [
            ('display_type', 'not in', ('line_section', 'line_note')),
            ('parent_state', '!=', 'cancel')
        ]

        # Generate SQL query
        where_clause, where_clause_params, tables = "", [], ""
        if domain:
            query = self._where_calc(domain)
            self._apply_ir_rules(query)  # Apply access control rules
            tables, where_clause, where_clause_params = query.get_sql()

        return tables, where_clause, where_clause_params

# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.osv import expression
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class AccountAccountTemplate(models.Model):
    _inherit = 'account.account.template'

    parent_id = fields.Many2one(
    'account.account.template', 
    'Parent Account', 
    ondelete="set null"
    )

    account_type = fields.Selection(
        selection_add=[('view', 'View')], 
        ondelete={'view': 'cascade'}
    )

    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        context = self._context or {}
        new_args = []

        # Update search criteria to include code search
        if args:
            for arg in args:
                if isinstance(arg, (list, tuple)) and arg[0] == 'name' and isinstance(arg[2], str):
                    new_args.extend(['|', arg, ['code', arg[1], arg[2]]])
                else:
                    new_args.append(arg)

        # Add condition to exclude 'view' account type if not in specific context
        if not context.get('show_parent_account', False):
            new_args = expression.AND([[('account_type', '!=', 'view')], new_args])

        return super(AccountAccountTemplate, self)._search(
            new_args, offset=offset, limit=limit, 
            order=order, count=count, 
            access_rights_uid=access_rights_uid
        )


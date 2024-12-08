# -*- coding: utf-8 -*-
from . import models
from odoo import api, SUPERUSER_ID


def _assign_account_parent(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    env['account.account']._parent_store_compute()
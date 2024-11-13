from odoo import models, api, fields, Command, _
from odoo.exceptions import ValidationError

from dateutil.relativedelta import relativedelta

class ClosingProjectPlantation(models.Model):
    _name = 'closing.project.plant'
    _description = 'Closing Project Plantation'

    
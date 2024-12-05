# -*- coding: utf-8 -*-

from collections import defaultdict
from pytz import timezone, utc

from odoo import api, fields, models, _
from odoo.addons.base.models.res_partner import _tz_get
from odoo.exceptions import ValidationError

from odoo.addons.resource.models.resource import Intervals, datetime_to_string, string_to_datetime

class ResourceCalendar(models.Model):
    _inherit = "resource.calendar"

    def _leave_intervals_batch(self, start_dt, end_dt, resources=None, domain=None, tz=None, any_calendar=False):
        """ Return the leave intervals in the given datetime range.
            The returned intervals are expressed in specified tz or in the calendar's timezone.
        """
        assert start_dt.tzinfo and end_dt.tzinfo
        self.ensure_one()
        # print(">>>>>>>>>>>>>>>>>>>>", self._context)
        if not self._context.get('leave_premi_sadap',False):
            return super(ResourceCalendar, self)._leave_intervals_batch(start_dt, end_dt, resources=resources, domain=domain, tz=tz, any_calendar=any_calendar)

        if not resources:
            resources = self.env['resource.resource']
            resources_list = [resources]
        else:
            resources_list = list(resources) + [self.env['resource.resource']]
        if domain is None:
            domain = [('time_type', '=', 'leave')]
        if not any_calendar:
            domain = domain + [('calendar_id', 'in', [False, self.id])]
        # for the computation, express all datetimes in UTC
        # Public leave don't have a resource_id
        domain = domain + [
            ('resource_id', 'in', [False] + [r.id for r in resources_list]),
            ('date_from', '<=', datetime_to_string(end_dt)),
            ('date_to', '>=', datetime_to_string(start_dt)),
            ('leave_premi_sadap', '=', True),
        ]

        # retrieve leave intervals in (start_dt, end_dt)
        result = defaultdict(lambda: [])
        tz_dates = {}
        for leave in self.env['resource.calendar.leaves'].search(domain):
            for resource in resources_list:
                if leave.resource_id.id not in [False, resource.id] or (not leave.resource_id and resource and resource.company_id != leave.company_id):
                    continue
                tz = tz if tz else timezone((resource or self).tz)
                if (tz, start_dt) in tz_dates:
                    start = tz_dates[(tz, start_dt)]
                else:
                    start = start_dt.astimezone(tz)
                    tz_dates[(tz, start_dt)] = start
                if (tz, end_dt) in tz_dates:
                    end = tz_dates[(tz, end_dt)]
                else:
                    end = end_dt.astimezone(tz)
                    tz_dates[(tz, end_dt)] = end
                dt0 = string_to_datetime(leave.date_from).astimezone(tz)
                dt1 = string_to_datetime(leave.date_to).astimezone(tz)
                result[resource.id].append((max(start, dt0), min(end, dt1), leave))

        return {r.id: Intervals(result[r.id]) for r in resources_list}

class ResourceCalendarLeaves(models.Model):
    _inherit = "resource.calendar.leaves"

    leave_premi_sadap = fields.Boolean()
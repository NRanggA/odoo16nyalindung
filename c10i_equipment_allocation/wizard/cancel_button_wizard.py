# -*- coding: utf-8 -*-
 
from odoo import models, fields, api,_
from datetime import datetime,date

class ButtonCancel(models.TransientModel):
    _name = 'button.cancel'
    _description = "Button Cancel"

    reason = fields.Text(string="Reason")

    def do_cancel(self):
        active_ids=self.env['allocation.request'].browse(self.env.context.get('active_id'))
        for request in active_ids:
            display_reason=""" Hello """ + request.assigned_id.name + """,""" + """
                        <br/>
                        <br/>
                        Your allocation request for a set of """+ """<b>"""+request.equipment_id.name+"""</b>""" +"""/""" +"""<b>"""+request.equipment_id.serial_no +"""</b>""" +""" 
                        has been cancelled. """ + """
                        <br/>
                        <br/>
                        <b>Reason</b> for cancelling this request is stated below:
                        </br>
                        </br>""" + """<br/>"""+self.reason
            request.message_post(body=display_reason) 
            request.equipment_id.write({'state':'available','employee_id':False})
            request.update({'cancelled_by':self.env.user.id,
                'state':'cancel'})








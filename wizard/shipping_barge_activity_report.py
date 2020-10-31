# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError
import datetime
import calendar 
import logging
_logger = logging.getLogger(__name__)

class ShippingBargeSctivityReport(models.TransientModel):
    _name = 'shipping.barge.activity.report'

    start_date = fields.Date('Start Date', required=True)
    end_date = fields.Date(string="End Date", required=True)
    
    @api.multi
    def action_print(self):
        barge_activities = self.env['shipping.barge.activity'].search([ ( 'arrive_date', '>=', self.start_date ), ( 'arrive_date', '<=', self.end_date ) ])
        final_dict = {}
        loc_barge_dict = {}
        for barge_activity in barge_activities:
            row = {}
            row["doc_name"] = barge_activity.barge_id.location_id.name
            row["location_name"] = barge_activity.barge_id.location_id.name
            row["arrive_date"] = barge_activity.arrive_date
            row["start_barging_date"] = barge_activity.start_barging_date
            row["end_barging_date"] = barge_activity.end_barging_date
            row["depart_date"] = barge_activity.depart_date
            row["quantity"] = barge_activity.quantity
            row["progress"] = barge_activity.progress
            row["remarks"] = barge_activity.remarks

            if loc_barge_dict.get( row["location_name"] , False):
                loc_barge_dict[ row["location_name"] ] += [row]
            else :
                loc_barge_dict[ row["location_name"] ] = [row]

        final_dict = loc_barge_dict
        datas = {
            'ids': self.ids,
            'model': 'shipping.barge.activity.report',
            'form': final_dict,
            'start_date': self.start_date,
            'end_date': self.end_date,

        }
        return self.env['report'].get_action(self,'shipping.shipping_barge_activity_temp', data=datas)
# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError
import datetime
import calendar 
import logging
_logger = logging.getLogger(__name__)

class ShippingOrderReport(models.TransientModel):
    _name = 'shipping.order.report'

    start_date = fields.Date('Start Date', required=True)
    end_date = fields.Date(string="End Date", required=True)
    
    @api.multi
    def action_print(self):
        shippings = self.env['shipping.order'].search([ ( 'arrive_date', '>=', self.start_date ), ( 'arrive_date', '<=', self.end_date ) ])
        final_dict = {}
        month_shipping_dict = {}
        for shipping in shippings:
            row = {}
            row["doc_name"] = shipping.location_id.name + " " + shipping.sale_contract_id.name
            row["arrive_date"] = shipping.arrive_date
            row["depart_date"] = shipping.depart_date
            row["quantity"] = shipping.quantity
            row["loading_port"] = shipping.loading_port.name
            row["discharging_port"] = shipping.discharging_port.name

            date = datetime.datetime.strptime(shipping.arrive_date, '%Y-%m-%d %H:%M:%S')
            if date :
                if month_shipping_dict.get( calendar.month_name[ date.month ] , False):
                    month_shipping_dict[ calendar.month_name[ date.month ] ] += [row]
                else :
                    month_shipping_dict[ calendar.month_name[ date.month ] ] = [row]

        final_dict = month_shipping_dict
        datas = {
            'ids': self.ids,
            'model': 'shipping.order.report',
            'form': final_dict,
            'start_date': self.start_date,
            'end_date': self.end_date,

        }
        return self.env['report'].get_action(self,'shipping.shipping_order_temp', data=datas)
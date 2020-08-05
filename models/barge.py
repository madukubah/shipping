 # -*- coding: utf-8 -*-
from odoo import api, fields, models, _
import time
import odoo.addons.decimal_precision as dp

class Barge(models.Model):
	_name = "shipping.barge"

	name = fields.Char(string="Name", size=100 , required=True)
	capacity = fields.Float( string="Capacity (WMT)", required=True, default=0, digits=dp.get_precision('Shipping') )
	# shipping_ids = fields.One2many("shipping.shipping", inverse_name="barge_id", string="Shippings", readonly=True)


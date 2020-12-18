 # -*- coding: utf-8 -*-
from odoo import api, fields, models, _
import time

class Port(models.Model):
	_name = "shipping.port"

	name = fields.Char(string="Name", size=100 , required=True)
	# partner_id = fields.Many2one("res.partner", string="Factory", ondelete="restrict" )
	


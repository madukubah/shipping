 # -*- coding: utf-8 -*-
from odoo import api, fields, models, _

class Partner(models.Model):
	_inherit = "res.partner"

	port_ids = fields.One2many(
		'shipping.port', 
        'partner_id',
		string='Ports', 
		index=True,
        store=True
		)
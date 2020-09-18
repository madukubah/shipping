 # -*- coding: utf-8 -*-
from odoo import api, fields, models, _
import time
from odoo.exceptions import UserError, ValidationError
import odoo.addons.decimal_precision as dp
import logging
_logger = logging.getLogger(__name__)

class BargeActivity(models.Model):
	_name = "shipping.barge.activity"

	READONLY_STATES = {
        'close': [('readonly', True)],
        'open': [('readonly', False)],
    }

	name = fields.Char(compute='_compute_name', store=True, readonly=True, default="New" )
	
	barge_id = fields.Many2one('shipping.barge', string='Barge', domain=[ ('active','=',True)], required=True, states=READONLY_STATES, change_default=True, index=True, track_visibility='always')
	product_id = fields.Many2one('product.product', 'Material', required=True, states=READONLY_STATES )
	quantity = fields.Float( string="Quantity (WMT)", digits=dp.get_precision('QAQC') ,readonly=True, default=0, compute="_set_progress" )
	capacity = fields.Float( string="Capacity (WMT)", digits=dp.get_precision('Shipping'), readonly=True, default=0, compute="_set_progress" )

	depart_date = fields.Datetime('Depart Date', help='', states=READONLY_STATES )
	arrive_date = fields.Datetime('Arrived Date', help='', states=READONLY_STATES )

	start_barging_date = fields.Datetime('Start Barging Date', help='', states=READONLY_STATES )
	end_barging_date = fields.Datetime('End Barging Date', help='', states=READONLY_STATES )

	clearence_out_date = fields.Datetime('Clearence Date', help='', states=READONLY_STATES )
	
	progress = fields.Float( string="Progress", readonly=True, default=0, compute="_set_progress" )

	state = fields.Selection([
        ('open', 'Open'), 
		('close', 'Closed'),
        ], string='Status', readonly=True, copy=False, index=True, track_visibility='onchange', default='open')

	@api.depends("barge_id", "product_id")
	def _set_progress(self):
		for rec in self:
			if( rec.barge_id and rec.product_id ):
				product_qty = rec.product_id.with_context({'location' : rec.barge_id.location_id.id})
				rec.progress = product_qty.qty_available / rec.barge_id.capacity * 100
				rec.capacity = rec.barge_id.capacity
				rec.quantity = product_qty.qty_available


	@api.depends('barge_id' )
	def _compute_name(self):
		for record in self:
			name = record.barge_id.name
			self.name = name

	@api.multi
	def button_close(self):
		if not self.env.user.has_group('shipping.shipping_group_manager') :
			raise UserError(_("You are not manager") )
		self.state = 'close'

	@api.multi
	def button_open(self):
		if not self.env.user.has_group('shipping.shipping_group_manager') :
			raise UserError(_("You are not manager") )
		self.state = 'open'
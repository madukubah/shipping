 # -*- coding: utf-8 -*-
from odoo import api, fields, models, _
import time
from odoo.exceptions import UserError, ValidationError
import odoo.addons.decimal_precision as dp
import logging
_logger = logging.getLogger(__name__)

class BargeActivity(models.Model):
	_name = "shipping.barge.activity"
	_inherit = ['mail.thread', 'ir.needaction_mixin']
	_order = "id desc"


	READONLY_STATES = {
        'draft': [('readonly', False)],
        'cancel': [('readonly', True)],
        'confirm': [('readonly', True)],
        'done': [('readonly', True)],
    }

	name = fields.Char(compute='_compute_name', store=True, readonly=True, default="New" )
	
	barge_id = fields.Many2one('shipping.barge', string='Barge', domain=[ ('active','=',True)], required=True, states=READONLY_STATES, change_default=True, index=True, track_visibility='always')
	product_id = fields.Many2one('product.product', 'Material', domain=[('type', 'in', ['product', 'consu'])], required=True, states=READONLY_STATES )
	quantity = fields.Float( string="Quantity (WMT)", digits=dp.get_precision('QAQC') ,readonly=True, default=0, compute="_set_progress" )
	capacity = fields.Float( string="Capacity (WMT)", digits=dp.get_precision('Shipping'), readonly=True, default=0, compute="_set_progress" )

	depart_date = fields.Datetime('Cast Off Date', help='', states=READONLY_STATES )
	arrive_date = fields.Datetime('Alongside Date', help='', states=READONLY_STATES )

	start_barging_date = fields.Datetime('Start Barging Date', help='', states=READONLY_STATES )
	end_barging_date = fields.Datetime('End Barging Date', help='', states=READONLY_STATES )

	# clearence_out_date = fields.Datetime('Clearence Date', help='', states=READONLY_STATES )
	
	progress = fields.Float( string="Progress", readonly=True, default=0, compute="_set_progress" )
	remarks = fields.Char( string="Remarks" )

	state = fields.Selection([
        ('draft', 'Draft'), 
		('cancel', 'Cancelled'),
		('confirm', 'Approve'),
		('done', 'Done'),
        ], string='Status', readonly=True, copy=False, index=True, track_visibility='onchange', default='draft')

	active = fields.Boolean(
        'Active', default=True,
        help="If unchecked, it will allow you to hide the rule without removing it.")

	@api.depends("barge_id", "product_id")
	def _set_progress(self):
		for record in self:
			if( record.barge_id and record.product_id ):
				product_qty = record.product_id.with_context({'location' : record.barge_id.location_id.id})
				record.progress = product_qty.qty_available / record.barge_id.capacity * 100
				record.capacity = record.barge_id.capacity
				record.quantity = product_qty.qty_available


	@api.depends('barge_id' )
	def _compute_name(self):
		for record in self:
			name = record.barge_id.name
			self.name = name
	
	@api.multi
	def action_draft(self):
		for record in self:
			if not self.env.user.has_group('shipping.shipping_group_manager') :
				raise UserError(_("You are not manager") )
			record.state = 'draft'

	@api.multi
	def action_cancel(self):
		for record in self:
			if not self.env.user.has_group('shipping.shipping_group_manager') :
				raise UserError(_("You are not manager") )
			record.state = 'cancel'

	@api.multi
	def action_confirm(self):
		for record in self:
			if not self.env.user.has_group('shipping.shipping_group_manager') :
				raise UserError(_("You are not manager") )
			record.state = 'confirm'

	@api.multi
	def action_done(self):
		for record in self:
			if not self.env.user.has_group('shipping.shipping_group_manager') :
				raise UserError(_("You are not manager") )
			record.state = 'done'
			record.active = False

	@api.multi
	def unlink(self):
		for record in self:
			if record.state != "draft" :
				raise UserError(_("Only Delete data in Open State") )
		
		return super(BargeActivity, self ).unlink()
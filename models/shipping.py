 # -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
import time
import odoo.addons.decimal_precision as dp

class Shipping(models.Model):
	_name = "shipping.shipping"
	_order = "id desc"

	name = fields.Char(string="Name", size=100 , store=True,index=True,copy=False, required=True, readonly=True, states={'draft': [('readonly', False)]})
	barge_id = fields.Many2one('shipping.barge', string='Barge', readonly=True, states={'draft': [('readonly', False)]}, required=True, change_default=True, index=True, track_visibility='always')
	sale_contract_id = fields.Many2one('sale.contract', string='Contract', readonly=True, states={'draft': [('readonly', False)]}, required=True, change_default=True, index=True, track_visibility='always')

	depart_date = fields.Date('Depart Date', help='',  default=time.strftime("%Y-%m-%d") )
	arrive_date = fields.Date('Arrived Date', help='',  default=time.strftime("%Y-%m-%d") )
	quantity = fields.Float( string="Quantity (WMT)", readonly=True, states={'draft': [('readonly', False)], 'approve': [('readonly', False)] }  , required=True, default=0, digits=dp.get_precision('Shipping') )

	loading_port = fields.Many2one("shipping.port", string="Loading Port", required=True, ondelete="restrict", readonly=True, states={'draft': [('readonly', False)], 'approve': [('readonly', False)] }  )
	discharging_port = fields.Many2one("shipping.port", string="Discharging Port", required=True, ondelete="restrict", readonly=True, states={'draft': [('readonly', False)], 'approve': [('readonly', False)] }  )

	state = fields.Selection([
        ('draft', 'Draft'), 
		('approve', 'Approved'),
		('done', 'Done')
        ], string='Status', readonly=True, copy=False, index=True, track_visibility='onchange', default='draft')
        

	@api.onchange("barge_id", "sale_contract_id" )
	def _set_name(self):
		for rec in self:
			barge_name = ""
			contract_name = ""
			if( rec.barge_id ) :
				barge_name = rec.barge_id.name
			if( rec.sale_contract_id ) :
				contract_name = rec.sale_contract_id.name
			rec.name = barge_name + " " + contract_name
	
	@api.multi
	def _check_quantity(self):
		for rec in self:
			if( rec.quantity > rec.barge_id.capacity ) :
				return False	
		return True
	
	@api.multi
	def _check_port(self):
		for rec in self:
			if( rec.loading_port.id == rec.discharging_port.id ) :
				return False	
		return True

	@api.multi
	def button_cancel(self):
		if not self.env.user.has_group('shipping.shipping_group_manager') :
			raise UserError(_("You are not manager") )
		self.state = 'draft'

	@api.multi
	def button_approve(self):
		if not self.env.user.has_group('shipping.shipping_group_manager') :
			raise UserError(_("You are not manager") )
		self.state = 'approve'

	@api.multi
	def button_done(self):
		if not self.env.user.has_group('shipping.shipping_group_manager') :
			raise UserError(_("You are not manager") )
		self.state = 'done'
	
	@api.model
	def create(self, values):
		seq = self.env['ir.sequence'].next_by_code('shipping')
		values["name"] = values["name"] + " /" +seq
		res = super(Shipping, self ).create(values)
		return res

	_constraints = [ 
        (_check_quantity, 'Out of Capacity', ['quantity','barge_id'] ) ,
        (_check_port, 'Loading Port and Discharging Port Must Different', ['loading_port','discharging_port'] ) ,
        ]
		
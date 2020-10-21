 # -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
import time
import datetime
from odoo.addons import decimal_precision as dp
import logging
_logger = logging.getLogger(__name__)

class Shipping(models.Model):
	_name = "shipping.order"
	_inherit = ['mail.thread', 'ir.needaction_mixin']
	_order = "id desc"

	READONLY_STATES = {
        'draft': [('readonly', False)],
        'cancel': [('readonly', True)],
        'confirm': [('readonly', True)],
        'done': [('readonly', True)],
    }

	name = fields.Char(string="Name", size=100 , store=True,index=True, required=True, states=READONLY_STATES )
	coa_id = fields.Many2one("qaqc.coa.order", 
        string="QAQC COA", 
        required=True, store=True, 
        ondelete="restrict", 
		domain=[ "&",('state','=',"confirm") , ('surveyor_id.surveyor','=',"intertek") ], 
        states=READONLY_STATES
        )
	barge_activity_id = fields.Many2one(
            'shipping.barge.activity', string='Barging',
			domain=[ ('state','=',"confirm")  ],
            ondelete="restrict", required=True, states=READONLY_STATES )

	location_id = fields.Many2one(
            'stock.location', string='Location',
			related="coa_id.location_id", 
			domain=[ ('usage','=',"internal")  ],
            ondelete="restrict", required=True, readonly=True)

	sale_contract_id = fields.Many2one('sale.contract', string='Contract', domain=[ '&', ('state','=',"open"), ('is_expired','=',"False") ], states=READONLY_STATES, required=True, change_default=True, index=True, track_visibility='always', ondelete="restrict" )

	depart_date = fields.Datetime('Cast Off Date', help='', related="barge_activity_id.depart_date" )
	arrive_date = fields.Datetime('Alongside Date', help='', related="barge_activity_id.arrive_date" )

	start_barging_date = fields.Datetime('Start Barging Date', help='', related="barge_activity_id.start_barging_date" )
	end_barging_date = fields.Datetime('End Barging Date', help='', related="barge_activity_id.end_barging_date" )
	# clearence_out_date = fields.Datetime('Clearence Date', help='', related="barge_activity_id.clearence_out_date" )
	quantity = fields.Float( string="Quantity (WMT)", readonly=True , default=2, digits=dp.get_precision('Shipping'), compute="_set_quantity" )

	loading_port = fields.Many2one("shipping.port", string="Loading Port", required=True, ondelete="restrict", states=READONLY_STATES  )
	discharging_port = fields.Many2one("shipping.port", string="Discharging Port", required=True, ondelete="restrict", states=READONLY_STATES  )
	user_id = fields.Many2one('res.users', string='User', index=True, track_visibility='onchange', default=lambda self: self.env.user)
	state = fields.Selection([
        ('draft', 'Draft'), 
		('cancel', 'Cancelled'),
		('confirm', 'Approve'),
		('done', 'Done'),
        ], string='Status', readonly=True, copy=False, index=True, track_visibility='onchange', default='draft')
        
	@api.depends( "coa_id" )
	def _set_quantity(self):
		for record in self:
			record.quantity = record.coa_id.quantity
	   
	@api.onchange("location_id", "sale_contract_id" )
	def _set_name(self):
		for record in self:
			barge_name = ""
			contract_name = ""
			if( record.location_id ) :
				barge_name = record.location_id.name
			if( record.sale_contract_id ) :
				contract_name = record.sale_contract_id.name
			record.name = barge_name + " " + contract_name
	
	@api.multi
	def _check_port(self):
		for record in self:
			if( record.loading_port.id == record.discharging_port.id ) :
				return False	
		return True

	@api.multi
	def _check_barge(self):
		for record in self:
			if( record.coa_id.barge_id.id != record.barge_activity_id.barge_id.id ) :
				return False	
		return True

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
	
	@api.model
	def create(self, values):
		seq = self.env['ir.sequence'].next_by_code('shipping')
		values["name"] = seq + " /" + values["name"] 
		res = super(Shipping, self ).create(values)
		return res

	_constraints = [ 
        (_check_port, 'Loading Port and Discharging Port Must Different', ['loading_port','discharging_port'] ) ,
        (_check_barge, 'COA Barge Does Not Match With Barging Barge', ['coa_id','barge_activity_id'] ) 
        ]

	@api.multi
	def unlink(self):
		for record in self:
			if record.state != "draft" :
				raise UserError(_("Only Delete data in Draft State") )
		
		return super(Shipping, self ).unlink()
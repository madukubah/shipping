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
	_order = "id desc"

	READONLY_STATES = {
        'draft': [('readonly', False)],
        'approve': [('readonly', True)],
        'done': [('readonly', True)],
    }

	name = fields.Char(string="Name", size=100 , store=True,index=True,copy=False, required=True, states=READONLY_STATES )
	# barge_id = fields.Many2one('shipping.barge', string='Barge', readonly=True, states={'draft': [('readonly', False)]}, required=True, change_default=True, index=True, track_visibility='always')
	coa_id = fields.Many2one("qaqc.coa.order", 
        string="QAQC COA", 
        required=True, store=True, 
        ondelete="restrict", 
		domain=[ "&",('state','=',"final") , ('surveyor_id.surveyor','=',"intertek") ], 
        states=READONLY_STATES
        )
	location_id = fields.Many2one(
            'stock.location', string='Barge',
			related="coa_id.location_id", 
			domain=[ ('usage','=',"internal")  ],
            ondelete="restrict", required=True, readonly=True)
	sale_contract_id = fields.Many2one('sale.contract', string='Contract', domain=[ '&', ('state','=',"open"), ('is_expired','=',"False") ], states=READONLY_STATES, required=True, change_default=True, index=True, track_visibility='always', ondelete="restrict" )

	depart_date = fields.Datetime('Depart Date', help='',  default=time.strftime("%Y-%m-%d %H:%M:%S") )
	arrive_date = fields.Datetime('Arrived Date', help='',  default=time.strftime("%Y-%m-%d %H:%M:%S") )

	start_barging_date = fields.Datetime('Start Barging Date', help='',  default=time.strftime("%Y-%m-%d %H:%M:%S") )
	end_barging_date = fields.Datetime('End Barging Date', help='',  default=time.strftime("%Y-%m-%d %H:%M:%S") )

	clearence_out_date = fields.Datetime('Clearence Date', help='',  default=time.strftime("%Y-%m-%d %H:%M:%S") )

	quantity = fields.Float( string="Quantity (WMT)", readonly=True , default=2, digits=dp.get_precision('Shipping'), )
	# ritase_count = fields.Float( string="Ritase Count", readonly=True, states={'draft': [('readonly', False)] }  , required=True, default=0, digits=dp.get_precision('Shipping') )
	# ton_p_rit = fields.Float( string="Ton/Rit", readonly=True, default=0, digits=dp.get_precision('Shipping'), compute="_set_ton_p_rit" )
	# progress = fields.Float( string="Progress", readonly=True, default=0, compute="_set_progress" )

	loading_port = fields.Many2one("shipping.port", string="Loading Port", required=True, ondelete="restrict", readonly=True, states={'draft': [('readonly', False)], 'approve': [('readonly', False)] }  )
	discharging_port = fields.Many2one("shipping.port", string="Discharging Port", required=True, ondelete="restrict", readonly=True, states={'draft': [('readonly', False)], 'approve': [('readonly', False)] }  )

	# barging_lines = fields.One2many(
    #     'shipping.barging.line',
    #     'shipping_id',
    #     string='Barging Lines',
    #     copy=True )

	state = fields.Selection([
        ('draft', 'Draft'), 
		('approve', 'Approved'),
		('done', 'Done')
        ], string='Status', readonly=True, copy=False, index=True, track_visibility='onchange', default='draft')
        
	@api.onchange( "coa_id" )
	def _set_quantity(self):
		for rec in self:
			_logger.warning("_set_quantity")
			rec.quantity = rec.coa_id.quantity
	   
	# @api.depends("quantity")
	# def _set_progress(self):
	# 	for rec in self:
	# 		capacity = rec.barge_id.capacity if rec.barge_id.capacity else 1.0
	# 		rec.progress = rec.quantity /capacity * 100

	# @api.depends("barging_lines")
	# def _compute_barging_line(self):
	# 	for rec in self:
	# 		rec.quantity = sum([ barging_line.quantity for barging_line in rec.barging_lines ])

	@api.onchange("location_id", "sale_contract_id" )
	def _set_name(self):
		for rec in self:
			barge_name = ""
			contract_name = ""
			if( rec.location_id ) :
				barge_name = rec.location_id.name
			if( rec.sale_contract_id ) :
				contract_name = rec.sale_contract_id.name
			rec.name = barge_name + " " + contract_name
	
	# @api.multi
	# def _check_quantity(self):
	# 	for rec in self:
	# 		if( rec.quantity > rec.barge_id.capacity ) :
	# 			return False	
	# 	return True
	
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
        (_check_port, 'Loading Port and Discharging Port Must Different', ['loading_port','discharging_port'] ) ,
        ]
		
class BargingLine(models.Model):
	_name = "shipping.barging.line"
	_order = "id asc"

	shipping_id = fields.Many2one("shipping.order", string="Shipping", ondelete="cascade" )
	barging_date = fields.Datetime('Date', help='',  default=time.strftime("%Y-%m-%d %H:%M:%S") )
	quantity = fields.Float( string="Quantity (WMT)", default=0, digits=dp.get_precision('Shipping') )
#!/usr/bin/env python
# -*- coding: utf-8 -*-
#################################################################################
#
#    Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#
#################################################################################
from openerp import api,fields,models
from woocommerce import API
from openerp.tools.translate import _
from datetime import datetime,timedelta
from openerp.addons.odoo_multi_channel_sale.tools import extract_list as EL
from openerp.osv import osv
import logging
_logger	 = logging.getLogger(__name__)

class MultiChannelSale(models.Model):
	_inherit = "multi.channel.sale"

	@api.multi
	def get_channel(self):
		res = super(MultiChannelSale, self).get_channel()
		res.append(('woocommerce', "WooCommerce"))
		return res


	url=fields.Char(string="Url", help='eg. http://xyz.com')
	consumer_key=fields.Char(
		string='Consumer Key',
		help='eg. ck_ccac94fc4362ba12a2045086ea9db285e8f02ac9',
		)
	secret_key = fields.Char(string='Secret Key',
		 help='eg. cs_a4c0092684bf08cf7a83606b44c82a6e0d8a4cae'
		 )
	api_version=fields.Selection([
        ('legacyv3', 'Legacy v3'),
        ('wpapi', 'WP REST API')
        ], string='APi Version', default='legacyv3',
    	)
	sftp=fields.Char(
		string='SFTP server',
		)
	sftp_port=fields.Char(
		string='SFTP port',
		)
	sftp_user=fields.Char(
		string='SFTP user',
		)
	sftp_pass=fields.Char(
		string='SFTP pass',
		)


	@api.multi
	def get_woocommerce_import_date(self):
		date=''
		if self._context.has_key('name'):
			if self._context['name'] == 'product':
				date=datetime.strptime(self.woocommerce_import_product_date,'%Y-%m-%d').date()
			elif self._context['name'] == 'order':
				date=datetime.strptime(self.woocommerce_import_order_date,'%Y-%m-%d').date()
			elif self._context['name'] == 'customer':
				date=datetime.strptime(self.woocommerce_import_customer_date,'%Y-%m-%d').date()
			else:
				raise osv.except_osv(_('Error'),_('Context Empty'))
		date = date-timedelta(days=1)
		return str(date)

	@api.multi
	def get_woocommerce_update_date(self):
		date=''
		if self._context.has_key('name'):
			if self._context['name'] == 'product':
				date=datetime.strptime(self.woocommerce_update_product_date,'%Y-%m-%d').date()
			elif self._context['name'] == 'order':
				date=datetime.strptime(self.woocommerce_update_order_date,'%Y-%m-%d').date()
			elif self._context['name'] == 'customer':
				date=datetime.strptime(self.woocommerce_update_customer_date,'%Y-%m-%d').date()
			elif self._context['name'] == 'category':
				date=datetime.strptime(self.woocommerce_update_product_date,'%Y-%m-%d').date()
			else:
				raise osv.except_osv(_('Error'),_('Context Empty'))
		date = date-timedelta(days=1)
		date = str(date)
		return date

	@api.multi
	def test_woocommerce_connection(self):
		message=""
		if self.api_version == 'legacyv3':
			woocommerce=API(
				url 			=	self.url,
				consumer_key    =	self.consumer_key,
				consumer_secret = 	self.secret_key,
				wp_api			=	False,
				version			=	"v3",
				timeout			=	50,
				)
		else:
			woocommerce=API(
				url 			=	self.url,
				consumer_key    =	self.consumer_key,
				consumer_secret = 	self.secret_key,
				wp_api			=	True,
				version			=	"wc/v3",
				timeout			=	50,
				query_string_auth =  True,
				)
		date = datetime.now().date()
		date = date + timedelta(days=5)
		date = str(date)
		try:
			# woocommerce_api=woocommerce.get('products?filter[created_at_min]='+date)
			woocommerce_api=woocommerce.get('system_status')
		except Exception as e:
			raise osv.except_osv(_('Error'),_("Error:"+str(e)))
		# _logger.error('########### Valor de woocommerce_api en test_woocommerce_connection: %s', woocommerce_api.json())
		if  woocommerce_api.json().has_key('message'):
			message="Connection Failed :"+'Status Code :'+str(woocommerce_api.status_code)+" Error :"+str(woocommerce_api.text)
		else :
			self.state 	=	'validate'
			message		=	"Connection Successful!!"
		return self.display_message(message)

	@api.multi
	def get_woocommerce_connection(self):
		if self.api_version == 'legacyv3':
			woocommerce=API(
				url 			=	self.url,
				consumer_key	=	self.consumer_key,
				consumer_secret	=	self.secret_key,
				wp_api			=	False,
				version			=	"v3",
				timeout			=	50,
				)
		else:
			woocommerce=API(
				url 			=	self.url,
				consumer_key    =	self.consumer_key,
				consumer_secret = 	self.secret_key,
				wp_api			=	True,
				version			=	"wc/v3",
				timeout			=	50,
				query_string_auth =  True,
				)

		date = datetime.now().date()
		date = date + timedelta(days=5)
		date = str(date)
		try:
			# woocommerce_api=woocommerce.get('products?filter[created_at_min]='+date)
			woocommerce_api=woocommerce.get('system_status')
		except Exception as e:
			raise osv.except_osv(_('Error'),_("Error:"+str(e)))
		if  woocommerce_api.json().has_key('message'):
			message=str(woocommerce_api.text)+", Status Code:"+str(woocommerce_api.status_code)
		else :
			return woocommerce
		raise osv.except_osv(_('Error'),_(message))


	@api.multi
	def woocommerce_export_api_config(self):
		if self.api_version == 'legacyv3':
			woocommerce = API(
				url 			=	self.url,
				consumer_key	=	self.consumer_key,
				consumer_secret	=	self.secret_key,
				wp_api			=	False,
				version			=	"v3",
				timeout			=	150,
				# verify_ssl		=	False,
			)
		else:
			woocommerce=API(
				url 			=	self.url,
				consumer_key    =	self.consumer_key,
				consumer_secret = 	self.secret_key,
				wp_api			=	True,
				version			=	"wc/v3",
				timeout			=	50,
				query_string_auth =  True,
				)
		try:
			# woocommerce_api=woocommerce.get('products?per_page=1')
			woocommerce_api=woocommerce.get('system_status')
		except Exception as e:
			raise osv.except_osv(_('Error'),_("Error:"+str(e)))
		# _logger.error('########### Valor de woocomerce export api: %s', woocommerce_api.json())
		if  woocommerce_api.json().has_key('message'):
			message = "Connection Error"+str(woocommerce_api.status_code)+" : "+str(woocommerce_api.text)
			raise osv.except_osv(_('Error'),_(message))
		else:
			return woocommerce


	@api.multi
	def update_woocommerce_quantity(self, woocommerce, quantity, product_map_rec):
		_logger.error('########### Valor de update woocomerce qty en product_map_rec: %s', product_map_rec)
		if woocommerce and product_map_rec:
			if product_map_rec.store_variant_id == 'No Variants':
				product_dict = woocommerce.get('products/'+str(product_map_rec.store_product_id)).json()
				_logger.error('########### Valor de update woocomerce qty en product_dict entrada: %s', product_dict)
				# quantity = (product_dict['stock_quantity']+quantity)
				product_dict.update({
									'stock_quantity': quantity,
				})
				_logger.error('########### Valor de update woocomerce qty en product_dict salida: %s', product_dict)
				try:
					return_dict = woocommerce.put('products/'+str(product_map_rec.store_product_id),product_dict).json()
					if return_dict.has_key('message'):
						raise osv.except_osv(_('Error'),_("Can't update product stock , "+str(return_dict['message'])))
				except Exception as e:
					raise osv.except_osv(_('Error'),_("Can't update product stock, "+str(e)))
			else:
				if self.api_version == 'legacyv3':
					product_dict = woocommerce.get('products/'+str(product_map_rec.store_product_id)+product_map_rec.store_variant_id).json()
					variant_dict = product_dict['variations']
				else:
					variant_dict = woocommerce.get('products/'+str(product_map_rec.store_product_id)+"/variations/"+product_map_rec.store_variant_id).json()

				# quantity = int(variant_dict['stock_quantity'])+quantity
				variant_dict.update({
									'stock_quantity': quantity,
				})
				try:
					if self.api_version == 'legacyv3':
						product_dict.update({
							'variations':variant_dict,
							})
						return_dict = woocommerce.put('products/'+str(product_map_rec.store_product_id),product_dict).json()
					else:
						return_dict = woocommerce.put('products/'+str(product_map_rec.store_product_id)+"/variations/"+product_map_rec.store_variant_id,variant_dict).json()
					if return_dict.has_key('message'):
						raise osv.except_osv(_('Error'),_("Can't update product stock , "+str(return_dict['message'])))
				except Exception as e:
					raise osv.except_osv(_('Error'),_("Can't update product stock, "+str(e)))
		return True


	@api.multi
	def woocommerce_post_do_transfer(self, stock_picking, mapping_ids, result):
		order_status = self.env['channel.order.states'].search([('odoo_ship_order','=',True)])
		status = order_status.channel_state
		woocommerce_order_id = mapping_ids.store_order_id
		# wcapi = self.get_woocommerce_connection()
		# data = wcapi.get('orders/'+woocommerce_order_id).json()
		# data['order'].update({'status':status})
		# msg = wcapi.put('orders/'+woocommerce_order_id,data)

	@api.multi
	def woocommerce_post_confirm_paid(self, invoice, mapping_ids, result):
		order_status = self.env['channel.order.states'].search([('odoo_set_invoice_state','=','paid')])
		status = order_status.channel_state
		woocommerce_order_id = mapping_ids.store_order_id
		# wcapi = self.get_woocommerce_connection()
		# data = wcapi.get('orders/'+woocommerce_order_id).json()
		# data['order'].update({'status':status})
		# msg = wcapi.put('orders/'+woocommerce_order_id,data)

############################CRON FUNCTIONS##################################################-
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@---Export--@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@-
	@api.model
	def export_woocommerce_product_cron(self):
		all_channel = self.env['multi.channel.sale'].search([('channel','=','woocommerce'),('state','=','validate')])
		for channel in all_channel:
			if channel.sudo().woocommerce_is_export:
				# channel.sudo().export_woocommerce_product()
				return True

	@api.model
	def update_woocommerce_customer_cron(self):
		all_channel = self.env['multi.channel.sale'].search([('channel','=','woocommerce'),('state','=','validate')])
		for channel in all_channel:
			if channel.sudo().woocommerce_is_export:
				channel.sudo().action_update_woocommerce_customers()
				# para activar la creacion de nuevos clientes comentar la linea anterior y descomentar la siguiente
				# channel.sudo().action_update_create_woocomerce_customers()
				return True

	@api.model
	def update_woocommerce_stock_cron(self):
		_logger.error('########### Entramos en update_woocommerce_stock_cron')
		all_channel = self.env['multi.channel.sale'].search([('channel','=','woocommerce'),('state','=','validate')])
		for channel in all_channel:
			if channel.sudo().woocommerce_is_export:
				_logger.error('########### Pasamos a export_woocommerce_available_stock')
				channel.sudo().export_woocommerce_available_stock()
				return True

	@api.model
	def update_woocommerce_stock_all_cron(self):
		all_channel = self.env['multi.channel.sale'].search([('channel','=','woocommerce'),('state','=','validate')])
		for channel in all_channel:
			if channel.sudo().woocommerce_is_export:
				channel.sudo().export_woocommerce_all_available_stock()
				return True

	# @api.model
	# def export_woocommerce_category_cron(self):
	# 	all_channel = self.env['multi.channel.sale'].search([('channel','=','woocommerce')])
	# 	for channel in all_channel:
	# 		if channel.woocommerce_is_export:
	# 			channel.export_woocommerce_category()
	# 			return True

#@@@@@@@@@@@@@@@@@@@@@@@@@@@@---Import--@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@-
	# @api.model
	# def import_woocommerce_products_cron(self):
	# 	all_channel = self.env['multi.channel.sale'].search([('channel','=','woocommerce'),('state','=','validate')])
	# 	for channel in all_channel:
	# 		if channel.sudo().woocommerce_is_import:
	# 			channel.sudo().import_woocommerce_products()
	# 			return True

	@api.model
	def import_woocommerce_orders_cron(self):
		all_channel = self.env['multi.channel.sale'].search([('channel','=','woocommerce')])
		for channel in all_channel:
			if channel.woocommerce_is_import:
				channel.import_woocommerce_orders()
				return True


# class ProductFeed(models.Model):
# 	_inherit = "product.feed"

# 	@api.multi
# 	def import_product(self, channel_id):
# 		mapping_dict=super(ProductFeed, self).import_product(channel_id)
# 		mapping_id=mapping_dict.get('mapping_id')
# 		if mapping_id and channel_id.id in self.env['multi.channel.sale'].search([('channel','=','woocommerce')]):
# 			template_id=mapping_id.template_name
# 			template_id.type= template_id.name in ['shipping','voucher'] and 'service' or 'product'
# 			template_id.sale_ok = template_id.type in ['service'] and False or True
# 		return mapping_dict

class ProductTempalte(models.Model):
	_inherit = "product.template"

	@api.multi
	def write(self, vals):
		status = super(ProductTempalte, self).write(vals)
		map_record = self.env['channel.template.mappings'].search([('odoo_template_id','in',self.ids)])
		if map_record:
			map_record.write(dict(need_sync = 'yes'))
		return status

class ProductProduct(models.Model):
	_inherit = "product.product"

	@api.multi
	def write(self, vals):
		status = super(ProductProduct, self).write(vals)
		product_tmpl_ids =self.mapped('product_tmpl_id.id')
		map_record = self.env['channel.template.mappings'].search([('odoo_template_id','in',product_tmpl_ids)])
		if map_record:
			map_record.write(dict(need_sync = 'yes'))
		return status


class ProductCategory(models.Model):
	_inherit = "product.category"

	@api.multi
	def write(self, vals):
		status = super(ProductCategory, self).write(vals)
		map_record = self.env['channel.category.mappings'].search([('odoo_category_id','in',self.ids)])
		if map_record:
			map_record.write(dict(need_sync = 'yes'))
		return status


class ResPartner(models.Model):
	_inherit = "res.partner"

	@api.multi
	def write(self, vals):
		status = super(ResPartner, self).write(vals)
		map_record = self.env['channel.partner.mappings'].search([('odoo_partner_id','in',self.ids)])
		if map_record:
			map_record.write(dict(need_sync = 'yes'))
		return status

class StockMove(models.Model):	
	_inherit = 'stock.move'
	
	@api.multi
	def synch_quantity(self, pick_details):
		_logger.error('########### Valor de woocomerce export entrada en synch_qty: %s', pick_details)
		for channel in pick_details['channel_ids']:
			channel_obj = self.env['multi.channel.sale']
			channel_rec = channel_obj.browse(channel)
			if channel_rec.channel == 'woocommerce':
				product_record = channel_rec.env['channel.product.mappings'].search([('erp_product_id','=',pick_details['product_id']),('channel_id.id','=',channel_rec.id)])
				if product_record:
					woocommerce = channel_rec.woocommerce_export_api_config()
					if channel_rec.location_id.id != pick_details['source_loc_id']:
						channel_rec.update_woocommerce_quantity(woocommerce, pick_details['product_qty'], product_record)
					else:
						channel_rec.update_woocommerce_quantity(woocommerce,-(pick_details['product_qty']), product_record)
		return super(StockMove, self).synch_quantity(pick_details)
	
	
class ChannelProductMappings(models.Model):
    _inherit = 'channel.product.mappings'

    act_stock = fields.Boolean(string='When selected, sync with Woocommerce', default=False)
	
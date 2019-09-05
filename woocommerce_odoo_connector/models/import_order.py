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
	def create_or_get_woocommerce_voucher(self, vouchers):
		voucher_rec = self.env['product.feed'].search([('name','=','voucher')])
		if not voucher_rec:
			voucher_rec = self.create_woocommerce_voucher()
		voucher_list = []
		for voucher in vouchers:
			voucher_line = {
							'line_name'		  		: "Voucher",
							'line_price_unit' 		: -(float(voucher['amount'])),
							'line_product_uom_qty'  : 1,
							'line_product_id'		: voucher_rec.store_id,
							'line_source'			: 'discount'
			}
			voucher_list.append((0,0,voucher_line))
		return voucher_list

	@api.multi
	def create_woocommerce_voucher(self):
		data = {
				'name'		:"voucher",
				'store_id'	:"wc",
				'channel_id':self.id,
				'type'		:'service'
		}
		product_rec = self.env['product.feed'].create(data)
		feed_res = dict(create_ids=[product_rec],update_ids=[])
		self.env['channel.operation'].post_feed_import_process(self,feed_res)
		return product_rec


	@api.multi
	def create_or_get_woocommerce_shipping(self,shipping_line,taxes):
		shipping_rec = self.env['product.feed'].search([('name','=','shipping')])
		if not shipping_rec:
			shipping_rec = self.create_woocommerce_shipping()
		shipping_list = []
		for shipping in shipping_line:
			if float(shipping['total'])>0:
				tax = (float(taxes)*100)/float(shipping['total'])
				shipping_line = {
								'line_name'		  		: "Shipping",
								'line_price_unit' 		: float(shipping['total']),
								'line_product_uom_qty'  : 1,
								'line_product_id'		: shipping_rec.store_id,
								'line_taxes'			: [{'rate':tax}],
								'line_source'			: 'delivery',
				}
				shipping_list.append((0,0,shipping_line))
		return shipping_list

	@api.multi
	def create_woocommerce_shipping(self):
		data = {
				'name'		:"shipping",
				'store_id'	:"sh",
				'channel_id':self.id,
				'type'		:'service'
		}
		product_rec = self.env['product.feed'].create(data)
		feed_res = dict(create_ids=[product_rec],update_ids=[])
		self.env['channel.operation'].post_feed_import_process(self,feed_res)
		return product_rec


	@api.multi
	def get_woocommerce_taxes(self,data):
		l = []
		# if data:
		# 	if isinstance(data['total_tax'],list):
		# 		for taxes in data:
		# 			tax = float(taxes['total_tax'])*100
		# 			tax = tax/float(taxes['total'])
		# 			l.append({'rate':tax})
		# 	else:
		# 		if float(data['total']) > 0:
		# 			tax = float(data['total_tax'])*100
		# 			tax = tax/float(data['total'])
		# 			l.append({'rate':tax})
		#los impuestos los basamos en el detalle de taxes con su id mapeado, no haciendo divisiones que nunca seran exactas
		#tomamos los impuestos totales del pedido, asi que suponemos mismos impuestos en todas las lineas
		if data:
			for d in data:
				# _logger.error('########### Valor de data -> get woocomerce taxes en import order: %s', d)
				l.append({'rate':d['rate_id']})

		return l

	@api.multi
	def get_woocommerce_order_line(self, data, taxes):
		order_lines = []
		variant = 0
		for line in data:
			# _logger.error('########### Valor de line -> get woocomerce order line en import order: %s', line)
			line_desc=''
			if line.has_key('variation_id') and line['variation_id']!=0:
				product_template_id = self.env['channel.product.mappings'].search([('store_variant_id','=',str(line['variation_id'])),('channel_id.id','=',self.id)])
			else:
				# en api legacy product_id es cada variant, no tiene valor de variation_id
				# o si no tiene variante muestra valor cero
				# product_template_id = self.env['channel.product.mappings'].search([('store_product_id','=',str(line['product_id'])),('channel_id.id','=',self.id)])
				# _logger.error('########### Buscando default_code -> get woocomerce order line en import order: %s', str(line['sku']))
				product_template_id = self.env['channel.product.mappings'].search([
					('default_code','=',str(line['sku'])),
					('channel_id.id','=',self.id)])
			# _logger.error('########### Valor de product_template_id -> get woocomerce order line en import order: %s', product_template_id)
			if len(product_template_id) > 0:
				# _logger.error('########### Valor de product_name -> get woocomerce order line en import order: %s', product_template_id[0].product_name)
				#para el name de la linea tenemos que buscar el sale_description del product en Odoo
				od_product = self.env['product.product'].browse(int(product_template_id[0].product_name))
				if od_product.description_sale:
					line_desc = od_product.description_sale
				else:
					line_desc = str(od_product.default_code) &"    "& str(od_product.name_template)
			else:
				continue
				# product_template_id = self.env['channel.product.mappings'].search([('store_product_id','=',line['product_id']),('channel_id.id','=',self.id)])
				# if product_template_id:
				# 	od_product = self.env['product.product'].browse(int(product_template_id[0].product_name))
				# 	line_desc = od_product.description_sale
				# 	if not line_desc:
				# 		line_desc = str(od_product.default_code) &"    "& str(od_product.name_template)
				# else:
				# 	# si no encuentra el producto mapeado sigue a otra linea del pedido
				# 	continue

			# if line['meta']:
			# 	variant=line['product_id']
			# else:
			# 	variant="No Variants"
			tax_lines = self.get_woocommerce_taxes(taxes)
			

			order_line_dict = {
					'line_name'				:line_desc,
					'line_price_unit'		:line['price'],
					'line_product_uom_qty'	:line['quantity'],
					'line_product_id'		:product_template_id.store_product_id,
					'line_variant_ids'		:product_template_id.store_variant_id,
					# 'line_taxes'			:self.get_woocommerce_taxes(line)
					# pasamos las lineas de impuestos utilizados en el pedido, tenemos que suponer los mismos en todas las lineas
					'line_taxes'			: tax_lines
			}
			order_lines.append((0,0,order_line_dict))
		return order_lines



	@api.multi
	def import_woocommerce_orders(self):
		# self.import_woocommerce_products()
		woocommerce = self.get_woocommerce_connection()
		# message = self.update_woocommerce_orders(woocommerce);
		message = ''
		list_order = []		
		count = 0
		context = dict(self._context)
		order_feed_data = self.env['order.feed']
		date = self.with_context({'name':'order'}).get_woocommerce_import_date()
		try:
			order_data = woocommerce.get('orders?filter[limit]=-1&filter[created_at_min]='+date).json()
		except Exception as e:
			raise osv.except_osv(_('Error'),_("Error : "+str(e)))
		# orders devuelve en WP API [{id,..},{id,...}]
		# y en legacy devuelve {'orders':[{id,...},{id,...}]}
		
		if self.api_version == 'legacyv3' and order_data.has_key('errors'):
			raise osv.except_osv(_('Error'),_("Error : "+str(order_data['errors'][0]['message'])))
		else :
			if order_data[0].has_key('message'):
				raise osv.except_osv(_('Error'),_("Error : "+str(order_data[0]['message'])))

		if self.api_version=='legacyv3':
			order_data = order_data['orders']

		# _logger.error('########### Valor de order_data en import orders %s', order_data)
		
		for order in order_data:
			if not order_feed_data.search([('store_id','=',order['id'])]):
				count = count + 1
					#order_lines = self.get_woocommerce_order_line(order['line_items'])
					# usamos la forma en la API Legacy las tax lines son de pedido, no de cada linea (igual en API WP)
				order_lines = self.get_woocommerce_order_line(order['line_items'],order['tax_lines'])
					# if order['shipping_lines']:
					#	order_lines += self.create_or_get_woocommerce_shipping(order['shipping_lines'],order['shipping_tax'])
					# if order['coupon_lines']:
					# 	order_lines+=self.create_or_get_woocommerce_voucher(order['coupon_lines'])
				if self.api_version == 'legacyv3':
					pay_method = order['payment_details']['method_title']
					comment = order['note']
				else:
					pay_method = order['payment_method_title']
					comment = order['customer_note']
				order_dict={
								'store_id'		 : order['id'],
								'channel_id'	 : self.id,
								'partner_id'	 : order['customer_id'],
								'payment_method' : pay_method,
								'line_type'		 : 'multi',
								#'carrier_id'	 : order['shipping_methods'],
								'line_ids'		 : order_lines,
								'currency'		 : order['currency'],
								#'customer_name'  : order['customer']['first_name']+" "+order['customer']['last_name'],
								#'customer_email' : order['customer']['email'],
								'order_state'	 : order['status'],
								'note'		 : comment,
								}
					# if order['billing_address']:
					# 	order_dict.update({
					# 					'invoice_partner_id': order['billing_address']['email'],
					# 					'invoice_name'	   	: order['billing_address']['first_name']+" "+order['billing_address']['last_name'],
					# 					'invoice_email'    	: order['billing_address']['email'],
					# 					'invoice_phone'    	: order['billing_address']['phone'],
					# 					'invoice_street'   	: order['billing_address']['address_1'],
					# 					'invoice_street2'  	: order['billing_address']['address_2'],
					# 					'invoice_zip'	   	: order['billing_address']['postcode'],
					# 					'invoice_city'	   	: order['billing_address']['city'],
					# 					'invoice_state_id' 	: order['billing_address']['state'],
					# 					'invoice_country_id': order['billing_address']['country'],
					# 					})
					# if order['shipping_address']:
					# 	order_dict['same_shipping_billing'] = False
					# 	order_dict.update({
					# 					'shipping_partner_id'   :order['billing_address']['email'],
					# 					'shipping_name'	   		:order['shipping_address']['first_name']+" "+order['billing_address']['last_name'],
					# 					'shipping_street'   	:order['shipping_address']['address_1'],
					# 					'shipping_street2'  	:order['shipping_address']['address_2'],
					# 					'shipping_email'		:order['billing_address']['email'],
					# 					'shipping_zip'	   		:order['shipping_address']['postcode'],
					# 					'shipping_city'	   		:order['shipping_address']['city'],
					# 					'shipping_state_id' 	:order['shipping_address']['state'],
					# 					'shipping_country_id'	:order['shipping_address']['country'],
					# 					})
				order_rec = order_feed_data.with_context(context).create(order_dict)
				list_order.append(order_rec)
		
		context.update({'group_by':'state',
						})
		feed_res = dict(create_ids=list_order,update_ids=[])
		self.env['channel.operation'].with_context(context).post_feed_import_process(self,feed_res)
		# actualiza fecha para cargar solo ordenes a partir de esta fecha de registro
		date = datetime.now().date()
		# movemos atrás un dia por si en el tiempo de importacion se registraron nuevos pedidos
		date = date - timedelta(days=1)
		# self.woocommerce_import_order_date = str(date)
		message +=  str(count)+" Order(s) Imported!"
		return self.display_message(message)
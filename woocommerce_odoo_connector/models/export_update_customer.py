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
from openerp.osv import osv
import logging
_logger	 = logging.getLogger(__name__)

class MultiChannelSale(models.Model):
	_inherit = "multi.channel.sale"

	@api.multi
	def action_update_create_woocomerce_customers(self):
		# este proceso para crear los clientes que no existen aun en Woocommerce y actualizar los restantes
		cust_n = 0
		message ='No customer updated or created'
		default_email = self.env.user.company_id.email
		odoo_customers = self.env['res.partner'].search([('customer','=',True)])
		odoo_list =[]
		for o in odoo_customers:
			customer_mapping_record = self.env['channel.partner.mappings'].search([('odoo_partner','=',o.id),('channel_id.id','=',self.id)])
			if len(customer_mapping_record) == 0:
				odoo_list.append(o.id)

		if len (odoo_list) > 0:
			for cust_record in odoo_list:
				cust = self.env['res.partner'].browse(cust_record)
				if not cust.vat:
					continue
				if cust.property_account_position and 'Recargo' in str(cust.property_account_position.name):
					rol = 'cliente_re'
				else:
					rol = 'customer'
				if self.api_version == 'legacyv3':
					cust_value_dict = {'customer':{
							"email": cust.email or default_email,
							"first_name": cust.name,
							"username": str(cust.vat)[2:],
							"password": str(cust.ref)[-4:],
							"role":rol,
							"billing_address":{
								"first_name": cust.name,
								"email": cust.email or default_email,
								},
							}
						}
				else:
					cust_value_dict = {
						"email": cust.email or default_email,
						"first_name": cust.name,
						"username": str(cust.vat)[2:],
						"password": str(cust.ref)[-4:],
						"role":rol,
						"billing":{
							"first_name": cust.name,
							"email": cust.email or default_email,
						},
					}
				return_value_dict = woocommerce.post(
					'customers', cust_value_dict
					).json()
				# _logger.error('########### Valor de return_value_dict en wooc export customers: %s', return_value_dict)

				if self.api_version == 'legacyv3' and return_value_dict.has_key('errors'):
					error = return_value_dict['errors']
					raise osv.except_osv(_('Error'),_('Error in Creating customers '+str(error[0]['message'])))
				else:
					if self.api_version == 'wpapi' and return_value_dict.has_key('message'):
						raise osv.except_osv(_('Error'),_('Error in Creating customers '+return_value_dict['message']))

				
				if self.api_version == 'legacyv3':
					result = return_value_dict['customer']
				else:
					result = return_value_dict

				cust_n += 1
				mapping_dict={
						'channel_id'		: self.id,
						'store_customer_id'	: result['id'],
						'odoo_partner_id'	: cust.id,
						'odoo_partner'		: cust.id,
				}
				obj = self.env['channel.partner.mappings']
				self._create_mapping(obj, mapping_dict)
				self._cr.commit()
			message = str(cust_n) + " customers have been exported"
		# ahora llamamos al update para actualizar el resto de posibles mapeados con need_sync
		value = self.action_update_woocommerce_customers()
		if value != '' and message != '':
			message = str(message) +' '+ str(value)
		
		return self.display_message(message)



	@api.multi
	def action_update_woocommerce_customers(self):
		message=''
		customer_mapping_record =[]
		# primero cargamos en un dict los resultados de los registros actuales
		count = 0
		if self._context.has_key('active_ids'):
			#store_category_id = 0
			#message = self.export_woocommerce_categories(0)
			customer_ids = self._context['active_ids']
			customer_mapping_record = self.env['channel.partner.mappings'].search([('odoo_partner','in',customer_ids),('channel_id.id','=',self.id)])
		else:
			# si no hay active_ids, se actualizan todos los que necesiten sincronizacion
			customer_mapping_record = self.env['channel.partner.mappings'].search([('need_sync','=','yes'),('channel_id.id','=',self.id)])
		# _logger.error('########### Valor de customer_mapping_record en action_update_wooc_customer: %s', customer_mapping_record)
		if customer_mapping_record:
			for c in customer_mapping_record:
				customer = c.store_customer_id
				customer_id = c.odoo_partner_id
				if c.need_sync == 'yes':
					count += 1
					woocommerce = self.woocommerce_export_api_config()
					result_dict = woocommerce.get('customers/'+str(customer)).json()
					# _logger.error('########### Valor de result_dict en action_update_wooc_customer: %s', result_dict)
					if result_dict.has_key('errors'):
						customer_dict = result_dict['errors']
						raise osv.except_osv(_('Error'),_("Can't fetch customer "+str(customer_dict['message'])))
					else:
						if self.api_version == 'legacyv3':
							customer_dict = result_dict['customer']
						else:
							customer_dict = result_dict
						self.ex_update_woocommerce_customers(customer_id, customer, customer_dict, woocommerce)
				c.need_sync = 'no'
			message = str(count)+" Customers has been Updated"
		else:
			message = "No Customers has been Updated" 


		return self.display_message(message)


	@api.multi
	def ex_update_woocommerce_customers(self,customer_id,store_id, customer_dict,woocommerce):
		default_email = self.env.user.company_id.email or ''
		if woocommerce and customer_id:
			cust = self.env['res.partner'].browse(customer_id)
			rol=''
			if cust.property_account_position and 'Recargo' in str(cust.property_account_position.name):
				rol = 'cliente_re'
			else:
				rol = 'customer'
			# _logger.error('########### Entra en update_wooc_customer: %s', customer_dict)

			# customer_dict.update({
			# 					"first_name" 		: cust.name,
			# 					"username" 			: str(cust.vat)[2:],
			# 					"email"				: cust.email or default_email,
			# 					"password"			: str(cust.ref)[-4:],
			# 					"role"				: rol,

			# })
			# como mandan los datos de Odoo en lugar de recuperar valores y actualizar que da problemas, reescribimos los de Odoo
			if self.api_version == 'legacyv3':
				cust_value_dict = {'customer':{
					"email": cust.email or default_email,
					"first_name": cust.name,
					"username": str(cust.vat)[2:],
					"password": str(cust.ref)[-4:],
					"role":rol,
					"billing_address":{
						"first_name": cust.name,
						"email": cust.email or default_email,
						},
					}
				}
			else:
				cust_value_dict = {
					"email": cust.email or default_email,
					"first_name": cust.name,
					"username": str(cust.vat)[2:],
					"password": str(cust.ref)[-4:],
					"role":rol,
					"billing":{
						"first_name": cust.name,
						"email": cust.email or default_email,
					},
				}


			# _logger.error('########### Valor en ex_update_woocommerce_customers del cust_value_dict: %s', cust_value_dict)
			try:
				return_dict = woocommerce.put('customers/'+str(store_id),cust_value_dict).json()
				# _logger.error('########### Valor en ex_update_woocommerce_customers del return: %s', return_dict)
				if return_dict.has_key('message'):
					raise osv.except_osv(_('Error'),_("Can't update customer , "+str(return_dict['message'])))
			except Exception as e:
				raise osv.except_osv(_('Error'),_("Can't update customer , "+str(customer_id)))
		return True
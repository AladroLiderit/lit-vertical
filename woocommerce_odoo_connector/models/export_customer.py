#!/usr/bin/env python
# -*- coding: utf-8 -*-
#################################################################################
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
	def export_woocommerce_customer_value(self):
		value = self.export_woocommerce_customers()
		message = str(value) + " customers have been exported"
		return self.display_message(message)

	@api.multi
	def export_woocommerce_customers(self):
		active_ids = self.env.context.get('active_ids')
		# default_email = self.env.user.company_id.email
		# no podemos usar default email porque nos e puede duplicar el dato de email
		cust_n = 0
		cust_records = ''
		cust_records = self.env['res.partner'].search([('id','in',active_ids)])
		woocommerce = self.woocommerce_export_api_config()
		for cust in cust_records:
			# rechazamos clientes sin NIF porque es su username
			if not cust.vat:
				continue
			mapping_rec = self.env['channel.partner.mappings'].search([('odoo_partner','=',cust.id),('channel_id.id','=',self.id)])
			if not mapping_rec:
				# para cliente con RE hay que asociar el role creado en WOC de cliente_re
				if cust.property_account_position and 'Recargo' in str(cust.property_account_position.name):
					rol = 'cliente_re'
				else:
					rol = 'customer'
				# para cliente sin correo uno inventado con su id+@ex.com
				if cust.email:
					if len(cust.email) ==0:
						cust_mail = str(cust.id) + "@ex.com"
					else:
						cust_mail = cust.email
				else:
					cust_mail = str(cust.id) + "@ex.com"

				if self.api_version == 'legacyv3':
					cust_value_dict = {'customer':{
							"email": cust_mail,
							"first_name": cust.name,
							"username": str(cust.vat)[2:],
							"password": str(cust.ref)[-4:],
							"role":rol,
							"billing_address":{
								"first_name": cust.name,
								"email": cust_mail,
								},
							}
						}
				else:
					cust_value_dict = {
						"email": cust_mail,
						"first_name": cust.name,
						"username": str(cust.vat)[2:],
						"password": str(cust.ref)[-4:],
						"role":rol,
						"billing":{
							"first_name": cust.name,
							"email": cust_mail,
						},
					}

				_logger.error('########### Valor de cust_value_dict en wooc export customers: %s', cust_value_dict)
				return_value_dict = woocommerce.post(
					'customers', cust_value_dict
					).json()
				_logger.error('########### Valor de return_value_dict en wooc export customers: %s', return_value_dict)
				if return_value_dict.has_key('errors'):
					error = return_value_dict['errors']
					raise osv.except_osv(_('Error'),_('Error in Creating customers '+str(error[0]['message'])))
				else:
					if self.api_version == 'wpapi' and return_value_dict.has_key('message'):
						raise osv.except_osv(_('Error'),_('Error in Creating customers '+return_value_dict['message']))
						
				if self.api_version == 'legacyv3':
					result = return_value_dict['customer']
				else:
					result = return_value_dict
				_logger.error('########### Valor de result en wooc export customers: %s', result)
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


		return cust_n
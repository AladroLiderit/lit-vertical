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
from openerp.osv import osv
from openerp import SUPERUSER_ID
import logging
_logger	 = logging.getLogger(__name__)

class MultiChannelSale(models.Model):
	_inherit = "multi.channel.sale"

	@api.multi
	def export_all_woocommerce_values(self):
		attr_val = 0
		attribute_value_records = ''
		attribute_value_records = self.env['product.attribute.value'].search([])
		for attribute_value in attribute_value_records:
			mapping_rec = self.env['channel.attribute.value.mappings'].search([('odoo_attribute_value_id','=',attribute_value.id),('channel_id.id','=',self.id)])
			if not mapping_rec:
				woocommerce = self.woocommerce_export_api_config()
				woocommerce_attribute_id = self.env['channel.attribute.mappings'].search([('odoo_attribute_id','=',attribute_value.attribute_id.id),('channel_id.id','=',self.id)])
				if woocommerce_attribute_id:
					attribute_id = woocommerce_attribute_id.store_attribute_id
					if self.api_version == 'legacyv3':
						attribute_value_dict = {"product_attribute_term":{
												"name": attribute_value.name,
												}
						}
					else:
						attribute_value_dict = {
											"name": attribute_value.name,
						}
					return_value_dict = woocommerce.post(
															'products/attributes/'+str(attribute_id)+"/terms",
															attribute_value_dict
					).json()
					if return_value_dict.has_key('message'):
						raise osv.except_osv(_('Error'),_('Error in Creating terms '+str(return_dict['message'])))
					attr_val += 1
					if self.api_version=='legacyv3':
						return_dict = return_value_dict['product_attribute_term']
					else:
						return_dict = return_value_dict
					mapping_dict={
								'channel_id'				: self.id,
								'store_attribute_value_id'	: return_dict['id'],
								'odoo_attribute_value_id'	: attribute_value.id,
								'attribute_value_name'		: attribute_value.id,
					}
					obj = self.env['channel.attribute.value.mappings']
					self._create_mapping(obj, mapping_dict)
					self._cr.commit()
		return attr_val

	@api.multi
	def export_all_woocommerce_attribute_values(self):
		attr = 0
		attr_val = 0
		attribute_value_records = ''
		attribute_records = self.env['product.attribute'].search([])
		for attribute in attribute_records:
			mapping_rec = self.env['channel.attribute.mappings'].search([('odoo_attribute_id','=',attribute.id),('channel_id.id','=',self.id)])
			if not mapping_rec:
				woocommerce = self.woocommerce_export_api_config()
				if self.api_version == 'legacyv3':
					attribute_dict = {"product_attribute":{
									    "name"			: attribute.name,
										"type"			: "select",
									    "order_by"		: "menu_order",
									    "has_archives"	: True
									    }
					}
				else:
					attribute_dict = {
								    "name"			: attribute.name,
									"type"			: "select",
								    "order_by"		: "menu_order",
								    "has_archives"	: True
								    }

				return_dict = woocommerce.post('products/attributes',
												attribute_dict
				).json()
				# _logger.error('########### Valor de return_dict en wooc export atributes: %s', return_dict)
				attr += 1
				if return_dict.has_key('errors'):
					raise osv.except_osv(_('Error'),_('Error in Creating Attributes :'+str(return_dict['errors'])))
				if self.api_version == 'legacyv3':
					result = return_dict['product_attribute']
				else:
					result = return_dict
				mapping_dict = {
							'channel_id'		: self.id,
							'store_attribute_id': result['id'],
							'odoo_attribute_id' : attribute.id,
							'attribute_name'	: attribute.id,
				}
				obj = self.env['channel.attribute.mappings']
				self._create_mapping(obj, mapping_dict)
				attribute_value_records = self.env['product.attribute.value'].search(
												[('attribute_id','=',attribute.id)]
										)
				for attribute_value in attribute_value_records:
					mapping_rec = self.env['channel.attribute.value.mappings'].search(
								[('odoo_attribute_value_id','=',attribute_value.id),('channel_id.id','=',self.id)]
								)
					if not mapping_rec:
						if self.api_version == 'legacyv3':
							attribute_value_dict = {"product_attribute_term":{
													"name": attribute_value.name,
													}
							}
						else:
							attribute_value_dict = {
												"name": attribute_value.name,
												}

						return_value_dict = woocommerce.post('products/attributes/' + str(result['id']) + "/terms", attribute_value_dict).json()
						if return_value_dict.has_key('message'):
							raise osv.except_osv(_('Error'),_('Error in Creating Attributes Terms :'+str(return_dict['message'])))
						if self.api_version == 'legacyv3':
							result_val = return_value_dict['product_attribute_term']
						else:
							result_val = return_value_dict
						attr_val += 1
						mapping_dict = {
									'channel_id'				: self.id,
									'store_attribute_value_id'	: result_val['id'],
									'odoo_attribute_value_id'	: attribute_value.id,
									'attribute_value_name'		: attribute_value.id,
						}
						obj = self.env['channel.attribute.value.mappings']
						self._create_mapping(obj, mapping_dict)
						self._cr.commit()
		return attr,attr_val

	#export attribute and value
	@api.multi
	def export_woocommerce_attributes_values(self):
		# self.import_woocommerce_attribute()
		attribute,value = self.export_all_woocommerce_attribute_values()
		value1 = self.export_all_woocommerce_values()
		value = value + value1
		message = str(attribute) + " Attributes have been exported & " + str(value) + " Attribute Terms have been exported"
		return self.display_message(message)

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
import os
import base64
import logging
_logger	 = logging.getLogger(__name__)

class MultiChannelSale(models.Model):
	_inherit = "multi.channel.sale"

	@api.multi
	def export_update_woocommerce_product(self):
		count = 0
		# self.export_woocommerce_categories(0);
		# self.export_all_woocommerce_attribute_values()
		template_mapping = self.env['channel.template.mappings'].search([('need_sync','=','yes'),('channel_id.id','=',self.id)])
		for check in template_mapping:
			count=len(template_mapping)
			template = check.template_name
			store_id = check.store_product_id
			woocommerce = self.woocommerce_export_api_config()
			try:
				product_dict = woocommerce.get('products/'+str(store_id)).json()

				if product_dict.has_key('message'):
					raise osv.except_osv(_('Error'),_("Can't fetch product "+str(product_dict['message'])))
				else:
					if self.api_version == 'legacyv3':
						product_dict = product_dict ['product']
					if product_dict['type'] == 'simple':
						if len(template.product_variant_ids) == 1 and not template.attribute_line_ids:
							status = self.update_woocommerce_simple_product(template, store_id, product_dict, woocommerce)
							if status:
								message = "Products Updated Successfully , "
						elif len(template.product_variant_ids) >= 1 and template.attribute_line_ids:
							count = self.update_woocommerce_simple2variable_product(template, store_id,  product_dict, woocommerce)
							if count:
								message = str(count)+" Variants added, Product updated Successfully , "
						else:
							raise osv.except_osv(_('Error'),_('No Variant'))
					elif product_dict['type'] == 'variable':
						product_map = self.env['channel.product.mappings'].search([('odoo_template_id.id','=',template.id),('channel_id.id','=',self.id)])
						if len(product_map) == len(template.product_variant_ids):
							status = self.update_woocommerce_variable_product(template, product_map, product_dict, woocommerce)
							if status:
								message = "Products Updated! , "
						else:
							status = self.update_create_woocommerce_variable_product(template, product_map, product_dict, woocommerce)
							if status:
								message = "Products Updated! , "
					else:
						raise osv.except_osv(_('Error'),_("Product Type Not Supported"))
			except Exception as e:
				raise osv.except_osv(_('Error'),_("Can't fetch product"+str(template)))
			check.need_sync = 'no'
		return str(count) + " Products Updated! , "


	@api.multi
	def action_update_woocommerce_products(self):
		template_ids = []
		message = ''
		if self._context.has_key('active_ids'):
			if self._context['active_model'] == 'product.template':
				template_ids = self._context['active_ids']
			elif self._context['active_model'] == 'product.product':
				product_records = self.env['product.product'].browse(self._context['active_ids'])
				for product in product_records:
					template_ids.append(product.product_tmpl_id.id)
			else:
				raise osv.except_osv(_('Error'),_('Context is Empty'))

			for template_id in template_ids:
				check = self.env['channel.template.mappings'].search([('odoo_template_id','=',template_id),('channel_id.id','=',self.id)])
				if not check:
					return self.action_export_woocommerce_products()
				else:
					template = check.template_name
					store_id = check.store_product_id
					woocommerce = self.woocommerce_export_api_config()

					try:
						_logger.error('########### Valor en update wooc products para store_id: %s', str(store_id))
						result_dict = woocommerce.get('products/'+str(store_id)).json()
						if result_dict.has_key('message'):
							raise osv.except_osv(_('Error'),_("Can't fetch product "+str(product_dict['message'])))
						else:
							if self.api_version == 'legacyv3':
								product_dict = result_dict['product']
							else:
								product_dict = result_dict
							# _logger.error('########### Valor de product_dict en update wooc products: %s', product_dict)
							# _logger.error('########### Valor de product_dict_type en update wooc products: %s', product_dict['type'])
							if product_dict['type'] == 'simple':
								if len(template.product_variant_ids) == 1 and not template.attribute_line_ids:
									status = self.update_woocommerce_simple_product(template, store_id, product_dict, woocommerce)
									if status:
										message = "Product Updated Successfully , "
								elif len(template.product_variant_ids) >= 1 and template.attribute_line_ids:
									count = self.update_woocommerce_simple2variable_product(template, store_id,  product_dict, woocommerce)
									if count:
										message = str(count)+" Variants added, Product updated Successfully , "
								else:
									raise osv.except_osv(_('Error'),_('No Variant'))
							elif product_dict['type'] == 'variable':
								product_map = self.env['channel.product.mappings'].search([('odoo_template_id.id','=',template.id),('channel_id.id','=',self.id)])
								if len(product_map) == len(template.product_variant_ids):
									status = self.update_woocommerce_variable_product(template, product_map, product_dict, woocommerce)
									if status:
										message = "Products Updated! , "
								else:
									status = self.update_create_woocommerce_variable_product(template, product_map, product_dict, woocommerce)
									if status:
										message = "Products Updated! , "
							else:
								raise osv.except_osv(_('Error'),_("Product Type Not Supported"))
					except Exception as e:
						raise osv.except_osv(_('Error'),_("Can't fetch product , "+str(template)))
				check.need_sync = 'no'
			return self.display_message(message)

	@api.multi
	def update_woocommerce_simple_product(self, template, store_id, product_dict, woocommerce):
		if woocommerce and template:
			_logger.error('########### Entra en update_wooc_simple_product: %s', product_dict)
			status = 'draft'
			if template.active:
				status = 'publish'
			quantity = template.immediately_usable_qty
			product_dict.update({
								'name' 				: template.name,
								'title' 			: template.name,
								# 'images'			: self.create_woocommerce_product_image(template),
								'sku' 				: template.default_code or "",
								'regular_price'		: str(template.list_price) or "",
								'categories'		: self.set_woocommerce_product_categories(template),
								# 'short_description'	: template.description_sale  or "" ,
								'description'		: template.name or "",
								'price'				: template.list_price,
								'status'			: status,
								'stock_quantity'	: quantity,

			})
			_logger.error('########### Valor en update_wooc_simple_product del product_dict con uptada: %s', product_dict)
			try:
				result_dict = {}
				if self.api_version == 'legacyv3':
					result_dict['product']= product_dict
				else:
					result_dict= product_dict
				_logger.error('########### Valor en update_wooc_simple_product del result_dict: %s', result_dict)
				return_dict = woocommerce.put('products/'+str(store_id),result_dict).json()
				_logger.error('########### Valor en update_wooc_simple_product del return: %s', return_dict)
				if return_dict.has_key('message'):
					raise osv.except_osv(_('Error'),_("Can't update product , "+str(return_dict['message'])))
			except Exception as e:
				raise osv.except_osv(_('Error'),_("Can't update product , "+str(template.name)))
		return True

	@api.multi
	def update_woocommerce_simple2variable_product(self, template, store_id, product_dict, woocommerce):
		# al cambiar la API hay que agregar aqui las variaciones al crear el producto, no se hacen luego por separado
		variant_data=[]
		count = 0
		for variant in template.product_variant_ids:
			match_record = self.env['channel.product.mappings'].search([('product_name','=',variant.id),('channel_id.id','=',self.id)])
			if not match_record:
				quantity = variant.immediately_usable_qty

				variant_data.append( {
									'regular_price'	: str(variant.list_price) or "",
									'visible'		: True,
									# 'sku'			: variant.default_code or "",
									'stock_quantity': quantity,
									'description'	: variant.name or "",
									'price'			: variant.list_price,
									#'manage_stock'	: True,
									'managing_stock'	: True,
									'stock_quantity'	: quantity,
									# 'in_stock'		: True,
									'attributes'	: self.get_woocommerce_attribute_dict(variant),
								})
				count +=1


		if woocommerce and template:
			status = 'draft'
			if template.active:
				status = 'publish'
			product_dict.update({
								'name' 				: template.name,
								'title' 			: template.name,
								#'images'			: self.create_woocommerce_product_image(template, True),
								'sku' 				: template.default_code or "",
								'regular_price'		: str(template.list_price) or "",
								'type'				: 'variable',
								'attributes'		: self.set_woocommerce_attribute_line(template),
								'default_attributes': self.get_woocommerce_attribute_dict(template.product_variant_ids[0]),
								'categories'		: self.set_woocommerce_product_categories(template),
								# 'short_description'	: template.description_sale  or "" ,
								# 'description'		: template.description or "",
								'description'		: template.name,
								'price'				: template.list_price,
								'status'			: status,
								'variations'		: variant_data,
			})
			try:
				result_dict = {}
				if self.api_version == 'legacyv3':
					result_dict['product']= product_dict
				else:
					result_dict= product_dict
				return_dict  = woocommerce.put('products/'+str(store_id),result_dict).json()
				unlink_record = self.env['channel.product.mappings'].search([('odoo_template_id.id','=',template.id),('channel_id.id','=',self.id)])
				unlink_record.unlink()
				if return_dict.has_key('message'):
					raise osv.except_osv(_('Error'),_("Can't update product from simple to variable"+str(return_dict['message'])))
				else:
					# image_ids = []
					# for image in return_dict['images']:
					# 	if image['position'] != 0:
					# 		image_ids.append(image['id'])
					# if image_ids:
					# 	count = self.create_woocommerce_variation(return_dict['id'], template, woocommerce, image_ids)
					# else:
					# 	count = self.create_woocommerce_variation(return_dict['id'], template, woocommerce)
					if count:
						return count
			except Exception as e:
				raise osv.except_osv(_('Error'),_("Can't update product from simple to variable"))

	def update_woocommerce_variable_product(self, template, product_map, product_dict, woocommerce):
		# al cambiar la API hay que agregar aqui las variaciones al crear el producto, no se hacen luego por separado
		variant_data=[]
		count = 0
		for variant in template.product_variant_ids:
			match_record = self.env['channel.product.mappings'].search([('product_name','=',variant.id),('channel_id.id','=',self.id)])
			if not match_record:
				quantity = variant.immediately_usable_qty

				variant_data.append( {
									'regular_price'	: str(variant.list_price) or "",
									'visible'		: True,
									# 'sku'			: variant.default_code or "",
									'stock_quantity': quantity,
									'description'	: variant.name or "",
									'price'			: variant.list_price,
									#'manage_stock'	: True,
									'managing_stock'	: True,
									'stock_quantity'	: quantity,
									# 'in_stock'		: True,
									'attributes'	: self.get_woocommerce_attribute_dict(variant),
								})
				count +=1

		if woocommerce and template:
			status = 'draft'
			if template.active:
				status = 'publish'
			product_dict.update({
								'name' 				: template.name,
								'title' 				: template.name,
								# 'images'			: self.create_woocommerce_product_image(template, True),
								'sku' 				: "",
								'regular_price'		: str(template.list_price) or "",
								'type'				: 'variable',
								'attributes'		: self.set_woocommerce_attribute_line(template),
								'default_attributes': self.get_woocommerce_attribute_dict(template.product_variant_ids[0]),
								'categories'		: self.set_woocommerce_product_categories(template),
								# 'short_description'	: template.description_sale  or "" ,
								# 'description'		: template.description or "",
								'description'		: template.name,
								'price'				: template.list_price,
								'status'			: status,
								'variations'		: variant_data,
			})
			try:
				result_dict = {}
				if self.api_version == 'legacyv3':
					result_dict['product']= product_dict
				else:
					result_dict= product_dict
				return_dict  = woocommerce.put('products/'+str(product_dict['id']),result_dict).json()
				if return_dict.has_key('message'):
					raise osv.except_osv(_('Error'),_("Can't update variable product : "+str(return_dict['message'])))
				else:
					if self.api_version == 'wpapi':
						image_ids = []
						for image in return_dict['images']:
							if image['position'] != 0:
								image_ids.append(image['id'])
						if image_ids:
							count = self.update_woocommerce_variation(return_dict['id'],template, product_map,woocommerce, image_ids)
						else:
							count = self.update_woocommerce_variation(return_dict['id'], template, product_map,woocommerce)
					if count:
						return count
			except Exception as e:
				raise osv.except_osv(_('Error'),_("Can't update  variable product "+str(template.name)))

	@api.multi
	def update_woocommerce_variation(self, store_product_id, template, product_map, woocommerce, image_ids = False):
		count = 0
		if store_product_id and woocommerce and product_map:
			for product in product_map:
				store_variant_id = product.store_variant_id
				variant = product.product_name
				variant_data = {
								'regular_price'	: str(variant.lst_price) or "",
								'visible'		: True,
								'sku'			: variant.default_code or "",
								'description'	: variant.description or "",
								'price'			: variant.lst_price,
								'attributes'	: self.get_woocommerce_attribute_dict(variant),
				}
				if image_ids:
					variant_data.update({'image': {'id':image_ids[count]}})
				if woocommerce:
					try:
						return_dict = woocommerce.put("products/"+str(store_product_id)+"/variations/"+str(store_variant_id),variant_data).json()
						if return_dict.has_key('message'):
							raise osv.except_osv(_('Error'),_("Can't Update variant "+str(return_dict['message'])))
						count += 1
					except Exception as e:
						raise osv.except_osv(_('Error'),_("Can't Update variant "+str(product.name)))
			return count

	@api.multi
	def update_create_woocommerce_variable_product(self, template, product_map, product_dict, woocommerce):
		if woocommerce and template:
			status = 'draft'
			if template.active:
				status = 'publish'
			product_dict.update({
								'name' 				: template.name,
								# 'images'			: self.create_woocommerce_product_image(template, True),
								'sku' 				: "",
								'regular_price'		: str(template.list_price) or "",
								'type'				: 'variable',
								'attributes'		: self.set_woocommerce_attribute_line(template),
								'default_attributes': self.get_woocommerce_attribute_dict(template.product_variant_ids[0]),
								'categories'		: self.set_woocommerce_product_categories(template),
								# 'short_description'	: template.description_sale  or "" ,
								# 'description'		: template.description or "",
								'description'		: template.name,
								'price'				: template.list_price,
								'status'			: status,
			})
			try:
				return_dict  = woocommerce.put('products/'+str(product_dict['id']),product_dict).json()
				if return_dict.has_key('message'):
					raise osv.except_osv(_('Error'),_("Can't update product from simple to variable"+str(return_dict['message'])))
				else:
					image_ids = []
					for image in return_dict['images']:
						if image['position'] != 0:
							image_ids.append(image['id'])
					if image_ids:
						count = self.update_woocommerce_variation(return_dict['id'],template, product_map,woocommerce, image_ids)
					else:
						count = self.update_woocommerce_variation(return_dict['id'], template, product_map,woocommerce)
					if count:
						if image_ids:
							self.create_woocommerce_extra_variation(return_dict['id'], template, woocommerce ,  count, image_ids)
						else:
							self.create_woocommerce_extra_variation(return_dict['id'], template, woocommerce ,  count)
					return count
			except Exception as e:
				raise osv.except_osv(_('Error'),_("Can't update product from simple to variable"))

	@api.multi
	def create_woocommerce_extra_variation(self, store_product_id, template,woocommerce , count, image_ids=False):
		if store_product_id and woocommerce:
			if store_product_id and template:
				for variant in template.product_variant_ids:
					match_record = self.env['channel.product.mappings'].search([('erp_product_id','=',variant.id),('channel_id.id','=',self.id)])
					if not match_record:
						qty = variant._product_available()
						quantity = qty[variant.id]['qty_available'] - qty[variant.id]['outgoing_qty']
						variant_data = {
										'regular_price'	: str(variant.lst_price) or "",
										'visible'		: True,
										'sku'			: variant.default_code or "",
										'stock_quantity': quantity,
										'description'	: variant.description or "",
										'price'			: variant.lst_price,
										'manage_stock'	: True,
										'in_stock'		: True,
										'attributes'	: self.get_woocommerce_attribute_dict(variant),
									}
						if image_ids:
							variant_data.update({'image' : {'id':image_ids[count]},})
						if woocommerce:
							try:
								return_dict = woocommerce.post("products/"+str(store_product_id)+"/variations",variant_data).json()
								if return_dict.has_key('message'):
									raise  osv.except_osv(_('Error'),"Error in Updation and Creation of variant during update"+str(return_dict['message']))
								count += 1
							except Exception as e:
								raise osv.except_osv(_('Error'),"Error in Updation and Creation of variant during update"+str(variant.name))
							if 	return_dict.has_key('id'):
								mapping_dict = {
											'channel_id'		: self.id,
											'store_product_id'	: store_product_id,
											'store_variant_id'	: return_dict['id'],
											'odoo_template_id'	: template.id,
											'product_name'		: variant.id,
											'erp_product_id'	: variant.id,
											'default_code'		: variant.default_code or "",
								}
								obj = self.env['channel.product.mappings']
								self._create_mapping(obj, mapping_dict)
							else :
								raise osv.except_osv(_('Error'),_('Error in creating variant : '+str(return_dict['message'])))
				return count
			else:
				raise osv.except_osv(_('Error'),_('Error in creating variant'))

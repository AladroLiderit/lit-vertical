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
from openerp import SUPERUSER_ID
import base64
import logging
import paramiko

_logger	 = logging.getLogger(__name__)

class MultiChannelSale(models.Model):
	_inherit = "multi.channel.sale"

	@api.multi
	def action_export_woocommerce_products(self):
		# self.sudo().export_woocommerce_attributes_values()
		# self.sudo().export_woocommerce_categories(0)
		# antes de nada, solo podemos enlazar productos en API REST de WP por las variantes
		if self.api_version == 'legacyv3':
			raise osv.except_osv(_('Error'),_('No se puede enlazar productos en Legacy V3'))
		woocommerce = self.woocommerce_export_api_config()
		count = 0;
		template_ids = []
		if self._context.has_key('active_ids'):
			if self._context['active_model'] == 'product.template':
				template_ids = self._context['active_ids']
			elif self._context['active_model'] == 'product.product':
				product_records = self.env['product.product'].browse(self._context['active_ids'])
				for product in product_records:
					template_ids.append(product.product_tmpl_id.id)
			else:
				raise osv.except_osv(_('Error'),_('Context Empty'))
		template_records = self.env['product.template'].browse(template_ids)
		for template in template_records:
			mapping_record = self.env['channel.template.mappings'].search([('odoo_template_id','=',template.id),('channel_id.id','=',self.id)])
			if not mapping_record:
				if template.attribute_line_ids:
					# todos los product template con mas de una variante
					count += self.create_woocommerce_variable_product(template, woocommerce)
				else:
					# los producto template que solo tienen una variante
					count += self.create_woocommerce_simple_product(template, woocommerce)
		return self.display_message(str(count)+" Products have been exported")

	# @api.multi
	# def set_woocommerce_image_path(self, name, data):
	# 	name = str(name)
	# 	name = name.replace(" ","")
	# 	base_url = self.env['ir.config_parameter'].get_param('web.base.url')
	# 	direct = os.path.abspath(os.path.join(os.path.realpath(__file__+'/../'), os.pardir))
	# 	f = open(direct+'/static/img/'+name+'.png','w')
	# 	f.write(base64.decodestring(data))
	# 	f.close
	# 	url = base_url+"/woocommerce_odoo_connector/static/img/"+name+".png"
	# 	return url,name

	# cambiamos la funcion para que busque la imagen en el repositorio del servidor
	# aunque esto queda pendiente sin aplicar por si se puede utilizar la imagen en URL externa y asi no almacena imagen
	@api.multi
	def set_woocommerce_image_path(self, name, code):
		name = str(name)
		name = name.replace(" ","")
		base_url = self.env['ir.config_parameter'].get_param('stylearistos.foto.url')
		# _logger.error('########### En image_path valor de base_url: %s', base_url)
		if base_url:
			url=''
			if str(base_url)[-1] != '/':
				base_url = str(base_url)+ '/'
				# _logger.error('########### Agregando slash final en el path del image: %s', base_url)
			carpeta = code[:3]
			url = base_url+carpeta+"/"+code+".jpg"
			return url,name
		else:
			return False, False
		
	@api.multi
	def get_woocommerce_image(self, code):
		
		host = self.sftp
		puerto = self.sftp_port
		usuario = self.sftp_user
		passwd = self.sfpt_pass

		count = 0 

		if host and puerto and usuario and passwd:
			datos = dict(hostname=host, port=puerto, username=usuario, password=passwd)

			ssh_client = paramiko.SSHClient()
			ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
			ssh_client.connect(**datos)

			sftp = ssh_client.open_sftp()
			archivos = sftp.listdir()
			carpeta = code[:3]
			file_name = carpeta+'/'+code+'.jpg'
			
			for archivo in archivos:
				if archivo == file_name:
					count += 1
					sftp.close()
					ssh_client.close()
					return file_name
			sftp.close()
					
		if count == 0:
			ssh_client.close()
			return False


	@api.multi
	def move_woocommerce_image(self, code):

		host = self.sftp
		puerto = self.sftp_port
		usuario = self.sftp_user
		passwd = self.sfpt_pass

		if host and puerto and usuario and passwd:
			datos = dict(hostname=host, port=puerto, username=usuario, password=passwd)

			ssh_client = paramiko.SSHClient()
			ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
			ssh_client.connect(**datos)

			sftp = ssh_client.open_sftp()

			try:
				local = self.env['ir.config_parameter'].get_param('stylearistos.foto.url')
				carpeta = code[:3]
				local = local+'/'+code+'.jpg'
				remoto = '/html/wp-content/upload/images/'+carpeta+'/'+code+'.jpg'
				sftp.put(local, remoto)
				print "copiado archivo %s." % local
			except:
				print "Fallo al intentar copiar %s. Tal vez es un directorio." % remoto

			sftp.close()
			ssh_client.close()


	@api.multi
	def create_woocommerce_product_image(self, template, variant = False):
		# se utiliza el Woocommerce pluggin 'Media Library Folders' y se crea la carpeta images para estas imagenes
		# hay una subcarpeta para cada grupo de productos por los 3 primeros digitos de la ref. interna
		# ademas se tiene que registrar en Parametros de Sistema el valor para stylearistos.foto.url del path anterior
		if template.image and template.default_code:
			image_list = []
			count = 0;
			## comprobamos que exista el fichero con el nombre de la imagen
			# alta_imagen = self.get_woocommerce_image(template.default_code)
			## si no retorna un nombre de fichero hay que mover el fichero con sftp
			# if not alta_imagen:
			# 	self.move_woocomerce_image(template.default_code)
			## template_url,name = self.set_woocommerce_image_path(template.name, template.image)
			# template_url,name = self.set_woocommerce_image_path(template.name, template.default_code)
			code = template.default_code[:3]
			template_url = self.url+'/wp-content/uploads/images/'+code+'/'+template.default_code+'.jpg'
			_logger.error('########### Valor del product_image retornado: %s', template_url)
			if template_url:
				image_list.append({
					'src'		: template_url,
					'name'		: template.name,
					'alt'		: template.name,
					'position'	: 0,
				})
			# imagen solo en el producto principal, variantes sin imagen
			# if variant:
			# 	for variation in template.product_variant_ids:
			# 		count += 1
			# 		# variant_url,name = self.set_woocommerce_image_path(variation.name+str(count),variation.image)
			# 		variant_url,name = self.set_woocommerce_image_path(variation.name+str(count),variation.default_code)
			# 		image_list.append({
			# 			'src'		: variant_url,
			# 			'name'		: name,
			# 			'position'	: count,
			# 		})
			_logger.error('########### Valor del image_list retornado: %s', template_url)
			return image_list

	@api.multi
	def get_woocommerce_attribute_dict(self, variant):
		if variant:
			attribute_dict = []
			if variant.attribute_value_ids:
				for attribute_line in variant.attribute_value_ids:
					attr_name,attr_id  = self.get_woocommerce_attribute(attribute_line.attribute_id)
					value_name = attribute_line.name
					attribute_dict.append({
										'id'	: attr_id,
										'name'	: attr_name,
										'option': value_name, 
															})
				return attribute_dict

	@api.multi
	def get_woocommerce_attribute_value(self, attribute_line):
		value_list = []
		if attribute_line:
			for value in attribute_line.value_ids:
				value_list.append(value.name)
		return value_list

	@api.multi
	def get_woocommerce_attribute(self, attribute_id):
		if  attribute_id:
			record  =  self.env['channel.attribute.mappings'].search([('odoo_attribute_id','=',attribute_id.id),('channel_id.id','=',self.id)])
			if record:
				return attribute_id.name,record.store_attribute_id

	@api.multi
	def set_woocommerce_attribute_line(self, template):
		attribute_list = []
		attribute_count = 0
		if template.attribute_line_ids:
			for attribute_line in template.attribute_line_ids:
				attr_name,attr_id = self.get_woocommerce_attribute(attribute_line.attribute_id)
				values = self.get_woocommerce_attribute_value(attribute_line)
				attribute_dict = {
								'name'		: attr_name,
								'id'		: attr_id,
								'variation'	: True,
								'visible'	: True,
								'position'	: attribute_count,
								'options'	: values,
				}
				attribute_count += 1
				attribute_list.append(attribute_dict)
		return attribute_list

	@api.multi
	def set_woocommerce_tags(self, template):
		tag_list = []
		tag_count = 0
		if template.type_of_material_id:
			record  =  self.env['channel.tag.mappings'].search([('odoo_tag_id','=',template.type_of_material_id.id),('channel_id.id','=',self.id)])
			if len(record)==0:
				raise osv.except_osv(_('Error'),_('New tags values in Type of Material'))

			tag_dict = {
					'id'		: record[0].store_tag_id,
			}
			tag_count += 1
			tag_list.append(tag_dict)
		if template.gender:
			record  =  self.env['channel.gender.mappings'].search([('odoo_tag_id','=',template.gender),('channel_id.id','=',self.id)])
			if len(record)==0:
				raise osv.except_osv(_('Error'),_('New tags values in Gender'))
			tag_dict = {
					'id'		: record[0].store_tag_id,
			}
			tag_count += 1
			tag_list.append(tag_dict)

		return tag_list


	# Las variantes en la API Legacy no se crean por separado del producto
	@api.multi
	def create_woocommerce_variation(self, woo_product_id, template, woocommerce, image_ids = False):
		count = 0
		if woo_product_id and template:
			for variant in template.product_variant_ids:
				match_record = self.env['channel.product.mappings'].search([('product_name','=',variant.id),('channel_id.id','=',self.id)])
				if not match_record:
					# qty = variant._product_available()
					# quantity = qty[variant.id]['qty_available'] - qty[variant.id]['outgoing_qty']
					quantity = variant.immediately_usable_qty
					variant_data = {
									'regular_price'	: str(variant.list_price) or "",
									'visible'		: True,
									# 'sku'			: variant.default_code or "",
									'stock_quantity': quantity,
									'description'	: variant.name or "",
									'price'			: variant.list_price,
									'manage_stock'	: True,
									# 'in_stock'		: True,
									'attributes'	: self.get_woocommerce_attribute_dict(variant),
								}
					# if image_ids:
					# 	variant_data.update({'image': {'id':image_ids[count]}})
					if woocommerce:
						return_dict = woocommerce.post("products/"+str(woo_product_id)+"/variations",variant_data).json()
						count += 1
						if 	return_dict.has_key('id'):
							mapping_dict = {
										'channel_id'		: self.id,
										'store_product_id'	: woo_product_id,
										'store_variant_id'	: return_dict['id'],
										'odoo_template_id'	: template.id,
										'product_name'		: variant.id,
										'erp_product_id'	: variant.id,
										'default_code'		: variant.default_code or "",
							}
							obj = self.env['channel.product.mappings']
							self._create_mapping(obj, mapping_dict)
						else :
							raise osv.except_osv(_('Error'),_('Error in creating variant'))
			return count
		else:
			raise osv.except_osv(_('Error'),_('Error in creating variant'))

	@api.multi
	def create_woocommerce_variable_product(self, template, woocommerce):
		if template:
			# al cambiar la API hay que agregar aqui las variaciones al crear el producto, no se hacen luego por separado
			
			variant_data=[]
			count = 0
			if self.api_version == 'legacyv3':
				for variant in template.product_variant_ids:
					match_record = self.env['channel.product.mappings'].search([('product_name','=',variant.id),('channel_id.id','=',self.id)])
					if not match_record:
						# qty = variant._product_available()
						# quantity = qty[variant.id]['qty_available'] - qty[variant.id]['outgoing_qty']
						quantity = variant.immediately_usable_qty

						variant_data.append( {
										'regular_price'	: str(variant.list_price) or "",
										'visible'		: True,
										# 'sku'			: variant.default_code or "",
										'description'	: variant.name or "",
										'price'			: variant.list_price,
										#'manage_stock'	: True,
										'managing_stock': True,
										'stock_quantity': quantity,
										# 'in_stock'	: True,
										'attributes'	: self.get_woocommerce_attribute_dict(variant),
									})
						# y falta hacer el mapping de las variantes en product
						count+=1
			if self.api_version == 'legacyv3':
				product_dict = {'product':{
							'name'				: template.name,
							'title'				: template.name,
							# 'sku' 				: "",
							# al manejar mismo codigo para todas las variantes tenemos que ponerlo aqui y no en las variaciones
							'sku' 				: template.default_code or "",
							'images'			: self.create_woocommerce_product_image(template,True),
							'type'				: 'variable',
							'categories'		: self.set_woocommerce_product_categories(template),
							'status'			: 'publish',
							#'manage_stock'		: False,
							'managing_stock'		: False,
							'attributes'		: self.set_woocommerce_attribute_line(template),
							'tags'				: self.set_woocommerce_tags(template),
							'default_attributes': self.get_woocommerce_attribute_dict(template.product_variant_ids[0]),
							# 'short_description'	: template.description_sale  or "",
							'description'		: template.name  or "",
							'variations'		: variant_data,
					}
				}
			else:
				product_dict = {
						'name'				: template.name,
						'title'				: template.name,
						# 'sku' 				: "",
						# al manejar mismo codigo para todas las variantes tenemos que ponerlo aqui y no en las variaciones
						'sku' 				: template.default_code or "",
						'images'			: self.create_woocommerce_product_image(template,True),
						'type'				: 'variable',
						'categories'		: self.set_woocommerce_product_categories(template),
						'status'			: 'publish',
						'manage_stock'		: False,
						'attributes'		: self.set_woocommerce_attribute_line(template),
						'tags'				: self.set_woocommerce_tags(template),
						'default_attributes': self.get_woocommerce_attribute_dict(template.product_variant_ids[0]),
						# 'short_description'	: template.description_sale  or "",
						'description'		: template.name  or "",
				}

			_logger.error('########### Valor en create variant product del dict: %s', product_dict)
			if woocommerce:
				result  = woocommerce.post('products',product_dict).json()
				_logger.error('########### Valor en create variant product del result: %s', result)
				if self.api_version == 'legacyv3':
					return_dict = result['product']
				else:
					return_dict = result
					# en wpapi tenemos que crear las variantes despues del producto
					count = self.create_woocommerce_variation(return_dict['id'], template, woocommerce)
				
				# image_ids = []
				# for image in return_dict['images']:
				# 	if image['position'] != 0:
				# 		image_ids.append(image['id'])
				if return_dict.has_key('id'):
					mapping_dict = {
								'channel_id'		: self.id,
								'store_product_id'	: return_dict['id'],
								'odoo_template_id'	: template.id,
								'template_name'		: template.id,
								'default_code'		: template.default_code or "",
					}
					obj = self.env['channel.template.mappings']
					self._create_mapping(obj, mapping_dict)

				# if return_dict.has_key('variations'):
				# 	variant = return_dict['variations']
				# 	for v in variant:
				# 		mapping_dict = {
				# 							'channel_id'		: self.id,
				# 							'store_product_id'	: return_dict['id'],
				# 							'store_variant_id'	: return_dict['id'],
				# 							'odoo_template_id'	: template.id,
				# 							'product_name'		: variant.id,
				# 							'erp_product_id'	: variant.id,
				# 							'default_code'		: variant.default_code or "",
				# 				}
				# 		obj = self.env['channel.product.mappings']
				# 		self._create_mapping(obj, mapping_dict)

				else:
					raise osv.except_osv(_('Error'),_("Error in Creating Variable product"))
			return count

	@api.multi
	def create_woocommerce_simple_product(self, template, woocommerce):
		if template:
			record = self.env['product.product'].search([('product_tmpl_id','=',template.id)])
			# qty = record._product_available()
			# quantity = qty[template.product_variant_ids[0].id]['qty_available'] - qty[template.product_variant_ids[0].id]['outgoing_qty']
			quantity = template.product_variant_ids[0].immediately_usable_qty
			product_dict = {
						'name'				: template.name,
						'title'				: template.name,
						'sku' 				: template.default_code or "",
						'images'			: self.create_woocommerce_product_image(template),
						'regular_price'		: str(template.list_price) or "",
						'type'				: 'simple',
						'categories'		: self.set_woocommerce_product_categories(template),
						'status'			: 'publish',
						# 'short_description'	: template.description_sale  or "" ,
						'description'		: template.name or "",
						'price'				: template.list_price,
						'manage_stock'	: True,
						'stock_quantity'	: quantity,
						# 'in_stock'			: True,
						}

			if self.api_version == 'legacyv3':
				product_dict = {'product':+product_dict}
			_logger.error('########### Valor en create simple product del dict: %s', product_dict)
			if woocommerce:
				result  = woocommerce.post('products',product_dict).json()
				# _logger.error('########### Valor en create simple product del result: %s', result)
				if self.api_version == 'legacyv3':
					return_dict = result['product']
				else:
					return_dict = result
			if 	return_dict.has_key('id'):
				mapping_dict = {
							'channel_id'		: self.id,
							'store_product_id'	: return_dict['id'],
							'odoo_template_id'	: template.id,
							'template_name'		: template.id,
							'default_code'		: template.default_code or "",
				}
				obj = self.env['channel.template.mappings']
				self._create_mapping(obj, mapping_dict)
				mapping_dict = {
							'channel_id'		: self.id,
							'store_product_id'	: return_dict['id'],
							'odoo_template_id'	: template.id,
							'product_name'		: template.product_variant_ids[0].id,
							'erp_product_id'	: template.product_variant_ids[0].id,
							'default_code'		: template.product_variant_ids[0].default_code or "",
				}
				obj = self.env['channel.product.mappings']
				self._create_mapping(obj, mapping_dict)
				return 1
			else:
				raise osv.except_osv(_('Error'),_('Simple Product Creation Failed'))
		else:
			raise osv.except_osv(_('Error'),_('Simple Product Creation Failed'))

	@api.multi
	def set_woocommerce_product_categories(self, template):
		categ_list = []
		if template.categ_id:
			rec  =  self.env['channel.category.mappings'].search([('odoo_category_id','=',template.categ_id.id),('channel_id.id','=',self.id)])
			if rec:
				if self.api_version == 'legacyv3':
					# para api Legacy solo se registra el id de categoria:
					categ_list.append(rec.store_category_id)
				else:
					categ_list.append({'id':rec.store_category_id})
				
			else:
				raise Warning("Category doesn't exist at WooCommerce End")
		if template.channel_category_ids:
			for category_channel in template.channel_category_ids:
				if category_channel.instance_id.id == self.id:
					for category in category_channel.extra_category_ids:
						record = self.env['channel.category.mappings'].search([('odoo_category_id','=',category.id),('channel_id.id','=',self.id)])
						if record:
							if self.api_version == 'legacyv3':
								categ_list.append(record.store_category_id)
							else:
								categ_list.append({'id':record.store_category_id})
						else:
							raise Warning("Category doesn't exist at WooCommerce End")
		return categ_list

	@api.multi
	def export_woocommerce_product(self):
		# self.export_woocommerce_attributes_values()
		# self.export_woocommerce_categories(0)
		message = self.export_update_woocommerce_product()
		woocommerce = self.woocommerce_export_api_config()
		count = 0;
		template_records =  self.env['product.template'].search([('type','=','product'),('sale_ok','=',True),('active','=',True)])
		for template in template_records:
			mapping_record = self.env['channel.template.mappings'].search([('odoo_template_id','=',template.id),('channel_id.id','=',self.id)])
			if not mapping_record:
				if template.attribute_line_ids:
					count += self.create_woocommerce_variable_product(template, woocommerce)
				else:
					count += self.create_woocommerce_simple_product(template, woocommerce)
		message += 	str(count)+" Products have been exported"
		#en el mismo cron de export product actualizamos los stocks
		self.export_woocommerce_available_stock()
		return self.display_message(message)

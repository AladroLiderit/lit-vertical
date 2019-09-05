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
	def export_all_woocommerce_categories(self):
		message = self.sudo().export_update_woocommerce_categories()
		count = self.sudo().export_woocommerce_categories(0)
		# self._cr.commit()
		message += str(count)+" Categories have been exported"
		return self.display_message(message)

	@api.multi
	def export_woocommerce_categories(self, count , parent_id = False):
		# self.import_woocommerce_categories()	
		category_records = ''
		if parent_id:
			# _logger.error('########### Valor en export categories con parent_id: %s', parent_id)
			category_records = self.env['product.category'].browse(parent_id)
		else:
			if self._context.has_key('active_model') and self._context['active_model'] == 'product.category':
				if self._context.has_key('active_ids'):
					category_records=self.env['product.category'].browse(self._context['active_ids'])
				else:
					category_records = self.env['product.category'].search([])
			else:
				category_records = self.env['product.category'].search([])

					
		for category in category_records:
			parent = 0
			mapping_rec = self.env['channel.category.mappings'].search([('odoo_category_id','=',category.id),('channel_id.id','=',self.id)])
			# _logger.error('########### Valor en export categories de mapping para : %s', category.id)
			if mapping_rec and parent_id:
				return mapping_rec.store_category_id
			if not mapping_rec:
				# solo categorias que tengan algun producto asociado
				prod_cat = self.env['product.template'].search(['categ_id','=',category.id])
				if len(prod_cat)==0:
					prod_channel_cat = self.env['extra.categories'].search(['category_id','=',category.id])
					if len (prod_channel_cat)==0:
						continue
				count = count + 1
				if category.parent_id:
					parent = self.export_woocommerce_categories(count, category.parent_id.id)
				woocommerce = self.woocommerce_export_api_config()
				if self.api_version == 'legacyv3':
					category_dict = {'product_category':{
									'name'  : category.name,
									'parent': parent,
									}
					}
				else:
					category_dict = {
								'name'  : category.name,
								'parent': parent,
								}

				# _logger.error('########### Valor en export categories de category_dict : %s', category_dict)
				return_dict = woocommerce.post('products/categories',category_dict).json()
				if return_dict.has_key('message'):
					raise osv.except_osv(_('Error'),_('Error in Creating Categories : '+str(return_dict['message'])))
				if self.api_version == 'legacyv3':
					result = return_dict['product_category']
				else:
					result = return_dict
				# _logger.error('########### Valor en export categories de result : %s', result)
				mapping_dict = {
							'channel_id'		: self.id,
							'store_category_id'	: result['id'],
							'odoo_category_id'	: category.id,
							'category_name'		: category.id,
				}
				obj = self.env['channel.category.mappings']
				self._create_mapping(obj, mapping_dict)
				if parent_id:
					return result['id']
		# self._cr.commit()
		return count

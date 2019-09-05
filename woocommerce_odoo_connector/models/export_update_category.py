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
	def action_export_update_woocommerce_categories(self):
		if self._context['active_ids']:
			count = 0
			store_category_id = 0
			message = self.export_woocommerce_categories(0)
			category_ids = self._context['active_ids']
			for category_id in category_ids:
				category_mapping_record = self.env['channel.category.mappings'].search([('odoo_category_id','=',category_id),('channel_id.id','=',self.id)])
				if category_mapping_record:
					category = category_mapping_record.category_name
					if category_mapping_record.need_sync == 'yes':
						count += 1
						if category.parent_id:
							parent_category_id = self.self.env['channel.category.mappings'].search([('odoo_category_id','=',category.parent_id),('channel_id.id','=',self.id)])
							store_category_id = parent_category_id.store_category_id
						if self.api_version == 'legacyv3':
							category_dict = {'product_category':{
								'name' 		: category.name,
								'parent_id'	: store_category_id,
								}
							}
						else:
							category_dict = {
								'name' 		: category.name,
								'parent_id'	: store_category_id,
							}
						woocommerce = self.woocommerce_export_api_config()
						woocommerce.put('products/categories/'+category_mapping_record.store_category_id,category_dict)
						category_mapping_record.need_sync = 'no'
			message = str(message)+" Categories have been exported"+", "+str(count)+" Categories have been Updated"
			return self.display_message(message)

	@api.multi
	def export_update_woocommerce_categories(self):
		count = 0
		store_category_id = 0
		category_update = self.env['channel.category.mappings'].search([('need_sync','=','yes'),('channel_id.id','=',self.id)])
		for category_map in category_update:
				category = category_map.category_name
				count += 1
				if category.parent_id:
					parent_category = self.env['channel.category.mappings'].search([('odoo_category_id','=',category.parent_id.id),('channel_id.id','=',self.id)])
					if not parent_category:
						self.export_woocommerce_categories(0)
						parent_category = self.env['channel.category.mappings'].search([('odoo_category_id','=',category.parent_id.id),('channel_id.id','=',self.id)])
						store_category_id = parent_category.store_category_id
				if self.api_version == 'legacyv3':
					category_dict = {'product_category':{
						'name' 		: category.name,
						'parent_id'	: store_category_id,
						}
					}
				else:
					category_dict = {
						'name' 		: category.name,
						'parent_id'	: store_category_id,
					}
				woocommerce = self.woocommerce_export_api_config()
				return_dict = woocommerce.put('products/categories/'+category_map.store_category_id,category_dict).json()
				if return_dict.has_key('message'):
					raise osv.except_osv(_('Error'),_('Error in Updating Categories : '+str(return_dict['message'])))
				category_map.need_sync = 'no'
		return str(count)+" Categories Updated , "

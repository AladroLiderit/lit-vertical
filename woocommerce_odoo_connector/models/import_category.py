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
	def import_woocommerce_categories(self,parent_id=False):
		message = self.update_woocommerce_categories()
		list_category = []
		if self.id:
			woocommerce = message['instance']
			message = message['message']			
			cat_url = 'products/categories'
			category_map_data = self.env['channel.category.mappings']
			count = 0
			if parent_id and not isinstance(parent_id,(dict)):
				cat_url = cat_url+"/"+str(parent_id)
			category_data = woocommerce.get(cat_url).json()
			if category_data.has_key('product_categories'):
				category_data = category_data['product_categories']
			else:
				category_data = category_data['product_category']

			if isinstance(category_data,(dict)):
				category_data = [category_data]
			for category in category_data:
				if category['parent'] and not category_map_data.search([('store_category_id','=',category['parent'])]):
					self.import_woocommerce_categories(category['parent'])
				if not category_map_data.search([('store_category_id','=',category['id'])]) and not self.env['category.feed'].search([('store_id','=',category['id'])]):
					category_search_record = self.env['product.category'].search([('name','=',category['name'])])
					if category_search_record:
						mapping_dict = {
									'channel_id'		: self.id,
									'store_category_id'	: category['id'],
									'odoo_category_id'	: category_search_record.id,
									'category_name'		: category_search_record.id,
						}
						obj = self.env['channel.category.mappings']
						self._create_mapping(obj, mapping_dict)
					else:
						count = count+1
						category_dict = {
										'name'		:category['name'],
										'parent_id'	:category['parent'],
										'store_id'	:category['id'],
										'channel_id':self.id,
						}
						category_rec = self.env['category.feed'].create(category_dict)
						list_category.append(category_rec)
			feed_res = dict(create_ids=list_category,update_ids=[])
			self.env['channel.operation'].post_feed_import_process(self,feed_res)
			self._cr.commit()
			message += str(count)+" Categories Imported!"
			return self.display_message(message)

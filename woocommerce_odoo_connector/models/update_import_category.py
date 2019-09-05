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
	def update_woocommerce_categories(self):
		update_rec = []
		create_rec = []
		count = 0
		woocommerce = self.get_woocommerce_connection()
		category_feed_data = self.env['category.feed']
		date = self.with_context({'name':'category'}).get_woocommerce_update_date()
		try:
			category_data = woocommerce.get('products/categories?filter[updated_at_min]='+date).json()
		except Exception as e:
			raise osv.except_osv(_('Error'),_("Error : "+str(e)))
		if category_data.has_key('errors'):
			raise osv.except_osv(_('Error'),_("Error : "+str(category_data['errors'][0]['message'])))
		else :
			for category in category_data['product_categories']:
				check_mapping = self.env['channel.category.mappings'].search([('store_category_id','=',category['id']),('channel_id.id','=',self.id)])
				if check_mapping:
					update_record = category_feed_data.search([('store_id','=',category['id'])])
					if update_record:
						count += 1
						update_record.state = 'update'
						category_dict = {
									'name'		:category['name'],
									'parent_id'	:category['parent'],
						}
						update_record.write(category_dict)
						update_rec.append(update_record)
					else:
						count = count+1
						category_dict = {
										'name'		:category['name'],
										'parent_id'	:category['parent'],
										'store_id'	:category['id'],
										'channel_id':self.id,
						}
						category_rec = self.env['category.feed'].create(category_dict)
						category_rec.state = 'update'
						update_rec.append(category_rec)					
			feed_res = dict(create_ids=create_rec,update_ids=update_rec)
			self.env['channel.operation'].post_feed_import_process(self, feed_res)
			message = str(count)+" Categories Updated! , "
			return {'instance':woocommerce,'message':message}

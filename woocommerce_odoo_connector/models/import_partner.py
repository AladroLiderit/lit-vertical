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
	def import_woocommerce_customers(self):
		message = self.update_woocommerce_customers()
		list_customer = []
		count = 0
		woocommerce = self.get_woocommerce_connection()
		partner_feed_data = self.env['partner.feed']
		date = self.with_context({'name':'customer'}).get_woocommerce_import_date()
		_logger.error('##### AIKO ###### Valor de date en import customer woocomerce: %s' % date)
		try:
			partner_data = woocommerce.get('customers?filter[limit]=-1&filter[created_at_min]='+date).json()
		except Exception as e:
			raise osv.except_osv(_('Error'),_("Error : "+str(e)))
		if partner_data.has_key('errors'):
			raise osv.except_osv(_('Error'),_("Error : "+str(partner_data['errors'][0]['message'])))
		else :
			_logger.error('##### AIKO ###### Valor de partner_data en import woocomerce: %s' % partner_data)
			for partner in partner_data['customers']:
				_logger.error('##### AIKO ###### Valor de partner en import woocomerce: %s' % partner)
				_logger.error('##### AIKO ###### Valor de partner_feed search en import woocomerce: %s' % partner_feed_data.search([('store_id','=',partner['id'])]))
				if not partner_feed_data.search([('store_id','=',partner['id'])]):
					count = count +1
					partner_dict = {
								'name'		: partner['first_name'],
								'last_name'	: partner['last_name'],
								'channel_id': self.id,
								'email'		: partner['email'],
								'store_id'	: partner['id'],
					}
					partner_rec = partner_feed_data.create(partner_dict)
					list_customer.append(partner_rec)
			feed_res = dict(create_ids = list_customer,update_ids = [])
			self.env['channel.operation'].post_feed_import_process(self, feed_res)
			self.woocommerce_import_customer_date = str(datetime.now().date())
			message +=  str(count)+" Customer(s) Imported!"
			return self.display_message(message)

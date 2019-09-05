# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2017-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE URL <https://store.webkul.com/license.html/> for full copyright and licensing details.
#################################################################################

from openerp import http, SUPERUSER_ID
from openerp.http import request
import logging
_logger = logging.getLogger(__name__)
MAPPINGMODEL={
	'product.product':'channel.product.mappings',
	'sale.order':'channel.order.mappings',
	}
MAPPINGFIELD={
	'product.product':'erp_product_id',
	'sale.order':'odoo_order_id',
}

class Channel(http.Controller):
	@http.route(['/channel/update/mapping',],auth="public", type='json')
	def update_mapping(self, **post):
		field =MAPPINGFIELD.get(str(post.get('model')))
		model = MAPPINGMODEL.get(str(post.get('model')))
		if field and model:
			domain = [(field,'=',int(post.get('id')))]
			mappings=request.env[model].sudo().search(domain)
			for mapping in mappings:pass
				#mapping.need_sync='yes'
		return True
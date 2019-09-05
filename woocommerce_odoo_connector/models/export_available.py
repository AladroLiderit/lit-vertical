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
	def export_woocommerce_available_stock(self):
		cust_n = 0
		_logger.error('########### Entramos en export_woocommerce_available_stock')
		# un limit de 25 para que en cada conexión actualice solo 25 productos y no sature los procesos
		mapping_rec = self.env['channel.product.mappings'].search([
			('act_stock','=',True),
			('channel_id.id','=',self.id),], order="write_date asc",limit=5)
		if mapping_rec:
			woocommerce = self.woocommerce_export_api_config()
			for mprod in mapping_rec:
				_logger.error('########### Valor en export_woocommerce_available para mprod: %s', str(mprod))
				product_rec = self.env['product.product'].browse(mprod.product_name.id)
				quantity = product_rec.immediately_usable_qty
				store_id = mprod.store_product_id
				product_dict={
								'stock_quantity'	: quantity,
					}
				result_dict = {}
				if self.api_version == 'legacyv3':
					result_dict['product']= product_dict
				else:
					result_dict = product_dict
				_logger.error('########### Valor en export_woocommerce_available para result_dict: %s', result_dict)
				try:
					return_dict = woocommerce.put('products/'+str(store_id),result_dict).json()
					_logger.error('########### Valor en export_woocommerce_available para return_dict: %s', return_dict)
					if self.api_version == 'legacyv3' and return_dict.has_key('errors'):
						error = return_dict['errors']
						raise osv.except_osv(_('Error'),_('Error in updating product stock '+str(error[0]['message'])))
					if self.api_version == 'wpapi' and return_dict.has_key('message'):
						raise osv.except_osv(_('Error'),_('Error in updating product stock '+str(['message'])))

					mprod.write({'act_stock':False})
					cust_n+=1
					
				except Exception, e:
					raise osv.except_osv(_('Error'),_("Can't update product , "+str(mprod.product_name)))

		return cust_n

	# funcion para actualizar todos los productos en su stock, por movimientos internos y bajas de almacen
	# previsto para que se lance en horario nocturno una vez al dia
	@api.multi
	def export_woocommerce_all_available_stock(self):
		cust_n = 0
		mapping_rec = self.env['channel.product.mappings'].search([('channel_id.id','=',self.id),('act_stock','=',True)])
		if mapping_rec:
			woocommerce = self.woocommerce_export_api_config()
			for mprod in mapping_rec:
				product_rec = self.env['product.product'].browse(mprod.product_name.id)
				quantity = product_rec.immediately_usable_qty
				store_id = mprod.store_product_id
				product_dict={
								'stock_quantity'	: quantity,
					}
				result_dict = {}
				if self.api_version == 'legacyv3':
					result_dict['product']= product_dict
				else:
					result_dict = product_dict
				try:
					return_dict = woocommerce.put('products/'+str(store_id),result_dict).json()
					if self.api_version == 'legacyv3' and return_dict.has_key('errors'):
						error = return_dict['errors']
						raise osv.except_osv(_('Error'),_('Error in updating product stock '+str(error[0]['message'])))
					if self.api_version == 'wpapi' and return_dict.has_key('message'):
						raise osv.except_osv(_('Error'),_('Error in updating product stock '+str(['message'])))

					mprod.write({'act_stock':False})
					cust_n+=1
					
				except Exception, e:
					raise osv.except_osv(_('Error'),_("Can't update product , "+str(mprod.product_name)))

		return cust_n


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.multi
    def write(self, vals):
    	for line in self:
    		if line.product_id:
    			mapping_rec = self.env['channel.product.mappings'].search([('erp_product_id','=',line.product_id.id)])
    			for mprod in mapping_rec:
    				mprod.write({'act_stock': True})
    	res = super(SaleOrderLine, self).write(vals)
    	return res


    @api.model
    def create(self, values):        
        line = super(SaleOrderLine, self).create(values)
        for l in line:
        	if l.product_id:
        		mapping_rec = self.env['channel.product.mappings'].search([('erp_product_id','=',l.product_id.id)])
    			for mprod in mapping_rec:
    				mprod.write({'act_stock': True})
    	return line

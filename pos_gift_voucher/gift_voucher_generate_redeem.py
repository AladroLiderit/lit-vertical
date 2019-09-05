from openerp.osv import fields, osv
from openerp.tools.translate import _
# from mx.DateTime import RelativeDateTime
# import mx.DateTime
# import datetime
from datetime import datetime
from dateutil.relativedelta import relativedelta

import logging 
_logger = logging.getLogger(__name__)

class pos_order(osv.osv):
    _inherit = "pos.order"
    _columns = {
                 'batch_qty_values':fields.char('Batch No.', size=128),
      }
    def create_from_ui(self, cr, uid, orders, context=None):
        order_ids=super(pos_order,self).create_from_ui(cr,uid,orders,context=context)
        data=orders[0]['data']
        if data.has_key('coupon_redeemed') and data['coupon_redeemed']:
                i=0;
                while(i < len(data['coupon_redeemed'])):
                    iddd=self.pool.get('gift.voucher').search(cr,uid,[('voucher_serial_no','=',data['coupon_redeemed'][i])])
                       
                    browse_id=self.pool.get('gift.voucher').browse(cr, uid, iddd[0])
                    self.pool.get('gift.voucher').write(cr,uid,[int(iddd[0])],{
                                                                'in': True,                                                                  
                                                                    }) 
                    i=i+1;
        
        if data.has_key('coupon_name') and data['coupon_name']==True:
            coup_id=data['coupon_id']
            c_unique_no=data['coupon_unique_no']
            i=0;
            while (i < len(c_unique_no)): 
#                 _id=self.pool.get('product.product').search(cr,uid,[('id','=',coup_id[i])])
#                 b_id=self.pool.get('product.product').browse(cr, uid, _id[0])
#                 prod_tmpl_id=b_id.product_tmpl_id
#                 coupon_id=self.pool.get('product.template').search(cr,uid,[('id','=',prod_tmpl_id.id)])
#                 browse_id=self.pool.get('product.template').browse(cr, uid, coupon_id[0])
#                 
                coupon = self.pool.get('product.product').browse(cr, uid, int(coup_id[i]))
                
#                 coupon_name = browse_id.name;
#                 coupon_price = browse_id.list_price
#                 uom = browse_id.uom_id.id;
#                 p_id = browse_id.id
                validity_in_days = coupon.validity;
                _logger.error('##### AIKO ###### Valor de validty_in_days para crear pos gift voucher: %s' % validity_in_days)
                # order_date = mx.DateTime.strptime(str(datetime.date.today()),'%Y-%m-%d')
                order_date = datetime.now().strftime('%Y-%m-%d')
                _logger.error('##### AIKO ###### Valor de order_date para crear pos gift voucher: %s' % order_date)
                # exp_date = order_date +  RelativeDateTime(days=validity_in_days)
                exp_date = (datetime.strptime(order_date, '%Y-%m-%d') + relativedelta(days=validity_in_days))
                _logger.error('##### AIKO ###### Valor de las_date para crear pos gift voucher: %s' % exp_date)
                self.pool.get('gift.voucher').create(cr,uid,{
                                                            'voucher_name': coupon.name,
                                                            'qty':1.0,
                                                            'uom':coupon.uom_id.id,
                                                            'shop_id':data['shop'],
                                                            'company_id':data['company'], 
                                                            'date':order_date,
                                                            'voucher_serial_no':data['coupon_unique_no'][i],
                                                            'source':data['name'],
                                                            'out':True,
                                                            'amount':coupon.list_price,
                                                            'voucher_validity':validity_in_days,
                                                            'last_date':exp_date,
                                                            'product_id':coupon.id,
                                                            'state':'approve',
                                                                })
                i=i+1;
        return order_ids
pos_order()

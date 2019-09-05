from openerp.osv import osv
from openerp.osv import fields
import openerp
from openerp.osv.fields import _column

class gift_voucher(osv.osv):
    _name='gift.voucher'
    _description='Loyalty Gift Voucher Master'
    
    _columns = {
                'state': fields.selection([
                                           ('draft','Request'),
                                           ('approve','Approved'),
                                           ('cancel','Cancelled'),
                                           ('done', 'Done'),
           
                                            ], 'Status', readonly=True,select=True),
        'source':fields.char('Source'),
        'voucher_name':fields.char('Gift Coupon Name',size=64,required=True),
        'coupon_value':fields.float('Coupon Value',size=64),
        'voucher_serial_no':fields.char('Gift Coupon Serial no.'),
        'qty':fields.float('Product qty',size=64),
        'uom': fields.many2one('product.uom', 'Product Unit of Measure', required=True),
        'in':fields.boolean('IN'),
        'out':fields.boolean('OUT'),
        'shop_id':fields.char('Shop'),
        'company_id':fields.char('Company'),
        'date':fields.date('Creation Date'),
        'amount':fields.float('Amount',size=64),
        'voucher_validity':fields.integer('Validity'),
        'last_date':fields.date('Expiry Date'),
        'product_id':fields.many2one('product.product'),
        }
    
    _defaults={
             'state': 'draft',
             'voucher_validity':1,
        }
    
    def approve(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'approve'}, context=context)
        return True
    
    def cancel(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'cancel'})
    
gift_voucher()


class product_template(osv.osv):   
    _inherit="product.template"

    _columns = {
            'coupon':fields.boolean('Coupon'),
            'validity':fields.integer('Coupon Validity(days)',help='Coupon validity in days from the date of sale'),
            'is_prepaid_card':fields.boolean('Is Prepaid Card'),
        }
    
    _defaults = {
                 'validity':1
                 }
    
    def on_click_of_coupon(self,cr, uid, coupon,name, context=None):
        if not name:
            return {'value':{'type':'consu'}}
        else:
            return {'value':{'type':'service'}}

        
product_template()


class account_journal(osv.osv):
    _inherit = 'account.journal'

    def onchange_of_for_gift_coupen(self, cr, uid, ids,for_gift_coupens, context=None):
        return True
    
    _columns = {
        'for_gift_coupens' : fields.boolean('For Gift Coupons'),
    }
   
account_journal()        
     




    


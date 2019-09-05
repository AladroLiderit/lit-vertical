# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import openerp.addons.decimal_precision as dp
from openerp.osv import fields, osv
from openerp.tools.translate import _


class purchase_order(osv.osv):
    _inherit = "purchase.order"
    _name = "purchase.order"
    _columns = {
        'discount_type': fields.selection([('percen','Porcentaje'), ('total','Importe')],'Tipo de Descuento'),
        'global_discount': fields.float('Descuento (%)', digits_compute=dp.get_precision('Discount'), readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}),
        'amount_discount': fields.float('Descuento (€)', digits_compute=dp.get_precision('Product_Price'), readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}),
    }
    _defaults = {
        'discount_type': 'percen',
    }
    
    def onchange_global_discount(self, cr, uid, ids, global_discount, context):
        for order in self.browse(cr, uid, ids, context=context):
            order.amount_discount = 0
            for line in order.order_line:
                line.discount = global_discount
        return True

    def onchange_amount_discount(self, cr, uid, ids, amount_discount, context):
        for order in self.browse(cr, uid, ids, context=context):
            order.global_discount = 0
            dto_entero = 0
            if amount_discount > 0:
                dto_entero = (amount_discount / (order.amount_untaxed + order.amount_discount)) * 100
            for line in order.order_line:
                line.discount = dto_entero
        return True

    def onchange_type_discount(self, cr, uid, ids, context):
        res = {
            'value': {
                'amount_discount': 0,
                'global_discount': 0,
            }
        }
        # Return the values to update it in the view.
        return res

purchase_order()

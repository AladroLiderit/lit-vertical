# -*- encoding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution
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

from openerp import models, fields, api
import openerp.addons.product.product


class product_product(models.Model):
    
    _inherit = 'product.product'

    respect_ean = fields.Boolean (string='Respect EAN code value', default = False)

    def ajusta_defaultcode(self, default_code):

    	def_code =str(default_code)
    	largo_defcode = len(def_code)
    	
    	if largo_defcode >= 12:
        	def_code = def_code[:12]
        else:
        	i= 12
        	while i > largo_defcode:
        		if largo_defcode==11:
        			def_code = "1"+def_code
        		else:
        			def_code = "0"+def_code
        		largo_defcode = len(def_code)

        return def_code


    @api.onchange('default_code')
    def onchange_defaultcode(self):

        if self.respect_ean == False:
            def_code = self.ajusta_defaultcode(self.default_code)
            self.ean13 = openerp.addons.product.product.sanitize_ean13(str(def_code))

    @api.onchange('respect_ean')
    def onchange_respect_ean(self):

        if self.respect_ean == False:
            def_code = self.ajusta_defaultcode(self.default_code)
            self.ean13 = openerp.addons.product.product.sanitize_ean13(str(def_code))



class product_template(models.Model):
    
    _inherit = 'product.template'

    respect_ean = fields.Boolean (string='Respect EAN code value', default = False)

    def ajusta_defaultcode(self, default_code):

        def_code =str(default_code)
        largo_defcode = len(def_code)
        
        if largo_defcode >= 12:
            def_code = def_code[:12]
        else:
            i= 12
            while i > largo_defcode:
                if largo_defcode==11:
                    def_code = "1"+def_code
                else:
                    def_code = "0"+def_code
                largo_defcode = len(def_code)

        return def_code


    @api.onchange('default_code')
    def onchange_defaultcode(self):

        if self.respect_ean == False:
            def_code = self.ajusta_defaultcode(self.default_code)
            self.ean13 = openerp.addons.product.product.sanitize_ean13(str(def_code))


    @api.onchange('respect_ean')
    def onchange_respect_ean(self):

        if self.respect_ean == False:
            def_code = self.ajusta_defaultcode(self.default_code)
            self.ean13 = openerp.addons.product.product.sanitize_ean13(str(def_code))



class ean_generator(models.Model):
    _name = 'ean.generator'
    
    def create_ean(self, cr, uid, ids, context=None):
        prod_obj = self.pool.get('product.product')
        for product in prod_obj.browse(cr, uid, context['active_ids'],context):
        	def_code = product.ajusta_defaultcode(product.default_code)
        	ean13 = openerp.addons.product.product.sanitize_ean13(def_code)
        	m_id =  product.id
        	prod_obj.write(cr,uid,[m_id],{'ean13':ean13})
        return { 'type' : 'ir.actions.act_window_close' }

# coding: utf-8
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
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

from openerp import models,api
 
class product_product(models.Model):
    _inherit = 'product.product'
 
    @api.multi
    def name_get(self):
 
        res = super(product_product, self).name_get()
        data = []
        for product in self:
            data.append((product.id, product.name))
        return data
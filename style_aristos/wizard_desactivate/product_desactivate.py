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
from openerp import models, fields, api, exceptions
from openerp.tools.translate import _
import logging
_logger = logging.getLogger(__name__)

class product_desactivate(models.TransientModel):
    _name = "product.desactivate"
    _description = "Desactivate products"

    keep_references = fields.Boolean('Keep references'
                                     ' from original',
                                     default=True)

    @api.model
    def _dirty_check(self):
        
        if self.env.context.get('active_model', '') == 'product.template':            
            ids = self.env.context['active_ids']
            if len(ids) < 2:
                raise exceptions.Warning(
                    _('Please select multiple products in the list '
                      'view.'))
            p_obj = self.env['product.template']
            p = p_obj.browse(ids)
           
            for d in p:
                if d['active'] == False:
                    raise exceptions.Warning(
                        _('At least one of the selected product is ready desactivate is %s!') %
                        d['name'])
                if d['qty_available'] > 0:
                    raise exceptions.Warning(
                        _('Product in stock  %s !') %
                        d['name'])
 
                if d['virtual_available'] > 0:
                    raise exceptions.Warning(
                        _('Product with open quantities  %s !') %
                        d['name'])
                
                d.write({'active':False})
        return {}
    @api.multi
    def p_desactivar(self):
        self._dirty_check()
        return       

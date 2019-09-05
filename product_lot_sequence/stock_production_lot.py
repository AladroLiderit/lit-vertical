# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2014 Pexego (<www.pexego.es>). All Rights Reserved
#    $Omar Castiñeira Saavedra$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

"""Creates prodlot sequence chooose product sequence"""

from openerp import models, api


class StockProductionLot(models.Model):

    _inherit = "stock.production.lot"

    @api.model
    def make_sscc(self):
        """return production lot number"""
        if 'in_pick' in self._context.keys():
            return ''
        seq_obj = self.env['ir.sequence']
        product_id = self._context.get('product_id', False) or \
            self._context.get('default_product_id', False)
        product = self.env['product.product'].browse(product_id)
        if product and product.sequence_id:
            sequence_id = product.sequence_id.id
        else:
            sequence_id = self.env.ref('stock.sequence_production_lots').id
        sequence = seq_obj.get_id(sequence_id)
        return sequence

    _defaults = {
        'name': make_sscc
    }


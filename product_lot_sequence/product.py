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

"""add lot sequence field in products"""

from openerp import models, fields, api
from stock_production_lot_sequence import get_default_seq_id


class ProductTemplate(models.Model):
    """add lot sequence field in products"""

    _inherit = "product.template"

    sequence_id = fields.Many2one('ir.sequence', 'Prodlots Sequence')

'''
#Paramos esto porque no queremos que se creen nuevos lotes al crear productos

    @api.model
    def create(self, vals):
        """overwrites create method to create new sequence
to production lots"""
        product = super(ProductTemplate, self).create(vals)
        # Manages the sequence number
        if not vals.get('sequence_id') and vals.get('type') == 'product':
            sequence_id = get_default_seq_id(self._cr, self.env.user.id,
                                             product.default_code,
                                             product.default_code and
                                             product.name or False,
                                             company_id=product.company_id and
                                             product.company_id.id or False)
            if sequence_id:
                product.sequence_id = sequence_id

        return product
'''

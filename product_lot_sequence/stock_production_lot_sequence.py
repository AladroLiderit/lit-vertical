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

"""
Manages prodlots sequences by product
"""

from openerp import pooler

_sequences_cache = {}


def _get_fix_prefix():
    return u"L%(doy)s%(y)s ("


def _get_fix_suffix():
    return ")"


def _get_padding():
    return 3


def get_default_seq_id(cr, uid, seq_name=False, name=False,
                       seq_code='stock.production.lot', company_id=False):
    """
    Get by default a sequence for active product.
    If the sequence not exists it creates.
    """
    pool = pooler.get_pool(cr.dbname)
    seq_obj = pool.get('ir.sequence')
    sequence_ids = False

    if company_id and seq_name:
        # cache system for massive creation of sequences
        if not _sequences_cache.get(company_id):
            _sequences_cache[company_id] = {}

        if _sequences_cache[company_id].get(seq_name):
            return _sequences_cache[company_id][seq_name]

    if name:
        sequence_ids = seq_obj.search(cr, uid, [('code', '=', seq_code),
                                                ('name', '=', name)])
    if sequence_ids:
        sequence_id = sequence_ids[0]
    elif name:
        #
        # Creamos una nueva secuencia
        #
        sequence_id = seq_obj.create(cr, uid, {
            'name': name,
            'code': seq_code,
            'padding': _get_padding(),
            'prefix': _get_fix_prefix() + seq_name,
            'suffix': _get_fix_suffix(),
            'company_id': company_id
        })
    else:
        sequence_id = seq_obj.search(cr, uid, [('code', '=',
                                                'stock.lot.serial')])[0]

    if seq_name:
        _sequences_cache[company_id][seq_name] = sequence_id

    return sequence_id

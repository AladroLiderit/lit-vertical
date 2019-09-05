# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution, third party addon
#    Copyright (C) 2004-2016 Vertel AB (<http://vertel.se>).
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
from openerp import models, fields, api, _

import logging
_logger = logging.getLogger(__name__)



class res_partner(models.Model):
    _inherit = 'res.partner'

    @api.multi
    def _count_stock_move(self):
        for partner in self:
            st_moves = self.env['stock.move'].search([('picking_partner', '=', partner.id)])
            partner.count_stock_move = len(st_moves)

    count_stock_move = fields.Integer(string='Movimientos', compute='_count_stock_move')


class stock_move(models.Model):
    _inherit = 'stock.move'

    @api.multi
    def _get_lot_id(self):
        for move in self:
        	quant = move.quant_ids
        	if quant:
        		lot_id = quant[0].lot_id.id
        		move.lot_id = lot_id

    lot_id = fields.Many2one(comodel_name='stock.production.lot',string='Lote', compute='_get_lot_id')


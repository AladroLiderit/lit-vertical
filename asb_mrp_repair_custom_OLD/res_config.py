# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Business Applications
#    Copyright (C) 2004-2012 OpenERP S.A. (<http://openerp.com>).
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

from openerp.tools.translate import _

from openerp import models, fields, api
        

class MrpConfigSettings(models.TransientModel):
    _inherit = 'mrp.config.settings'

    def _default_repair_journal_id(self):
    	journal = self.env['account.journal'].search([('type','=','sale')])
    	return journal and journal[0].id or False

    def _default_repair_location_dest_id(self):
    	location_dest = self.env['stock.location'].search([('usage','=','internal'),('active','=','True')])
    	return location_dest and location_dest[0].id or False


    repair_journal_id = fields.Many2one(
        comodel_name='account.journal',
        string='Diario Reparaciones',
        help="Diario para factura de reparaciones",
        default=_default_repair_journal_id
    )
    repair_location_dest_id = fields.Many2one(
        comodel_name='stock.location',
        string='Almacén Reparaciones',
        help="Almacén para destino de reparaciones",
        default=_default_repair_location_dest_id
    )

    @api.multi
    def set_secret_key_validation(self):
    	return self.env['ir.values'].sudo().set_default(
    		'mrp.config.settings', 'repair_journal_id', self.repair_journal_id.id)

    @api.multi
    def set_secret_key2_validation(self):
    	return self.env['ir.values'].sudo().set_default(
    		'mrp.config.settings', 'repair_location_dest_id', self.repair_location_dest_id.id)

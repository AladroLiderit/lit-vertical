# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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
from datetime import timedelta

from openerp import models, fields, api, _

class center_type(models.Model):
    """ Center Type """
    _name = 'center.type'
    _description = 'Center Type'

    name = fields.Char(string='Center Type', required=True)
    active = fields.Boolean(string='Active',
        default='True')


class syg_centros(models.Model):
    """Center"""
    _name = 'syg.centros'
    _description = 'Centers'
    _inherit = 'res.partner'


    code = fields.Char(string='Code',required=True)
    center_titular = fields.Selection([
            ('public', 'Public'),
            ('concert', 'Concert'),
            ('private', 'Private')
        ], string='Type of Center', default='public', required=True)
    center_type = fields.Many2one('center.type', string='Type of Center')

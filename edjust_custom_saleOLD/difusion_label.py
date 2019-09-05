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
from openerp.osv import osv, fields
from openerp import tools
from openerp.tools.translate import _

import logging
_logger = logging.getLogger(__name__)

#creamos una clase para tener en una vista los datos a exporta a excel
class difusion_line_label(osv.osv):
    _name = "difusion.line.label"
    #auto False para que no genere una tabla, porque es una vista
    _auto = False
    _columns = {
        'id': fields.float(_('Line ID'), readonly=True),
        'difusion_id': fields.float(_('Difusion ID'), readonly=True),
        'difusion_name': fields.char(_('Difusion Name'), readonly=True),
        'difusion_type': fields.char(_('Difusion Type'), readonly=True),
        'parent_name': fields.char(_('Partner Parent Name'), readonly=True),
        'name': fields.char(_('Contact Name'), readonly=True),
        'street': fields.char(_('Contact Street'), readonly=True),
        'zip': fields.char(_('Contact Zip Code'), readonly=True),
        'city': fields.char(_('Contact City'), readonly=True),
        'provincia': fields.char(_('Contact Country State'), readonly=True),
        'country': fields.char(_('Contact Country'), readonly=True),
        'ref': fields.char(_('Contact Ref'), readonly=True),
        }
    # _order = 'fecha_emision desc, n_factura desc'


    def init(self, cr):
        tools.sql.drop_view_if_exists(cr, 'difusion_line_label')
        cr.execute("""
            CREATE OR REPLACE VIEW difusion_line_label AS (
        select 
            l.id as id,
            d.id as difusion_id,
            d.name as difusion_name,
            l.difusion_type as difusion_type,
            parent.name as parent_name, 
            p.name as name,
            p.street as street,
            p.zip as zip, 
            p.city as city,
            s.name as provincia,
            c.name as country, 
            p.ref as ref
        from edjust_difusion_lines l join
            edjust_difusion d on d.id = l.difusion_id join
            res_partner p on l.partner_id = p.id left join
            res_partner parent on parent.id = p.parent_id left join
            res_country_state s on s.id = p.state_id left join
            res_country c on c.id = p.country_id
            )
        """)

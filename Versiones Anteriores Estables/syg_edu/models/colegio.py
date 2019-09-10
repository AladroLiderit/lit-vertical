# -*- coding: utf-8 -*-
###############################################################################
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
###############################################################################

import openerp
from openerp import api
from openerp.osv import fields, osv, expression

import logging
logger = logging.getLogger(__name__)

class SygColegio(osv.osv):
    _name = 'syg.colegio'
    _inherits = {'res.partner': 'partner_id'}

    def _get_default_company(self, cr, uid, context=None):
        # logger.error('Colegio entra en get default company')
        user_obj = self.pool.get('res.users')
        company_obj = self.pool.get('res.company')
        user = user_obj.browse(cr, uid, uid, context=context)

        if user.company_id:
            # logger.error('Colegio get company con user %s'%user.company_id.id)
            return user.company_id.id
        else:
            # logger.error('Colegio get company sin user %s'%company_obj.search(cr, uid, [('id', '=', 1)])[0])
            return company_obj.search(cr, uid, [('id', '=', 1)])[0]


    _columns={
    	'colegio_boolean' : fields.boolean('Es Colegio?'),
    	'partner_id' : fields.many2one(
            'res.partner', 'Partner', required=True, ondelete="cascade"),
        'pertenece_id' : fields.many2one('syg.colegio.belongs', 'Pertenece a'),
        'ampa_id' : fields.many2one('res.partner','AMPA'),
        #'tipo_centro' : fields.selection(
        #[('EEI', 'EEI'), ('EP', 'EP'), ('ESec', 'ESec'), ('Bach', 'Bach'), ('EOI', 'EOI'), ('AK', 'Academia'), ('CFor', 'Ciclos Formativos')],"Tipo de centro"),
        'tipo_centro': fields.many2many ('syg.tipo.colegio','syg_colegio_tipo_rel','colegio_id','tipo_colegio_id','Tipo de Colegio'),
        'titular' : fields.selection(
        [('P', 'Publico'), ('R', 'Privado'), ('C', 'Concertado')],"Titularidad"),
        'bilingue' : fields.boolean('Es Bilingüe?'),
        'segundo_idioma' : fields.selection([('ingles','Inglés'),('frances','Francés')],'Segundo Idioma'),
        'company_id': fields.many2one('res.company', string="Company", required=True),
    }

    _defaults = {
        'company_id': _get_default_company,
    }

    
    def onchange_state(self, cr, uid, ids, state_id, context=None):
        partner_ids = [user.partner_id.id for user in self.browse(cr, uid, ids, context=context)]
        return self.pool.get('res.partner').onchange_state(cr, uid, partner_ids, state_id, context=context)

    def onchange_type(self, cr, uid, ids, is_company, context=None):
        """ Wrapper on the user.partner onchange_type, because some calls to the
            partner form view applied to the user may trigger the
            partner.onchange_type method, but applied to the user object.
        """
        partner_ids = [user.partner_id.id for user in self.browse(cr, uid, ids, context=context)]
        return self.pool['res.partner'].onchange_type(cr, uid, partner_ids, is_company, context=context)

    def onchange_address(self, cr, uid, ids, use_parent_address, parent_id, context=None):
        """ Wrapper on the user.partner onchange_address, because some calls to the
            partner form view applied to the user may trigger the
            partner.onchange_type method, but applied to the user object.
        """
        partner_ids = [user.partner_id.id for user in self.browse(cr, uid, ids, context=context)]
        return self.pool['res.partner'].onchange_address(cr, uid, partner_ids, use_parent_address, parent_id, context=context)

    def onchange_zip_id(self, cr, uid, ids, context=None):
        partner_ids = [user.partner_id.id for user in self.browse(cr, uid, ids, context=context)]
        return self.pool.get('res.partner').onchange_zip_id(cr, uid, partner_ids, context=context)



class SygColegioBelongs(osv.osv):
    _name = 'syg.colegio.belongs'

    _columns={
        'name': fields.char('Gestor de Colegio', size=150),
    }


class SygTipoColegio(osv.osv):
    _name = 'syg.tipo.colegio'

    _columns={
        'name': fields.char('Tipo de Centro', size=150),
    }

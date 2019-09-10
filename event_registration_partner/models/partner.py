# -*- encoding: utf-8 -*-
##############################################################################
#    event_invoice_wizard
#    Copyright (c) 2017 Francisco Manuel García Claramonte <francisco@garciac.es>
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
from openerp import models, fields, api


#ampliamos clase partner para poder enlazar con las inscripciones
class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.multi
    def _inscripciones_count(self):
        for partner in self:
            partner.inscripciones_count = len(partner.inscripciones)

    inscripciones = fields.One2many('event.registration', 'partner_id',
                                  'Inscripciones')
    inscripciones_count = fields.Integer('Inscripciones',
                                 compute='_inscripciones_count')


    @api.multi
    def inscripcion_open(self):
        #view_id = self.env.ref('event.view_event_registration_form').id
        view_ref = self.env['ir.model.data'].get_object_reference('event', 'view_event_registration_form')
        view_id = view_ref[1] if view_ref else False
        #context = self._context.copy()
        partner_id = self.id

        res = {
           'type': 'ir.actions.act_window',
           'name': 'Nueva Inscripcion',
           'res_model': 'event.registration',
           'view_type': 'form',
           'view_mode': 'form',
           'view_id': view_id,
           'target': 'current',
           'context': {'default_partner_id': partner_id}
        }

        return res

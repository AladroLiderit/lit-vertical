# -*- encoding: utf-8 -*-
##############################################################################
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


REGISTRATION_STATES = [
    ('pendiente','Sin facturar'),
    ('inscripcion', 'Reserva'),
    ('total','Facturado')
    ]


class event_registration(models.Model):
    _name = 'event.registration'
    _description = 'Event Registration'
    _inherit = ['event.registration']

    estado = fields.Selection(string='Estado', selection=REGISTRATION_STATES, default='pendiente')

    factura = fields.Many2many('account.invoice', string='Factura', readonly=True, required=False)

    colegio_id = fields.Many2one (related='partner_id.study_center',store=True,string='Colegio')

    #valores para nombre, apellidos, sms, dni del alumno y centro de actividad
    nombre_alumno = fields.Char (related='partner_id.firstname', string="Nombre", store=True)
    apellido_alumno = fields.Char (related='partner_id.lastname', string="Apellido", store=True)
    sms_alumno = fields.Char (related='partner_id.sms_phone', string="SMS", store=True)
    dni_alumno = fields.Char (related='partner_id.vat', string="DNI / NIE", store=True)
    centro_registro = fields.Many2one (related='event_id.centro_actividad_event', string="Centro de Actividad", store=True)
    codigo_fotos = fields.Char (related='event_id.codigo_fotos', string="Código Fotos", store=True)
    rep_alumno = fields.Char (related='partner_id.representante.name',store=True,string='Representante', readonly=True)
    de_cliente = fields.Char (related='partner_id.de_cliente.name',store=True,string='Pertenece a', readonly=True)
    alumno_en_factura = fields.Boolean(string="Incluir nombre del alumno en factura", default=False)
    extemporanea = fields.Boolean(string='Fuera de Plazo', help="Supone recargo adicional en el importe de la actividad")

    @api.multi
    def factura_reserva(self):
        return {
            'name': 'Facturar Reserva',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
            'res_model': 'event.registration.singleinvoice_wizard',
            'type': 'ir.actions.act_window',
            'context': {'default_cliente':self.partner_id.id,'default_importe':'inscripcion'},
        }

    @api.multi
    def factura_final(self):
        return {
            'name': 'Factura Fianl',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
            'res_model': 'event.registration.singleinvoice_wizard',
            'type': 'ir.actions.act_window',
            'context': {'default_cliente':self.partner_id.id,'default_importe':'total'},
        }


event_registration()

#ampliamos clases de syg.colegio y syg.profesor para que funcione actualizar el zip_code
class SyGColegio(models.Model):
    _inherit = 'syg.colegio'

    @api.one
    @api.onchange('zip_id')
    def onchange_zip_id(self):
        if self.zip_id:
            self.zip = self.zip_id.name
            self.city = self.zip_id.city
            self.state_id = self.zip_id.state_id
            self.country_id = self.zip_id.country_id
            if self.zip_id.state_id.ccaa_id:
                self.ccaa_id = self.zip_id.state_id.ccaa_id


class SyGProfesor(models.Model):
    _inherit = 'syg.profesor'

    @api.one
    @api.onchange('zip_id')
    def onchange_zip_id(self):
        if self.zip_id:
            self.zip = self.zip_id.name
            self.city = self.zip_id.city
            self.state_id = self.zip_id.state_id
            self.country_id = self.zip_id.country_id
            if self.zip_id.state_id.ccaa_id:
                self.ccaa_id = self.zip_id.state_id.ccaa_id

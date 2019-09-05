# -*- encoding: utf-8 -*-
##############################################################################
#    event_advanced
#    Copyright (c) 2016 Francisco Manuel García Claramonte <francisco@garciac.es>
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
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp

from datetime import datetime, timedelta
import logging
logger = logging.getLogger(__name__)


#ampliamos clases de res.user para poder registrar los que son audiprotesistas
# y para poder asociar un color a cada usuario que se utilice en el calendario
class ResUsers(models.Model):
    _inherit = 'res.users'

    is_protesist = fields.Boolean('Audioprotesista')
    color = fields.Char(
        string="Color",
        help="Choose your color",
        size=7
    )

class event_event(models.Model):
    _name = 'event.event'
    _description = 'Event'
    _inherit = ['event.event']


    state = fields.Selection([
            ('draft', 'Nueva'),
            ('propolsal', 'A documentar'),
            ('cancel', 'Cancelled'),
            ('confirm', 'Presupuesto'),
            ('done', 'Contrato'),
            ('end', 'Completa')
        ],)
    not_asisted = fields.Boolean('No acudió a la cita')
    gabinete_id = fields.Many2one ('asb.gabinete', string="Gabinete")
    protesist_id = fields.Many2one ('res.users', string="Audioprotesista")
    color_state_id = fields.Many2one ('res.users', string="Estado cita")
    hex_value = fields.Char(
        string="Valor Color",
        related="color_state_id.color",
        store=False,
        size=7
    )


    @api.one
    def button_documentar(self):
        self.state = 'propolsal'

    @api.one
    def button_presupuesto(self):
        self.state = 'confirm'

    @api.one
    def button_completa(self):
        self.state = 'end'

    @api.onchange ('type')
    def _change_end (self):
        for event in self:
            fmt = "%Y-%m-%d %H:%M:%S"
            if event.type:
                if event.date_begin:
                    start = datetime.strptime(event.date_begin, fmt)
                    event.date_end = start + timedelta(minutes=event.type.duracion_min)

    @api.onchange ('gabinete_id')
    def _change_gabinete (self):
        for event in self:
            if event.gabinete_id.protesist_id:
                event.protesist_id = event.gabinete_id.protesist_id.id
                event.color_state_id = event.gabinete_id.protesist_id.id

    @api.onchange ('protesist_id')
    def _change_protesist (self):
        for event in self:
            if event.protesist_id:
                event.color_state_id = event.protesist_id.id

event_event()


#ampliamos clases de even.type para poder manejar duraciones por defecto en cada tipo de cita
class event_type(models.Model):
    _inherit = 'event.type'

    duracion_min = fields.Float('Duración en minutos')


#ampliamos clases de res.partner para poder registrar gabinetes como partners
class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_box = fields.Boolean('Gabinete')
    contacto = fields.Char('Contacto')
    fallecido = fields.Boolean('Fallecido')


class asb_gabinete(models.Model):
    _name = 'asb.gabinete'

    name = fields.Char('Gabinete')
    protesist_id = fields.Many2one ('res.users', string="Audioprotesista")

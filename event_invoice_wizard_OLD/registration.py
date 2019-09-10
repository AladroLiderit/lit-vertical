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
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp

import logging
logger = logging.getLogger(__name__)


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

    
    suplidos_invoiced = fields.Many2many('event.suplidos.registro', string='Suplidos facturados')

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
    cargo_maleta = fields.Boolean(string='Maleta Facturada', help="Supone recargo adicional por el coste de facturar equipaje")
    num_maletas = fields.Float('Num. Maletas',default=1.0)
    peso_maletas = fields.Float('Peso Maletas')
    fact_agrupada = fields.Selection(selection=[('group','Agrupado'),('indiv','Individual')], string='Facturación')

    #valores facturados por inscripcion (factura del mismo evento y del mismo partner por cada tipo)
    factura = fields.Many2many('account.invoice','account_invoice_registration_rel','invoice_id','registration_id', string='Factura', readonly=True, required=False)
    facturado_reserva = fields.Float('Facturado por inscripcion',digits_compute=dp.get_precision('Product Price'),compute='_compute_factura_reserva', store=True)
    facturado_fraccion = fields.Float('Facturado por fracciones',digits_compute=dp.get_precision('Product Price'),compute='_compute_factura_fraccion', store=True)
    facturado_final = fields.Float('Facturado final',digits_compute=dp.get_precision('Product Price'),compute='_compute_factura_final', store=True)
    total_facturado = fields.Float('Facturado total',digits_compute=dp.get_precision('Product Price'),compute='_compute_factura_total', store=True)

    financiado = fields.Boolean('A financiar',default=False)
    importe_financiado = fields.Float('Importe a financiar',digits_compute=dp.get_precision('Product Price'))
    plazo_financiado = fields.Char('Plazo de financiación')

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
            'name': 'Factura Final',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
            # 'res_model': 'event.registration.singleinvoice_wizard',
            'res_model': 'event.registration.multiinvoice_wizard',
            'type': 'ir.actions.act_window',
            'context': {'default_cliente':self.partner_id.id,'default_importe':'total'},
        }

    @api.one
    @api.depends('factura')
    def _compute_factura_reserva(self):
        for reg in self:
            total_inscripcion = 0
            
            facturaciones = self.env['account.invoice'].search([
                ('partner_id','=',reg.partner_id.id),
                ('event_id','=',reg.event_id.id)])
            # if len (facturaciones)==0:
            #     facturaciones = self.env['account.invoice'].search([
            #     ('partner_id','=',reg.event_id.colegio_event.id),
            #     ('event_id','=',reg.event_id.id)])
            # logger.info('En comp_fact_reserva valor de facturaciones %s'%facturaciones)

            for fac in facturaciones:
                # logger.info('En comp_fact_reserva valor de causa_factura %s'%fac.causa_factura)
                if fac.causa_factura == 'inscripcion':
                    total_inscripcion += fac.amount_total
                    # logger.info('En comp_fact_reserva valor de total_inscripcion %s'%total_inscripcion)
            reg.facturado_reserva = total_inscripcion

    @api.one
    @api.depends('factura')
    def _compute_factura_fraccion(self):
        for reg in self:
            total_inscripcion = 0
            facturaciones = self.env['account.invoice'].search([
                ('partner_id','=',reg.partner_id.id),
                ('event_id','=',reg.event_id.id)])
            # if len (facturaciones)==0:
            #     facturaciones = self.env['account.invoice'].search([
            #     ('partner_id','=',reg.event_id.colegio_event.id),
            #     ('event_id','=',reg.event_id.id)])
            for fac in facturaciones:
                if fac.causa_factura == 'fraccion':
                    total_inscripcion += fac.amount_total
            reg.facturado_fraccion = total_inscripcion

    @api.one
    @api.depends('factura')
    def _compute_factura_final(self):
        for reg in self:
            total_inscripcion = 0
            facturaciones = self.env['account.invoice'].search([
                ('partner_id','=',reg.partner_id.id),
                ('event_id','=',reg.event_id.id)])
            # if len (facturaciones)==0:
            #     facturaciones = self.env['account.invoice'].search([
            #     ('partner_id','=',reg.event_id.colegio_event.id),
            #     ('event_id','=',reg.event_id.id)])
            for fac in facturaciones:
                if fac.causa_factura == 'total':
                    total_inscripcion += fac.amount_total
            reg.facturado_final = total_inscripcion

    @api.one
    @api.depends('factura')
    def _compute_factura_total(self):
        for reg in self:
            reg.total_facturado = reg.facturado_reserva + reg.facturado_fraccion + reg.facturado_final



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

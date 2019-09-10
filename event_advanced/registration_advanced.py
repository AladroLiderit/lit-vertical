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
from openerp import models, fields, api, exceptions, _
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp

import logging
logger = logging.getLogger(__name__)


class alojamiento_registro (models.Model):
    _name = 'event_advanced.alojamiento_registro'
    name = fields.Char(string='Alojamiento')

class caracterisiticas_registro (models.Model):
    _name = 'event_advanced.caracteristicas_registro'
    name = fields.Char(string='Características')

class regimen_registro (models.Model):
    _name = 'event_advanced.regimen_registro'
    name = fields.Char(string='Regimen')

class forma_pago_registro (models.Model):
    _name = 'event_advanced.forma_pago_registro'
    name = fields.Char(string='Forma de pago')

class forma_pago_resto_registro (models.Model):
    _name = 'event_advanced.forma_pago_resto_registro'
    name = fields.Char(string='Forma de pago del resto')

class conceptos_contratados_registro (models.Model):
    _name = 'event_advanced.conceptos_contratados_registro'
    name = fields.Char(string='Conceptos contratados', required=True)
    # importe_concepto = fields.Float(string='Importe del Suplido', digits_compute=dp.get_precision('Product Price'))
    # tax_id = fields.Many2one ('account.tax', string='Tipo de IVA')
    # facturable = fields.Boolean (string='Es facturable', default=True)

class event_suplido (models.Model):
    _name = 'event.suplido'
    name = fields.Char(string='Suplido', required=True)
    importe_concepto = fields.Float(string='Importe del Suplido', digits_compute=dp.get_precision('Product Price'))
    tax_id = fields.Many2one ('account.tax', string='Tipo de IVA')

class event_suplidos_registro (models.Model):
    _name = 'event.suplidos.registro'
    suplido_id = fields.Many2one ('event.suplido', string='Suplido')
    event_id = fields.Many2one ('event.event', string='Actividad')
    importe_concepto = fields.Float(string='Importe del Suplido', digits_compute=dp.get_precision('Product Price'))
    tax_id = fields.Many2one ('account.tax', string='Tipo de IVA')
    importe_impuesto = fields.Float(string='Importe con Impuestos', digits_compute=dp.get_precision('Product Price'))
    facturable = fields.Boolean(string='Facturable', default=True)
    invoiced = fields.Boolean(string='Facturado', default=False)

    @api.onchange('suplido_id')
    def _onchange_suplido_id(self):
        if self.suplido_id:
            self.importe_concepto = self.suplido_id.importe_concepto
            self.tax_id = self.suplido_id.tax_id
            self.importe_impuesto = self.suplido_id.importe_concepto * (1+self.suplido_id.tax_id.amount)

    @api.onchange('importe_concepto')
    def _onchange_importe_concepto(self):
        if self.importe_concepto:
            if self.tax_id:
                self.importe_impuesto = self.importe_concepto * (1+self.tax_id.amount)
            else:
                self.importe_impuesto = self.importe_concepto

    @api.onchange('tax_id')
    def _onchange_tax_id(self):
        if self.tax_id:
            if self.importe_concepto:
                self.importe_impuesto = self.importe_concepto * (1+self.tax_id.amount)
            else:
                self.importe_impuesto = 0

    @api.multi
    def name_get(self):
 
        res = super(event_suplidos_registro, self).name_get()
        data = []
        for suplido in self:
            display_value = ''
            display_value += suplido.suplido_id.name or ""
            display_value += ' '+str(suplido.importe_concepto)+'€' or ""
            data.append((suplido.id, display_value))
        return data

class idioma_registro (models.Model):
    _name = 'event_advanced.idioma_registro'
    name = fields.Char(string='Idioma')

class event_registration(models.Model):
    _name = 'event.registration'
    _description = 'Event Registration'
    _inherit = ['event.registration']


    def _get_importe_reserva(self):
        if self.event_id:       
            importe_reserva = self.event_id.precio_reserva_event
        else:
            importe_reserva = 0
        # logger.info('Entro en get_importe_reserva con reserva %d'%importe_reserva)
        return self.env.context.get('pago_inscripcion_registro_default', importe_reserva)

        if importe_reserva > 0:
            self.pago_fraccionado_registro = True


    alojamiento_registro = fields.Many2one('event_advanced.alojamiento_registro', string='Alojamiento', required=False)
    caracteristicas_registro = fields.Many2many('event_advanced.caracteristicas_registro', 'caracteristicas', 'registro_id','caracteristica_id', string='Características')
    regimen_registro = fields.Many2one('event_advanced.regimen_registro', string='Regimen', required=False)
    madrugador_registro = fields.Selection(selection=[('si', 'Sí'),('no','No')], string='Madrugador')
    madrugador_inscripcion = fields.Boolean('Madrugador')
    pago_fraccionado_registro = fields.Boolean('Pago fraccionado')
    pago_inscripcion_registro = fields.Float(string='Inscripción a cobrar', digits_compute=dp.get_precision('Product Price'), default=_get_importe_reserva)
    #forma_pago_registro = fields.Many2one('event_advanced.forma_pago_registro', string='Forma de pago', required=False)
    pago_resto_registro = fields.Float(string='Final a cobrar', compute='_compute_pago_resto_registro', digits_compute=dp.get_precision('Product Price'), readonly=True, store=True)
    #forma_pago_resto_registro = fields.Many2one('event_advanced.forma_pago_resto_registro', string='Forma de pago del resto', required=False)
    total_inscripcion = fields.Float(string='Total a cobrar', compute='_compute_total_inscripcion', digits_compute=dp.get_precision('Product Price'), readonly=True, store=True)
    conceptos_contratados_registro = fields.Many2many('event_advanced.conceptos_contratados_registro', 'conceptos_contratados_registros', 'registro_id','concepto_id', string='Conceptos contratados')
    suplidos_registro = fields.Many2many('event.suplidos.registro', 'suplidos_registros', 'registro_id','suplido_id', string='Suplidos')
    idioma_registro = fields.Many2one('event_advanced.idioma_registro', string='Idioma', required=False)
    forma_pago_registro = fields.Many2one(comodel_name='payment.mode', string="F.Pago Inscripción")
    plazo_pago_registro = fields.Many2one(comodel_name='account.payment.term', string="Vencimiento Inscripción")
    forma_pago_resto_registro = fields.Many2one(comodel_name='payment.mode', string="F.Pago Factura")
    plazo_pago_resto_registro = fields.Many2one(comodel_name='account.payment.term', string="Vencimiento Factura")
    jornada_registration = fields.Many2one('event_advanced.jornada_event', string='Jornada', required=False)
    horas_registration = fields.Many2one('event_advanced.horas_event', string='Horas', required=False)
    transporte_registration = fields.Boolean(string="Incluye transporte")
    tipo_transporte_registration = fields.Many2one('event_advanced.tipo_transporte_event', string='Tipo de transporte', required=False)
    dto_alumno = fields.Float(string='Descuento especial para alumno (importe total)', digits_compute=dp.get_precision('Product Price'))
    
    #valores para comedor, animales, compartir_con
    comedor_registro = fields.Boolean('Comedor')
    animales_registro = fields.Boolean('No Animales')
    quiere_compartir = fields.Char('Quiere compartir con:', size=150)

    total_fraccionados = fields.Float('Fraccionados a cobrar',related='event_id.total_fraccionados')
    

    @api.one
    @api.depends('pago_inscripcion_registro','dto_alumno')
    def _compute_pago_resto_registro(self):
        self.pago_resto_registro = self.event_id.precio_total_event - self.event_id.descuento_event - self.pago_inscripcion_registro - self.dto_alumno - self.total_fraccionados

    @api.one
    @api.depends('event_id')
    def _compute_total_inscripcion(self):
        self.total_inscripcion = self.event_id.precio_total_event - self.event_id.descuento_event - self.dto_alumno


    @api.onchange('event_id')
    def _onchange_event_id(self):
        if self.event_id.precio_total_event:
            self.total_inscripcion = self.event_id.precio_total_event - self.event_id.descuento_event

        if self.event_id.precio_reserva_event > 0:
            self.pago_inscripcion_registro = self.event_id.precio_reserva_event
            self.pago_fraccionado_registro = True

        if self.event_id:
            jornada_id = self.event_id.jornada_event
            horas_id = self.event_id.horas_event
            tpte_bool = self.event_id.transporte_event
            tipo_tpte_id = self.event_id.tipo_transporte_event
            conceptos_ids = self.event_id.conceptos_contratados_event
            if jornada_id:
                self.jornada_registration = jornada_id
            if horas_id:
                self.horas_registration = horas_id
            if tpte_bool:
                self.transporte_registration = True
                self.tipo_transporte_registration = tipo_tpte_id
            if conceptos_ids:
                self.conceptos_contratados_registro = conceptos_ids
            self.pago_resto_registro = self.event_id.precio_total_event - self.event_id.descuento_event - self.pago_inscripcion_registro - self.dto_alumno


    @api.onchange('pago_inscripcion_registro','dto_alumno')
    def _onchange_pago_inscripcion_registro(self):
        if self.pago_inscripcion_registro:
            self.pago_resto_registro = self.event_id.precio_total_event - self.event_id.descuento_event - self.pago_inscripcion_registro - self.dto_alumno
        
    @api.one
    @api.constrains('event_id','partner_id')
    def _check_registration(self):
        if self.partner_id:
            # logger.info('ID del evento%s'%self.event_id.id)
            # logger.info('ID del alumno%s'%self.partner_id.id)
            # logger.info('ID del registro%s'%self.id)
            registration_doble = self.search([
                ('event_id', '=', self.event_id.id),
                ('partner_id', '=', self.partner_id.id),
                ('id','<',self.id)], limit=1)
            # logger.info('ID del registro duplicado%s'%registration_doble.id)

            if registration_doble:
                raise exceptions.Warning(
                    _("Error! El alumno %s ya tiene inscripción en esta actividad." %
                      self.partner_id.name)
                )


    
event_registration()

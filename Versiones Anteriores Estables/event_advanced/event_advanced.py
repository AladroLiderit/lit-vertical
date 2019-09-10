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

from datetime import datetime
import logging
logger = logging.getLogger(__name__)

class programa_event (models.Model):
    _name = 'event_advanced.programa_event'
    name = fields.Char(string='Programa')

class actividad_event (models.Model):
    _name = 'event_advanced.actividad_event'
    name = fields.Char(string='Actividad')

class duracion_event (models.Model):
    _name = 'event_advanced.duracion_event'
    name = fields.Char(string='Duración')
    dias_duracion = fields.Integer('Duración en días')

class subtipo_event (models.Model):
    _name = 'event_advanced.subtipo_event'
    name = fields.Char(string='Subtipo')
    tipo = fields.Selection(selection=[('junior', 'Junior'),('adulto','Adulto')])

class facturacion_event (models.Model):
    _name = 'event_advanced.facturacion_event'
    name = fields.Char(string='Facturación')
    es_global = fields.Boolean(string='Facturar agrupados')

class centro_actividad_event (models.Model):
    _name = 'event_advanced.centro_actividad_event'
    name = fields.Char(string='Nombre')
    city = fields.Char(string='Ciudad')
    state_id = fields.Many2one("res.country.state", string='Provincia', ondelete='restrict')
    country_id = fields.Many2one('res.country', string='País', ondelete='restrict')

class jornada_event (models.Model):
    _name = 'event_advanced.jornada_event'
    name = fields.Char(string='Jornada')

class tipo_transporte_event (models.Model):
    _name = 'event_advanced.tipo_transporte_event'
    name = fields.Char(string='Tipo de transporte')

class horas_event (models.Model):
    _name = 'event_advanced.horas_event'
    name = fields.Char(string='Horas')

@api.model
def get_taxes(self):
    return self.env['account.tax'].search([('description','like', 'S_IVA0'),('name','ilike', 'exento')]).ids or ''


class event_event(models.Model):
    _name = 'event.event'
    _description = 'Event'
    _inherit = ['event.event']

    def select_jornada_completa(self):
        jornada_completa = self.env['event_advanced.jornada_event'].search([('name','ilike','completa')])
        if len(jornada_completa)>1:
            return jornada_completa[0].id
        if len(jornada_completa)==1:
            return jornada_completa.id
        else:
            return False

    @api.depends('precio_total_event', 'descuento_event', 'suplidos_event')
    @api.onchange('precio_total_event', 'descuento_event', 'suplidos_event')
    def _compute_total_formacion(self):
        for event in self:
            total_suplidos = 0
            for record in event.suplidos_event:
                total_suplidos += record.importe_impuesto
            #los cargos pueden llevar IVA:
            suma_ivas = 0
            for t in event.tax_ids:
                suma_ivas += t.amount
            # logger.error('Total suplidos en compute_total_formacion %s'%total_suplidos)
            # logger.error('Total iva en compute_total_formacion %s'%suma_ivas)
            neto_event = event.precio_total_event - event.descuento_event
            event.total_formacion = (float(neto_event)/(1+suma_ivas)) - total_suplidos

    programa_event = fields.Many2one('event_advanced.programa_event', string='Programa', required=False)
    actividad_event = fields.Many2one('event_advanced.actividad_event', string='Actividad', required=False)
    comercial_event = fields.Many2one('res.partner', 'Comercial', ondelete='restrict', required=False)
    duracion_event = fields.Many2one('event_advanced.duracion_event', string='Duración del programa', required=False)
    duracion = fields.Integer(string='Duración en días',store=True,related='duracion_event.dias_duracion')
    tipo_event = fields.Selection(selection=[('junior', 'Junior'),('adulto','Adulto')], string='Tipo de Curso')
    subtipo_event = fields.Many2one('event_advanced.subtipo_event', string='Subtipo de curso', required=False)
    facturacion_event = fields.Many2one('event_advanced.facturacion_event', string='Facturación de curso', required=False)
    #fecha_inicio_event = fields.Date(string="Fecha de inicio")
    #fecha_fin_event = fields.Date(string="Fecha de fin")
    centro_actividad_event = fields.Many2one('event_advanced.centro_actividad_event', string='Centro de actividad', required=False)

    date_begin = fields.Datetime(string='Start Date', required=False,
        readonly=True, states={'draft': [('readonly', False)]})
    date_end = fields.Datetime(string='End Date', required=False,
        readonly=True, states={'draft': [('readonly', False)]})

    destino_event = fields.Char(related='centro_actividad_event.city', string="Ciudad destino", readonly=True, store=True)
    pais_event = fields.Char(related='centro_actividad_event.country_id.name',string="País de destino", readonly=True, store=True)

    jornada_event = fields.Many2one('event_advanced.jornada_event', string='Jornada', required=False, default=select_jornada_completa)
    transporte_event = fields.Boolean(string="Incluye transporte")
    tipo_transporte_event = fields.Many2one('event_advanced.tipo_transporte_event', string='Tipo de transporte', required=False)
    horas_event = fields.Many2one('event_advanced.horas_event', string='Horas', required=False)
    precio_total_event = fields.Float(string='Precio total (por alumno)', digits_compute=dp.get_precision('Product Price'))
    precio_reserva_event = fields.Float(string='Precio Reserva (por alumno)', digits_compute=dp.get_precision('Product Price'))
    descuento_event = fields.Float(string='Descuento (por alumno)', digits_compute=dp.get_precision('Product Price'))
    tax_ids = fields.Many2many('account.tax', string='Impuestos', required=True, default=get_taxes)
    account_id = fields.Many2one('account.account', string='Cuenta', required=True, domain="[('type','=','receivable')]")
    account_analytic_id = fields.Many2one('account.analytic.account', string='Cuenta analítica')
    conceptos_contratados_event = fields.Many2many('event_advanced.conceptos_contratados_registro', 'conceptos_contratados_eventos', 'event_id','concepto_id', string='Conceptos contratados')
    suplidos_event = fields.One2many('event.suplidos.registro','event_id',string='Suplidos')
    invoice_concept = fields.Char(string="Concepto Facturable", default="Actividades lingüísticas y formación")
    total_formacion = fields.Float(string='Total formación (por alumno)', digits_compute=dp.get_precision('Product Price'), compute='_compute_total_formacion')
    recargo_extemporaneo = fields.Float(string='Recargo por fuera de plazo', digits_compute=dp.get_precision('Product Price'))
    
    

    @api.onchange('centro_actividad_event')
    def _onchange_centro_actividad_event(self):
        if self.centro_actividad_event:
            self.destino_event = self.centro_actividad_event.city
            self.pais_event = self.centro_actividad_event.country_id.name

    @api.onchange('tipo_event')
    def _onchange_tipo_event(self):
        if self.tipo_event:
            res = {}
            res['domain'] = {'subtipo_event': [('tipo', '=', self.tipo_event)]}
            return res

    @api.onchange('date_end')
    def _onchange_date_end(self):
        if self.date_end and self.date_begin:
            # para obtener el intervalo de dias
            fmt = '%Y-%m-%d %H:%M:%S'
            from_date = self.date_begin
            to_date = self.date_end
            d1 = datetime.strptime(from_date, fmt)
            # logger.error('Dias de duracion obtenidas en d1 %s'%d1)
            d2 = datetime.strptime(to_date, fmt)
            # logger.error('Dias de duracion obtenidas en d2 %s'%d2)
            daysDiff = str((d2-d1).days)
            daysDiff = str((d2-d1).days + 1)
            # logger.error('Dias de duracion obtenidas %s'%daysDiff)
            dur_event = self.env['event_advanced.duracion_event'].search([('dias_duracion','=', int(daysDiff))])
            if len(dur_event)>1:
                self.duracion_event = dur_event[0].id
            if len(dur_event)==1:
                self.duracion_event = dur_event.id

    @api.v7
    def add_multiple_partner(self, cr, uid, id_, partner_ids_to_add, context=None):
        super(event_event, self).add_multiple_partner(cr, uid, id_, partner_ids_to_add, context=context)
        partner_ids = [partner.id for partner in partner_ids_to_add]
        regs = self.pool.get('event.registration')
        regsrch = regs.search(cr,uid,[('event_id','=',id_),('partner_id','in',partner_ids)])
        for r in regsrch:
            thisr = regs.browse(cr,uid,r)
            # logger.error('Valor para add_multiple de id registro %s'%r)
            # logger.error('Valor para add_multiple de jornada %s'%thisr.event_id.jornada_event.id)
            # logger.error('Valor para add_multiple de horas %s'%thisr.event_id.horas_event.id)
            # logger.error('Valor para add_multiple de transporte_bool %s'%thisr.event_id.transporte_event)
            # logger.error('Valor para add_multiple de transporte_tipo %s'%thisr.event_id.tipo_transporte_event.id)
            
            t_insc = thisr.event_id.precio_total_event - thisr.event_id.descuento_event
            # logger.error('Valor para add_multiple de total_inscripcion %d'%t_insc)

            regs.write(cr,uid,r,{'jornada_registration': thisr.event_id.jornada_event.id or '', 
                    'horas_registration': thisr.event_id.horas_event.id or '',
                    'transporte_registration': thisr.event_id.transporte_event,
                    'tipo_transporte_registration': thisr.event_id.tipo_transporte_event.id or '',
                    'total_inscripcion': t_insc or '',   
                    })
            if thisr.event_id.conceptos_contratados_event.ids:
                regs.write(cr,uid,r,{'conceptos_contratados_registro': [(6, 0, thisr.event_id.conceptos_contratados_event.ids)]})
            # logger.error('Valor para add_multiple de precio reserva %d'%thisr.event_id.precio_reserva_event)
            if thisr.event_id.precio_reserva_event > 0:
                # logger.error('Valor para add_multiple de pago_inscripcion_registro %d'%thisr.event_id.precio_reserva_event)
                regs.write(cr,uid,r,{'pago_inscripcion_registro': thisr.event_id.precio_reserva_event,
                        'pago_fraccionado_registro': True})

event_event()

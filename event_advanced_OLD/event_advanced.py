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
                if record.facturable:
                    total_suplidos += record.importe_impuesto
            #los cargos pueden llevar IVA:
            suma_ivas = 0
            for t in event.tax_ids:
                suma_ivas += t.amount
            # logger.error('Total suplidos en compute_total_formacion %s'%total_suplidos)
            # logger.error('Total iva en compute_total_formacion %s'%suma_ivas)
            neto_event = event.precio_total_event - event.descuento_event
            event.total_formacion = (float(neto_event)/(1+suma_ivas)) - total_suplidos

    @api.depends('registration_ids')
    @api.onchange('registration_ids')
    def _compute_total_nenos(self):
        for event in self:
            total_nenos = 0
            total_nenas = 0
            for record in event.registration_ids:
                if record.partner_id.gender == 'M':
                    total_nenas += 1
                if record.partner_id.gender == 'H':
                    total_nenos += 1

            # logger.error('Total suplidos en compute_total_formacion %s'%total_suplidos)
            event.total_nenos = float(total_nenos)
            event.total_nenas = float(total_nenas)

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
    has_fly = fields.Boolean(string='View flight info', default = False)
    fly_number = fields.Char(string='Flight number', size = 30)
    fly_date = fields.Date (string='Flight date')
    fly_time = fields.Char (string='Flight time', size = 70)
    

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
    # cambio de Oct 2018 para permitir varias facturas por pagos a cuenta
    reserva_ids = fields.One2many('event.reserva','event_id',string='Reservas')
    pago_web = fields.Float(string='Precio a pagar en Web (por alumno)', digits_compute=dp.get_precision('Product Price'))
    descuento_event = fields.Float(string='Descuento (por alumno)', digits_compute=dp.get_precision('Product Price'))
    tax_ids = fields.Many2many('account.tax', string='Impuestos', required=True, default=get_taxes)
    account_id = fields.Many2one('account.account', string='Cuenta', required=True, domain="[('type','=','receivable')]")
    account_analytic_id = fields.Many2one('account.analytic.account', string='Cuenta analítica')
    conceptos_contratados_event = fields.Many2many('event_advanced.conceptos_contratados_registro', 'conceptos_contratados_eventos', 'event_id','concepto_id', string='Conceptos contratados')
    suplidos_event = fields.One2many('event.suplidos.registro','event_id',string='Suplidos')
    invoice_concept = fields.Char(string="Concepto Facturable", default="Actividades lingüísticas y formación")
    total_formacion = fields.Float(string='Total formación (por alumno)', digits_compute=dp.get_precision('Product Price'), compute='_compute_total_formacion')
    total_nenos = fields.Float(string='Total niños inscritos', digits_compute=dp.get_precision('Product Price'), compute='_compute_total_nenos')
    total_nenas = fields.Float(string='Total niñas inscritas', digits_compute=dp.get_precision('Product Price'), compute='_compute_total_nenos')
    recargo_extemporaneo = fields.Float(string='Recargo por fuera de plazo', digits_compute=dp.get_precision('Product Price'))
    recargo_maleta = fields.Float(string='Cargo por maleta facturada (sin IVA)', digits_compute=dp.get_precision('Product Price'))
    tax_maleta = fields.Many2one('account.tax', string='Impuesto en maletas')
# campos que pasan en setp 2017 del registros a la actividad
    alojamiento_actividad = fields.Many2one('event_advanced.alojamiento_registro', string='Alojamiento', required=False)
    caracteristicas_actividad = fields.Many2many('event_advanced.caracteristicas_registro', 'caracteristicas_actividad', 'actividad_id','caracteristica_id', string='Características')
    regimen_actividad = fields.Many2one('event_advanced.regimen_registro', string='Regimen', required=False)
    idioma_actividad = fields.Many2one('event_advanced.idioma_registro', string='Idioma', required=False)

    total_fraccionados = fields.Float(string="Total de pagos fraccionados", digits_compute=dp.get_precision('Product Price'), compute='_compute_total_fraccionados')
    

    @api.onchange('reserva_ids')
    def _onchange_reserva_ids(self):
        for event in self:
            total_reservas = 0
            for r in event.reserva_ids:
                total_reservas += r.importe_concepto
            
            if total_reservas + event.precio_reserva_event > event.total_formacion:
                # last_reserva = self. env['event.reserva'].search([('event_id','=',event.id)], order='id desc', limit=1)
                # event.reserva_ids = (2,last_reserva.id)
                raise exceptions.Warning(
                        _("Error! La suma de pagos anticipados no puede superar los %s € del total de formación."\
                         "Debe eliminar o modificar este registro" % event.total_formacion)
                    )

    @api.onchange('reserva_ids')
    def _compute_total_fraccionados(self):
        for event in self:
            total_fraccionado = 0
            for r in event.reserva_ids:
                total_fraccionado += r.importe_concepto + r.importe_impuesto
            event.total_fraccionados = total_fraccionado

    @api.onchange('precio_reserva_event')
    def _onchange_precio_reserva_event(self):
        registration = self.env['event.registration']
        # logger.error('Cambiando pago inscripcion en registro reserva_ids %s'%self.registration_ids)
        for r in self.registration_ids:
            # logger.error('Cambiando pago inscripcion en registro %s'%r)
            reg = registration.browse(r.id)
            reg.write({'pago_inscripcion_registro' : self.precio_reserva_event})

    @api.onchange('precio_total_event')
    def _onchange_precio_total_event(self):
        registration = self.env['event.registration']
        for r in self.registration_ids:
            reg = registration.browse(r.id)
            th_total_inscripcion = self.precio_total_event - self.descuento_event - r.dto_alumno
            reg.write({'total_inscripcion' : th_total_inscripcion})

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


class event_reserva (models.Model):
    _name = 'event.reserva'

    # name = fields.Char('Nombre')
    pago_name = fields.Char('Concepto de pago',required=True)
    event_id = fields.Many2one ('event.event', string='Actividad',required=True)
    importe_concepto = fields.Float(string='Anticipo con IVA', digits_compute=dp.get_precision('Product Price'))
    # tax_id = fields.Many2one ('account.tax', string='Tipo de IVA')
    tax_ids = fields.Many2many ('account.tax', required=True, default=get_taxes, string='Tipo de IVA')
    importe_impuesto = fields.Float(string='Importe de Impuestos', digits_compute=dp.get_precision('Product Price'))
    invoiced = fields.Boolean('Facturado')



    # @api.onchange('importe_concepto')
    # def _onchange_importe_concepto(self):
    #     if self.importe_concepto:
    #         amount_tax = 0
    #         if self.tax_ids:
    #             for tax in self.tax_ids:
    #                 amount_tax += float(self.importe_concepto * tax.amount)
    #             self.importe_impuesto = float(self.importe_concepto + amount_tax)
    #         else:
    #             self.importe_impuesto = self.importe_concepto


    @api.onchange('tax_ids')
    def _onchange_tax_ids(self):
        if self.tax_ids:
            if self.importe_concepto:       
                amount_tax = 0
                for tax in self.tax_ids:
                    amount_tax += float(self.importe_concepto * tax.amount)

                self.importe_impuesto = amount_tax

            else:
                self.importe_impuesto = 0


    @api.multi
    def name_get(self):
 
        res = super(event_reserva, self).name_get()
        data = []
        for reserva in self:
            display_value = ''
            display_value += reserva.pago_name or ""
            display_value += ' '+str(reserva.importe_concepto)+'€' or ""
            data.append((reserva.id, display_value))
        return data


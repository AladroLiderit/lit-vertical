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
from openerp import exceptions
import sys  
from datetime import datetime

import logging 
_logger = logging.getLogger(__name__)

reload(sys)  
sys.setdefaultencoding('utf8')


REGISTRATION_STATES = [
    ('inscripcion', 'Reserva'),
    ('total','Total pendiente'),
    ('fraccion','Pagos Fraccionados'),
    ('suplido','Suplidos')
    ]

VOUCHER_STATES = [
    ('inscripcion', 'Reserva'),
    ('pendiente','Pendiente'),
    ('total','Total actividad')
    ]


#creamos un valor para asociar una factura con un evento, aunque pueda tener varias inscripciones
class account_invoice(models.Model):
    _inherit = ['account.invoice']

    event_id = fields.Many2one('event.event', 'Actividad')
    #creamos un campo para saber si se genero por el pago de reserva o por pago final
    causa_factura = fields.Selection(selection=REGISTRATION_STATES , string="Origen de la factura")
    #creamos un bool para identificar los anticipos ya compensados en factura final
    ant_compensado = fields.Boolean(string="Anticipo ya compensado", default = False)
    reserva_id = fields.Many2one('event.reserva', 'Pago Fraccionado')
    suplido_id = fields.Many2one('event.suplidos.registro', string='Pago Fraccionado')
    is_agencia = fields.Boolean('Regimen Agencia Viajes', default=False)


class event_event(models.Model):
    _inherit = ['event.event']

    invoice_ids = fields.One2many ('account.invoice','event_id',string='Facturaciones')


class EventMultiInvoiceWizard(models.TransientModel):
    _name = 'event.registration.multiinvoice_wizard'
    _description = 'Create multiple invoices for events'

    importe = fields.Selection(selection=REGISTRATION_STATES , string="Importe a facturar")
    event_id = fields.Many2one('event.event')
    reserva_id = fields.Many2one('event.reserva',string='Anticipo a facturar')
    suplido_id = fields.Many2one('event.suplidos.registro',string='Suplido a facturar')

    # al cambiar el concepto de importe si es de tipo fraccionado actualizar en el context el event_id
    @api.onchange('importe')
    def set_event_context(self):
        if self.importe == 'fraccion' or self.importe =='suplido':
            # _logger.info('Cambio en importe %s'%self.importe)
            regs_obj = self.env['event.registration']
            active_ids = self.env.context['active_ids'] or []
            all_regs = regs_obj.browse(active_ids)

            ids=[]
            event = 0
            for reg in all_regs:
                if event != reg.event_id.id:
                    # _logger.info('Registrado evento en ids %s'%reg.event_id.id)
                    ids.append(reg.event_id.id)
                    event = reg.event_id.id

            # _logger.info('Ingreso en context para event_id %s'%ids[0])
            # return {'context': {'event_id': ids[0]}}
            self.event_id = ids[0]


    #do_create_inovices genera una factura para cada inscripcion o alumno
    @api.multi
    def do_create_invoices(self):
        self.ensure_one()

        if not (self.importe):
            raise exceptions.ValidationError('Debe seleccionar un importe a facturar')
        
        regs_obj = self.env['event.registration']
        active_ids = self.env.context['active_ids'] or []
        all_regs = regs_obj.browse(active_ids)

        # Validación de que solo se factura un evento.
        evento_correcto = False
        reg_eventos = iter(all_regs)
        try:
            primer_reg = next(reg_eventos)
        except StopIteration:
            evento_correcto = True

        if not evento_correcto:
            evento_correcto = all(primer_reg.event_id == resto.event_id for resto in reg_eventos)
        
        if not evento_correcto:
            raise exceptions.ValidationError('Debe seleccionar una sola actividad')
        else:
            #comprobamos que la actividad (evento) no tiene marcada una facturación agrupada
            if primer_reg.event_id.facturacion_event.es_global:
                raise exceptions.ValidationError('La actividad %s solo permite facturación agrupada de las inscripciones'%primer_reg.event_id.name)


        # Validacion de que todas las inscripciones estan en el mismo estado de facturacion
        estado_ins = all_regs[0].estado
        cambios = regs_obj.search([('id','in',active_ids),('estado','!=',estado_ins)])
        if len(cambios)>0:
            raise exceptions.ValidationError('Las inscripciones deben estar todas en el mismo estado de facturación')


        invoice_obj = self.env['account.invoice']
        line_obj = self.env['account.invoice.line']

        cuenta_obj = self.env['account.account']

        cont_facturado = 0 
        idf_ids=[]


        for reg in all_regs:   
            try:
                #import pudb; pudb.set_trace()
                facturar = True # Para evitar facturar 2 veces el mismo concepto.

                
                # para facturar la reserva
                if self.importe == 'inscripcion' and reg.estado == 'pendiente' and reg.state == 'open':
                    precio_facturar = reg.pago_inscripcion_registro
                    reg.estado = 'inscripcion'
                    causa_factura = 'inscripcion'
                    concepto_linea = "Adelanto por reserva formación %s" %str(reg.event_id.name)
                    if reg.alumno_en_factura:
                        nombre_alumno = str(reg.nombre_alumno)+' '+str(reg.apellido_alumno)
                        concepto_linea = concepto_linea + ' para %s' %nombre_alumno
                    
                    if reg.forma_pago_registro:
                        payment_id = reg.forma_pago_registro.id
                    else:
                        if reg.partner_id.customer_payment_mode:
                            payment_id = reg.partner_id.customer_payment_mode.id
                        else:
                            payment_id = None

                    if reg.plazo_pago_registro:
                        payment_term_id = reg.plazo_pago_registro.id
                    else:
                        if reg.partner_id.property_payment_term:
                            payment_term_id = reg.partner_id.property_payment_term.id
                        else:
                            payment_term_id = None

                elif self.importe == 'inscripcion' and not reg.estado == 'pendiente':
                    facturar = False
                elif reg.state != 'open':
                    facturar = False

                # para facturar pagos fraccionados
                if self.importe == 'fraccion' and not reg.estado == 'total' and reg.state == 'open' and self.reserva_id:
                    #para no facturar dos veces comprobamos si hay una factura para esta inscripcion y pago fraccionado
                    dupl = False
                    for f in reg.factura:
                        if f.reserva_id and f.reserva_id.id == self.reserva_id.id:
                            dupl = True
                    if dupl:
                        facturar = False
                    else:
                        precio_facturar = self.reserva_id.importe_concepto - self.reserva_id.importe_impuesto
                        reg.estado = 'inscripcion'
                        causa_factura = 'fraccion'
                        concepto_linea = "%s a cuenta formación %s"% (str(self.reserva_id.pago_name),str(reg.event_id.name))

                        if reg.alumno_en_factura:
                            nombre_alumno = str(reg.nombre_alumno)+' '+str(reg.apellido_alumno)
                            concepto_linea = concepto_linea + ' para %s' %nombre_alumno
                        
                        if reg.forma_pago_registro:
                            payment_id = reg.forma_pago_registro.id
                        else:
                            if reg.partner_id.customer_payment_mode:
                                payment_id = reg.partner_id.customer_payment_mode.id
                            else:
                                payment_id = None

                        if reg.plazo_pago_registro:
                            payment_term_id = reg.plazo_pago_registro.id
                        else:
                            if reg.partner_id.property_payment_term:
                                payment_term_id = reg.partner_id.property_payment_term.id
                            else:
                                payment_term_id = None

                elif self.importe == 'fraccion':
                    facturar = False
                # elif reg.state != 'open':
                #    facturar = False

                # para facturar suplidos
                if self.importe == 'suplido' and self.suplido_id and not reg.estado == 'total':
                    #para no facturar dos veces comprobamos si hay una factura para esta inscripcion y suplido
                    dupl = False
                    for f in reg.factura:
                        if f.suplido_id and f.suplido_id.id == self.suplido_id.id:
                            dupl = True
                    if dupl:
                        facturar = False
                    else:
                        precio_facturar=0
                        causa_factura = 'suplido'

                        if not self.suplido_id.facturable:
                            facturar = False
                        else:
                            concepto_linea = 'Suplido: %s en actividad %s'%\
                                (str(self.suplido_id.suplido_id.name), str(reg.event_id.name))

                            precio_facturar += self.suplido_id.importe_concepto


                            if reg.forma_pago_registro:
                                payment_id = reg.forma_pago_registro.id
                            else:
                                if reg.partner_id.customer_payment_mode:
                                    payment_id = reg.partner_id.customer_payment_mode.id
                                else:
                                    payment_id = None

                            if reg.plazo_pago_registro:
                                payment_term_id = reg.plazo_pago_registro.id
                            else:
                                if reg.partner_id.property_payment_term:
                                    payment_term_id = reg.partner_id.property_payment_term.id
                                else:
                                    payment_term_id = None

                elif self.importe == 'suplido' and reg.estado == 'total':
                    facturar = False


                # para controlar si al facturar el total tiene un anticipo que descontar 
                anticipo = False
                if self.importe == 'total' and not reg.estado == 'total' and reg.state == 'open':
                    if reg.estado == 'inscripcion':
                        #comprobamos que la factura de inscripcion es valida antes de seguir
                        fact_anticipo_draft = invoice_obj.search([
                            ('event_id','=',reg.event_id.id),
                            ('causa_factura','in',('inscripcion','fraccion')),
                            ('partner_id','=',reg.partner_id.id),
                            ('state','=','("draft")'),
                            ('ant_compensado','=',False)
                            ])
                        if fact_anticipo_draft:
                            raise exceptions.Warning("Antes de seguir debe revisar las facturas de anticipo no validadas")

                        anticipo = True
                    # cambiamos, el precio a facturar solo de la formacion
                    # precio_facturar = reg.pago_resto_registro
                    precio_facturar = reg.event_id.total_formacion
                    

                    reg.estado = 'total'
                    causa_factura = 'total'
                    # cambiamos el concepto_linea para que sea solo la parte de formacion
                    # concepto_linea = "Facturación de Actividad %s" % str(reg.event_id.name)
                    concepto_linea = reg.event_id.invoice_concept
                    if (reg.alumno_en_factura) :
                        nombre_alumno = str(reg.nombre_alumno)+' '+str(reg.apellido_alumno)
                        concepto_linea = concepto_linea +' para %s' %nombre_alumno


                    if reg.forma_pago_resto_registro:
                        payment_id = reg.forma_pago_resto_registro.id
                    else:
                        if reg.partner_id.customer_payment_mode:
                            payment_id = reg.partner_id.customer_payment_mode.id
                        else:
                            payment_id = None

                    if reg.plazo_pago_resto_registro:
                        payment_term_id = reg.plazo_pago_resto_registro.id
                    else:
                        if reg.partner_id.property_payment_term:
                            payment_term_id = reg.partner_id.property_payment_term.id
                        else:
                            payment_term_id = None
                    # nuevo caso: inscripciones fuera de plazo que pueden tener recargo
                    if reg.extemporanea and reg.event_id.recargo_extemporaneo>0:
                        precio_facturar += reg.event_id.recargo_extemporaneo
                        concepto_linea = concepto_linea +' incluso recargo fuera de plazo'

                elif self.importe == 'total' and reg.estado == 'total':
                    facturar = False
                elif reg.state != 'open':
                    facturar = False
                
                
                #tenemos que comprobar si es un alumno con un tutor al que facturar
                '''
                if reg.partner_id.factura_rpte:
                    if reg.partner_id.representante:
                        partner_id = reg.partner_id.representante.id
                    else:
                        partner_id = reg.partner_id.id
                else:
                    partner_id = reg.partner_id.id
                '''
                #1-3-17 cambiamos este funcionamiento, factura a representante si existe valor
                if reg.partner_id.representante:
                    partner_id = reg.partner_id.representante.id
                else:
                    partner_id = reg.partner_id.id

                #cuenta_id = reg.partner_id.property_account_receivable.id or cuenta_obj.search([('code','=', '430')]).id
                cuenta_id = reg.event_id.account_id.id
                if reg.event_id.account_analytic_id.id:
                    cuenta_analitica_id = reg.event_id.account_analytic_id.id
                else:
                    cuenta_analitica_id = None

                #registramos el evento con el que se asocia la factura
                evento_id = reg.event_id.id
                # registramos si es de regimen especial de agencia de viajes
                if reg.event_id.reg_agencia:
                    agencia = True
                else:
                    agencia = False


                if facturar and precio_facturar > 0:
                    idf = invoice_obj.create({'partner_id' : partner_id,
                                              'account_id' : cuenta_id,
                                              'payment_mode_id' : payment_id,
                                              'payment_term' : payment_term_id,
                                              'event_id' : evento_id,
                                              'causa_factura' : causa_factura,
                                              'is_agencia' : agencia,
                    })

                    fact = invoice_obj.browse(idf.id)
                    cuenta_linea = fact.journal_id.default_credit_account_id.id

                    # en caso de pago fraccionado lo asociamos a la factura
                    if self.importe == 'fraccion':
                        fact.write ({'reserva_id' : self.reserva_id.id})

                    # en caso de pago de suplido lo asociamos a la factura
                    if self.importe == 'suplido':
                        fact.write ({'suplido_id' : self.suplido_id.id})

                    # hay que facturar por separado la formacion de los suplidos
                    # if self.importe != 'suplido':

                    idlinef = line_obj.create({'invoice_id' : idf.id,
                                                   #'name' : "Facturación de Actividad %s" % str(reg.event_id.name),
                                                   'name' : concepto_linea,
                                                   'price_unit' : precio_facturar,
                                                   'account_id' : cuenta_linea,
                                                   'invoice_line_tax_id' : [[6, 0, reg.event_id.tax_ids.ids]],
                                                   'account_analytic_id' : cuenta_analitica_id,
                                                   })

                    # if self.importe == 'suplido':
                    #     for sup in self.event_id.suplidos_event:
                    #         if sup.facturable and not sup.invoiced:
                    #             idlinef = line_obj.create({'invoice_id' : idf.id,
                    #                                    'name' : 'Suplidos: ' +sup.suplido_id.name,
                    #                                    'account_id' : cuenta_linea,
                    #                                    'account_analytic_id' : cuenta_analitica_id,
                    #                                    'price_unit' : sup.importe_impuesto,
                    #                                    })
                    #             reg.suplidos_event = [(4, sup.id)]
                                
                    # si estamos facturando un total y hay un descuento para esta inscripcion creamos la linea del descuento
                    if self.importe == 'total':
                        if reg.dto_alumno > 0:
                            texto_linea = 'Descuento sobre actividad de formación'
                            idlinef = line_obj.create({'invoice_id' : idf.id,
                                                       'name' : texto_linea,
                                                       'invoice_line_tax_id' : [[6, 0, reg.event_id.tax_ids.ids]],
                                                       'account_id' : cuenta_linea,
                                                       'account_analytic_id' : cuenta_analitica_id,
                                                       'price_unit' : (reg.dto_alumno*-1),
                                    })

                    # agregamos una linea a la factura por cada suplido no facturado en caso de factura final
                    if self.importe == 'total':                        
                        for sup in reg.event_id.suplidos_event:
                            if sup.facturable:
                                sup_facturado = False
                                for f in reg.factura:
                                    fact_suplido = invoice_obj.search([
                                        ('event_id','=',evento_id),
                                        ('suplido_id','=', sup.id),
                                        ('id','=',f.id),
                                        ('state','in',('open','paid')),
                                        ('ant_compensado','!=',True)
                                        ])
                                    if fact_suplido:
                                        sup_facturado = True
                                        break
                                if sup_facturado == False:
                                    texto_linea = 'Suplidos: '+sup.suplido_id.name

                                    idlinef = line_obj.create({'invoice_id' : idf.id,
                                                       'name' : texto_linea,
                                                       # modificado el 26/1 por reuníon con asesor
                                                       # 'price_unit' : sup.importe_concepto,
                                                       # 'invoice_line_tax_id' : [[6, 0, sup.tax_id.ids]],
                                                       'account_id' : cuenta_linea,
                                                       'account_analytic_id' : cuenta_analitica_id,
                                                       'price_unit' : sup.importe_impuesto,
                                    })

                    # si hay recargo de maleta agregamos una linea a la factura por ese concepto en factura final
                    if self.importe == 'total':
                        if reg.cargo_maleta and reg.event_id.recargo_maleta>0 :
                            if not reg.event_id.tax_maleta:
                                raise exceptions.MissingError('Falta el tipo de IVA para maletas en la actividad %d' % reg.event_id.name)
                            if reg.num_maletas > 0 and reg.peso_maletas > 0:
                                texto_linea = 'Cargo por %s maleta facturada con un peso de %s kg.'%\
                                (str(reg.num_maletas),str(reg.peso_maletas))
                            else:
                                texto_linea = 'Cargo por maleta facturada'

                            idlinef = line_obj.create({'invoice_id' : idf.id,
                                                       'name' : texto_linea,
                                                       # modificado el 26/1 por reuníon con asesor
                                                       # 'price_unit' : sup.importe_concepto,
                                                       'invoice_line_tax_id' : [[4, reg.event_id.tax_maleta.id]],
                                                       'account_id' : cuenta_linea,
                                                       'account_analytic_id' : cuenta_analitica_id,
                                                       'price_unit' : reg.event_id.recargo_maleta,
                                    })


                    # si estamos facturando un total y hay un pago de adelanto hay que descontarlo
                    if self.importe == 'total' and anticipo:
                        #!!!!Tenemos que localizar la factura donde esta el anticipo!!!
                        fact_anticipo = invoice_obj.search([
                            ('event_id','=',evento_id),
                            ('causa_factura','in',('inscripcion','fraccion')),
                            ('partner_id','=',partner_id),
                            ('state','in',('open','paid')),
                            ('ant_compensado','!=',True)
                            ])
                        for fa in fact_anticipo:

                            fecha_fac = str(fa[0].date_invoice)

                            dia_fact = fecha_fac[-2:]
                            mes_fact = fecha_fac[5:7]
                            ano_fac = fecha_fac[:4]
                            fecha_fac = dia_fact +'-'+mes_fact+'-'+ano_fac
                            texto_linea = '- Adelanto según factura '+str(fa[0].number)+ ' de fecha '+ fecha_fac
                            idlinef = line_obj.create({'invoice_id' : idf.id,
                                                   'name' : texto_linea,
                                                   'quantity': -1,
                                                   'price_unit' : fa[0].amount_untaxed,
                                                   'account_id' : cuenta_linea,
                                                   'invoice_line_tax_id' : [[6, 0, reg.event_id.tax_ids.ids]],
                                                   'account_analytic_id' : cuenta_analitica_id,
                            })
                            fa.write({'ant_compensado': True})

                    


                    reg.factura = [(4, idf.id)]
                    cont_facturado += 1
                    idf_ids.append(idf.id)


            except exceptions.MissingError:
                pass
                #raise exceptions.MissingError('Registro: %d' % regxs.id)
        if cont_facturado == 0:
            raise exceptions.Warning("Nada que facturar")
        else:
        #     #si el importe son suplidos hay que marcar con facturados los que no lo esten
        #     if self.importe == 'suplido':
        #         for sup in self.event_id.suplidos_event:
        #             if sup.facturable and not sup.invoiced:
        #                 sup.write({'invoiced':True})

            #_logger.info('Valor de domain entre [] %s'%idf_ids)

            #puede ser este id el que nos de limitaciones a la hora de editar las facturas mostradas
            # inv_view = self.env['ir.ui.view'].search([('name','=','account.invoice.select')])[0].id
            inv_view = self.env['ir.ui.view'].search([('name','=','account.invoice.tree')])[0].id
            inv_fview = self.env['ir.ui.view'].search([('name','=','account.invoice.form')])[0].id
            #_logger.info('Valor de inv_view %s'%inv_view)
            #_logger.info('Valor de inv_fview %s'%inv_fview)

            return {
                'name': 'Facturas de la actividad',
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'account.invoice',
                'views': [(inv_view, 'tree'),(inv_fview,'form')],
                # 'domain': [('date_order','>=',my_date)],
                'domain': [('id','in', idf_ids)],
                # 'context': "{}",
                'target': 'current',
            }

        


class EventSingleInvoiceWizard(models.TransientModel):
    _name = 'event.registration.singleinvoice_wizard'
    _description = 'Create single invoice for events'

    cliente = fields.Many2one('res.partner', 'Cliente')
    importe = fields.Selection(selection=REGISTRATION_STATES, string="Importe a facturar")
    event_id = fields.Many2one('event.event')
    reserva_id = fields.Many2one('event.reserva',string='Anticipo a facturar')
    suplido_id = fields.Many2one('event.suplidos.registro',string='Suplido a facturar')


    # al cambiar el concepto de importe si es de tipo fraccionado actualizar en el context el event_id
    @api.onchange('importe')
    def set_event_context(self):
        if self.importe == 'fraccion' or self.importe =='suplido':
            # _logger.info('Cambio en importe %s'%self.importe)
            regs_obj = self.env['event.registration']
            active_ids = self.env.context['active_ids'] or []
            all_regs = regs_obj.browse(active_ids)

            ids=[]
            event = 0
            for reg in all_regs:
                if event != reg.event_id.id:
                    # _logger.info('Registrado evento en ids %s'%reg.event_id.id)
                    ids.append(reg.event_id.id)
                    event = reg.event_id.id

            # _logger.info('Ingreso en context para event_id %s'%ids[0])
            # return {'context': {'event_id': ids[0]}}
            self.event_id = ids[0]



    
    @api.multi
    def do_create_invoice(self):
        self.ensure_one()
        if not (self.cliente):
            raise exceptions.ValidationError('Debe seleccionar un cliente a facturar')

        if not (self.importe):
            raise exceptions.ValidationError('Debe seleccionar un importe a facturar')

        
        regs_obj = self.env['event.registration']
        active_ids = self.env.context['active_ids'] or []
        all_regs = regs_obj.browse(active_ids)

        # Validación de que solo se factura un evento.
        evento_correcto = False
        reg_eventos = iter(all_regs)
        try:
            primer_reg = next(reg_eventos)
        except StopIteration:
            evento_correcto = True

        if not evento_correcto:
            evento_correcto = all(primer_reg.event_id == resto.event_id for resto in reg_eventos)
        
        if not evento_correcto:
            raise exceptions.ValidationError('Debe seleccionar una sola actividad')


        # Validacion de que todas las inscripciones estan en el mismo estado de facturacion
        estado_ins = all_regs[0].estado
        cambios = regs_obj.search([('id','in',active_ids),('estado','!=',estado_ins)])
        if len(cambios)>0:
            raise exceptions.ValidationError('Las inscripciones deben estar todas en el mismo estado de facturación')

        # Validacion de que no hay inscripciones facturadas de forma individual
        # cambios = regs_obj.search([('id','in',active_ids),('fact_agrupada','=','indiv')])
        # if len(cambios)>0:
        #     raise exceptions.ValidationError('Algunas inscripciones se facturaron en parte individuales, no se pueden agrupar')
                

        invoice_obj = self.env['account.invoice']
        line_obj = self.env['account.invoice.line']

        cuenta_obj = self.env['account.account']
        evento_obj = self.env['event.event']
        cuenta_id = primer_reg.event_id.account_id.id
        if primer_reg.event_id.account_analytic_id:
            acc_analytic = primer_reg.event_id.account_analytic_id.id
        else:
            acc_analytic = None


        #comprobamos en factura final que no hay otras facturas en borrador del evento
        if self.importe == 'total':
            invoice_draft = invoice_obj.search([('state','=','draft'),('event_id','=',primer_reg.event_id.id)])
            if invoice_draft : 
                raise exceptions.ValidationError('Hay facturas en borrador de esta actividad. Valide antes esas facturas')



        #comprobamos que el cliente no sea un alumno que se factura al representante
        if self.cliente.factura_rpte:
            if self.cliente.representante:
                partner_id = self.cliente.representante.id
            else:
                partner_id = self.cliente.id
        else:
            partner_id = self.cliente.id

        if self.cliente.property_payment_term:
            payment_term_id = self.cliente.property_payment_term.id
        else:
            payment_term_id = None

        if self.cliente.customer_payment_mode:
            payment_mode = self.cliente.customer_payment_mode.id
        else:
            payment_mode = None

        #registramos el evento con el que se asocia la factura
        evento_id = primer_reg.event_id.id
        #registramos el origen de la factura
        if self.importe == 'inscripcion':
            causa_factura = 'inscripcion'
        elif self.importe == 'fraccion':
            causa_factura = 'fraccion'
        elif self.importe == 'suplido':
            causa_factura = 'suplido'
        else:
            causa_factura = 'total'

        # registramos si es de agencia de viajes
        if primer_reg.event_id.reg_agencia:
            agencia = True
        else:
            agencia = False

        idf = invoice_obj.create({'partner_id' : partner_id,
                                  'account_id' : cuenta_id,
                                  'payment_term_id' : payment_term_id,
                                  'payment_mode' : payment_mode,
                                  'event_id' : evento_id,
                                  'causa_factura' : causa_factura,
                                  'is_agencia' : agencia,
        })
        fact = invoice_obj.browse(idf.id)
        if self.importe == 'fraccion' and self.reserva_id:
            fact.write ({'reserva_id' : self.reserva_id.id})

        if self.importe == 'suplido' and self.suplido_id:
            # _logger.info('Valor de suplido_id en self %s'%self.suplido_id)
            fact.write ({'suplido_id' : self.suplido_id.id})

        cont = 0
        precio_total = 0
        precio_facturar = 0
        formacion_total = 0

        #vamos a contar el numero de inscritos que se facturan
        num_inscritos = 0
        for reg in all_regs: 
            num_inscritos += 1

        # comprobamos en caso de factura de pago fraccionado que no este ya facturado en todos los registros
        nuevo_pago = 0
        if self.importe == 'fraccion':
            for reg in all_regs:
                for f in reg.factura:
                    if f.reserva_id.id != self.reserva_id.id:
                        nuevo_pago += 1
            if nuevo_pago == 0:
                raise exceptions.ValidationError('Este pago está facturado en todas las inscripciones seleccionadas')

        # comprobamos en caso de factura de suplido que no este ya facturado en todos los registros
        if self.importe == 'suplido':
            for reg in all_regs:
                # _logger.info('Valor en suplido para reg.factura %s'%reg.factura)
                if reg.factura:
                    fact_sup = False
                    for f in reg.factura:
                        f_fact = invoice_obj.search([
                            ('suplido_id','=',self.suplido_id.id),
                            ('id','=',f.id)
                            ])
                        if f_fact:
                            fact_sup = True
                            break
                    if fact_sup == False:
                        nuevo_pago+=1
                else:
                    nuevo_pago+=1
            if nuevo_pago == 0:
                raise exceptions.ValidationError('Este suplido está facturado en todas las inscripciones seleccionadas')


        for reg in all_regs:
            try:
                #import pudb; pudb.set_trace()
                facturar = True # Para evitar facturar 2 veces el mismo concepto.

                if self.importe == 'inscripcion' and reg.estado == 'pendiente':
                    precio_facturar = reg.pago_inscripcion_registro
                    reg.estado = 'inscripcion'
                    reg.fact_agrupada = 'group'
                elif self.importe == 'inscripcion' and not reg.estado == 'pendiente':
                    facturar = False

                if self.importe == 'fraccion' and self.event_id and not reg.estado == 'total':
                    # solo sumamos los no facturados
                    fr_fact = invoice_obj.search([
                        ('reserva_id','=',self.reserva_id.id)
                        ])
                    if fr_fact:
                        for fr in fr_fact:
                            if reg.factura:
                                for insc in reg.factura:
                                    if fr.id == insc.id:
                                        facturar = False
                                        break
                                    else:
                                        precio_facturar = float(self.reserva_id.importe_concepto - self.reserva_id.importe_impuesto)
                                        reg.estado = 'inscripcion'
                                        reg.fact_agrupada = 'group'
                                if facturar == False:
                                        break
                            else:
                                precio_facturar = float(self.reserva_id.importe_concepto - self.reserva_id.importe_impuesto)
                                reg.estado = 'inscripcion'
                                reg.fact_agrupada = 'group'
                    else:
                        precio_facturar = float(self.reserva_id.importe_concepto - self.reserva_id.importe_impuesto)
                        reg.estado = 'inscripcion'
                        reg.fact_agrupada = 'group'

                elif self.importe == 'fraccion' and reg.estado == 'total':
                    facturar = False

                if self.importe == 'suplido' and self.event_id and not reg.estado == 'total':
                    # solo sumamos los no facturados
                    fr_fact = invoice_obj.search([
                        ('suplido_id','=',self.suplido_id.id)
                        ])
                    if fr_fact:
                        for fr in fr_fact:
                            # _logger.info('Valor de fr_fact para reg %s'%fr)
                            if reg.factura:
                                for insc in reg.factura:
                                    # _logger.info('Valor de insc para reg %s'%insc)
                                    if fr.id == insc.id:
                                        # _logger.info('Break para reg %s'%insc)
                                        facturar = False
                                        break
                                    else:
                                        precio_facturar = float(self.suplido_id.importe_impuesto)
                                if facturar == False:
                                    break
                            else:
                                precio_facturar = float(self.suplido_id.importe_impuesto)
                    else:
                        precio_facturar = float(self.suplido_id.importe_impuesto)
                elif self.importe == 'suplido' and reg.estado == 'total':
                    facturar = False

                if self.importe == 'total' and not reg.estado == 'total':
                    precio_facturar = reg.pago_resto_registro
                    formacion_total += reg.event_id.total_formacion
                    causa_factura = 'total'
                    reg.estado = 'total'
                    reg.fact_agrupada = 'group'
                elif self.importe == 'total' and reg.estado == 'total':
                    facturar = False

               
                #_logger.info('Valor de facturar parar reg %s'%facturar)
                if facturar:
                    cont += 1
                    precio_total += precio_facturar
                    reg.factura = [(4, idf.id)]
                        

            except exceptions.MissingError:
                pass
                #raise exceptions.MissingError('Registro: %d' % regxs.id)
        fact = invoice_obj.browse(idf.id)

        

        if cont > 0 and precio_total > 0:
            cuenta_linea = fact.journal_id.default_credit_account_id.id
            #el concepto de la factura cambia en inscripciones
            if fact.causa_factura == 'inscripcion':
                if cont == 1:
                    if (primer_reg.alumno_en_factura):
                        nombre_alumno = str(primer_reg.nombre_alumno)+' '+str(primer_reg.apellido_alumno)
                        texto_linea = 'Adelanto por reserva formación %s para %s'% (str(primer_reg.event_id.name),nombre_alumno)
                    else:
                        texto_linea = 'Adelanto por reserva formación %s'% str(primer_reg.event_id.name)
                else:
                    texto_linea = 'Adelanto por reserva formación %s para %d alumnos'% (str(primer_reg.event_id.name), cont)
                idlinef = line_obj.create({'invoice_id' : idf.id,
                                       'name' : texto_linea,
                                       'price_unit' : precio_total,
                                       'account_id' : cuenta_linea,
                                       'account_analytic_id' : acc_analytic,
                                       'invoice_line_tax_id' : [[6, 0, primer_reg.event_id.tax_ids.ids]],
                })

            elif fact.causa_factura == 'fraccion':
                # if cont == 1:
                #     if (primer_reg.alumno_en_factura):
                #         nombre_alumno = str(primer_reg.nombre_alumno)+' '+str(primer_reg.apellido_alumno)
                #         texto_linea = '%s a cuenta formación %s para %s'%\
                #         (str(self.reserva_id.pago_name),str(primer_reg.event_id.name),nombre_alumno)
                #     else:
                #         texto_linea = '%s a cuenta formación %s'% (str(self.reserva_id.pago_name),str(primer_reg.event_id.name))
                # else:
                texto_linea = '%s a cuenta formación %s para %d alumnos'%\
                    (str(self.reserva_id.pago_name),str(self.event_id.name), cont)

                idlinef = line_obj.create({'invoice_id' : idf.id,
                                       'name' : texto_linea,
                                       'price_unit' : precio_total,
                                       'account_id' : cuenta_linea,
                                       'account_analytic_id' : acc_analytic,
                                       'invoice_line_tax_id' : [[6, 0, self.reserva_id.tax_ids.ids]],
                })
                # self.reserva_id.invoiced = True

            elif fact.causa_factura == 'suplido':
                # if cont == 1:
                #     if (primer_reg.alumno_en_factura):
                #         nombre_alumno = str(primer_reg.nombre_alumno)+' '+str(primer_reg.apellido_alumno)
                #         texto_linea = '%s a cuenta formación %s para %s'%\
                #         (str(self.reserva_id.pago_name),str(primer_reg.event_id.name),nombre_alumno)
                #     else:
                #         texto_linea = '%s a cuenta formación %s'% (str(self.reserva_id.pago_name),str(primer_reg.event_id.name))
                # else:
                texto_linea = 'Suplidos: %s para %d alumnos'%\
                    (str(self.suplido_id.suplido_id.name), cont)

                idlinef = line_obj.create({'invoice_id' : idf.id,
                                       'name' : texto_linea,
                                       'price_unit' : precio_total,
                                       'account_id' : cuenta_linea,
                                       'account_analytic_id' : acc_analytic,
                })

            else:
                # este caso ahora es más complejo, habrá una línea para la formación, otras para suplidos y puede haber otra para compensar la reserva
                # linea de formacion
                texto_linea = primer_reg.event_id.invoice_concept
                if (primer_reg.alumno_en_factura) and cont == 1:
                    nombre_alumno = str(primer_reg.nombre_alumno)+' '+str(primer_reg.apellido_alumno)
                    texto_linea = texto_linea +' para %s' %nombre_alumno
                else:
                    texto_linea = texto_linea +' para %s alumnos'%cont
                idlinef = line_obj.create({'invoice_id' : idf.id,
                                       'name' : texto_linea,
                                       'price_unit' : formacion_total,
                                       'account_id' : cuenta_linea,
                                       'account_analytic_id' : acc_analytic,
                                       'invoice_line_tax_id' : [[6, 0, primer_reg.event_id.tax_ids.ids]],
                })
                # otra linea para sumar los posibles recargos por inscripciones fuera de plazo
                fuera_plazo = 0
                num_recargos = 0
                for reg in all_regs:
                    if reg.extemporanea and reg.event_id.recargo_extemporaneo>0:
                        fuera_plazo += reg.event_id.recargo_extemporaneo
                        num_recargos += 1
                if fuera_plazo > 0:
                    idlinef = line_obj.create({'invoice_id' : idf.id,
                                       'name' : 'Recargo por %s inscripciones fuera de plazo'% str(num_recargos),
                                       'price_unit' : fuera_plazo,
                                       'account_id' : cuenta_linea,
                                       'account_analytic_id' : acc_analytic,
                                       'invoice_line_tax_id' : [[6, 0, primer_reg.event_id.tax_ids.ids]],
                    })

                # otra linea para sumar los posibles recargos de maletas facturadas
                factura_maleta = 0
                num_maletas = 0
                peso_maletas = 0
                for reg in all_regs:
                    if reg.cargo_maleta and reg.event_id.recargo_maleta>0:
                        if not reg.event_id.tax_maleta:
                            raise exceptions.MissingError('Falta el tipo de IVA para maletas en la actividad %d' % reg.event_id.name)
                        else:
                            tipo_iva = reg.event_id.tax_maleta.id
                        factura_maleta += reg.event_id.recargo_maleta
                        # num_maletas += 1
                        if reg.num_maletas > 0:
                            num_maletas += reg.num_maletas
                        if reg.peso_maletas > 0:
                            peso_maletas += reg.peso_maletas
                concepto_maletas =""
                if peso_maletas > 0:
                    concepto_maletas = 'Cargo por %s maletas facturadas con un peso total de %s kg.'%\
                                        (str(num_maletas),str(peso_maletas))
                else:
                    concepto_maletas ='Cargo por %s maletas facturadas'%str(num_maletas)

                if factura_maleta > 0:
                    idlinef = line_obj.create({'invoice_id' : idf.id,
                                       'name' : concepto_maletas,
                                       'price_unit' : factura_maleta,
                                       'account_id' : cuenta_linea,
                                       'account_analytic_id' : acc_analytic,
                                       'invoice_line_tax_id' : [[4, tipo_iva ]],
                    })

                # lineas de suplidos
                # modificado el 26/1 por reuníon con asesor para quitar el IVA de suplidos
                # modificado el 17/10 para no facturar los suplidos ya facturados (o no facturables)
                

                for sup in primer_reg.event_id.suplidos_event:
                    cont_sup = 0
                    sup_facturado = 0
                    # solo suplidos facturables no facturados ya
                    if sup.facturable:
                        for reg in all_regs:
                            ids=[]
                            if reg.factura:
                                for i in reg.factura:
                                    # _logger.info('Valores en reg.factura de invoice_id %s'%i)
                                    ids.append(i.id)
                                fr_fact = invoice_obj.search([
                                    ('suplido_id','=',sup.id),
                                    ('id','in',ids)
                                    ])
                                if fr_fact:
                                    for fr in fr_fact:
                                        sup_facturado += sup.importe_impuesto
                                else:
                                    cont_sup +=1
                            else:
                                cont_sup +=1
                            
                            # sup_facturado nos dice lo que se lleva facturado por el suplido
                            # usamos el numero de inscriciones seleccionadas para comparar
                            # el total facturable con el facturado

                        if sup_facturado < float(sup.importe_impuesto*num_inscritos):
                            total_suplido = float(sup.importe_impuesto*num_inscritos)- sup_facturado
                            
                            texto_linea = 'Suplidos: '+sup.suplido_id.name+ ' para %d alumnos'%cont_sup
                                
                            idlinef = line_obj.create({'invoice_id' : idf.id,
                                                       'name' : texto_linea,
                                                       'price_unit' : total_suplido,
                                                       'account_id' : cuenta_linea,
                                                       'account_analytic_id' : acc_analytic,
                                                       # 'invoice_line_tax_id' : [[6, 0, sup.tax_id.ids]],
                                    })


                # por ultimo restar las reservas facturadas, ojo quitar la que se esta creando ahora
                facturas_anticipos = invoice_obj.search([
                    ('event_id','=',primer_reg.event_id.id),
                    ('causa_factura','in',('inscripcion','fraccion')),
                    ('partner_id','=',partner_id),
                    ('state','in',('open','paid')),
                    ('ant_compensado','!=',True),
                    ('id','!=',idf.id)
                    ])
                for ant in facturas_anticipos:
                    #_logger.info('Valor de invoice ant %s'%ant.id)
                    # comprobamos que la factura este validada
                    if ant.state == 'draft':
                        raise exceptions.Warning("Antes de seguir debe revisar las facturas de anticipo no validadas")
                    if ant.state== 'cancel':
                        continue
                    for ant_lines in ant.invoice_line:
                        ant_tax_id = ant_lines.invoice_line_tax_id.ids

                    fecha_fac = str(ant.date_invoice)
                    dia_fact = fecha_fac[-2:]
                    mes_fact = fecha_fac[5:7]
                    ano_fac = fecha_fac[:4]
                    fecha_fac = dia_fact +'-'+mes_fact+'-'+ano_fac

                    texto_linea = '- Anticipo según factura '+ant.number+ ' de fecha '+ fecha_fac
                    idlinef = line_obj.create({'invoice_id' : idf.id,
                                       'name' : texto_linea,
                                       'quantity': -1,
                                       'price_unit' : ant.amount_untaxed,
                                       'account_id' : cuenta_linea,
                                       'account_analytic_id' : acc_analytic,
                                       'invoice_line_tax_id' : [[6, 0, ant_tax_id]],
                    })
                    ant.write({'ant_compensado': True})
           

            inv_view = self.env['ir.ui.view'].search([('name','=','account.invoice.form')])[0].id

            return {
                'type': 'ir.actions.act_window',
                'name': 'Facturas del cliente',
                'view_type': 'form',
                'view_mode': 'form',
                'view_id': inv_view,
                'res_model': 'account.invoice',
                #'context': "{}",
                'res_id': idf.id  or False,##provide the id of the record to be opened 
                #'domain': "[('id','in', ["+','.join(map(str,idf_ids))+"])]",
            }

        else:
            fact.unlink()
            raise exceptions.Warning("Nada que facturar")


# para creacion masiva de recibos de cobro

    class EventMultiVoucherWizard(models.TransientModel):
        _name = 'event.registration.multivoucher_wizard'
        _description = 'Create multiple vouchers for event registrations'

        importe = fields.Selection(selection=VOUCHER_STATES , string="Importe del recibo")
        journal_id = fields.Many2one ('account.journal','Forma de pago')

        #do_create_inovices genera una sola factura para cada inscripcion o alumno
        @api.multi
        def do_create_vouchers(self):
            self.ensure_one()

            if not (self.importe):
                raise exceptions.ValidationError('Debe registrar el importe de los recibos')

            if not (self.journal_id):
                raise exceptions.ValidationError('Debe registrar la forma de pago del recibo')
            
            regs_obj = self.env['event.registration']
            active_ids = self.env.context['active_ids'] or []
            all_regs = regs_obj.browse(active_ids)

            voucher_obj = self.env['account.voucher']
            # line_obj = self.env['account.invoice.line']

            # cuenta_obj = self.env['account.account']

            cont_facturado = 0 
            idf_ids=[]


            for reg in all_regs:   
                try:
                    #import pudb; pudb.set_trace()
                    # facturar = True # Para evitar facturar 2 veces el mismo concepto.
                    
                    # if self.importe == 'inscripcion' and reg.estado == 'pendiente' and reg.state == 'open':
                    if self.importe == 'inscripcion':
                        precio_facturar = reg.pago_inscripcion_registro
                        concepto = "Pago de reserva %s" %str(reg.event_id.name)

                    if self.importe == 'pendiente':
                        precio_facturar = reg.pago_resto_registro
                        concepto = "Pago de resto %s" %str(reg.event_id.name)

                    if self.importe == 'total':
                        precio_facturar = reg.event_id.precio_total_event
                        concepto = "Pago de actividad %s" %str(reg.event_id.name)
                    

                    if reg.alumno_en_factura:
                        nombre_alumno = str(reg.nombre_alumno)+' '+str(reg.apellido_alumno)
                        concepto = concepto + ' para %s' %nombre_alumno


                    #1-3-17 cambiamos este funcionamiento, factura a representante si existe valor
                    if reg.partner_id.representante:
                        partner_id = reg.partner_id.representante.id
                    else:
                        partner_id = reg.partner_id.id

                    #registramos el evento con el que se asocia el recibo
                    evento_id = reg.event_id.id
                    cia_id = reg.company_id.id

                    # evitamos crear recibos con importe cero
                    if precio_facturar ==0:
                        continue

                    idf = voucher_obj.create({'partner_id' : partner_id,
                                                  'amount' : precio_facturar,
                                                  'event_id' : evento_id,
                                                  'reference' : concepto,
                                                  'name' : concepto,
                                                  'journal_id' : self.journal_id.id,
                                                  'account_id': self.journal_id.default_credit_account_id.id,
                                                  'date': datetime.now().date(),
                                                  'company_id': cia_id,
                                                  'type':'receipt',
                        })

                    cont_facturado += 1
                    idf_ids.append(idf.id)

                except exceptions.MissingError:
                    pass
                    #raise exceptions.MissingError('Registro: %d' % regxs.id)
            if cont_facturado == 0:
                raise exceptions.Warning("Sin datos para recibos")
            else:
                #_logger.info('Valor de domain entre [] %s'%idf_ids)

                #puede ser este id el que nos de limitaciones a la hora de editar las facturas mostradas
                # inv_view = self.env['ir.ui.view'].search([('name','=','account.invoice.select')])[0].id
                inv_view = self.env['ir.ui.view'].search([('name','=','account.voucher.tree')])[0].id
                inv_fview = self.env['ir.ui.view'].search([('name','=','account.voucher.receipt.form')])[0].id
                #_logger.info('Valor de inv_view %s'%inv_view)
                #_logger.info('Valor de inv_fview %s'%inv_fview)

                return {
                    'name': 'Recibos de la actividad',
                    'type': 'ir.actions.act_window',
                    'view_type': 'form',
                    'view_mode': 'tree,form',
                    'res_model': 'account.voucher',
                    'views': [(inv_view, 'tree'),(inv_fview,'form')],
                    # 'domain': [('date_order','>=',my_date)],
                    'domain': [('id','in', idf_ids)],
                    # 'context': "{}",
                    'target': 'current',
                }

        


    '''
    ############################################
    Primer desarrollo:
     - Genera una linea por cada registro seleccionado.
     - Si tienen cuentas análiticas las incluye también en cada linea
    ############################################

    @api.multi
    def do_create_invoice(self):
        self.ensure_one()
        if not (self.cliente):
            raise exceptions.ValidationError('Debe seleccionar un cliente a facturar')

        if not (self.importe):
            raise exceptions.ValidationError('Debe seleccionar un importe a facturar')

        
        regs_obj = self.env['event.registration']
        active_ids = self.env.context['active_ids'] or []
        all_regs = regs_obj.browse(active_ids)

        # Validación de que solo se factura un evento.
        evento_correcto = False
        reg_eventos = iter(all_regs)
        try:
            primer_reg = next(reg_eventos)
        except StopIteration:
            evento_correcto = True

        if not evento_correcto:
            evento_correcto = all(primer_reg.event_id == resto.event_id for resto in reg_eventos)
        
        if not evento_correcto:
            raise exceptions.ValidationError('Debe seleccionar un único evento')
                

        invoice_obj = self.env['account.invoice']
        line_obj = self.env['account.invoice.line']

        cuenta_obj = self.env['account.account']
        cuenta_id = primer_reg.event_id.account_id.id
        partner_id = self.cliente.id
        idf = invoice_obj.create({'partner_id' : partner_id,
                                  'account_id' : cuenta_id,
        })

        cont = 0
        for reg in all_regs:
            try:
                #import pudb; pudb.set_trace()
                facturar = True # Para evitar facturar 2 veces el mismo concepto.

                if self.importe == 'inscripcion' and reg.estado == 'pendiente':
                    precio_facturar = reg.pago_inscripcion_registro
                    reg.estado = 'inscripcion'
                elif self.importe == 'inscripcion' and not reg.estado == 'pendiente':
                    facturar = False

                if self.importe == 'total' and not reg.estado == 'total':
                    precio_facturar = reg.pago_resto_registro
                    reg.estado = 'total'
                elif self.importe == 'total' and reg.estado == 'total':
                    facturar = False
                
                if facturar:
                    if reg.event_id.account_analytic_id.id:
                        cuenta_analitica_id = reg.event_id.account_analytic_id.id
                    else:
                        cuenta_analitica_id = None
                    
                    idlinef = line_obj.create({'invoice_id' : idf.id,
                                               'name' : "%s (Evento %s)" % (str(reg.partner_id.name),str(reg.event_id.name)),
                                               'price_unit' : precio_facturar,
                                               'invoice_line_tax_id' : [[6, 0, reg.event_id.tax_ids.ids]],
                                               'account_analytic_id' : cuenta_analitica_id,
                    })
                    cont += 1
                    reg.factura = [(4, idf.id)]
            except exceptions.MissingError:
                pass
                #raise exceptions.MissingError('Registro: %d' % regxs.id)

        # editar la factura.
        fact = invoice_obj.browse(idf.id)
        res = fact.write({'comment' : 'facturado "%s" para %d alumnos.' % (str(primer_reg.event_id.name), cont) })
    '''

#modificamos el name_get de res_partner para mostrar ciudad con contexto
class res_partner(models.Model):
    _inherit = ['res.partner']


    def name_get(self, cr, uid, ids, context=None):
        data = super(res_partner, self).name_get(cr, uid, ids, context=context)

        if context is None:
            context = {}
        if isinstance(ids, (int, long)):
            ids = [ids]
        res = []
        for record in self.browse(cr, uid, ids, context=context):
            name = record.name
            if record.parent_id and not record.is_company:
                name =  "%s, %s" % (record.parent_id.name, name)
            if context.get('show_address_only'):
                name = self._display_address(cr, uid, record, without_company=True, context=context)
            if context.get('show_address'):
                name = name + "\n" + self._display_address(cr, uid, record, without_company=True, context=context)
            name = name.replace('\n\n','\n')
            name = name.replace('\n\n','\n')
            if context.get('show_email') and record.email:
                name = "%s <%s>" % (name, record.email)
            if context.get('show_city') and record.city:
                name = "%s (%s)" % (record.name, record.city)
            res.append((record.id, name))
        return res


#ampliamos el move line para poder buscar por actividad (event_id)
class AccountMoveLine(models.Model):
    _inherit = ['account.move.line']


    event_id = fields.Many2one (string='Actividad',related='invoice.event_id')
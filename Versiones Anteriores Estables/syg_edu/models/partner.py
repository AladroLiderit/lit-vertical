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


from openerp import models, fields, api

from dateutil.relativedelta import *
from datetime import date

import logging
logger = logging.getLogger(__name__)

class res_partner(models.Model):
    _inherit = 'res.partner'

    comisiona = fields.Boolean(string='Es comisionista', default=False)
    birth_date = fields.Date('Fecha de nacimiento')
    edad = fields.Char('Edad', compute='_calcula_edad', readonly=True, store=True)
    estado_civil = fields.Selection(
        [('S', 'Soltero/a'), ('C', 'Casado/a'), ('D', 'Divorciado/a'),('V', 'Viudo/a')],"Estado civil")
    gender = fields.Selection(
        [('H', 'Hombre'), ('M', 'Mujer')], 'Gender')
    nationality = fields.Many2one('res.country', 'Nacionalidad')
    alumni_boolean = fields.Boolean('Es Alumno?')
    tutor_boolean = fields.Boolean('Es Tutor?')
    parent_ids = fields.Many2many(comodel_name='res.partner', relation='tutor_student_relation',column1= 'tutor_id', column2='student_id', string="Padres", domain=[('alumni_boolean','!=',True)])
    representante = fields.Many2one('res.partner','Representante')
    factura_rpte = fields.Boolean('Facturar al Representante')
    study_center = fields.Many2one('syg.colegio', 'Centro de estudios')
    de_cliente = fields.Many2one('res.partner', 'Cliente de', domain=[('comisiona','=',True)])
    vat_caduc = fields.Date('Caducidad DNI')
    passport_num = fields.Char('Pasaporte', size=25)
    pass_caduc = fields.Date('Caducidad Pasaporte')
    sms_phone = fields.Char('Tel. SMS', size=25)
    other_phone = fields.Char('Segundo Tel.', size=25)
    health_lines = fields.One2many('res.health', 'student_id', 'Notas de salud')
    camiseta = fields.Selection(
        [('S', 'S'), ('M', 'M'), ('L', 'L'), ('XL', 'XL'), ('XXL', 'XXL'), ('XXXL', 'XXXL')],"Talla de camiseta")
    nada = fields.Boolean('Sabe nadar?')
    vacunas = fields.Boolean('Vacunas al dia?')
    otras_obsv = fields.Text('Otras observaciones')
    #estadistica = fields.Char('Como conocio nuestra oferta?', size=250)
    estadistica = fields.Many2one ('syg.estadistica','Cómo nos conoció')
    emergency_contact = fields.Char('Nombre contacto',size=150)
    emergency_phone1 = fields.Char('Teléfono contacto',size=50)
    emergency_phone2 = fields.Char('Móvil contacto',size=50)
    emergency_email = fields.Char('Correo contacto',size=150)
    a_inscribir = fields.Many2one('event.event', 'A inscribirse en:')
    quiere_compartir = fields.Char('Quiere compartir con:', size=150)
    # agregamos un campo que nos cuenta si el partner tiene registros de salud o no
    lineas_salud = fields.Float('Registros de salud', compute='_calcula_salud', readonly=True, store=True)


    @api.one
    @api.depends('birth_date')
    def _calcula_edad(self):
        today = date.today()
        dob = fields.Date.from_string(self.birth_date)
        age = relativedelta(today, dob)
        edad = age.years
        self.edad = edad

    @api.one
    @api.depends('health_lines')
    def _calcula_salud(self):
        count = 0
        for hl in self.health_lines:
            count +=1
        self.lineas_salud = count

    @api.onchange('birth_date')
    def _on_change_birth_date(self):
        if self.birth_date:
            today = date.today()
            dob = fields.Date.from_string(self.birth_date)
            age = relativedelta(today, dob)
            edad = age.years
            self.edad = edad

    @api.onchange('de_cliente')
    def _on_change_de_cliente(self):
        if not self.alumni_boolean:
            self.alumni_boolean = True

    @api.onchange('study_center')
    def _on_change_study_center(self):
        if not self.alumni_boolean:
            self.alumni_boolean = True


    @api.model
    def _actualiza_edad(self):
        logger.info('Buscando edades para actualizar')
        today = date.today()
        

        #expire_limit_date = datetime.today() + \
        #    relativedelta(months=-NUMBER_OF_UNUSED_MONTHS_BEFORE_EXPIRY)
        #expire_limit_date_str = expire_limit_date.strftime('%Y-%m-%d')
        #expired_mandates = self.search(
        #    ['|',
        #     ('last_debit_date', '=', False),
        #     ('last_debit_date', '<=', expire_limit_date_str),
        #     ('state', '=', 'valid'),
        #     ('signature_date', '<=', expire_limit_date_str)])
        nueva_edad = self.search(
            ['|',
            ('birth_date', '!=', False),
            ('edad', '!=', 0)])
        #if expired_mandates:
        #    expired_mandates.write({'state': 'expired'})
        #    logger.info(
        #        'The following SDD Mandate IDs has been set to expired: %s'
        #        % expired_mandates.ids)
        #else:
        #    logger.info('0 SDD Mandates must be set to Expired')

        if nueva_edad:
            for ed in nueva_edad:
                dob = fields.Date.from_string(ed.birth_date)
                age = relativedelta(today, dob)
                edad = age.years
                if ed.edad <> edad:
                    ed.write({'edad':edad})

            #expired_mandates.write({'state': 'expired'})
                    logger.info(
                        'Actualizada la edad del partner con ID: %s'
                        % ed.id)
        else:
            logger.info('Ninguna edad para actualizar')

        return True


class res_health(models.Model):
    _name = 'res.health'

    tipo_nota = fields.Selection(
        [('T', 'Tratamiento'), ('A', 'Alergia'), ('D', 'Dieta'), ('P', 'Propenso a'), ('N', 'Nota')],"Tipo de nota")
    texto_nota = fields.Text('Comentario Salud')
    student_id = fields.Many2one('res.partner', 'Alumno')
    date = fields.Date('Fecha', default=lambda self: fields.Date.today())

class res_estadistica(models.Model):
    _name = 'syg.estadistica'

    name = fields.Char('Cómo nos conocen', size=150)


class res_company(models.Model):
    _inherit = 'res.company'

    representante = fields.Char('Representante legal',size = 150)
    texto_contratos = fields.Text('Texto para contratos')
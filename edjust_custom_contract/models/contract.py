# -*- coding: utf-8 -*-
from openerp import models, fields, api
from openerp.exceptions import except_orm, Warning, RedirectWarning
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp

from datetime import datetime, timedelta
import calendar

import logging
logger = logging.getLogger(__name__)


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    @api.depends ('recurring_invoice_line_ids')
    @api.multi
    def _medio_total(self):
        for contract in self:
            a_facturar = 0
            # logger.info('Valor de recurring lines [] %s'%contract.recurring_invoice_line_ids)
            for lines in contract.recurring_invoice_line_ids:
                a_facturar += lines.price_unit
                
            contract.total_toinvoice = a_facturar


    contact_partner_id = fields.Many2one(
        'res.partner',
        string=_('Deliver to'), required=True)
    medio_id = fields.Many2one (
        'edjust.sale.medio',string=_('publication to subscribe'),
        required=True)
    ed_inicial = fields.Many2one ('edjust.sale.edicion', string=_('Start Edition'), required=True)
    ed_final = fields.Many2one ('edjust.sale.edicion', string=_('End Edition'), required=True)
    gratuito = fields.Boolean (_('Free'), default=False)
    gratis_motiv = fields.Char (_('Free reason'), size=80)
    num_ejemplares = fields.Integer(
        string=_('Number of copies'), 
        help=_("Number of copies sent from eny edition"),
        default = 1)
    internal_description = fields.Text(_('Internal notes'))
    recurring_invoices = fields.Boolean (default=True)
    procedencia = fields.Many2one('edjust.procedencia.suscripcion',string=_('Class by provenance'))
    total_toinvoice = fields.Float(compute='_medio_total',string=_('Invoice Amount'),digits_compute=dp.get_precision('Account'), store=True)
    plazo_preaviso = fields.Integer(string=_("Preliminary notice period in days"), default=30)
    date_renove = fields.Date (string=_('Renewal notice'))
    causa_baja_ids = fields.One2many ('edjust.causa.baja','analytic_id',string=_("Contract terminations"))
    

    def _prepare_invoice_data(self, cr, uid, contract, context=None):
        context = context or {}
        invoice = super(AccountAnalyticAccount, self)._prepare_invoice_data(
            cr, uid, contract, context=context)
        invoice.update({
            'contact_partner_id': contract.contact_partner_id
            and contract.contact_partner_id.id})
        return invoice


    @api.onchange('partner_id')
    def onchange_partner_id(self):
        res={}
        if self.partner_id:
            partner = self.env['res.partner'].browse(self.partner_id.id)
            if partner.user_id:
                self.manager_id = partner.user_id.id
            if not self.name:
                self.name = 'Suscripción de '+ partner.name
            self.contact_partner_id = self.partner_id.id
            pricelist = partner.property_product_pricelist and partner.property_product_pricelist.id or False
            if pricelist:
                self.pricelist_id = pricelist
            else:
                self.pricelist_id = 1

            self.recurring_invoice_line_ids = False
            invoice_line_ids = []
            if self.medio_id and self.partner_id:
                pricelist = self.pricelist_id.id
                if pricelist:
                    price = self.env['product.pricelist'].price_get(
                            self.medio_id.product_id.id, 1,
                            self.partner_id.id, context={
                                'uom': self.medio_id.product_id.product_tmpl_id.uom_id.id,
                                'date': fields.datetime.now})[pricelist]
                else:
                    price = self.env['product.pricelist'].price_get(
                            self.medio_id.product_id.id, 1,
                            self.partner_id.id, context={
                                'uom': self.medio_id.product_id.product_tmpl_id.uom_id.id,
                                'date': fields.datetime.now})[1]

                values = {}
                values ['product_id'] = self.medio_id.product_id.id
                values ['uom_id'] = self.medio_id.product_id.product_tmpl_id.uom_id.id
                values ['name'] = self.medio_id.product_id.name + " desde el #START# al #END#"
                values ['quantity'] = 1
                if self.gratuito:
                    values ['price_unit'] = 0
                else:
                    if price:
                        values ['price_unit'] = price
                    else:
                        values ['price_unit'] = 1

                invoice_line_ids.append((0, 0,values))

            self.recurring_invoice_line_ids = invoice_line_ids

        # return {'value': res}

    @api.onchange('medio_id')
    def _onchange_medio_id(self):
        if not self.name and self.medio_id:
            self.name = 'Suscripción a '+ self.medio_id.name
        if self.medio_id.pub_interval:
            self.recurring_interval = self.medio_id.pub_interval
        if self.medio_id.pub_rule_type:
            self.recurring_rule_type = self.medio_id.pub_rule_type
        if self.date_start:
            self.date_start = False
        if self.date_renove:
            self.date_renove = False
        if self.ed_inicial:
            self.ed_inicial = False
        if self.ed_final:
            self.ed_final = False

        self.recurring_invoice_line_ids = False
        invoice_line_ids = []
        if self.medio_id:
            pricelist = self.pricelist_id.id
            if pricelist:
                if self.partner_id:
                    price = self.env['product.pricelist'].price_get(
                        self.medio_id.product_id.id, 1,
                        self.partner_id.id, context={
                            'uom': self.medio_id.product_id.product_tmpl_id.uom_id.id,
                            'date': fields.datetime.now})[pricelist]
                else:
                    price = 1

            else:
                if self.partner_id:
                    price = self.env['product.pricelist'].price_get(
                        self.medio_id.product_id.id, 1,
                        self.partner_id.id, context={
                            'uom': self.medio_id.product_id.product_tmpl_id.uom_id.id,
                            'date': fields.datetime.now})[1]
                else:
                    price = 1

            values = {}
            values ['product_id'] = self.medio_id.product_id.id
            values ['uom_id'] = self.medio_id.product_id.product_tmpl_id.uom_id.id
            values ['name'] = self.medio_id.product_id.name + " desde el #START# al #END#"
            values ['quantity'] = 1
            if self.gratuito:
                values ['price_unit'] = 0
            else:
                if price:
                    values ['price_unit'] = price
                else:
                    values ['price_unit'] = 1

            invoice_line_ids.append((0, 0,values))

        self.recurring_invoice_line_ids = invoice_line_ids

    @api.onchange('gratuito')
    def _onchange_gratuito(self):
        if self.medio_id and self.partner_id and self.recurring_invoice_line_ids:
            self.recurring_invoice_line_ids = False
            invoice_line_ids = []
           
            pricelist = self.pricelist_id.id
            if pricelist:
                price = self.env['product.pricelist'].price_get(
                        self.medio_id.product_id.id, 1,
                        self.partner_id.id, context={
                            'uom': self.medio_id.product_id.product_tmpl_id.uom_id.id,
                            'date': fields.datetime.now})[pricelist]
            else:
                price = self.env['product.pricelist'].price_get(
                        self.medio_id.product_id.id, 1,
                        self.partner_id.id, context={
                            'uom': self.medio_id.product_id.product_tmpl_id.uom_id.id,
                            'date': fields.datetime.now})[1]

            values = {}
            values ['product_id'] = self.medio_id.product_id.id
            values ['uom_id'] = self.medio_id.product_id.product_tmpl_id.uom_id.id
            values ['name'] = self.medio_id.product_id.name + " desde el #START# al #END#"
            values ['quantity'] = 1
            if self.gratuito:
                values ['price_unit'] = 0
            else:
                if price:
                    values ['price_unit'] = price
                else:
                    values ['price_unit'] = 1

            invoice_line_ids.append((0, 0,values))

            self.recurring_invoice_line_ids = invoice_line_ids


    @api.onchange('ed_inicial')
    def _onchange_ed_inicial(self):
        if self.ed_final and self.ed_final.year > self.ed_inicial.year:
            pass
        else:
            if self.ed_final and self.ed_final.year < self.ed_inicial.year:
                self.ed_final = False
            else:
                if self.ed_final and int(float(self.ed_final.mes_hasta)) < int(float(self.ed_inicial.mes_hasta)):
                    self.ed_final = False
        if self.ed_inicial:
            st_year = str(self.ed_inicial.year)
            st_month = str(self.ed_inicial.mes_desde)
            if len(st_month)==1:
                st_month='0'+st_month
            st_date = "01/"+st_month+"/"+st_year
            recurring_date = "30/"+st_month+"/"+st_year
            self.date_start = datetime.strptime(st_date,'%d/%m/%Y')
            self.recurring_next_date = datetime.strptime(recurring_date,'%d/%m/%Y')


    @api.onchange('ed_final')
    def _onchange_ed_final(self):
        if self.ed_inicial and self.ed_final.year < self.ed_inicial.year:           
            raise except_orm('Cambio edición final','La edición final no puede ser anterior a la inicial')

        else:
            if self.ed_inicial and self.ed_final.year > self.ed_inicial.year:
                pass
            else:
                if self.ed_inicial and int(float(self.ed_inicial.mes_hasta)) > int(float(self.ed_final.mes_hasta)):
                    # logger.info('Valor de ed_inicial.mes_hasta en onchange_ed_final %s'%int(float(self.ed_inicial.mes_hasta)))
                    # logger.info('Valor de ed_final.mes_desde en onchange_ed_final %s'%int(float(self.ed_final.mes_desde)))
                    raise except_orm('Cambio edición final','La edición final no puede ser anterior a la inicial')

        if self.ed_final:
            #get last day in month
            st_month = int(self.ed_final.mes_hasta)
            st_year = int(self.ed_final.year)
            num_days = calendar.monthrange(st_year, st_month)[1]
            num_days = str(num_days)
            st_year = str(st_year)
            st_month = str(st_month)
            st_date = num_days+"/"+st_month+"/"+st_year
            th_date = datetime.strptime(st_date,'%d/%m/%Y')
            if self.plazo_preaviso:
                th_plazo = self.plazo_preaviso
                if th_date - timedelta(days=self.plazo_preaviso)  < datetime.now()+ timedelta(days=2) :
                    self.ed_final = False
                    self.date_renove = False
                    self.plazo_preaviso = False
                    raise except_orm('Cambio plazo preaviso','El preaviso de fin de contrato es antes de 2 días')
            else:
                th_plazo = 0

            self.date_renove = th_date - timedelta(days=th_plazo) 


    @api.onchange('plazo_preaviso')
    def _onchange_plazo_preaviso(self):
        if self.date_renove and self.ed_final and self.plazo_preaviso:
            st_month = int(self.ed_final.mes_hasta)
            st_year = int(self.ed_final.year)
            num_days = calendar.monthrange(st_year, st_month)[1]
            num_days = str(num_days)
            st_year = str(st_year)
            st_month = str(st_month)
            st_date = num_days+"/"+st_month+"/"+st_year
            th_date = datetime.strptime(st_date,'%d/%m/%Y')

            if th_date - timedelta(days=self.plazo_preaviso)  < datetime.now()+ timedelta(days=30) :
                self.plazo_preaviso = False
                self.date_renove = False
                raise except_orm('Cambio edición final','El preaviso no puede ser inferior a 30 días')

            self.date_renove = th_date - timedelta(days=self.plazo_preaviso)


    @api.one
    def set_close(self):
        self.ensure_one
        self.write({'state':'close','date':datetime.now()})
        return True

    @api.one
    def set_cancel(self):
        self.ensure_one
        self.write({'state':'cancelled','date':datetime.now()})
        return True

    @api.one
    def set_open(self):
        self.ensure_one
        self.write({'state':'open','date':False})
        return True

   


class edjust_procedencia_suscricpion(models.Model):
    _name = 'edjust.procedencia.suscripcion'

    name = fields.Char(_('Origin of the contract'), size=100, required = True)


class edjust_causa_baja(models.Model):
    _name = 'edjust.causa.baja'

    name = fields.Text(_('Reason for contract withdrawal'), required = True)
    date = fields.Date (string=_('Final Day'), required = True, default=datetime.now())
    analytic_id = fields.Many2one('account.analytic.account',string=_("Contract"))


class ContractMultiRenoveWizard(models.TransientModel):
    _name = 'contract.renove.multi.wizard'
    _description = 'Renueva varios contratos a la vez'

    medio = fields.Many2one ('edjust.sale.medio',string=_('Publication to subscribe'))
    ed_final = fields.Many2one ('edjust.sale.edicion', string=_('Edition until which is renewed'))


    #do_renove_contract renueva los contratos seleccionados
    # de momento no se desarrolla hasta ver si es necesario
    @api.multi
    def do_renove_contract(self):
        self.ensure_one()

        return True




 

        



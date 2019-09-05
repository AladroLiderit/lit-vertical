# -*- encoding: utf-8 -*-
##############################################################################

from openerp import models, fields, api, exceptions, _
from openerp.osv import orm, osv
import openerp.addons.decimal_precision as dp
from itertools import permutations

import logging
logger = logging.getLogger(__name__)



class asincar_employee_contrato(models.Model):
    _name = 'asincar.employee.contrato'

    name = fields.Char('Tipo de contrato', size=80)

class res_users(models.Model):
    _inherit = "res.users"

    perfil_id = fields.Many2one ('asincar.employee.perfil', string = 'Perfil de empleado')
     


class hr_employee(models.Model):
    _inherit = "hr.employee"
    
    tipo_contrato = fields.Many2one ('asincar.employee.contrato', string = 'Tipo de contrato')
    fecha_alta = fields.Date('Fecha de Alta en empresa')
    coste = fields.Float(string='Coste por perfil',store=True,related='product_id.standard_price')
    perfil_id = fields.Many2one(related='user_id.perfil_id',store=True)
    actual_cost = fields.Float(string='Coste horario actual',related='product_id.product_tmpl_id.actual_cost',store=True)


    @api.onchange('perfil_id')
    def _onchange_perfil_id(self):
        if self.perfil_id and self.user_id:
            self.product_id = self.perfil_id.product_id
            self.user_id.perfil_id = self.perfil_id

        if not self.user_id:
            raise exceptions.Warning(
                _("Debe asociar un usuario de sistema al empleado !"))



class asincar_employee_category(models.Model):
    _name = 'asincar.employee.perfil'

    name = fields.Char('Perfil de empleado', size=80)
    product_id = fields.Many2one ('product.product', string = 'Concepto de coste',required=True)



class hr_hourly_cost(models.Model):
    _name = 'hr.hourly.cost'
    _description = 'Hourly cost'

    rate = fields.Float(string='Coste Hora', required=True)
    date_start = fields.Date(string='Desde', required=True)
    date_end = fields.Date(string='Hasta')
    product_tmpl_id = fields.Many2one('product.template',
                               string='Producto Asociado',
                               ondelete='cascade',
                               required=True)


class product_template(models.Model):
    _inherit = "product.template"

    is_employee_cost = fields.Boolean (string='Coste Laboral')
    hourly_cost_ids = fields.One2many ('hr.hourly.cost','product_tmpl_id', string = 'Histórico de Costes')
    actual_cost = fields.Float(string='Coste horario actual',compute='_act_hourly_cost',digits_compute=dp.get_precision('Account'))


    @api.model
    @api.constrains('hourly_cost_ids')
    def _check_overlapping_rates(self):
        """
        Si hay varios costes sin fecha de fin, avisar que se tiene que marcar fecha de fin
        """
        cost_lines = self.env['hr.hourly.cost']
        cost_lines_open = cost_lines.search(
            [('id','in',[x.id for x in self.hourly_cost_ids]),('date_end','=',False)]
            ,order='date_start asc')
        # logger.error('Comprobando costes horarios, valor de lineas abiertas %s'%cost_lines_open)
        if len(cost_lines_open)>1:
            raise exceptions.Warning(
                        _("Error! Tiene que registrar fecha de fin para líneas anteriores de coste"))


        """
        Checks if a class has two rates that overlap in time.
        """
        
        for prod in self:
            for r1, r2 in permutations(prod.hourly_cost_ids, 2):
                if r1.date_end and \
                   (r1.date_start <= r2.date_start <= r1.date_end):
                    raise exceptions.Warning(
                        _("Error! You cannot have overlapping rates"))
                elif not r1.date_end and (r1.date_start <= r2.date_start):
                    raise exceptions.Warning(
                        _("Error! You cannot have overlapping rates"))
        return True

    @api.depends('hourly_cost_ids')
    def _act_hourly_cost(self):
        for p in self:
            if p.hourly_cost_ids:
                for line in p.hourly_cost_ids:
                    # logger.error('Cambio en tipo coste, valor de date end %s'%line.date_end)
                    if line.date_end == False:
                        p.actual_cost = line.rate
            else:
                p.actual_cost = 0.0



class hr_analytic_timesheet(osv.osv):
    _inherit = "hr.analytic.timesheet"


    #modificar el calculo del precio si el user tiene un coste registrado

    def on_change_unit_amount(
            self, cr, uid, sheet_id, prod_id, unit_amount, company_id,
            unit=False, journal_id=False, task_id=False, to_invoice=False,
            project_id=False, context=None):

        emp_cost = False

        if prod_id:
            prod_obj = self.pool.get('product.product')
            prod_srch = prod_obj.search(cr,uid,[('id','=',prod_id)],limit=1,context=context)
            if prod_srch:
                th_prod = prod_obj.browse(cr,uid,prod_srch)
                if th_prod.product_tmpl_id.is_employee_cost:
                    emp_cost = th_prod.product_tmpl_id.actual_cost


        res = super(hr_analytic_timesheet, self).on_change_unit_amount(
            cr, uid, sheet_id, prod_id, unit_amount, company_id, unit,
            journal_id, context=context)

        
        if 'value' in res:
            if emp_cost:
                amount = emp_cost * unit_amount
                logger.error('En on change unit amount valor de amount que se pasa es %s'%amount)
                res['value']['amount'] = amount

        return res




class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"


    @api.one
    def button_act_cost(self):
        empl = self.env['hr.employee']
        acc = self.env['account.analytic.account']
        for line in self:
            # primero verificamos que el proyecto no este ya cerrado
            if line.account_id:
                if line.account_id.state in ('cancel','closed'):
                    continue
            if line.user_id:
                th_empl = empl.search([('user_id','=',line.user_id.id)])
                if th_empl and th_empl.actual_cost<>0:
                    line.amount = float(th_empl.actual_cost * line.unit_amount)

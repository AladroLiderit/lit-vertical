# -*- encoding: utf-8 -*-
##############################################################################

from openerp import models, fields, api
from openerp import tools
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
from datetime import datetime, timedelta
from openerp.exceptions import Warning

import logging
logger = logging.getLogger(__name__)


class asincar_project_lineas(models.Model):
    _name = 'asincar.project.lineas'

    name = fields.Char('Líneas de actividad', size=80)


class asincar_project_convocat(models.Model):
    _name = 'asincar.project.convocat'

    name = fields.Char('Convocatoria del proyecto', size=80)
    # year = fields.Char('Año de la convocatoria', size=20)


class account_analytic_account(models.Model):
    _inherit = 'account.analytic.account'


    user_id = fields.Many2one(required=True)
    department_id = fields.Many2one(required=True)


class project_project(models.Model):
    _inherit = "project.project"

    _order = "project_code asc"


    project_type = fields.Selection (
        [('interno','Interno'),('cliente','Para Cliente')],
        string='Tipo de proyecto', default='cliente')
    linea_trabajo = fields.Many2one('asincar.project.lineas',string="Línea de trabajo")
    project_convoc = fields.Many2one('asincar.project.convocat',string="Convocatoria", required=True)
    project_year = fields.Char('Año de la convocatoria', size=80, required=True)
    partner_ids = fields.Many2many(
        comodel_name='res.partner', 
        relation='project_partner_relation',
        column1= 'project_id', 
        column2='partner_id', 
        string="Clientes", 
        domain=[('customer','=',True)])
    project_code = fields.Char('Código de Proyecto', size=50)
    sequence_id = fields.Many2one('ir.sequence',string='Secuencia Proyectos',)
    planned_cost = fields.Float(
        compute='_planned_costs', 
        string='Coste de personal estimado',
        digits_compute=dp.get_precision('Account'),
        store=True, 
        default=False,
        )
    planned_income= fields.Float(string='Total ingresos estimados',compute='_planned_income',digits_compute=dp.get_precision('Account'))
    public_planned_income= fields.Float(string='Ingresos estimados por subvenciones',digits_compute=dp.get_precision('Account'))
    invoice_planned_income= fields.Float(string='Ingresos estimados por facturación',digits_compute=dp.get_precision('Account'))
    planned_product= fields.Float(string='Costes de material estimados',digits_compute=dp.get_precision('Account'))
    planned_waste= fields.Float(string='Otros costes estimados',digits_compute=dp.get_precision('Account'))
    planned_indirect= fields.Float(string='Costes indirectos repercutidos',digits_compute=dp.get_precision('Account'))
    planned_total_cost = fields.Float(
       compute='_planned_total_cost',
       string='Coste total estimado',
       digits_compute=dp.get_precision('Account'),
       store=True, 
       default=False,
       )
    planned_result = fields.Float(
       compute='_planned_result',
       string='Resultado estimado',
       digits_compute=dp.get_precision('Account'),
       store=True, 
       default=False,
       )


    @api.one
    @api.depends('task_ids', 'task_ids.planned_cost', 'task_ids.user_ids')
    def _planned_costs(self):
        # suma de los planned costs de las tareas
        coste_total = 0.0
        for task in self.task_ids:
            coste_total += task.planned_cost

        self.planned_cost = coste_total

    @api.one
    @api.depends('planned_cost', 'planned_product', 'planned_waste', 'planned_indirect')
    def _planned_total_cost(self):
        # suma de los planned costs parciales
        coste_total = 0.0
        coste_total = self.planned_cost + self.planned_product + self.planned_waste + self.planned_indirect

        self.planned_total_cost = coste_total


    @api.one
    @api.depends('planned_total_cost', 'planned_income')
    def _planned_result(self):

        self.planned_result = self.planned_income - self.planned_total_cost


    @api.one
    @api.depends( 'public_planned_income', 'invoice_planned_income')
    def _planned_income(self):

        self.planned_income = self.public_planned_income + self.invoice_planned_income


    @api.model
    def _get_next_ref(self, seq_id):
        valor_seq = self.env['ir.sequence'].next_by_id(seq_id)
        return valor_seq

    @api.model
    def create(self, vals):
        if vals.get('sequence_id'):
            vals['project_code'] = self._get_next_ref(vals.get('sequence_id'))

        return super(project_project, self).create(vals)

    @api.multi
    def write(self,vals):
        if not vals.get('project_code') and vals.get('sequence_id'):
            vals['project_code'] = self._get_next_ref(vals.get('sequence_id'))

        return super(project_project, self).write(vals)

    @api.onchange('sequence_id')
    def _onchange_sequence(self):
        if self.project_code:
            self.project_code = False


class project_task(models.Model):
    _inherit = "project.task"

    perfil_id = fields.Many2one ('asincar.employee.perfil', string = 'Perfil de empleado',required=False)
    date_start = fields.Datetime(required=True, default=datetime.now())
    date_end = fields.Datetime(required=True, string="Fecha final planificada", default=datetime.now()+timedelta(days=1))
    date_closed = fields.Datetime('Fecha de cierre', copy=False)
    planned_hours = fields.Float(required=True, default=0)
    planned_cost = fields.Float(
        compute='_planned_costs', 
        string='Coste planificado',
        digits_compute=dp.get_precision('Product Price'),
        store=True, 
        default=False,
        )
    user_ids = fields.Many2many (
        comodel_name='res.users', 
        relation='task_user_relation',
        column1= 'task_id', 
        column2='user_id', 
        string="Empleados", 
        )


    @api.onchange('project_id')
    def _onchange_project(self, project_id):
        lids=self.env['res.users'].search([('id','in',[x.id for x in self.project_id.members])])
        pids = []
        for l in lids:
            pids.append(l.id)
        if len (pids)>0:
            return {'domain':{'user_ids':[('id','in',pids)]}}
        else:
            return {'domain':{'user_ids':[('perfil_id','=',False)]}}
        return super(project_task, self)._onchange_project(project_id)

    @api.onchange('perfil_id')
    def _onchange_perfil_id(self):
        if self.project_id:
            lids=self.env['res.users'].search(['&',('perfil_id','=',self.perfil_id.id),('id','in',[x.id for x in self.project_id.members])])
        else:
            lids=self.env['res.users'].search([('perfil_id','=',self.perfil_id.id)])
        pids = []
        for l in lids:
            pids.append(l.id)
        if len (pids)>0:
            return {'domain':{'user_ids':[('id','in',pids)]}}
        else:
            return {'domain':{'user_ids':[('perfil_id','=',False)]}}

    # para calculo de costes planificados por tarea
    @api.one
    @api.depends('planned_hours', 'perfil_id')
    def _planned_costs(self):
         # se basa en el coste para el perfil del empleado por el número de horas de cada tarea
        coste_promedio = 0.0
        if self.perfil_id and self.perfil_id.product_id:
            coste_promedio = self.perfil_id.product_id.standard_price
    
        self.planned_cost = float(coste_promedio * self.planned_hours)


    @api.multi
    def write(self, vals):
        if vals.get('stage_id'):
            th_stage = self.env['project.task.type'].search([('id','=',vals.get('stage_id'))])
            # logger.error('Cambio en task stage, nuevo valor %s'%th_stage[0].name)
            if th_stage[0].closed:
                vals['date_closed'] = datetime.now()
            else:
                vals['date_closed'] = False
        return super(project_task, self).write(vals)

    # para registrar estado finalizado si se rellena la fecha de cierre de una tarea
    @api.onchange('date_closed')
    def _onchange_date_closed(self):      
        if self.date_closed and self.stage_id.closed == False :
            th_stage = self.env['project.task.type'].search([('closed','=',True)])
            self.stage_id = th_stage[0]


#creamos clase para tener en una vista los datos de las tareas por usuario
class task_by_users_id(models.Model):
    _name = "task.by.users.id"
    #auto False para que no genere una tabla, porque es una vista
    _auto = False

    tarea = fields.Char(string="Tarea")
    limite = fields.Date(string="Fecha límite")
    empleado = fields.Char(string="Empleado")
    proyecto = fields.Char(string="Proyecto")
    planificado = fields.Float(string="Planificado")
    ejecutado = fields.Float(string="Ejecutado")
    pendiente = fields.Float(string="Pendiente")
    departamento = fields.Char(string="Departamento")
    estado = fields.Char(string="Estado")
    finalizada = fields.Boolean('Finalizada')




    def init(self, cr):
        tools.sql.drop_view_if_exists(cr, 'task_by_users_id')
        cr.execute("""
            CREATE OR REPLACE VIEW task_by_users_id AS (
select 
(users.id *1000000)+ task.id as id,
task.name as tarea,
task.date_deadline as limite,
partner.name as empleado, 
anal.name as proyecto, 
task.total_hours as planificado, 
task.effective_hours as ejecutado,
task.remaining_hours as pendiente, 
dep.name as departamento,
ttype.name as estado, 
ttype.closed as finalizada
from project_task task
join task_user_relation rel
on task.id = rel.task_id
join res_users users
on users.id = rel.user_id
join res_partner partner
on partner.id = users.partner_id
join project_task_type ttype on
ttype.id = task.stage_id
join project_project project
on project.id = task.project_id
join account_analytic_account anal
on anal.id = project.analytic_account_id
join hr_department dep
on dep.id = task.project_department_id
)
        """)


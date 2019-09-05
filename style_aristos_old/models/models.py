
from openerp import models, fields, api, exceptions, _
## import csv
## import glob, os
#from openerp.osv import osv
## from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
## from datetime import datetime, date, time, timedelta
##  from openerp import request
from openerp.exceptions import Warning
import logging
_logger = logging.getLogger(__name__)



class SaleCommission(models.Model):
    _name = "sale.commission"
    _inherit = "sale.commission"
    
    invoice_state = fields.Selection(
        selection_add=[('venc', 'Basado en Pagos Parciales  factura')])


class Settlement(models.Model):
    _name = "sale.commission.settlement"
    _inherit = "sale.commission.settlement"

    total_due = fields.Float(compute="_compute_total_due", readonly=True, store=True)

    @api.depends('lines', 'lines.settled_amount')
    def _compute_total_due(self):
        for record in self:
            record.total_due = sum(x.amount for x in record.lines)
    @api.multi
    def unlink(self):
        for l in self:
            for line in self.lines:
                #_logger.error('######## AIKO borrando desde cabecera1  ####### ->\n'+  str(self) +  '\n') 
                if line.invoice_line_vencimiento.state  in ('invoice', 'except_invoice'):
                    raise Warning(_('You cannot delete an invoice which is not invoice or except invoice.'))
                if line.invoice_line_vencimiento:
                    agent_line_vencimiento_obj = self.env['account.invoice.line.agent.vencimiento']   
                    agent_line_vencimiento_obj.unlink([line.invoice_line_vencimiento.id]) 
                    #_logger.error('######## AIKO borrando desde cabecera2  ####### ->\n'+  str(self) +  '\n')
        return models.Model.unlink(self) 





class sale_commission_settlement_line(models.Model):
    _name = "sale.commission.settlement.line"
    _inherit = "sale.commission.settlement.line"
    invoice_line_vencimiento = fields.Many2one(comodel_name='account.invoice.line.agent.vencimiento', 
                                               readonly=True, string="Payment Due")

    porcent = fields.Float(string='Porcent about total invoice',
                           compute="_compute_porcen", readonly=True, store=True,
                           help="Represents the payment percentage over the total invoice amount.")
    
    amount = fields.Float(string="Amount settled",
                          compute="_compute_amount", readonly=True, store=True)
    
    
    paid_date = fields.Date(string='date of paid',
                           compute="_compute_date", readonly=True, store=True)

    
    @api.depends('invoice_line_vencimiento.porcent')
    def _compute_date(self):
        for d in self:
            d.paid_date = d.invoice_line_vencimiento.paid_date
   
    @api.depends('invoice_line_vencimiento.porcent')
    def _compute_porcen(self):
        for r in self:
            r.porcent = r.invoice_line_vencimiento.porcent
                       
    @api.depends('invoice_line_vencimiento.amount')
    def _compute_amount(self):
        for i in self:  
            i.amount = i.invoice_line_vencimiento.amount     
    

#     @api.multi
#     def unlink(self):
#         for line in self:
#             _logger.error('######## AIKO borrando 1  ####### ->\n'+  str(self) +  '\n') 
#             if line.invoice_line_vencimiento.state  in ('invoice', 'except_invoice'):
#                 raise Warning(_('You cannot delete an invoice which is not invoice or except invoice.'))
#             if line.invoice_line_vencimiento:
#                 agent_line_vencimiento_obj = self.env['account.invoice.line.agent.vencimiento']   
#                 agent_line_vencimiento_obj.unlink([line.invoice_line_vencimiento.id]) 
#                 _logger.error('######## AIKO borrando 2  ####### ->\n'+  str(self) +  '\n')
#         return models.Model.unlink(self) 


class account_invoice_line_agent(models.Model):
    _name = 'account.invoice.line.agent'
    _inherit = 'account.invoice.line.agent' 
    vencimientos_ids = fields.One2many('account.invoice.line.agent.vencimiento', 'vencimiento_id', string='Expiration') 
class account_invoice_line_agent_vencimiento(models.Model):
    _name = "account.invoice.line.agent.vencimiento"
    _rec_name = 'payment_id'
    vencimiento_id = fields.Many2one('account.invoice.line.agent', readonly=True, 
                                     ondelete='cascade', required=True,  string="Paids")
    payment_id = fields.Many2one('account.move.line', readonly=True,  string="Account Moviment")
    settled_commission =fields.Boolean('Commission Settled', default=False) 
    porcent = fields.Float(string='Porcent about total invoice',
                           compute="_compute_porcen", readonly=True, store=True,
                           help="Represents the payment percentage over the total invoice amount.")
    
    amount = fields.Float(string="Amount settled",
                          compute="_compute_amount", readonly=True, store=True)
    state = fields.Selection(
        selection=[("settled", "Settled"),
                   ("invoiced", "Invoiced"),
                   ("cancel", "Canceled"),
                   ("except_invoice", "Invoice exception")], string="State",
        readonly=True, default="settled")
    
    paid_date = fields.Date(string='date of paid',
                           compute="_compute_date", readonly=True, store=True)

    
    @api.depends('payment_id.date')
    def _compute_date(self):
        for d in self:
            d.paid_date = d.payment_id.date
    
    @api.depends('payment_id.credit', 'vencimiento_id.invoice.amount_total')
    def _compute_porcen(self):
        for r in self:
            r.porcent = float((r.payment_id.credit * 100.0) / r.vencimiento_id.invoice.amount_total)
    @api.depends('porcent', 'vencimiento_id.amount')
    def _compute_amount(self):
        for i in self:
            if i.porcent > 0:
                i.amount = float(i.porcent * i.vencimiento_id.amount / 100.0)     
            

#     @api.multi
#     def _amount_final_price_template(self):        
#         for p in self:            
#             p.precio_masbajo = p.standard_price
#            
#             if p.supplier_ids:
#                 p_calculado = 99999999
#                 control_p = False                   
#                 for sup in p.supplier_ids:                    
#                     for lista in sup.pricelist_ids:
#                         control_p = True
#                         if lista.price < p_calculado:
#                             p_calculado = lista.price   
#                 if control_p:
#                     p.precio_masbajo = p_calculado          
#                                            
#     precio_masbajo = fields.Float(string='Lowest price',help="The lowest price found in the supplier price list.", compute='_amount_final_price_template')
#     _defaults = {
#     'type' : 'product',
#     }     
#     
# # class pricelist_partnerinfo(models.Model):
# #     _name = 'pricelist.partnerinfo'
# #     _inherit = 'pricelist.partnerinfo' 
# #     
# #     def tr_get_default_currency_id(self):
# #         return self.env.user.company_id.currency_id     
# #     @api.one
# #     @api.depends('price', 'discount','currency_id')  
# #     def _amount_final_price_catalog(self):
# #         for p in self:            
# #             p.final_price = p.price * (1 - (p.discount or 0.0) / 100.0)                
# #             if not p.currency_id:
# #                 p.currency_id = 1
# # 
# #             p.final_price = p.currency_id.compute(p.final_price, p.company_id.currency_id, round=False)
# # #     
# #     currency_id = fields.Many2one('res.currency', string='Currency', default=tr_get_default_currency_id)
# #     final_price = fields.Float(string='Catalogue Price',help="Price resulting from the initial catalogue price for the discount and by currency..", compute='_amount_final_price_catalog')
#     
# class ProjectProject(models.Model):
#     _inherit = "project.project"          
#     desplazamiento_hours = fields.Float('Travelling hours', copy=True)
#     kilometros = fields.Float('Kilometres of distance', copy=True)
#     project_type_id = fields.Many2one('ic.project_type', string="Type of Proyect",copy=True)
#      
# class ic_project_type(models.Model):
#     _name = 'ic.project_type'
#     _rec_name = 'name'
#     name= fields.Char(string = 'Project type', required=True)    
#     _sql_constraints = [('name_uniq', 'unique (name)', " Name of type project already exists !")]     
#      
# class ic_hr_employee(models.Model):
#     _name = 'hr.employee'
#     _inherit = 'hr.employee'
# 
#     product_extras_id = fields.Many2one('product.product', string="Extra Hours") 
#     product_nocturnas_id = fields.Many2one('product.product', string="Night Hours") 
#     product_sabados_id = fields.Many2one('product.product', string="Hours Saturday") 
#     product_domifestivos_id = fields.Many2one('product.product', string="Hours Sundays and Holidays") 
#     
# class ic_hr_analytic_timesheet(models.Model):
#     _name = 'hr.analytic.timesheet'
#     _inherit = 'hr.analytic.timesheet'
#     tipo_hora = fields.Selection([        
#             ("Normal", "Normal Hours"),
#             ("Extra", "Extra Hours"),
#             ("Nocturna", "Night Hours"),
#             ("Sabados", "Hours Saturday"),
#             ("Festivos", "Hours Sundays and Holidays")            
#         ], "Type of hours", default = 'Normal') 
# 
#     @api.onchange('tipo_hora')
#     def on_change_tipo_hora (self):
# #         emp_obj = self.env['hr.employee'].search([('user_id', '=', self.user_id.id)], limit=1)
# #         for t in self.env['hr.employee'].browse(emp_obj):  
#         
#         e = self.env['hr.employee'].search([('user_id', '=', self.user_id.id)], limit=1)              
#         if e: 
#             if self.tipo_hora == 'Normal':
#                 self.prod_id = e.product_id.id
#             elif self.tipo_hora == 'Extra':     
#                 self.prod_id = e.product_extras_id.id
#             elif self.tipo_hora == 'Nocturna':
#                 self.prod_id = e.product_nocturnas_id.id
#             elif self.tipo_hora == 'Sabados':
#                 self.prod_id = e.product_sabados_id.id
#             elif self.tipo_hora == 'Festivos':
#                 self.prod_id = e.product_domifestivos_id.id  
#             else:
#                 self.prod_id = e.product_id.id   
    
##    @api.depends('tipo_hora', 'user_id') 
#     @api.model
#     def _getEmployeeProduct(self):
#         if not self.user_id:
# ##            self.user_id = self._context.get('user_id')
# ##            self.user_id = self.env.context.get('user_id')
# ##            self.user_id = self._uid
# ##            self.user_id = context.get('user_id')
#             self.user_id = 9              
#         e = self.env['hr.employee'].search([('user_id', '=', self.user_id.id)], limit=1)  
#         _logger.error('## AIKO getemployeeproduct  ## ->\n'+  str(self.user_id) + str(self.tipo_hora) +'\n')            
#         if e:           
#             if self.tipo_hora == 'Normal':
#                 return e.product_id.id
#             elif self.tipo_hora == 'Extra':
#                 return e.product_extras_id.id
#             elif self.tipo_hora == 'Nocturna':
#                 return e.product_nocturnas_id.id
#             elif self.tipo_hora == 'Sabados':
#                 return e.product_sabados_id.id
#             elif self.tipo_hora == 'Festivos':
#                 return e.product_domifestivos_id.id       
#             else:
#                 return e.product_id.id
#         _logger.error('## AIKO 142 ## ->\n'+  str(e) + '\n')                     
#         return False      
         
#     def on_change_user_id(self, cr, uid, ids, user_id):        
#         if not user_id:
#             return {}
#         context = {'user_id': user_id}
#         _logger.error('## AIKO  on_change  ## ->\n'+  str(user_id) + '\n') 
#         return {'value': {
#             'product_id': self._getEmployeeProduct(cr, uid, context),
#             'product_uom_id': self._getEmployeeUnit(cr, uid, context),
#             'general_account_id': self._getGeneralAccount(cr, uid, context),
#             'journal_id': self._getAnalyticJournal(cr, uid, context),
#         }}       
#     def on_change_unit_amount(self, cr, uid, id, prod_id, unit_amount, company_id, unit=False, journal_id=False, context=None):
#         _logger.error('## AIKO 95 ## ->\n'+  str(prod_id) + '\n') 

#         res = {'value':{}}
#         if prod_id and unit_amount:
#             # find company
#             company_id = self.pool.get('res.company')._company_default_get(cr, uid, 'account.analytic.line', context=context)
#             r = self.pool.get('account.analytic.line').on_change_unit_amount(cr, uid, id, prod_id, unit_amount, company_id, unit, journal_id, context=context)
#             if r:
#                 res.update(r)
#         # update unit of measurement
#         if prod_id:
#             uom = self.pool.get('product.product').browse(cr, uid, prod_id, context=context)
#             if uom.uom_id:
#                 res['value'].update({'product_uom_id': uom.uom_id.id})
#         else:
#             res['value'].update({'product_uom_id': False})
#         return res 
class st_parameters(models.Model):
    _name = 'st.parameters'

    company_id = fields.Many2one('res.company', string="Company")       
    par_name = fields.Char(string = 'Paramener Name', required=True, size = 4)
    stock_tolerancia = fields.Integer('stock tolerance', default=1, store = True)
    
class product_template(models.Model):
    _name = "product.template"
    _inherit = 'product.template'
    type_of_material_id = fields.Many2one('st.type_material', string="Type of Material", copy=True)
    # stock_tolerancia_count = fields.Integer(compute="_stock_tolerancia", string='stock tolerance')
    collection_id = fields.Many2one('st.collection', string="Collection", copy=True)
    short_name = fields.Char(string ='short name', size = 40)
    abv_name = fields.Char(string ='abbreviated name', size = 20)
    gender = fields.Selection([('C', _('Gentleman')),('S', _('Lady')),('A', _('Both'))])
    muestrario = fields.Boolean(string='Muestrario')
    novedad = fields.Boolean(string='Novedad')
    outlet = fields.Boolean(string='Outlet')
    shaka = fields.Boolean(string='Shaka')

   
    # def _stock_tolerancia(self):
        # self.stock_tolerancia_count = 0
        # st  = self.env['st.parameters'].search([('company_id', '=', self.company_id.id),('par_name', '=', 'pa00')])
        # if not st: 
        #     return
        # self.stock_tolerancia_count = (self.qty_available - st.stock_tolerancia)

class product_product(models.Model):
    _inherit = 'product.product' 

    @api.multi
    def _stock_tolerancia(self):
        # self.stock_tolerancia = True
        st  = self.env['st.parameters'].search([('company_id', '=', self.company_id.id),('par_name', '=', 'pa00')])
        # _logger.error('######## AIKO stock_tolerancia el st nos da  %s ####### ->'%st)
        for p in self:
            if not st: 
                # _logger.error('######## AIKO stock_tolerancia no hay st, cambia a False ####### ->')
                # return
                p.stock_tolerancia_count = p.qty_available
            else:
                p.stock_tolerancia_count = (p.qty_available - st.stock_tolerancia)


    # stock_tolerancia = fields.Boolean(string='stock tolerance',compute="_stock_tolerancia")
    stock_tolerancia_count = fields.Integer(compute="_stock_tolerancia", string='stock tolerance')


    
class st_type_material(models.Model):
    _name = 'st.type_material'
    _rec_name = 'descripcion'
    descripcion = fields.Char(string ='Type of material', required=True)  
    _sql_constraints = [('name_uniq', 'unique (descripcion)', " Type of material already exists !")]
    
class st_collection(models.Model):
    _name = 'st.collection'
    _rec_name = 'descripcion'
    descripcion = fields.Char(string ='Type of material', required=True)  
    _sql_constraints = [('name_uniq', 'unique (descripcion)', " Name of collection already exists !")]    
    

class st_line_type(models.Model):
    _name = 'st.line.type'

    name = fields.Char(string ='Type of sale order line') 
    descripcion = fields.Char(string='Letter for resume')


class res_partner(models.Model):
    _inherit = 'res.partner'

    no_visible_aristos= fields.Boolean(string='No visibles en web')
    distr_shaka= fields.Boolean(string='Distribuidor Shaka')
    portes = fields.Selection([('P',_('Paid')),('D',_('Debited'))])

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    type_line = fields.Selection(
        selection=[("E", "Delivered"),
                   ("A", "Returns"),
                   ("C", "Change"),
                   ("S", "No Charge")], string="Type of Mov.",
                   )

    line_type = fields.Many2many(comodel_name='st.line.type',relation='order_line_type_rel',string="Entrega")

    @api.onchange('line_type')
    def _onchange_line_type(self):
        
        if self.product_uom_qty < 0:
                self.product_uom_qty = self.product_uom_qty * -1  
        if self.discount == 100.0:
            self.discount = 0.0
        cambio = False
        sincargo = False        
        
        for record in self.line_type:
  
            if record.descripcion == 'E':       
                wh = self.env['stock.warehouse'].search([('partner_id', '=', self.env.user.partner_id.id)], limit=1)               
                if wh: 
                    self.warehouse_id = wh.id
            if record.descripcion == 'A':
                if self.product_uom_qty > 0:
                    self.product_uom_qty = self.product_uom_qty * -1 
            if record.descripcion == 'C':
                cambio = True
            if record.descripcion == 'S/C':
                sincargo = True 
                                   
        if cambio and sincargo:
            self.discount = 100.0
    # aviso a comerciales para entregar la unidad del muestrario
    @api.multi
    def product_id_change(self, pricelist, product, qty=0,
                          uom=False, qty_uos=0, uos=False, name='',
                          partner_id=False, lang=False, update_tax=True,
                          date_order=False, packaging=False,
                          fiscal_position=False, flag=False):     

        res = super(SaleOrderLine, self).product_id_change(
            pricelist, product, qty=qty, uom=uom, qty_uos=qty_uos, uos=uos,
            name=name, partner_id=partner_id, lang=lang, update_tax=update_tax,
            date_order=date_order, packaging=packaging,
            fiscal_position=fiscal_position, flag=flag)

        if product and str(product).isdigit():
            # _logger.error('######## AIKO product_id_change valor de product es  %s'%product)

            th_product = self.env['product.product'].browse(product)
            # _logger.error('######## AIKO sale order line el st tolerance nos da  %s ####### ->'
            #    %th_product.stock_tolerancia_count)
            if th_product.qty_available > 0 and th_product.stock_tolerancia_count < 1:
                return {'value': res,'warning': {'title':"Stock", 'message':"Stock agotado. Entregue su muestra de %s"
                %th_product.default_code}}
                # raise Warning(_('Stock limit. Deliver your sample of %s') %
                #                       th_product.default_code)
            else:
                return res
        else:
            return res
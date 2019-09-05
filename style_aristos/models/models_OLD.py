
from openerp import models, fields, api, exceptions, _
from openerp.osv import osv
## import csv
## import glob, os
#from openerp.osv import osv
## from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
## from datetime import datetime, date, time, timedelta
##  from openerp import request
import openerp.addons.decimal_precision as dp
from dateutil.relativedelta import relativedelta
from openerp.exceptions import Warning
import logging
_logger = logging.getLogger(__name__)



class SaleCommission(models.Model):
    _name = "sale.commission"
    _inherit = "sale.commission"
    
    invoice_state = fields.Selection(
        selection_add=[('venc', 'Basado en Pagos Parciales  factura')])
    type_in_product = fields.Selection([('default','By default'),('promotion','In promotions'),('no','No commission')])


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







# ESTO COMENTADO EN CODIGO CHEMA    

##     @api.multi
##     def unlink(self):
##         for line in self:
##             _logger.error('######## AIKO borrando 1  ####### ->\n'+  str(self) +  '\n') 
##             if line.invoice_line_vencimiento.state  in ('invoice', 'except_invoice'):
##                 raise Warning(_('You cannot delete an invoice which is not invoice or except invoice.'))
##             if line.invoice_line_vencimiento:
##                 agent_line_vencimiento_obj = self.env['account.invoice.line.agent.vencimiento']   
##                 agent_line_vencimiento_obj.unlink([line.invoice_line_vencimiento.id]) 
##                 _logger.error('######## AIKO borrando 2  ####### ->\n'+  str(self) +  '\n')
##         return models.Model.unlink(self) 








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
            








# ESTO COMENTADO EN CODIGO CHEMA 

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
           
   
# FIN CODIGO COMMISSIONS


class st_parameters(models.Model):
    _name = 'st.parameters'

    company_id = fields.Many2one('res.company', string="Company")       
    par_name = fields.Char(string = 'Paramener Name', required=True, size = 4)
    stock_tolerancia = fields.Integer('stock tolerance', default=1, store = True)

class product_attribute_value(models.Model):
    # heredo para ordenar por nombre primero que por secuencia (por defecto)
    _inherit = 'product.attribute.value'
    _order = 'name, sequence'

    comment = fields.Char('Value descripction')
    

class product_template(models.Model):
    _name = "product.template"
    _inherit = 'product.template'


    @api.one
    @api.depends('attribute_line_ids','attribute_line_ids.value_ids')
    def _get_eti_colores(self):
        for p in self:
            if p.attribute_line_ids:
                for at in p.attribute_line_ids:
                    # _logger.error('######## AIKO en get_eti_colores valor de at  %s ####### ->'%p.attribute_line_ids)
                    if at.attribute_id.name.lower() == 'color' and at.value_ids:
                        # _logger.error('######## AIKO en get_eti_colores detectado color ####### ->')
                        if self.eti_muestrario_description:
                            self.eti_muestrario_description=""
                        for val in at.value_ids:
                            # _logger.error('######## AIKO en get_eti_colores valor de val  %s ####### ->'%val)
                            if self.eti_muestrario_description:
                                self.eti_muestrario_description += str(val.name)+" "
                            else:
                                self.eti_muestrario_description = str(val.name)+" "
                            # _logger.error('######## AIKO en get_eti_colores valor de eti  %s ####### ->'%self.eti_muestrario_description)



    type_of_material_id = fields.Many2one('st.type_material', string="Type of Material", copy=True)
    # stock_tolerancia_count = fields.Integer(compute="_stock_tolerancia", string='stock tolerance')
    collection_id = fields.Many2one('st.collection', string="Collection", copy=True)
    short_name = fields.Char(string ='short name', size = 40)
    abv_name = fields.Char(string ='abbreviated name', size = 20)
    gender = fields.Selection([('C', _('Gentleman')),('S', _('Lady')),('A', _('Both'))])
    muestrario = fields.Boolean(string='Muestrario')
    novedad = fields.Boolean(string='Top Ventas')
    outlet = fields.Boolean(string='Outlet')
    shaka = fields.Boolean(string='Oferta')
    eti_muestrario_description = fields.Text(string='Description for muestrario product label', compute='_get_eti_colores', store=True)

 
    @api.multi
    def write(self, vals):
        res = super(product_template, self).write(vals)
        extra = self.env['extra.categories']
        if self.env['multi.channel.sale'].search([]):
            th_channel = self.env['multi.channel.sale'].search([])[0].id
        else:
            raise Warning(_('Debe crear un canal woocommerce antes.'))

        # funcionamiento para Ofertas (shaka)
        oferta_categ = self.env['product.category'].search([('name','=','Oferta')],limit=1)
        if self.shaka and oferta_categ:
            tot_agents = self.env['res.partner'].search([('agent','=',True),('commission','!=',False)])
            # _logger.error('######## AIKO en onchange shaka valor de agentes %s ####### ->'%tot_agents)

            com_promo = self.env['sale.commission'].search([('type_in_product','=','promotion')])[0].id
            # _logger.error('######## AIKO en onchange shaka valor de com_promo %s ####### ->'%com_promo)
            # _logger.error('######## AIKO en onchange shaka valor de variant_ids %s ####### ->'%self.product_variant_ids)
            for variant in self.product_variant_ids:
                if variant.agents and com_promo:
                    # _logger.error('######## AIKO en onchange shaka variante con comisiones %s####### ->'%variant.agents)
                    #editar sus comisiones para que pasen al tipo de ofertas
                    for com in variant.agents:
                        com.write({'commission': com_promo})
                elif com_promo:
                    #crear una comision de oferta para cada agente
                    # _logger.error('######## AIKO en onchange shaka para crear nueva comision %s####### ->'%variant)
                    product_agent = self.env['product.product.agent']
                    values ={}
                    for ag in tot_agents:
                        # _logger.error('######## AIKO en onchange shaka para tipo de comision %s####### ->'%ag.commission.type_in_product)
                        if ag.commission.type_in_product != 'no':
                            values['agent'] = ag.id
                            values['commission']= com_promo
                            values['product_id']= variant.id
                            # _logger.error('######## AIKO en onchange shaka valores para product_agent %s####### ->'%values)

                            product_agent.create(values)
                else:
                    break

            # ademas por conexion con Woocommerce, hay que registrar en el producto una nueva categoria extra de oferta
            # siempre que no este registrada ya de antes (recordar que esto se revisa en cada write del product template)
            
            vals_extra ={}
            cat_exist = extra.search([('product_id','=',self.id),('instance_id','=',th_channel),('extra_category_ids','in',oferta_categ.id)])
            if not cat_exist:
                vals_extra['product_id'] = self.id
                vals_extra['instance_id'] = th_channel
                vals_extra['extra_category_ids'] = [(4,oferta_categ.id)]
                extra.create(vals_extra)

        else:
            #si se desmarca hay que borrar las comisiones de oferta
            for variant in self.product_variant_ids:
                if variant.agents:
                    # _logger.error('######## AIKO en onchange shaka variante con comisiones %s####### ->'%variant.agents)
                    #eliminar sus comisiones que sean del tipo ofertas
                    for com in variant.agents:
                        if com.commission.type_in_product == 'promotion':
                            com.unlink()
        
            # y habra que borrar tambien la categoria extra de oferta
            if oferta_categ:
                dele = extra.search([('product_id','=',self.id),('instance_id','=',th_channel),('extra_category_ids','in',oferta_categ.id)])
                if dele:
                    for d in dele:
                        d.unlink()


        # funcionamiento para Top Ventas (novedad)
        novedad_categ = self.env['product.category'].search([('name','=','Top Ventas')],limit=1)
        if self.novedad:
            vals_extra ={}
            cat_exist = extra.search([('product_id','=',self.id),('instance_id','=',th_channel),('extra_category_ids','in',novedad_categ.id)])
            if novedad_categ and not cat_exist:
                vals_extra['product_id'] = self.id
                vals_extra['instance_id'] = th_channel
                vals_extra['extra_category_ids'] = [(4,novedad_categ.id)]
                extra.create(vals_extra)
        else:
            # si no esta marcado y tiene la categoria registrada hay que quitarla
            if novedad_categ:
                dele = extra.search([('product_id','=',self.id),('instance_id','=',th_channel),('extra_category_ids','in',novedad_categ.id)])
                if dele:
                    for d in dele:
                        d.unlink()


        # funcionamiento para Outlet
        outlet_categ = self.env['product.category'].search([('name','=','Outlet')],limit=1)
        if self.outlet and outlet_categ:
            tot_agents = self.env['res.partner'].search([('agent','=',True),('commission','!=',False)])
            # _logger.error('######## AIKO en onchange shaka valor de agentes %s ####### ->'%tot_agents)

            com_no = self.env['sale.commission'].search([('type_in_product','=','no')])[0].id
            # _logger.error('######## AIKO en onchange shaka valor de com_no %s ####### ->'%com_no)
            # _logger.error('######## AIKO en onchange shaka valor de variant_ids %s ####### ->'%self.product_variant_ids)
            for variant in self.product_variant_ids:
                if variant.agents and com_no:
                    # _logger.error('######## AIKO en onchange shaka variante con comisiones %s####### ->'%variant.agents)
                    #editar sus comisiones para que pasen al tipo de ofertas
                    for com in variant.agents:
                        com.write({'commission': com_no})
                elif com_no:
                    #crear una comision de oferta para cada agente
                    # _logger.error('######## AIKO en onchange shaka para crear nueva comision %s####### ->'%variant)
                    product_agent = self.env['product.product.agent']
                    values ={}
                    for ag in tot_agents:
                        # _logger.error('######## AIKO en onchange shaka para tipo de comision %s####### ->'%ag.commission.type_in_product)
                        if ag.commission.type_in_product != 'no':
                            values['agent'] = ag.id
                            values['commission']= com_no
                            values['product_id']= variant.id
                            # _logger.error('######## AIKO en onchange shaka valores para product_agent %s####### ->'%values)
                            product_agent.create(values)
                else:
                    break

            # ademas por conexion con Woocommerce, hay que registrar en el producto una nueva categoria extra de oferta
            # siempre que no este registrada ya de antes (recordar que esto se revisa en cada write del product template)
            
            vals_extra ={}
            cat_exist = extra.search([('product_id','=',self.id),('instance_id','=',th_channel),('extra_category_ids','in',outlet_categ.id)])
            if not cat_exist:
                vals_extra['product_id'] = self.id
                vals_extra['instance_id'] = th_channel
                vals_extra['extra_category_ids'] = [(4,outlet_categ.id)]
                extra.create(vals_extra)

        else:
            #si se desmarca hay que borrar las comisiones de outlet
            for variant in self.product_variant_ids:
                if variant.agents:
                    # _logger.error('######## AIKO en onchange shaka variante con comisiones %s####### ->'%variant.agents)
                    #eliminar sus comisiones que sean del tipo ofertas
                    for com in variant.agents:
                        if com.commission.type_in_product == 'no':
                            com.unlink()
        
            # y habra que borrar tambien la categoria extra de oferta
            if outlet_categ:
                dele = extra.search([('product_id','=',self.id),('instance_id','=',th_channel),('extra_category_ids','in',outlet_categ.id)])
                if dele:
                    for d in dele:
                        d.unlink()


        return res



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
        st  = self.env['st.parameters'].search([('company_id', '=', self.env.user.company_id.id),('par_name', '=', 'pa00')])
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


    @api.multi
    @api.depends('line_type')
    def _set_delivered(self):
        for l in self:
            if l.line_type:
                for tp in l.line_type:
                    if tp.name == 'Entregado':
                        l.line_delivered = True
                    if tp.name == 'Abono':
                        l.line_abonado = True
                    if tp.name == 'Cambio':
                        l.line_cambiado = True
                    if tp.name == 'Sin Cargo':
                        l.line_nocharge = True



    type_line = fields.Selection(
        selection=[("E", "Delivered"),
                   ("A", "Returns"),
                   ("C", "Change"),
                   ("S", "No Charge")], string="Type of Mov.",
                   )

    line_type = fields.Many2many(comodel_name='st.line.type',relation='order_line_type_rel',string="Entrega")
    line_delivered = fields.Boolean(string='Line Delivered', compute='_set_delivered', store = True)
    line_abonado = fields.Boolean(string='Line Abonado', compute='_set_delivered', store = True)
    line_cambiado = fields.Boolean(string='Line Cambiado', compute='_set_delivered', store = True)
    line_nocharge = fields.Boolean(string='Line No Charge', compute='_set_delivered', store = True)

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
                self.discount = 0
            if record.descripcion == 'C':
                cambio = True
            if record.descripcion == 'S/C':
                sincargo = True 
                                   
        if cambio or sincargo:
            self.discount = 100.0
    # aviso a comerciales para entregar la unidad del muestrario
    # @api.model
    # def product_id_change(self, pricelist, product, qty=0,
    #                       uom=False, qty_uos=0, uos=False, name='',
    #                       partner_id=False, lang=False, update_tax=True,
    #                       date_order=False, packaging=False,
    #                       fiscal_position=False, flag=False):     

    #     res = super(SaleOrderLine, self).product_id_change(
    #         pricelist, product, qty=qty, uom=uom, qty_uos=qty_uos, uos=uos,
    #         name=name, partner_id=partner_id, lang=lang, update_tax=update_tax,
    #         date_order=date_order, packaging=packaging,
    #         fiscal_position=fiscal_position, flag=flag)

    #     if product:
    #         # _logger.error('######## AIKO product_id_change valor de product es  %s'%product)

    #         th_product = self.env['product.product'].browse(product)
    #         # _logger.error('######## AIKO sale order line el st tolerance nos da  %s ####### ->'
    #         #    %th_product.stock_tolerancia_count)
    #         if th_product.type != 'service' and th_product.qty_available > 0 and th_product.stock_tolerancia_count < 1:
    #             return {'value': res,'warning': {'title':"Stock", 'message':"Stock agotado. Entregue su muestra de %s"
    #             %th_product.default_code}}
    #             # raise Warning(_('Stock limit. Deliver your sample of %s') %
    #             #                       th_product.default_code)
    #         else:
    #             return res
    #     else:
    #         return res


# class Report(models.Model):
#     _inherit = 'report'

#     def _get_report_from_name(self, cr, uid, report_name):
#         """Get the first record of ir.actions.report.xml having the ``report_name`` as value for
#         the field report_name.
#         """
#         report_obj = self.pool['ir.actions.report.xml']
#         qwebtypes = ['qweb-pdf', 'qweb-html','pentaho']
#         conditions = [('report_type', 'in', qwebtypes), ('report_name', '=', report_name)]
#         # We won't get a context from the controller because the client would have to serialize it in the URL and that would be problematic
#         # We'll just use the user's default context, at least it will yield some language translation
#         context = self.pool['res.users'].context_get(cr, uid)
#         idreport = report_obj.search(cr, uid, conditions, context=context)[0]
#         return report_obj.browse(cr, uid, idreport, context=context)


class SaleOrder(models.Model):
    _inherit = 'sale.order'


    preparation_user = fields.Many2one('res.users',string='Responsable de pedido')
    tax_by_type = fields.Boolean(string='Taxes in sale order',related='type_id.taxes')

    @api.multi
    def sale_order_print(self):
        for s in self:

            s.signal_workflow('quotation_sent')

            return s.print_quotation()

    @api.multi
    def sale_order_print_multi(self):
        d_ids = []
        for s in self:
            if s.state == 'draft':
                d_ids.append(s.id)
                s.signal_workflow('quotation_sent')

        if len(d_ids)>0:
            draft_one = self.search([('id','in',d_ids)])

            return self.env['report'].get_action(draft_one,'style_aristos.report_saleorder')
        else:
            raise Warning(_('Ninguna orden por preparar.'))


            
    # para que al imprimir no pase a enviado
    @api.multi
    def print_quotation(self):
        '''
        This function change report name and mark it as sent, so that we can see more easily the next step of the workflow
        '''
        self.ensure_one(), 'This option should only be used for a single id at a time'
        res = self.env['report'].get_action(self, 'style_aristos.report_saleorder')
        # self.order_line.write({'state': 'draft'})
        # self.write({'state': 'draft'})
        # self.delete_workflow()
        # self.create_workflow()
        return res


    # al modificar el plazo de pago, si tiene un descuento asociado, sumar ese descuento en las lineas
    @api.onchange('payment_term')
    def onchange_payment_term(self):
        # _logger.error('######## AIKO onchange payterm en so  %s ####### ->'%self._context)
        for sale in self:
            # _logger.error('######## AIKO valor de payterm discount en so  %s ####### ->'%sale.payment_term.discount)
            if sale.payment_term.discount:
                self.global_discount = int(sale.payment_term.discount)
            else:
                self.global_discount = 0

    # al modificar el tipo de pedido, si tiene tratamiento de impuestos modificar las lineas del pedido
    @api.one
    @api.onchange('type_id')
    def onchange_type_id(self):
        for order in self:
            if order.type_id.taxes:
                for line in order.order_line:
                    line.tax_id = [(5,)]


# para gestionar descuentos asociados a plazos de pago
class AccountPaymentPartner(models.Model):
    _inherit = 'account.payment.term'

    discount = fields.Float('Global discount by term',digits_compute=dp.get_precision('Discount'))



# para no cambiar el estado de pedidos al enviar por correo
class MailComposeMessage(models.Model):
    _inherit = 'mail.compose.message'

    @api.multi
    def send_mail(self):

        res = super(MailComposeMessage, self).send_mail()
        # _logger.error('######## AIKO send mail el context tiene  %s ####### ->'%self._context)
        if (self._context.get('default_model') == 'sale.order' and self._context.get('default_res_id') and self._context.get('mark_so_as_sent')):
            th_sale = self.env['sale.order'].browse (self._context.get('default_res_id'))
            # _logger.error('######## AIKO send mail modificando estado para pedido  %s ####### ->'%th_sale)
            th_sale.order_line.write({'state': 'draft'})
            th_sale.write({'state': 'draft'})
            th_sale.delete_workflow()
            th_sale.create_workflow()
        return res


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'


    @api.multi
    def onchange_product_id(self, pricelist_id, product_id, qty, uom_id,
            partner_id, date_order=False, fiscal_position_id=False, date_planned=False,
            name=False, price_unit=False, state='draft'):
 
        res = super(PurchaseOrderLine, self).onchange_product_id(
            pricelist_id, product_id, qty=qty, uom_id=uom_id,
            partner_id=partner_id, date_order=date_order,fiscal_position_id=fiscal_position_id,
            date_planned=date_planned,name=name,price_unit=price_unit, state='draft')

        # para evitar el comportamiento por defecto que copia la descripcion de compra en la linea del pedido
        if product_id:
            # _logger.error('######## AIKO valor para product_id en purchase line  %s ####### ->'%product_id)
            lang = self.env['res.partner'].browse(partner_id).lang
            th_product = self.env['product.product'].with_context(lang=lang).browse(product_id)
            # _logger.error('######## AIKO valor para get_name en purchase line  %s ####### ->'%th_product.name_get())
            th_name=''
            if th_product.description_sale:
                th_name += th_product.description_sale
            else:
                if th_product.default_code:
                    th_name = th_product.default_code +'     '
                th_name += th_product.name_template

            # _logger.error('######## AIKO valor para name en purchase line  %s ####### ->'%th_name)
            res['value'].update({'name': th_name})

        return res


class SaleOrderType(models.Model):
    _inherit = 'sale.order.type'

    taxes = fields.Boolean(string='Update sale order taxes', default = False)


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    taxes = fields.Boolean(string='Update sale order taxes', default = False)

class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    @api.depends('partner_id')
    def _get_agents(self):
        partner = self.env['res.partner']
        for invoice in self:
            for agent in invoice.partner_id.agents:
                invoice.agents =([4,agent.id])


    taxes_updated = fields.Boolean(string='Update sale order taxes', related='journal_id.taxes')
    agents = fields.Many2many(
        comodel_name="res.partner", relation="invoice_agent_rel",
        column1="invoice_id", column2="agent_id",
        compute="_get_agents", store= True)


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'


    @api.depends('order_lines')
    def _set_delivered(self):
        for l in self:
            if l.order_lines:
                for tp in l.order_lines:
                    if tp.line_delivered:
                        l.line_delivered = True


    line_delivered = fields.Boolean(string='Line Delivered', compute='_set_delivered', store = True)



class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'


    taxes_updated = fields.Boolean(string='Update sale order taxes', related='journal_id.taxes')

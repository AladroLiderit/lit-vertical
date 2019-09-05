from openerp import models, fields, api
from openerp.exceptions import except_orm, Warning, RedirectWarning
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp

from datetime import datetime, timedelta
import calendar

import logging
logger = logging.getLogger(__name__)

class edjust_contracts_to_renove(models.Model):
        
    _name='edjust.contracts.to.renove'
    _inherit = ['mail.thread', 'ir.needaction_mixin']

    contract_id=fields.Many2one('account.analytic.account', string=_('contract'))
    #proceso para enviar plantilla de email a los clientes con suscripcion en plazo de preaviso
    @api.model
    def process_contracts_queue(self):
              
        #recuperamos todos los contratos que no esten cerrados.
        all_contracts=self.env['account.analytic.account'].search([('date','=',False)])
        today=datetime.now()
        sended_email=[]
        #recuperamos todos los contratos del modelo de notificados
        enviados=self.env['edjust.contracts.to.renove'].search([('id','>',0)])
        #creamos una lista con todos los que ya han sido notificados
        for contract in enviados:

            sended_email.append(contract.contract_id.id)
        
        
        #iteramos los contratos no cerrados
        for contract in all_contracts:
            
            #si tiene fecha de renovacion, y la fecha de renovacion es menor o igual a hoy y no esta en la lista de los ya notficados
            if contract.date_renove and (datetime.strptime(contract.date_renove, '%Y-%m-%d') <= today) and (contract.id not in sended_email):
                
                
                template_id = self.pool.get('ir.model.data').get_object_reference(self._cr, self._uid, 'edjust_custom_announ', 'email_edjust_subscription')

                ir_model_data = self.env['ir.model.data']
                email_tmp_obj = self.env['email.template']
 
                context = self._context.copy()
                #envia email con la plantilla y el objeto actual de la iteracion               
                mail = email_tmp_obj.with_context(context)
                self.pool.get('email.template').send_mail(self._cr, self._uid,
                    template_id[1], contract.id, force_send=True, context=context)
                
                #anade el el contrato a los notificados
                idf=self.create({'contract_id': contract.id})
                
                
                

class edjust_claim_notifications(models.Model):

    _name='edjust.claim.notifications'
    _inherit = ['mail.thread', 'ir.needaction_mixin']

    claim_id=fields.Many2one('crm.claim', string=_('claims'))


    @api.model
    def process_claim_queue(self):
        
        days=timedelta(days=15)
        data = {}
        stages = []
        open_stages= self.env['crm.claim.stage'].search([('is_close_stage','=',False)])
        
        today = datetime.now()
        

        for stg in open_stages:
            stages.append(stg.id)
        
        

        template_id = self.pool.get('ir.model.data').get_object_reference(self._cr, self._uid, 'edjust_custom_announ', 'email_edjust_claim2')
                

        ir_model_data = self.env['ir.model.data']
        email_tmp_obj = self.env['email.template']
 
        context = self._context.copy()
        #envia email con la plantilla y el objeto actual de la iteracion               
        mail = email_tmp_obj.with_context(context)

        users = self.env['res.users'].search([('active','=',True)])

        for user in users:
            remind = {}

            
            claims = self.env['crm.claim'].search([('stage_id','in',stages),('user_fault_id','=',user.id)])
           
            
            for claim in claims:
                
                if (datetime.strptime(claim.date, '%Y-%m-%d %H:%M:%S') <= today - days):
                    date_format=datetime.strptime(claim.date, '%Y-%m-%d %H:%M:%S')
                    date_format=date_format.strftime('%d-%m-%Y')
                    remind[claim]=date_format


            if remind:
                context["data"] = remind 
                
                self.pool.get('email.template').send_mail(self._cr, self._uid, template_id[1], user.id, force_send=True, context=context)  

        return True
             
class edjust_advert_notify(models.Model):
    
    _name='edjust.advert.notify'
    _inherit = ['mail.thread', 'ir.needaction_mixin']

    sale_order_line_id= fields.Many2one('sale.order.line', string=_('Sale order line'))
    date_edition = fields.Char(string=_('Edition Date'))
    sent_date=fields.Date(string=_('Sent Date'))
    sent_email=fields.Char(string=_('Sent Email'))

    @api.model
    def process_notify_advert(self):
        #dias de preaviso
        days=timedelta(days=30)
        today = datetime.now()
        sale_order_obj = self.env['sale.order.line'].search([('invoiced','=',False),('state','=','confirmed')])
        

        template_id = self.pool.get('ir.model.data').get_object_reference(self._cr, self._uid, 'edjust_custom_announ', 'email_edjust_advert_notify')
        ir_model_data = self.env['ir.model.data']
        email_tmp_obj = self.env['email.template']
        
        context = self._context.copy()
        #envia email con la plantilla y el objeto actual de la iteracion               
        mail = email_tmp_obj.with_context(context)

        sended_email=[]
        #recuperamos todos los contratos del modelo de notificados
        enviados=self.env['edjust.advert.notify'].search([('id','>',0)])
        #creamos una lista con todos los que ya han sido notificados
        for email in enviados:
            sended_email.append(email.sale_order_line_id.id)

        for sale in sale_order_obj:
            
            
            if sale.edicion_id:

                edition_date = datetime.strptime('01-' + str(sale.edicion_id.mes_desde) + '-'+ str(sale.edicion_id.year), '%d-%m-%Y')
                

                if (not sale.order_id.no_avisar) and (edition_date <= today - days) and (sale.order_id.contacto_aviso) and (sale.id not in sended_email):
                    
                                
                    #anade el el contrato a los notificados
                    idf=self.create({'sale_order_line_id': sale.id,
                                'date_edition': edition_date.strftime('%d-%m-%Y'),
                                'sent_date': today,
                                'sent_email': sale.order_id.contacto_aviso.email,
                            })
                    self.pool.get('email.template').send_mail(self._cr, self._uid,template_id[1], idf.id, force_send=True, context=context)
                

                   
class edjust_commitment_notify(models.Model):
    _name='edjust.commitment.notify'
    _inherit = ['mail.thread', 'ir.needaction_mixin']

    commitment_id= fields.Many2one('edjust.compromiso', string=_('Commitment'))
    date_edition = fields.Char(string=_('Edition Date'))
    sent_date=fields.Date(string=_('Sent Date'))
    sent_email=fields.Char(string=_('Sent Email'))

    @api.model
    def process_commit_advert(self):
        #dias de preaviso
        days=timedelta(days=15)
        today = datetime.now()
        commitment_obj = self.env['edjust.compromiso'].search([('realizado','=',False),('no_avisar','=',False)])
        

        template_id = self.pool.get('ir.model.data').get_object_reference(self._cr, self._uid, 'edjust_custom_announ', 'email_edjust_commit_notify')
        ir_model_data = self.env['ir.model.data']
        email_tmp_obj = self.env['email.template']
        
        context = self._context.copy()
        #envia email con la plantilla y el objeto actual de la iteracion               
        mail = email_tmp_obj.with_context(context)
        sended_email=[]
        #recuperamos todos los contratos del modelo de notificados
        enviados=self.env['edjust.commitment.notify'].search([('id','>',0)])
        #creamos una lista con todos los que ya han sido notificados
        for email in enviados:
            sended_email.append(email.commitment_id.id)

        for commit in commitment_obj:
            
            
            if commit.sale_id.edicion_id:

                edition_date = datetime.strptime('01-' + str(commit.sale_id.edicion_id.mes_desde) + '-'+ str(commit.sale_id.edicion_id.year), '%d-%m-%Y')
                

                if (edition_date <= today - days) and (commit.contacto_aviso) and (commit.id not in sended_email):
                    
                                
                    #anade el el contrato a los notificados
                    idf=self.create({'commitment_id': commit.id,
                                'date_edition': edition_date.strftime('%d-%m-%Y'),
                                'sent_date': today,
                                'sent_email': commit.contacto_aviso,
                            })
                    self.pool.get('email.template').send_mail(self._cr, self._uid,template_id[1], idf.id, force_send=True, context=context)
                

                                  
                




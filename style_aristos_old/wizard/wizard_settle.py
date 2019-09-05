# -*- coding: utf-8 -*-
# © 2011 Pexego Sistemas Informáticos (<http://www.pexego.es>)
# © 2015 Pedro M. Baeza (<http://www.serviciosbaeza.com>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp import models, fields, api, exceptions, _
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
import logging
_logger = logging.getLogger(__name__)

class SaleCommissionMakeSettle(models.TransientModel):
    _name = "sale.commission.make.settle"
    _inherit = "sale.commission.make.settle"

    @api.multi
    def action_settle(self):
        self.ensure_one()
        agent_line_obj = self.env['account.invoice.line.agent']
        
        agent_line_vencimiento_obj = self.env['account.invoice.line.agent.vencimiento']        
        account_invoice_obj = self.env['account.invoice']
        account_invoice_obj = self.env['account.move.line']
        
        settlement_obj = self.env['sale.commission.settlement']
        settlement_line_obj = self.env['sale.commission.settlement.line']       
        settlement_ids = []
      
        _logger.error('######## AIKO estoy en subrutina local  ####### ->\n'+  str(self) +  '\n') 
        if not self.agents:
            self.agents = self.env['res.partner'].search(
                [('agent', '=', True)])
        date_to = fields.Date.from_string(self.date_to)
        for agent in self.agents:
            date_to_agent = self._get_period_start(agent, date_to)
            # Get non settled invoices
            agent_lines = agent_line_obj.search(
                [('invoice_date', '<', date_to_agent),
                 ('agent', '=', agent.id),
                 ('settled', '=', False),
                 ('invoice.type', 'in', ('out_invoice', 'out_refund'))],
                order='invoice_date')
            for company in agent_lines.mapped('invoice_line.company_id'):
                agent_lines_company = agent_lines.filtered(
                    lambda r: r.invoice_line.company_id == company)
                if not agent_lines_company:
                    continue
                pos = 0
                sett_to = fields.Date.to_string(date(year=1900,
                                                     month=1,
                                                     day=1))
                cabecera = False
                while pos < len(agent_lines_company):
#========================                    
                    if (agent_lines_company[pos].invoice.state in ['draft','proforma','proforma2','cancel','debit_denied']):
                        _logger.error('######## AIKO estoy en movimientos de pago  ####### ->\n'+  str(agent_lines_company[pos].invoice.state) +  '\n')
                        pos += 1
                        continue
#========================                    
#                     if (agent.commission.invoice_state == 'paid' and
#                             agent_lines_company[pos].invoice.state !=
#                             'paid'):
#                         pos += 1
#                         continue
#========================
                    if (agent.commission.invoice_state == 'paid' and agent_lines_company[pos].invoice.state =='paid') \
                        or (agent.commission.invoice_state == 'open' and agent_lines_company[pos].invoice.state =='open'):
                    
                        if agent_lines_company[pos].invoice_date > sett_to:
                            sett_from = self._get_period_start(
                                agent, agent_lines_company[pos].invoice_date)
                            sett_to = fields.Date.to_string(
                                self._get_next_period_date(
                                    agent, sett_from) - timedelta(days=1))
                            sett_from = fields.Date.to_string(sett_from)
                            settlement = settlement_obj.create(
                                {'agent': agent.id,
                                 'date_from': sett_from,
                                 'date_to': sett_to,
                                 'company_id': company.id})
                            settlement_ids.append(settlement.id)
                        settlement_line_obj.create(
                            {'settlement': settlement.id,
                             'agent_line': [(6, 0,
                                             [agent_lines_company[pos].id])
                                            ]})
                        pos += 1
                        continue
#========================                    
                    if (agent.commission.invoice_state == 'venc' and agent_lines_company[pos].invoice.state =='open') \
                        or (agent.commission.invoice_state == 'venc' and agent_lines_company[pos].invoice.state =='paid'):
                        _logger.error('######## AIKO estoy en movimientos de pago  ####### ->\n'+  str(agent.commission.invoice_state) +  '\n')
                        # pagos inexistentes   
                        if not agent_lines_company[pos].invoice.payment_ids:
                            _logger.error('######## AIKO no tiene ids   ####### ->\n'+  str(agent_lines_company[pos].invoice.payment_ids) +  '\n')  
                            pos += 1
                            continue
#                       # lectura de pagos
                        for ml in agent_lines_company[pos].invoice.payment_ids:
                            _logger.error('######## AIKO estoy en movimientos de pago  ####### ->\n'+  str(ml) +  '\n')                                
                            if ml.state != 'valid': continue
                            # Control Si existe previamente. 
                            search_condition = [('payment_id', '=',ml.id),
                                                  ('vencimiento_id','=',agent_lines_company[pos].id)] 
                            _logger.error('######## AIKO busqueda   ####### ->\n'+  str(search_condition) +  '\n')                          
                            alv_id = agent_line_vencimiento_obj.search(search_condition, limit=1)
                            if alv_id: continue  
                            
                            # generar comision por vencimiento       
                            p_commision = {}
                            p_commision['vencimiento_id'] = agent_lines_company[pos].id
                            p_commision['payment_id'] = ml.id
                            line_venci = agent_line_vencimiento_obj.create(p_commision)
                            # generar cabecera liquidacion.
                            if not cabecera:                             
                                sett_from = self._get_period_start(agent, agent_lines_company[pos].invoice_date)
                                sett_to = fields.Date.to_string(self._get_next_period_date(agent, sett_from) - timedelta(days=1))
                                sett_from = fields.Date.to_string(sett_from)
                                settlement = settlement_obj.create(
                                    {'agent': agent.id,
                                     'date_from': sett_from,
                                     'date_to': sett_to,
                                     'company_id': company.id})
                                settlement_ids.append(settlement.id)
                                _logger.error('######## AIKO cabecera liquidacion   ####### ->\n'+  str(settlement) +  '\n')  
                                cabecera = True
                            # generar detalles liquidacion
                            settlement_line_obj.create(
                                        {'settlement': settlement.id,
                                         'invoice_line_vencimiento' : line_venci.id,
                                         'agent_line': [(6, 0,
                                        [agent_lines_company[pos].id])]})   
                            _logger.error('######## AIKO detalle liquidacion   ####### ->\n'+  str(line_venci) +  '\n')   
                    pos += 1
        # go to results
        if len(settlement_ids):
            return {
                'name': _('Created Settlements'),
                'type': 'ir.actions.act_window',
                'views': [[False, 'list'], [False, 'form']],
                'res_model': 'sale.commission.settlement',
                'domain': [['id', 'in', settlement_ids]],
            }

        else:
            return {'type': 'ir.actions.act_window_close'}
    
    
    
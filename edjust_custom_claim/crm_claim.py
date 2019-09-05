# -*- encoding: utf-8 -*-
##############################################################################
from openerp import models, fields, api, exceptions
from datetime import datetime, timedelta
from openerp.tools.translate import _

import logging
logger = logging.getLogger(__name__)



class crm_claim(models.Model):
    _inherit = "crm.claim"

    
    claim_order_line_id = fields.Many2one ('sale.order.line', string = _('Related Sale Order'))

    claim_analytic_id = fields.Many2one ('account.analytic.account', string = _('Related Contract'))

    user_fault_id = fields.Many2one ('res.users', string = _('Assing to User'), default=lambda self: self.env.user)

    action_ids = fields.One2many('crm.claim.action', 'claim_id',string=_('Action Lines'))

    closing_note = fields.Text (string=_('Closing Note'))


    # al estar en un widget statusbar, el cambio de stage_id se controla en el metodo write de la clase
    @api.multi
    def write (self, vals):
        
        # logger.error('########### Valor de stage en write: %s', self.stage_id)
        if vals.get('stage_id'):
            # logger.error('########### Valor de stage en vals write: %s', vals.get('stage_id'))
            crm_stg = self.env['crm.claim.stage'].browse(vals.get('stage_id'))
            if crm_stg.is_close_stage:
                if self.closing_note == False:
                    raise exceptions.Warning(
                 _("You have to fill a closing note in case you want to close this claim"))
                else:
                    vals['date_closed'] = datetime.now()

        res = super(crm_claim, self).write(vals)

        return res



class crm_claim_stage(models.Model):
    _inherit = "crm.claim.stage"

    is_close_stage = fields.Boolean (string=_('Closing Stage'))

    # permitimos varias etapas de tipo cierre
    # _sql_constraints = [
    #     ('close_stage_uniq', 'unique(close_stage)', _('Closing stage must be unique!'))]


class crm_claim_action(models.Model):
    _name = 'crm.claim.action'

    name = fields.Char (string=_('Claim Action Description'))
    date = fields.Date (string=_('Claim Action Date'), default=datetime.now())
    claim_id = fields.Many2one (comodel_name='crm.claim',string=_('Related Claim'))


class sale_order_line(models.Model):
    _inherit = "sale.order.line"

    partner_id = fields.Many2one (related='order_id.partner_id')


# -*- encoding: utf-8 -*-
##############################################################################
from openerp import models, fields, api, exceptions
from datetime import datetime, timedelta
from openerp.tools.translate import _

import logging
logger = logging.getLogger(__name__)


class crm_lead(models.Model):
    _inherit = "crm.lead"



class crm_claim(models.Model):
    _inherit = "crm.action"

    
    edjust_medio_id = fields.Reference (related='lead_id.ref', string = _('Reference'))

    action_note = fields.Text (string=_('Action Note'))

    action_result = fields.Text (string=_('Action Result'))

    reason_ids = fields.One2many('base.reason', 'lead_action_id', string=_('Reasons'))



class reason(models.Model):
    _inherit = 'base.reason'

    lead_action_id = fields.Many2one('crm.action', string=_('Lead Action'))


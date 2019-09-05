# -*- encoding: utf-8 -*-
##############################################################################
from openerp import models, fields, api, exceptions
from datetime import datetime, timedelta
from openerp.tools.translate import _

import logging
logger = logging.getLogger(__name__)



class crm_claim(models.Model):
    _inherit = "crm.action"

    
    edjust_medio_id = fields.Many2one (related='lead_id.campaign_id', string = _('Publication'))

    action_note = fields.Text (string=_('Action Note'))

    action_result = fields.Text (string=_('Action Result'))


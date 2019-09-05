# -*- coding: utf-8 -*-
##########################################################################
#
#    Copyright (c) 2017-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#    See LICENSE URL <https://store.webkul.com/license.html/> for full copyright and licensing details.
##########################################################################
from openerp import api, fields, models, _
class ImportPartners(models.TransientModel):

    _inherit = ['import.operation']
    _name = "import.partners"
    partner_ids = fields.Text(string='Partners ID(s)')

class ExportPartners(models.TransientModel):
    _inherit = ['export.operation']
    _name = "export.partners"

    @api.model
    def default_get(self,fields):
        res=super(ExportPartners,self).default_get(fields)
        if not res.get('partner_ids') and self._context.get('active_model')=='res.partner':
            res['partner_ids']=self._context.get('active_ids')
        return res

    partner_ids = fields.Many2many(
        'res.partner',
        string='Partner',
    )

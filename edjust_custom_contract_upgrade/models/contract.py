# -*- coding: utf-8 -*-
from openerp import models, fields, api

class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'
    contact_dn = fields.Char('Contact DN',related='contact_partner_id.name')
    contact_name = fields.Char('Contacto', compute='_update_contact_name')
    
    @api.depends('contact_dn')
    def _update_contact_name(self):
    	for line in self:
        	line.contact_name=line.contact_dn

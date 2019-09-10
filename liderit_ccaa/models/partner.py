# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api

import logging 
_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = 'res.partner'

    ccaa_id = fields.Many2one(
        comodel_name='res.partner.ccaa', string="CC.AA.")

    @api.one
    @api.onchange('zip_id')
    def onchange_zip_id(self):
        super(ResPartner, self).onchange_zip_id()

        #_logger.error('##### AIKO ###### Valor de state_id en onc_change_zip_id: %s' % self.state_id.id)
        #_logger.error('##### AIKO ###### Valor de country_id en onc_change_zip_id: %s' % self.country_id.id)
        partner_ccaa = self.env['res.country.state'].search([('id','=',self.state_id.id)])

        if partner_ccaa:
            #_logger.error('##### AIKO ###### Valor de partner_ccaa en on_change_zip_id: %s' % partner_ccaa.name)
            self.ccaa_id = partner_ccaa.id
        

class ResCountryState(models.Model):
    _inherit = 'res.country.state'

    ccaa_id = fields.Many2one(
        comodel_name='res.partner.ccaa', string="CC.AA.")


class ResPartnerCCAA(models.Model):
    _name = 'res.partner.ccaa'
    _description = u"Comunidades Autónomas"

    # NUTS fields
    name = fields.Char(required=True, string="CC.AA.")
    country_id = fields.Many2one(comodel_name='res.country', string="Country",
                                 required=True)
    state_id = fields.One2many('res.country.state','ccaa_id',string="CC.AA")

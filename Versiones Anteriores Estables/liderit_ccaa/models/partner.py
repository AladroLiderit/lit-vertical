# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    ccaa_id = fields.Many2one(
        comodel_name='res.partner.ccaa', string="CC.AA.")


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

# -*- encoding: utf-8 -*-
##############################################################################
from openerp import models, fields, api
from openerp.tools.translate import _

import logging
logger = logging.getLogger(__name__)


class edjust_partner_origin(models.Model):
    _name = 'edjust.partner.origin'

    name = fields.Char(_('Origin of the business relationship'), size=80)

class edjust_partner_activities(models.Model):
    _name = 'edjust.partner.activities'

    name = fields.Char(_('Name of Activity'), size=100)
    sector_id = fields.Many2one ('edjust.sector', string='Sector')


class edjust_sector(models.Model):
    _name = 'edjust.sector'

    name = fields.Char(_('Sector'), size=80)
    #parent_id = fields.Many2one ('edjust.sector', string='Sector Padre')


class edjust_partner_relation(models.Model):
    _name = 'edjust.partner.relation'

    name = fields.Char(_('Group criterion'), size=80)
    
class edjust_partner_position(models.Model):
    _name ='edjust.partner.position'

    name =fields.Char(_('Position'), size=80)


class res_partner(models.Model):
    _inherit = "res.partner"

    @api.one
    @api.depends(
        'cust_activities',
    )
    def _compute_sector_lines(self):
        lines=[]
        act_lines = self.env['edjust.partner.activities']
        for act in self.cust_activities:
            t_sector = act_lines.search([('id','=',act.id)])
            for s in t_sector:
                lines.append (s.sector_id.id)

        self.cust_sector = lines


    def _compute_cust_tipo(self):

        for p in self:
            if p.customer:
                contract_lines = self.env['account.analytic.account'].search([
                    ('partner_id','=',p.id),
                    ('type','like','contract'),
                    ('state','in',('open','pending'))])
                sale_lines = self.env['sale.order'].search([
                    ('partner_id','=',p.id),
                    ('state','not in',('draft','cancel'))])

                if len(contract_lines) > 0 and len (sale_lines)>0:
                    p.cust_tipo = 'ambos'
                    return

                if len (contract_lines) > 0:
                    p.cust_tipo = 'suscriptor'
                    return

                if len (sale_lines) > 0:
                    p.cust_tipo = 'anunciante'
                    return

                p.cust_tipo = 'potencial'


    
    cust_origin = fields.Many2one ('edjust.partner.origin', string = _('Origin of the business relationship'))
    cust_tipo = fields.Selection ([
        ('suscriptor',_('Subscriber')),
        ('anunciante',_('Avertiser')),
        ('ambos',_('Subscriber and advertiser')),
        ('potencial',_('Potential client')),
        ],string=_("Client type"), compute='_compute_cust_tipo')
    cust_activities = fields.Many2many(
        comodel_name='edjust.partner.activities', 
        relation='activities_partner_relation',
        column1= 'activity_id', 
        column2='partner_id', 
        string=_('Activities'),
        required = True
        )
    cust_sector = fields.Many2many(comodel_name='edjust.sector', string=_('Sector'),
    compute='_compute_sector_lines', relation='sector_partner_relation',store=True)
    #cust_sector = fields.Many2many(
    #    comodel_name='edjust.sector', 
    #    relation='sector_partner_relation',
    #    column1= 'sector_id', 
    #    column2='partner_id', 
    #    string="Sectores",
    #    )
    cust_relation2 = fields.Many2many ('edjust.partner.relation', string = _('Partners Group'))
    cust_reten = fields.Boolean(_('retain shipments'), default=False)
    write_user_name = fields.Char(string=_('User Modify'),store=True,related='write_uid.name')
    cust_origin_name = fields.Char(string=_('Origin Name'),related='cust_origin.name')
    # cust_subsector= fields.Many2one ('asincar.sector', string = 'Sub Sector')
    cust_position = fields.Many2one('edjust.partner.position', string =_('Position'))

#     @api.onchange('cust_relacion')
#     def _onchange_cust_relacion(self):
#         if self.cust_asociado:
#             self.cust_asociado = False



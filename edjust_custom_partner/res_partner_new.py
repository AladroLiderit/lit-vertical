# -*- encoding: utf-8 -*-
##############################################################################
from openerp import models, fields, api
from openerp.tools.translate import _

import logging
logger = logging.getLogger(__name__)


class edjust_partner_origin(models.Model):
    _name = 'edjust.partner.origin'

    name = fields.Char('Origen de la relación comercial', size=80)

class edjust_partner_activities(models.Model):
    _name = 'edjust.partner.activities'

    name = fields.Char('Nombre de la actividad', size=100)
    sector_id = fields.Many2one ('edjust.sector', string='Sector')


class edjust_sector(models.Model):
    _name = 'edjust.sector'

    name = fields.Char('Sector', size=80)
    parent_id = fields.Many2one ('edjust.sector', string='Sector Padre')


class edjust_partner_relation(models.Model):
    _name = 'edjust.partner.relation'

    name = fields.Char('Criterio de agrupación', size=80)
    parent_id = fields.Many2one ('edjust.partner.relation', string='Grupo Padre')



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


    
    cust_origin = fields.Many2one ('edjust.partner.origin', string = 'Origen de la relación comercial')
    cust_tipo = fields.Selection ([
        ('suscriptor','Suscriptor'),
        ('anunciante','Anunciante'),
        ('ambos','Suscriptor y anunciante'),
        ('potencial','Potencial'),
        ],string="Tipo de cliente", default='potencial')
    cust_activities = fields.Many2many(
        comodel_name='edjust.partner.activities', 
        relation='activities_partner_relation',
        column1= 'activity_id', 
        column2='partner_id', 
        string="Actividades",
        )
    cust_sector = fields.Many2many(comodel_name='edjust.sector', string='Sector',
    compute='_compute_sector_lines')
    #cust_sector = fields.Many2many(
    #    comodel_name='edjust.sector', 
    #    relation='sector_partner_relation',
    #    column1= 'sector_id', 
    #    column2='partner_id', 
    #    string="Sectores",
    #    )
    cust_relation = fields.Many2one ('edjust.partner.relation', string = 'Grupo de clientes')
    cust_reten = fields.Boolean('Retener envíos', default=False)
    write_user_name = fields.Char(string='Usuario modifica',store=True,related='write_uid.name')
    cust_origin_name = fields.Char(string='Nombre origen',related='cust_origin.name')
    # cust_subsector= fields.Many2one ('asincar.sector', string = 'Sub Sector')


#     @api.onchange('cust_relacion')
#     def _onchange_cust_relacion(self):
#         if self.cust_asociado:
#             self.cust_asociado = False



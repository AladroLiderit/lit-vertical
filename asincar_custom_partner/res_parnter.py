# -*- encoding: utf-8 -*-
##############################################################################

from openerp import models, fields, api
from openerp.tools.translate import _

import logging
logger = logging.getLogger(__name__)


class asincar_tipo_entidad(models.Model):
    _name = 'asincar.tipo.entidad'

    name = fields.Char('Tipo de entidad', size=80)

class asincar_tipo_asociado(models.Model):
    _name = 'asincar.tipo.asociado'

    name = fields.Char('Tipo de asociado', size=80)
    relacion = fields.Selection ([('socio','Asociado'),('no_socio','No Asociado')],string="Tipo de relación")


class asincar_sector(models.Model):
    _name = 'asincar.sector'

    name = fields.Char('Sector', size=80)
    parent_id = fields.Many2one ('asincar.sector', string='Sector Padre')



class res_partner(models.Model):
    _inherit = "res.partner"
    
    cust_entidad = fields.Many2one ('asincar.tipo.entidad', string = 'Tipo de entidad')
    cust_relacion = fields.Selection ([('socio','Asociado'),('no_socio','No Asociado')],string="Tipo de relación", default='socio')
    cust_asociado = fields.Many2one ('asincar.tipo.asociado', string = 'Tipo de asociado')
    cust_sector= fields.Many2one ('asincar.sector', string = 'Sector')
    cust_subsector= fields.Many2one ('asincar.sector', string = 'Sub Sector')


    @api.onchange('cust_relacion')
    def _onchange_cust_relacion(self):
        if self.cust_asociado:
            self.cust_asociado = False

    @api.onchange('cust_sector')
    def _onchange_cust_sector(self):
        if self.cust_subsector:
            self.cust_subsector = False


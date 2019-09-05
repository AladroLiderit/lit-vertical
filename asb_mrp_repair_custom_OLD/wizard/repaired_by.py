# -*- encoding: utf-8 -*-
##############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp import models, fields, api
from openerp import exceptions


import logging 
_logger = logging.getLogger(__name__)


class RepairedByWizard(models.TransientModel):
    _name = 'mrp.repaired.by.wizard'
    _description = 'Register a user that make the repair job'


    name = fields.Char(string='name')
    repaired_by = fields.Many2one(comodel_name='res.users',string='Reparado por')

    #do_create_inovices genera una sola factura para cada inscripcion o alumno
    @api.multi
    def set_repaired_by(self):
        self.ensure_one()

        if not (self.repaired_by):
            raise exceptions.ValidationError('Debe seleccionar un tecnico para finalizar la reparacion')
        
        regs_obj = self.env['mrp.repair']
        active_ids = self.env.context['active_ids'] or []
        all_regs = regs_obj.browse(active_ids)

        for r in all_regs:
            r.repaired_by = self.repaired_by.id
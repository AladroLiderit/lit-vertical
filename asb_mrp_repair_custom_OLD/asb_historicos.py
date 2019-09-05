# -*- encoding: utf-8 -*-
##############################################################################
#    audiologia_historico_movimientos
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
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp

from datetime import date, datetime
import logging
logger = logging.getLogger(__name__)


class asb_albaran_historico(models.Model):
    _name = 'asb.albaran.historico'

    name = fields.Char(string='Num Parte')
    num_albaran = fields.Char (string='Num Albaran')
    date= fields.Date (string='Fecha Salida')
    cod_cliente = fields.Char (string='Código de Cliente')
    nom_cliente = fields.Char(string='Razón social')
    tipo = fields.Selection (selection=[('N', 'Nuevo'),('M', 'Moldes'),('R','Reparación')])
    lineas_albaran = fields.One2many('asb.lineas.historico','historico_id',string='Líneas')


class asb_lineas_historico(models.Model):
    _name = 'asb.lineas.historico'

    cod_producto = fields.Char (string='Código de Producto')
    descripcion = fields.Char (string='Descripción')
    historico_id = fields.Many2one ('asb.albaran.historico', string='Albaran')


# registramos en el move un valor historico que permita abrir el form de detalle de su albaran
class stock_move(models.Model):
    _inherit = ['stock.move']

    alb_historico = fields.Many2one ('asb.albaran.historico',string="Histórico")
    # inverso del relacionado move_id en mrp.repair
    repair_id = fields.One2many(comodel_name='mrp.repair', inverse_name='move_id')

'''
class mrp_repair(models.Model):
    _inherit = ['mrp.repair']

    albaran_historico_id = fields.Many2one ('asb.albaran.historico', string='Albaran')
    lineas_albaran = fields.One2many('asb.lineas.historico','historico_id',string='Líneas')
'''

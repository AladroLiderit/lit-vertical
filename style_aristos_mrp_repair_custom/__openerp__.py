# -*- encoding: utf-8 -*-
##############################################################################
#    event_advanced
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
{
    'name': 'Gestión de Reparaciones para Audiología.',
    'version': '8.0.0.0.1',
    'category': 'Tools',
    'description': """
Gestión de reparaciones Audiología
===============================

Este módulo personaliza la gestión de reparaciones para Audiología.

Publicado bajo licencia AGPL-v3.

Copyright (c) 2017 Lider I.T., S.L.


    """,
    'author': 'LiderIT',
    'website': 'http://www.liderit.es',
    'depends': [
        'base',
        'stock_account',
        'account',
        'mrp_repair',
        'mrp_repair_laborales',
    ],
    'data': [
        # 'security/ir.model.access.csv',
        'views/mrp_repair_view.xml',
        'views/res_config_view.xml',
    ],
    "installable": True,
}

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
    'name': 'Gestión de Eventos para Audiología.',
    'version': '8.0.0.0.1',
    'category': 'Tools',
    'description': """
Gestión de eventos Audiología
===============================

Este módulo personaliza la gestión de eventos para Audiología.
Orienta los eventos a la creación de una agenda de citas: 
paciente, audioprotesista, etapas personalizadas.

Publicado bajo licencia AGPL-v3.

Copyright (c) 2017 Lider I.T. S.L.


    """,
    'author': 'LiderIT',
    'website': 'http://www.liderit.es',
    'depends': [
        'base',
        'hr',
        'event',
        'calendar',
        'web_calendar',
        'web_widget_color',
        # 'event_sale',
        # 'event_multiple_registration',
        # 'base_setup',
        # 'account_payment_partner',
    ],
    'data': [
        'views/event_advanced_view.xml',
        'views/event_assets.xml',
        # 'views/registration_advanced_view.xml',
        # 'views/event_advanced_conf_view.xml',
        'security/ir.model.access.csv',
        # 'views/datos.xml',
    ],
    "installable": True,
    # poner un sequence mayor de 100 para que la traduccion del event original no reescriba la suya
    "sequence": 500,
}

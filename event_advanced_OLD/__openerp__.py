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
    'name': 'Gestión ampliada de Eventos.',
    'version': '8.0.0.0.1',
    'category': 'Tools',
    'description': """
Gestión ampliada de eventos
===============================

Este módulo añade información a los modelos 'Event' y 'Registration'.
Permite buscar eventos, y agrupar por los campos: 
programa, actividad, comercial y centro de actividad.

También modifica los campos fecha de inicio y fecha de fin del modelo Event
haciendo que no sean obligatorios.
Esto hace que los eventos que no tienen fecha no se muestren en la vista
Kanvan. Para consultarlos hay que activar la vista de lista.



Publicado bajo licencia AGPL-v3.

Copyright (c) 2017 Lider I.T. S.L.


    """,
    'author': 'LiderIT',
    'website': 'http://www.liderit.es',
    'depends': [
        'event',
        'event_sale',
        'event_multiple_registration',
        'base_setup',
        'account_payment_partner',
        'syg_edu',
    ],
    'data': [
        'views/event_advanced_view.xml',
        'views/registration_advanced_view.xml',
        'views/event_advanced_conf_view.xml',
        'security/ir.model.access.csv',
        'views/datos.xml',
    ],
    "installable": True,
}

# -*- encoding: utf-8 -*-
##############################################################################
#    event_invoice_wizard
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
    'name': 'Gestión de facturación de Eventos.',
    'version': '8.0.0.0.1',
    'category': 'Tools',
    'description': """
Gestión de facturación de eventos
=================================

Este módulo crea dos Wizard en la lista de Registros de eventos.

Se acceden desde el menú Más, al seleccionar registros.

Crear distintas facturas por registro.
--------------------------------------
Crea tantas facturas como registros se seleccionen.
El cliente al que se factura es el alumno del curso.


Crea una única factura para todos.
----------------------------------
Se puede seleccionar todos los registros de un curso, o todos los registros de un cliente, etc.

Todos los registros seleccionados los añade a una única factura, y pide introducir el cliente al que se facturará.


Este módulo también añade una nueva solapa para mostrar la referencia a la factura correspondiente a 
cada registro, si se ha creado.

Permite filtrar por registros "Facturados" y "No facturados".


Publicado bajo licencia AGPL-v3.

Copyright (c) 2017 Lider I.T. S.L.


    """,
    'author': 'LiderIT',
    'website': 'http://www.liderit.es',
    'depends': [
        'event',
        'event_sale',
        'account',
        'base_setup',
        'event_advanced',
        'syg_edu',
    ],
    'data': [
        'views/event_invoice_wizard_view.xml',
        'views/registration_view.xml',
     ],
    "installable": True,
}

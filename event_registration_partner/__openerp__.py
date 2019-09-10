# -*- encoding: utf-8 -*-
##############################################################################
#    event_invoice_wizard
#    Copyright (c) 2017 Francisco Manuel García Claramonte <francisco@garciac.es>
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
    'name': 'Enlace a inscripciones en la ficha de alumnos.',
    'version': '8.0.0.0.1',
    'category': 'Tools',
    'description': """
Gestion de las inscripciones de alumnos
=======================================
Crear un enlace en la ficha de alumno a las inscripciones.
--------------------------------------

Publicado bajo licencia AGPL-v3.

Copyright (c) 2017 Lider I.T. S.L.


    """,
    'author': 'LiderIT',
    'website': 'http://www.liderit.es',
    'depends': [
        'event',
        'syg_edu',
    ],
    'data': [
        'views/res_partner.xml',
     ],
    "installable": True,
}

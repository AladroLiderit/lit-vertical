# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2015 Comunitea Servicios Tecnológicos All Rights Reserved
#    $Omar Castiñeira Saaevdra <omar@comunitea.com>$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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
    'name': 'ASB Custom Invoice',
    'author': 'Lider It',
    'category': 'Sale',
    'website': 'www.liderit.es',
    'description': """
Personalizacion de factura para audiologia
=====================================================

    """,
    'images': [],
    'depends': ['base',
                'sale',
                'sale_order_dates',
                'account_payment_sale'
    ],
    'data': [
                'res_partner_view.xml',
                'sale_order_view.xml'
    ],
    'installable': True,
    'application': True,
}

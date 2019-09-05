
# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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
    'name': 'POS Gift Voucher',
    'version': '1.0',
    'category': 'Point Of Sale',
    'summary': '',
    'description': """
This module shows the basic processes functionality for Gift Voucher.
======================================================================================================

    """,
    'author': 'Pragmatic',
    'website': 'http://www.pragmatic.com',
    
    'depends': ['base','point_of_sale'],
    'data': [
             'security/ir.model.access.csv',
             'view/template.xml',
             'gift_voucher.xml',
         ],
    'installable': True,
    
    
    'qweb': ['static/src/xml/pos.xml'],
    'auto_install': False,
    
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

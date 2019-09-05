# -*- coding: utf-8 -*-
#################################################################################
# Author      : Acespritech Solutions Pvt. Ltd. (<www.acespritech.com>)
# Copyright(c): 2012-Present Acespritech Solutions Pvt. Ltd.
# All Rights Reserved.
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#################################################################################
{
    'name': 'Point of Sale for Unique Serial Number',
    'version': '1.0',
    'category': 'Point of Sale',
    'summary': 'Assign unique serial number to the products from Point of Sale.',
    'description': """
This module is used to assign unique serial number to the products from Point of Sale.
""",
    'author': "Acespritech Solutions Pvt. Ltd.",
    'website': "www.acespritech.com",
    'price': 170.00, 
    'currency': 'EUR',
    'depends': ['web', 'point_of_sale', 'base', 'sale', 'purchase'],
    'images': ['static/images/main_screenshot.png'],
    'data': [
        'views/pos_serial.xml',
        'pos/pos_view.xml',
        'stock/stock_view.xml'
    ],
    'demo': [],
    'test': [],
    'qweb': ['static/src/xml/pos.xml'],
    'installable': True,
    'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
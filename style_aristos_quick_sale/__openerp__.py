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
    'name': 'Style Aristos - ASPL Quick Sale',
    'version': '1.0',
    'category': 'Point of Sale',
    'summary': 'This module allows user to create quick sales.',
    'description': """
This module allows user to quick sales.
""",
    'author': 'Acespritech Solutions Pvt. Ltd. & Lider IT Consulting',
    'website': 'http://www.liderit.com',
    'price': 15, 
    'currency': 'EUR',
    'version': '1.0.1',
    'depends': [
        'base', 
        'sale',
        'sale_order_type_sale_journal',
        'account_accountant',
        'account_payment_partner',
        'account_payment_sale',
        'l10n_es_partner',
        'liderit_global_discount',
        'style_aristos'
        ],
    'images': ['static/description/main_screenshot.png'],
    "data": [
        'views/aspl_quick_sale.xml',
        'views/sale_order_views.xml',
    ],
    'qweb': ['static/src/xml/pos.xml'],
    'installable': True,
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
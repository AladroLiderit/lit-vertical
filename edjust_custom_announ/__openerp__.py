# -*- coding: utf-8 -*-
{
    'name': 'Ediciones Just Custom Announcements',
    'version': '8.0.1',
    'author': 'Lider IT',
    'summary': 'Ed. Just Custom Announcements',
    'website': 'http://www.liderit.es',

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    

    # any module necessary for this one to work correctly
    'depends': ['base',
        'edjust_custom_contract',
        'analytic',
    ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/announcements.xml',
        'data/contracts_to_renew.xml',
        'data/edjust_email_template.xml',
    ],
    
}
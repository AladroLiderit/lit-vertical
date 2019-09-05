# -*- coding: utf-8 -*-
{
    'name': "edjust_custom_contract_upgrade",

    'summary': """
        Modificaciones Ediciones Just Custom Contract""",

    'description': """
        Modificaciones Ediciones Just Custom Contract
    """,

    'author': "Lider IT",
    'website': "https://www.liderit.es",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base',
    	'account',
        'analytic',
        'account_analytic_analysis',
        'hr_timesheet_invoice',
        'contract_recurring_invoicing_marker',
        'edjust_custom_contract',
        'contract_payment_mode'],

    # always loaded
    'data': [
    	'views/contract_view.xml',
        # 'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    
}
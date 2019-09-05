# -*- coding: utf-8 -*-
{
    'name': 'Ediciones Just Custom Contract',
    'version': '8.0.1',
    'author': 'Lider IT',
    'summary': 'Ed. Just Custom Contract',
    'website': 'http://www.liderit.es',
    'images': [],
    'depends': [
        'account',
        'analytic',
        'account_analytic_analysis',
        'hr_timesheet_invoice',
        'contract_recurring_invoicing_marker'
        ],
    'category': 'Sales Management',
    'data': [
        'views/contract_view.xml',
        'views/invoice_view.xml',
        'security/ir.model.access.csv',
        ],
    'installable': True,
    'application': False,
    'auto_install': False,
}

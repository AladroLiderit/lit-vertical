# -*- c9ding: utf-8 -*-
# © 2019 


{
    'name': 'Liderit Informe Factura Hielos',
    'summary': 'Modulo factura hielos report',
    'version': '8.0.2.0',
    'license': 'AGPL-3',
    'author': "Alejandro Aladro, Fran Vega",
    'website': 'www.Liderit.es',
    'category': 'Custom Addons',
    'depends': [
        'base',
        'account',
    ],  
    'data': [
        'data/data.xml',
        'reports/liderit_hielos_invoice_report.xml',
        'reports/liderit_hielos_invoice_report_main.xml',
    ],
    'demo': [],
    'installable': True,
}

# -*- c9ding: utf-8 -*-
# © 2019 


{
    'name': 'Liderit SyG Etiqueta Report',
    'summary': 'Modulo para imprimir etiquetas alumno',
    'version': '8.0.2.0',
    'license': 'AGPL-3',
    'author': "Alejandro Aladro, Fran Vega",
    'website': 'www.Liderit.es',
    'category': 'Custom Report Addons',
    'depends': [
        'base',
        'syg_edu'
    ],  
    'data': [
        'data/data.xml',
        'reports/liderit_syg_etiqueta_alumno.xml',
        'reports/liderit_syg_report_main.xml',
    ],
    'demo': [],
    'installable': True,
}

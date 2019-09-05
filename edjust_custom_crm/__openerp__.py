# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    "name" : "Ediciones JUST personalizacion CRM",
    "version" : "1.0",
    "author": "LiderIT",
    "description": """
        Personalizacion de CRM en Ediciones JUST
    """,
    'license':'AGPL-3',
    "website" : "www.liderit.es",
    'summary': 'Personalizacion de CRM en Ediciones JUST',
    "depends" : ['base',
        'crm',
        'marketing_crm',
        'liderit_crm_action',
        'edjust_custom_sale',
        'base_reason'],
    "data" :[
            'security/ir.model.access.csv',
            'crm_view.xml',
            #'views/template.xml',
    ],
    'qweb':[
    ],
    "auto_install": False,
    "installable": True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

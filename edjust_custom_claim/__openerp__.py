# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    "name" : "Ediciones JUST personalizacion reclamaciones",
    "version" : "1.0",
    "author": "LiderIT",
    "description": """
        Personalizacion de reclamaciones en Ediciones JUST
    """,
    'license':'AGPL-3',
    "website" : "www.liderit.es",
    'summary': 'Personalizacion de reclamaciones en Ediciones JUST',
    "depends" : ['base','sale','crm_claim'],
    "data" :[
            'security/ir.model.access.csv',
            'crm_claim_view.xml',
            #'views/template.xml',
    ],
    'qweb':[
    ],
    "auto_install": False,
    "installable": True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

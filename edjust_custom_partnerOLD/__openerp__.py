# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    "name" : "Ediciones JUST personalizacion clientes",
    "version" : "1.0",
    "author": "LiderIT",
    "description": """
        Personalizacion de clientes en Ediciones JUST
    """,
    'license':'AGPL-3',
    "website" : "www.liderit.es",
    'summary': 'Personalizacion de clientes en Ediciones JUST',
    "depends" : ['base','partner_sequence_custom'],
    "data" :[
            'security/groups.xml',
            'security/ir.model.access.csv',
            'partner_view.xml',
            #'views/template.xml',
    ],
    'qweb':[
    ],
    "auto_install": False,
    "installable": True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

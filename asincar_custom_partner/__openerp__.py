# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    "name" : "ASINCAR personalizacion clientes",
    "version" : "1.0",
    "author": "LiderIT",
    "description": """
        Personalizacion de clientes en ASINCAR
    """,
    'license':'AGPL-3',
    "website" : "www.liderit.es",
    'summary': 'Personalizacion de clientes en ASINCAR',
    "depends" : ['base','asincar_security'],
    "data" :[
			'partner_view.xml',
            'security/ir.model.access.csv',
            #'views/template.xml',
    ],
    'qweb':[
    ],
    "auto_install": False,
    "installable": True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

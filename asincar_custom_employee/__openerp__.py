# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    "name" : "ASINCAR personalizacion trabajadores",
    "version" : "1.0",
    "author": "LiderIT",
    "description": """
        Personalizacion de trabajadores en ASINCAR
    """,
    'license':'AGPL-3',
    "website" : "www.liderit.es",
    'summary': 'Personalizacion de trabajadores en ASINCAR',
    "depends" : [
        'hr',
        'hr_timesheet',
        'hr_timesheet_sheet',
        'account',
        'analytic',
        'asincar_security',
        'product'
        ],
    "data" :[
			'employee_view.xml',
            'security/ir.model.access.csv',
            #'views/template.xml',
    ],
    'qweb':[
    ],
    "auto_install": False,
    "installable": True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

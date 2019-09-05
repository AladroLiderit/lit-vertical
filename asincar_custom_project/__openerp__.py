# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    "name" : "ASINCAR personalizacion proyectos",
    "version" : "1.0",
    "author": "LiderIT",
    "description": """
        Personalizacion de proyectos en ASINCAR
    """,
    'license':'AGPL-3',
    "website" : "www.liderit.es",
    'summary': 'Personalizacion de proyectos en ASINCAR',
    "depends" : [
        'project',
        'project_department',
        'analytic',
        'analytic_base_department',
        'asincar_custom_employee',
        'asincar_security',
        'hr_timesheet',
        'timesheet_task',
        'project_stage_closed',
    ],
    "data" :[
			'project_view.xml',
            #'security/groups.xml',
            'security/ir.model.access.csv',
            'views/resources.xml',
    ],
    'qweb':[
    ],
    "auto_install": False,
    "installable": True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

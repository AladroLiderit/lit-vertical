# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    "name" : "Ediciones JUST personalizacion ventas",
    "version" : "1.0",
    "author": "LiderIT",
    "description": """
        Personalizacion de ventas en Ediciones JUST
    """,
    'license':'AGPL-3',
    "website" : "www.liderit.es",
    'summary': 'Personalizacion de ventas en Ediciones JUST',
    "depends" : [
        'base',
        'sale',
        'product_supplierinfo_for_customer',
        'edjust_custom_partner',
        'liderit_sale_order_copy_line'
        ],
    "data" :[
            #'security/groups.xml',
            'security/ir.model.access.csv',
            'sale_view.xml',
            'difusion_label_view.xml',
            #'views/template.xml',
    ],
    'qweb':[
    ],
    "auto_install": False,
    "installable": True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

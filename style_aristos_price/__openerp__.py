{
    "name": "style_aristos_price",
    "version": "1.1",
    "depends": ['base','style_aristos','sale_margin'],
    "author": "Lider IT",
    "category": "Sales",
    "description": """	Tratamiento de precios especiales y su visualizacion """,
    "website":'http://www.liderit.es',
   
    "init_xml": [],
    'update_xml': [
                'security/ir.model.access.csv',   
#                'security/groups.xml',   
                'views/parameters_view.xml',
                'views/sale_order_view.xml',
                'views/product_view.xml',
                   ],
#     'data': ['workflow/workflow.xml'],
    'demo_xml': [],
#     'data': ['general_data.xml'],
    'installable': True,
	'active': False,
}   

#!/usr/bin/env python
# -*- coding: utf-8 -*-
#################################################################################
#
#    Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#
#################################################################################

{
	'name':'Woocommerce Odoo Connector',
	 "category": 'Bridge',
	 "summary": """
        Woocommerce Odoo Connector extension  provides in-depth integration with Odoo and Woocommerce.""",
	 "description": """

====================
**Help and Support**
====================
.. |icon_features| image:: woocommerce_odoo_connector/static/src/img/icon-features.png
.. |icon_support| image:: woocommerce_odoo_connector/static/src/img/icon-support.png
.. |icon_help| image:: woocommerce_odoo_connector/static/src/img/icon-help.png

|icon_help| `Help <https://webkul.com/ticket/open.php>`_ |icon_support| `Support <https://webkul.com/ticket/open.php>`_ |icon_features| `Request new Feature(s) <https://webkul.com/ticket/open.php>`_
    """,
    "sequence": 1,
    "author": "Webkul Software Pvt. Ltd.",
    "website": "http://www.webkul.com",
    "version": '1.0',
    "depends": [
        'odoo_multi_channel_sale',
        'stock_available_immediately',
        ],
    "external_dependencies":{
                              'python': ['woocommerce'
     									]
     },
	#"demo":['demo/woc_demo.xml'],
    "data":[
      		'views/woc_config_views.xml',
			'data/import_cron.xml',
			'data/default_data.xml',
			# 'data/category_server_action.xml',
			'views/inherited_woocommerce_dashboard_view.xml'
	],
	'images':['static/description/banner.png'],
	"installable": True,
    "application": True,
    "auto_install": False,
    "price": 100,
    "currency": "EUR",
    "live_test_url" :  "http://wpodoo.webkul.com/woocommerce_odoo_connector/",
}

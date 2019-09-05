# -*- coding: utf-8 -*-

{
    'name': 'Customization for Mountain Citrus / SAT 10020',
    'version': '1.0',
    'author': 'Lider IT',
    'category': 'Other',
    'website': 'www.liderit.es',
    'description': ''' 
Customization for Mountain Citrus / SAT 10020
  ''',
    'depends': [
        'base', 
        'product',
        'purchase',
        'stock',
        'stock_picking_invoicing_unified',
        'stock_packaging_info',
        'sale_packaging_info',
        'sale_stock',
        'stock_account',
        'stock_move_sale_line',
        'account',
        'account_invoice_production_lot'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/mct_custom.xml',
    ],
    'installable': True,
    'auto_install': False

}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

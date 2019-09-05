# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.osv import fields, osv

class res_compnay(osv.osv):
    _inherit = 'res.company'

    _columns = {
        'image_1': fields.binary("Image 1",
            help="This field holds an image, limited to 1024x1024px"),
        'image_2': fields.binary("Image 2",
            help="This field holds an image, limited to 1024x1024px"),
        'image_3': fields.binary("Image 3",
            help="This field holds an image, limited to 1024x1024px"),
    }


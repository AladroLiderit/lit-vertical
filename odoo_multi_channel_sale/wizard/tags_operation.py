# -*- coding: utf-8 -*-
##########################################################################
#
#    Copyright (c) 2017-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#    See LICENSE URL <https://store.webkul.com/license.html/> for full copyright and licensing details.
##########################################################################
import logging
_logger = logging.getLogger(__name__)
from openerp import api, fields, models, _
Source = [
    ('all','All'),
    ('categories_ids','Product ID(s)'),
]

class ImportTags(models.TransientModel):

    _inherit = ['import.operation']
    _name = "import.tags"

    tag_ids = fields.Text(string='Tags ID(s)')
    parent_categ_id = fields.Many2one(
        'channel.tag.mappings',
        'Parent Category',
    )

class ExportTags(models.TransientModel):

    _inherit = ['export.operation']
    _name = "export.tags"

    @api.model
    def default_get(self,fields):
        res=super(ExportTags,self).default_get(fields)
        if not res.get('tag_ids') and self._context.get('active_model')=='st.type_material':
            res['tag_ids']=self._context.get('active_ids')
        return res

    tag_ids = fields.Many2many(
        'st.type_material',
        string='Tag',
    )

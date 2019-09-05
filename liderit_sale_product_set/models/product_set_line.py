# -*- coding: utf-8 -*-
from openerp import fields, models, api

import openerp.addons.decimal_precision as dp


class ProductSetLine(models.Model):
    _name = 'product.set.line'
    _description = 'Product set line'
    _rec_name = 'product_id'
    _order = 'sequence'

    @api.depends('tipo')
    @api.onchange('tipo')
    def _change_fixed(self):
        for event in self:
            if event.tipo == 'interior':
                event.fixed = True
            else:
                event.fixed = False

    product_id = fields.Many2one(
        'product.product', domain=[('sale_ok', '=', True)],
        string=u"Product", required=True)
    quantity = fields.Float(
        string=u"Quantity",
        digits=dp.get_precision('Product Unit of Measure'),
        required=True, default=1)
    fixed = fields.Boolean(
        string=u"Invariable",default=False)
    tipo = fields.Selection(selection=[('pista', 'Pista'),('interior','Interior'),('exterior','Exterior')])
    product_set_id = fields.Many2one(
        'product.set', 'Set', ondelete='cascade')
    sequence = fields.Integer(
        string='Sequence',
        required=True, default=0,
    )

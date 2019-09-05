# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
import openerp.addons.decimal_precision as dp


class sale_order_line(models.Model):

    _inherit = ['sale.order.line']

    calc_quantity = fields.Float(
        string=_('Cálculo'),
        digits=dp.get_precision('Product Unit of Measure'))


class ProductSetAd(models.TransientModel):
    _name = 'product.set.add'
    _rec_name = 'product_set_id'
    _descritpion = "Wizard model to add product set into a quotation"

    @api.depends('largo', 'ancho', 'pistas')
    @api.onchange('largo', 'ancho', 'pistas')
    def _compute_total_quantity(self):
        for event in self:
            event.quantity = float(event.largo)*float(event.ancho)*float(event.pistas)


    product_set_id = fields.Many2one(
        'product.set', _('Product set'), required=True)
    quantity = fields.Float(
        string=_('Quantity'),
        digits=dp.get_precision('Product Unit of Measure'), required=True,
        compute='_compute_total_quantity')
    largo = fields.Float(
        string=_('Largo en Metros'),
        digits=dp.get_precision('Product Unit of Measure'), required=True)
    ancho = fields.Float(
        string=_('Ancho en Metros'),
        digits=dp.get_precision('Product Unit of Measure'), required=True)
    pistas = fields.Float(
        string=_('Nº Pistas'),
        digits=dp.get_precision('Product Unit of Measure'), required=True,
        default=1)

    @api.multi
    def add_set(self):
        """ Add product set, multiplied by quantity in sale order line """
        so_id = self._context['active_id']
        if not so_id:
            return
        so = self.env['sale.order'].browse(so_id)
        max_sequence = 0
        if so.order_line:
            max_sequence = max([line.sequence for line in so.order_line])
        sale_order_line = self.env['sale.order.line']
        for set_line in self.product_set_id.set_line_ids:
            sale_order_line.create(
                self.prepare_sale_order_line_data(
                    so_id, self.product_set_id, set_line,
                    max_sequence=max_sequence))

    def prepare_sale_order_line_data(self, sale_order_id, set, set_line,
                                     max_sequence=0):

       
        th_quantity = set_line.quantity * self.quantity
        if set_line.tipo == 'interior':
            th_quantity = set_line.quantity * self.pistas
        if set_line.tipo == 'exterior':
            #de momento lo dejamos asi: restar 5 bidones por pista
            th_quantity -= (5*self.pistas)
        if set_line.fixed:
            th_quantity = set_line.quantity * self.pistas

        return {
            'order_id': sale_order_id,
            'product_id': set_line.product_id.id,
            'product_uom_qty': th_quantity,
            'sequence': max_sequence + set_line.sequence,
            'calc_quantity': th_quantity,
        }



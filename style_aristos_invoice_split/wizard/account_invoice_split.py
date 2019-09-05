# -*- coding: utf-8 -*-
# Copyright 2009-2017 Noviat.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from lxml import etree

from openerp import api, fields, models, _
import openerp.addons.decimal_precision as dp
from openerp.exceptions import Warning as UserError
import operator
import openerp.addons.decimal_precision as dp

import logging
_logger = logging.getLogger(__name__)


class AccountInvoiceToSplit(models.TransientModel):
    _name = 'account.invoice.tosplit'


    
    invoice_id = fields.Many2one('account.invoice')
    split_amount =  fields.Float('Total amount to Split without taxes', digits_compute=dp.get_precision('Account'))
    reset_taxes = fields.Boolean('Reset taxes', default=True)
    split_journal = fields.Many2one ('account.journal')



class AccountInvoice(models.Model):
    _inherit = 'account.invoice'


    @api.multi
    def split_the_invoice(self,invoice_id):
        self.ensure_one()
        # old_id = self._context.get('active_id')
        old = self.env['account.invoice'].browse(invoice_id)

        # if len(old.invoice_line) == len(self.invoice_line_ids) and self.split_amount == 0:
        #     raise UserError(
        #         "You cannot move all lines.")


        ctx = dict(self._context, account_invoice_split=True)
        new = old.with_context(ctx).copy()
        if self.split_amount == 0 and len(self.invoice_line_ids) > 0:
            for line in self.invoice_line_ids:
                line.invoice_id = new
        elif self.split_amount != 0:
            if not self.split_journal:
                raise UserError(_(
                "You have to set a sale journal."))
            new.journal_id = self.split_journal.id
            amount_splited = 0
            # ordenar las lineas por importe creciente
            inv_lines = self.env['account.invoice.line']
            # como el price_subtotal es un campo calculado lo tenemos que registrar en un dict primero
            order_lines ={}
            old_lines = inv_lines.search([('id','in',old.invoice_line.ids)])
            for ol in old_lines:
                order_lines[ol.id] = ol.price_subtotal
            # para luego ordenar el dict en un list y recorrerlo ordenado
            _logger.error('######## AIKO en invoice split valor de order_lines  ####### ->\n'+  str(order_lines) +  '\n')

            if len(order_lines) > 0:
                sorted_ol = sorted(order_lines.items(), key=operator.itemgetter(1))
                _logger.error('######## AIKO en invoice split valor de sorted_ol  ####### ->\n'+  str(sorted_ol) +  '\n')
                for x in sorted_ol:
                    _logger.error('######## AIKO en invoice split valor de x[0] ####### ->\n'+  str(x[0]) +  '\n')
                    th_ol = inv_lines.search([('id','=',x[0])])

                    if (amount_splited + th_ol.price_subtotal) < self.split_amount:
                        th_ol.invoice_id = new
                        if self.reset_taxes:
                            th_ol.invoice_line_tax_id = [(6,0,[])]
                        amount_splited += th_ol.price_subtotal
                    else:
                        if amount_splited == 0:
                            raise UserError(_(
                                "Can't split invoice. No invoice line with subtotal minor than amount."))
                        break

        invoices = old + new
        invoices.button_reset_taxes()

        for invoice in invoices:
            if invoice.amount_total < 0:
                raise UserError(_(
                    "The amount of the resulting invoices must be > 0."))

        # make link with sale order if sale is installed
        if 'sale.order' in self.env.registry:
            so = self.env['sale.order'].search(
                [('invoice_ids', 'in', old_id)])
            so.write({'invoice_ids': [(4, new.id)]})

        # make link with purchase order if purchase is installed
        if 'purchase.order' in self.env.registry:
            po = self.env['purchase.order'].search(
                [('invoice_ids', 'in', old_id)])
            po.write({'invoice_ids': [(4, new.id)]})

        views = {
            'out_invoice': 'action_invoice_tree1',
            'out_refund': 'action_invoice_tree3',
            'in_invoice': 'action_invoice_tree2',
            'in_refund': 'action_invoice_tree4',
        }
        view = self.env.ref('account.%s' % views.get(old.type))
        return {
            'name': _('Invoices'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.invoice',
            'type': 'ir.actions.act_window',
            'view': view.id,
            'target': 'current',
            'context': self._context,
            'domain': [('id', 'in', invoices._ids)],
            }




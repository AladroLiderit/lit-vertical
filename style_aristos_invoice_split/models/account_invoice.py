# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openerp import api, models, fields, _
from openerp.exceptions import Warning as UserError
import openerp.addons.decimal_precision as dp
import operator
from lxml import etree
from openerp.osv.orm import setup_modifiers

import logging
_logger = logging.getLogger(__name__)


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.one
    @api.depends('invoice_line.conditional', 'invoice_line.price_subtotal')
    def _compute_split(self):
        total=0
        condition = 0
        for line in self.invoice_line:
            if line.conditional and self.invoice_to_split:
                condition += line.price_subtotal
            else:
                total += line.price_subtotal

        self.split_total = total
        self.split_condition = condition
        self.split_pendant = self.split_amount - condition


    @api.multi
    def end_split_invoice(self):
        if not self.split_journal:
            raise UserError(_(
                "Set a journal for the split invoice"))
            
        self.ensure_one()
        ids = self._ids
        old = self.browse(ids[0])
        old.invoice_to_split = False
        old.split_amount = 0

        # _logger.error('######## AIKO en end_split_invoice para old_id ####### ->\n'+  str(old) +  '\n')
        new = old.with_context(self._context).copy()
        # _logger.error('######## AIKO en end_split_invoice para new  ####### ->\n'+  str(new) +  '\n')
        new.journal_id = self.split_journal.id

        if new.invoice_line:
            new.invoice_line =[(6,0,[])]
        # _logger.error('######## AIKO en end_split_invoice limpiadas lineas  ####### ->\n'+  str(new.invoice_line) +  '\n')
        for line in old.invoice_line:
            if line.conditional:
                line.conditional = False
                if self.reset_taxes:
                    line.invoice_line_tax_id = [(6,0,[])]
                new.invoice_line = [(4,line.id)]
                old.invoice_line = [(3,line.id)]
        # _logger.error('######## AIKO en end_split_invoice valor final de new  ####### ->\n'+  str(new) +  '\n')
        
        invoices = old + new
        invoices.button_reset_taxes()

        # make link with sale order if sale is installed
        if 'sale.order' in self.env.registry:
            so = self.env['sale.order'].search(
                [('invoice_ids', 'in', old.id)])
            so.write({'invoice_ids': [(4, new.id)]})

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

    @api.multi
    def do_nothing(self):
        self.ensure_one()

    @api.multi
    def cancel_split_invoice(self):
        self.ensure_one()

        self.split_amount = 0

        for line in self.invoice_line:
            line.conditional = False


    @api.onchange('split_amount')
    def onchange_split_amount(self):

        if not self.split_journal:
            raise UserError(_(
                "Set a journal for the split invoice"))

        if self.split_amount >= self.amount_untaxed and self.split_amount>0:
            raise UserError(_(
                "Total amount is less than split amount"))

        order_lines ={}
        cond = 0
        inv_lines = self.env['account.invoice.line']
        for ol in self.invoice_line:
            ol.conditional = False
            order_lines[ol.id] = ol.price_subtotal
        if len(order_lines) > 0:
            if self.split_style == 'Min':
                sorted_ol = sorted(order_lines.items(), key=operator.itemgetter(1))
            else:
                sorted_ol = sorted(order_lines.items(), key=operator.itemgetter(1),reverse=True)
            _logger.error('######## AIKO en onchange split amount sorted_ol vale ####### ->\n'+  str(sorted_ol) +  '\n')
            for x in sorted_ol:
                if cond + int(x[1]) <= self.split_amount:
                    th_ol = inv_lines.browse(x[0])
                    th_ol.conditional = True
                    cond += x[1]
                else:
                    break
            if cond == 0:
                raise UserError(_(
                    "Can't split invoice. No invoice line with subtotal minor than amount."))




    invoice_to_split = fields.Boolean(string="To Split", default=False)
    split_style = fields.Selection(
        [('Min', 'Min First'), ('Max', 'Max First')],
        string='Order of Lines', required=True, default='Min')
    split_amount =  fields.Float('Total amount to Split without taxes', digits_compute=dp.get_precision('Account'))
    split_pendant =  fields.Float('Rest amount to Split without taxes', digits_compute=dp.get_precision('Account'),
        store=True, readonly=True, compute='_compute_split')
    reset_taxes = fields.Boolean('Reset taxes', default=True)
    split_journal = fields.Many2one ('account.journal')
    split_total = fields.Float(string='Total', digits=dp.get_precision('Account'),
        store=True, readonly=True, compute='_compute_split')
    split_condition = fields.Float(string='Conditional', digits=dp.get_precision('Account'),
        store=True, readonly=True, compute='_compute_split')


    @api.one
    def copy(self, default=None):
        if self._context.get('account_invoice_split'):
            default = {} if default is None else default.copy()
            default['invoice_line'] = []
            default['tax_line'] = []
        return super(AccountInvoice, self).copy(default=default)

    @api.multi
    def split_invoice(self):
        self.ensure_one()

        if self.state != 'draft':
            raise UserError(_(
                "Only draft invoices can be splitted"))

        if len(self.invoice_line) < 2:
            raise UserError(_(
                "At least two invoice lines required for a split"))

        if self.invoice_to_split:
            self.invoice_to_split = False
        else:
            self.invoice_to_split = True

        # module = __name__.split('addons.')[1].split('.')[0]
        # view = self.env.ref(
        #     '%s.account_invoice_tosplit_view_form' % module)

        # return {
        #     'name': _('Select Invoice Lines'),
        #     'view_type': 'form',
        #     'view_mode': 'form',
        #     'res_model': 'account.invoice.tosplit',
        #     'type': 'ir.actions.act_window',
        #     'view': view.id,
        #     #'target': 'new',
        #     'context': self._context,
        #     }


    # @api.model
    # def fields_view_get(self, view_id=None, view_type=False, toolbar=False, submenu=False):
    #     res = super(AccountInvoice, self).fields_view_get(view_id, view_type, toolbar=toolbar, submenu=submenu)
    #     _logger.error('######## AIKO en fields_view_get res vale ####### ->\n'+  str(res['name']) +  '\n')
    #     # print ('----type---', view_type)
    #     if res['name']=='account.invoice.form':
    #         doc = etree.XML(res['fields']['invoice_line']['views']['tree']['arch'])

    #         if not self.invoice_to_split:
    #             _logger.error('######## AIKO en fields_view_get invoice_to_split vale ##### ->\n'+str(self.invoice_to_split)+'\n')
    #             for node in doc.xpath("//field[@name='conditional']"):
    #                 node.set('invisible', '1')                   
    #                 setup_modifiers(node)
    #         else:
    #             for node in doc.xpath("//field[@name='conditional']"):
    #                 node.set('invisible', '0')                   
    #                 setup_modifiers(node)

    #             res['fields']['invoice_line']['views']['tree']['arch'] = etree.tostring(doc)

    #     return res


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    conditional = fields.Boolean(string='Conditional',default=False)


    

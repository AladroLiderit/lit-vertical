# -*- coding: utf-8 -*-
# Copyright 2009-2016 Noviat
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import xlwt
from datetime import datetime
from openerp.osv import orm
from openerp.report import report_sxw
from openerp.addons.report_xls.report_xls import report_xls
from openerp.addons.report_xls.utils import rowcol_to_cell, _render
from openerp.tools.translate import translate, _
import logging
_logger = logging.getLogger(__name__)

_ir_translation_name = 'move.line.list.xls'


class asb_move_line_xls_parser(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(asb_move_line_xls_parser, self).__init__(
            cr, uid, name, context=context)
        move_obj = self.pool.get('account.move.line')
        self.context = context
        wanted_list = move_obj._report_xls_fields(cr, uid, context)
        template_changes = move_obj._report_xls_template(cr, uid, context)
        self.localcontext.update({
            'datetime': datetime,
            'wanted_list': wanted_list,
            'template_changes': template_changes,
            '_': self._,
        })

    def _(self, src):
        #lang = self.context.get('lang', 'en_US')
        lang = self.context.get('lang', 'es_ES')
        return translate(self.cr, _ir_translation_name, 'report', lang, src) \
            or src


class asb_move_line_xls(report_xls):

    def __init__(self, name, table, rml=False, parser=False, header=True,
                 store=False):
        super(asb_move_line_xls, self).__init__(
            name, table, rml, parser, header, store)

        # Cell Styles
        _xs = self.xls_styles
        # header
        rh_cell_format = _xs['bold'] + _xs['fill'] + _xs['borders_all']
        self.rh_cell_style = xlwt.easyxf(rh_cell_format)
        self.rh_cell_style_center = xlwt.easyxf(rh_cell_format + _xs['center'])
        self.rh_cell_style_right = xlwt.easyxf(rh_cell_format + _xs['right'])
        # lines
        aml_cell_format = _xs['borders_all']
        self.aml_cell_style = xlwt.easyxf(aml_cell_format)
        self.aml_cell_style_center = xlwt.easyxf(
            aml_cell_format + _xs['center'])
        self.aml_cell_style_date = xlwt.easyxf(
            aml_cell_format + _xs['left'],
            num_format_str=report_xls.date_format)
        self.aml_cell_style_decimal = xlwt.easyxf(
            aml_cell_format + _xs['right'],
            num_format_str=report_xls.decimal_format)
        # totals
        rt_cell_format = _xs['bold'] + _xs['fill'] + _xs['borders_all']
        self.rt_cell_style = xlwt.easyxf(rt_cell_format)
        self.rt_cell_style_right = xlwt.easyxf(rt_cell_format + _xs['right'])
        self.rt_cell_style_decimal = xlwt.easyxf(
            rt_cell_format + _xs['right'],
            num_format_str=report_xls.decimal_format)

        # XLS Template
        self.col_specs_template = {
            'move': {
                #'header': [1, 20, 'text', _render("_('Entry')")],
                'header': [1, 20, 'text', _render("_('Asiento')")],
                'lines': [1, 0, 'text', _render("line.move_id.name or ''")],
                'totals': [1, 0, 'text', None]},
            'name': {
                #'header': [1, 42, 'text', _render("_('Name')")],
                'header': [1, 42, 'text', _render("_('Concepto')")],
                'lines': [1, 0, 'text', _render("line.name or ''")],
                'totals': [1, 0, 'text', None]},
            'ref': {
                #'header': [1, 42, 'text', _render("_('Reference')")],
                'header': [1, 42, 'text', _render("_('Ref.')")],
                'lines': [1, 0, 'text', _render("line.ref or ''")],
                'totals': [1, 0, 'text', None]},
            'date': {
                #'header': [1, 13, 'text', _render("_('Effective Date')")],
                'header': [1, 13, 'text', _render("_('Fecha Asiento')")],
                #'lines': [1, 0, 'date',
                #          _render("datetime.strptime(line.date,'%Y-%m-%d').strftime('%d/%m/%Y')"),
                #          None, self.aml_cell_style_date],
                'lines': [1, 0, 'text',
                          _render("datetime.strptime(line.date,'%Y-%m-%d').strftime('%d/%m/%Y')")],
                'totals': [1, 0, 'text', None]},
            'period': {
                #'header': [1, 12, 'text', _render("_('Period')")],
                'header': [1, 12, 'text', _render("_('Periodo')")],
                'lines':
                [1, 0, 'text',
                 _render("line.period_id.code or line.period_id.name")],
                'totals': [1, 0, 'text', None]},
            'partner': {
                #'header': [1, 36, 'text', _render("_('Partner')")],
                'header': [1, 36, 'text', _render("_('Empresa')")],
                'lines':
                [1, 0, 'text',
                 _render("line.partner_id.parent_id and line.partner_id.parent_id.name or line.partner_id and line.partner_id.name or ''")],
                'totals': [1, 0, 'text', None]},
            'partner_ref': {
                'header': [1, 36, 'text', _render("_('Partner Reference')")],
                'lines':
                [1, 0, 'text',
                 _render("line.partner_id.parent_id and line.partner_id.parent_id.ref or line.partner_id and line.partner_id.ref or ''")],
                'totals': [1, 0, 'text', None]},
            'account': {
                #'header': [1, 12, 'text', _render("_('Account')")],
                'header': [1, 12, 'text', _render("_('Cuenta')")],
                'lines': [1, 0, 'number', _render("line.account_id.code")],
                'totals': [1, 0, 'text', None]},
            'date_maturity': {
                #'header': [1, 13, 'text', _render("_('Maturity Date')")],
                'header': [1, 13, 'text', _render("_('Vencimiento')")],
                #'lines':
                #[1, 0,
                # _render("line.date_maturity and 'date' or 'text'"),
                # _render(
                #     "line.date_maturity"
                #     " and datetime.strptime(line.date_maturity,'%Y-%m-%d')"
                #     " or None"),
                #    None, self.aml_cell_style_date],
                'lines': [1, 0, 'text',
                          _render(
                            "line.date_maturity"
                            " and datetime.strptime(line.date_maturity,'%Y-%m-%d').strftime('%d/%m/%Y')"
                            " or None")],
                'totals': [1, 0, 'text', None]},
            'debit': {
                #'header': [1, 18, 'text', _render("_('Debit')"), None,
                #           self.rh_cell_style_right],
                'header': [1, 18, 'text', _render("_('Debe')"), None,
                           self.rh_cell_style_right],
                'lines': [1, 0, 'number', _render("line.debit"), None,
                          self.aml_cell_style_decimal],
                'totals': [1, 0, 'number', None, _render("debit_formula"),
                           self.rt_cell_style_decimal]},
            'credit': {
                #'header': [1, 18, 'text', _render("_('Credit')"), None,
                #           self.rh_cell_style_right],
                'header': [1, 18, 'text', _render("_('Haber')"), None,
                           self.rh_cell_style_right],
                'lines': [1, 0, 'number', _render("line.credit"), None,
                          self.aml_cell_style_decimal],
                'totals': [1, 0, 'number', None, _render("credit_formula"),
                           self.rt_cell_style_decimal]},
            'balance': {
                'header': [1, 18, 'text', _render("_('Balance')"), None,
                           self.rh_cell_style_right],
                'lines': [1, 0, 'number', None, _render("bal_formula"),
                          self.aml_cell_style_decimal],
                'totals': [1, 0, 'number', None, _render("bal_formula"),
                           self.rt_cell_style_decimal]},
            'reconcile': {
                'header': [1, 12, 'text', _render("_('Rec.')"), None,
                           self.rh_cell_style_center],
                'lines': [1, 0, 'text',
                          _render("line.reconcile_id.name or ''"), None,
                          self.aml_cell_style_center],
                'totals': [1, 0, 'text', None]},
            'reconcile_partial': {
                'header': [1, 12, 'text', _render("_('Part. Rec.')"), None,
                           self.rh_cell_style_center],
                'lines': [1, 0, 'text',
                          _render("line.reconcile_partial_id.name or ''"),
                          None, self.aml_cell_style_center],
                'totals': [1, 0, 'text', None]},
            'tax_code': {
                #'header': [1, 12, 'text', _render("_('Tax Code')"), None,
                #          self.rh_cell_style_center],
                'header': [1, 12, 'text', _render("_('Impuesto')"), None,
                           self.rh_cell_style_center],
                'lines': [1, 0, 'text', _render("line.tax_code_id.name or ''"),
                          None],
                'totals': [1, 0, 'text', None]},
            'tax_info': {
                #'header': [1, 12, 'text', _render("_('Tax Code')"), None,
                #          self.rh_cell_style_center],
                'header': [1, 12, 'text', _render("_('Info Impuesto')"), None,
                           self.rh_cell_style_center],
                'lines': [1, 0, 'text', _render("line.tax_code_id.info or 'N/A'"),
                          None],
                'totals': [1, 0, 'text', None]},
            'tax_amount': {
                'header': [1, 18, 'text', _render("_('Tax/Base Amount')"),
                           None, self.rh_cell_style_right],
                'lines': [1, 0, 'number', _render("line.tax_amount"), None,
                          self.aml_cell_style_decimal],
                'totals': [1, 0, 'text', None]},
            'amount_currency': {
                'header': [1, 18, 'text', _render("_('Am. Currency')"), None,
                           self.rh_cell_style_right],
                'lines':
                [1, 0,
                 _render("line.amount_currency and 'number' or 'text'"),
                 _render("line.amount_currency or None"),
                 None, self.aml_cell_style_decimal],
                'totals': [1, 0, 'text', None]},
            'currency_name': {
                'header': [1, 6, 'text', _render("_('Curr.')"), None,
                           self.rh_cell_style_center],
                'lines':
                [1, 0, 'text',
                 _render("line.currency_id and line.currency_id.name or ''"),
                 None, self.aml_cell_style_center],
                'totals': [1, 0, 'text', None]},
            'journal': {
                #'header': [1, 12, 'text', _render("_('Journal')")],
                'header': [1, 12, 'text', _render("_('Diario')")],
                'lines': [1, 0, 'text', _render("line.journal_id.code or ''")],
                'totals': [1, 0, 'text', None]},
            'company_currency': {
                'header': [1, 10, 'text', _render("_('Comp. Curr.')")],
                'lines': [1, 0, 'text',
                          _render("line.company_id.currency_id.name or ''"),
                          None, self.aml_cell_style_center],
                'totals': [1, 0, 'text', None]},
            'analytic_account': {
                #'header': [1, 36, 'text', _render("_('Analytic Account')")],
                'header': [1, 36, 'text', _render("_('Analitica')")],
                'lines': [1, 0, 'text',
                          _render("line.analytic_account_id.code or ''")],
                'totals': [1, 0, 'text', None]},
            'product': {
                'header': [1, 36, 'text', _render("_('Product')")],
                'lines': [1, 0, 'text', _render("line.product_id.name or ''")],
                'totals': [1, 0, 'text', None]},
            'product_ref': {
                'header': [1, 36, 'text', _render("_('Product Reference')")],
                'lines': [1, 0, 'text',
                          _render("line.product_id.default_code or ''")],
                'totals': [1, 0, 'text', None]},
            'product_uom': {
                'header': [1, 20, 'text', _render("_('Unit of Measure')")],
                'lines': [1, 0, 'text',
                          _render("line.product_uom_id.name or ''")],
                'totals': [1, 0, 'text', None]},
            'quantity': {
                'header': [1, 8, 'text', _render("_('Qty')"), None,
                           self.rh_cell_style_right],
                'lines': [1, 0,
                          _render("line.quantity and 'number' or 'text'"),
                          _render("line.quantity or None"), None,
                          self.aml_cell_style_decimal],
                'totals': [1, 0, 'text', None]},
            'statement': {
                'header': [1, 20, 'text', _render("_('Statement')")],
                'lines':
                [1, 0, 'text',
                 _render("line.statement_id and line.statement_id.name or ''")
                 ],
                'totals': [1, 0, 'text', None]},
            'invoice': {
                #'header': [1, 20, 'text', _render("_('Invoice')")],
                'header': [1, 20, 'text', _render("_('Factura')")],
                'lines':
                [1, 0, 'text',
                 _render("line.invoice and line.invoice.number or ''")],
                'totals': [1, 0, 'text', None]},
            'amount_residual': {
                'header': [1, 18, 'text', _render("_('Residual Amount')"),
                           None, self.rh_cell_style_right],
                'lines':
                [1, 0,
                 _render("line.amount_residual and 'number' or 'text'"),
                 _render("line.amount_residual or None"),
                 None, self.aml_cell_style_decimal],
                'totals': [1, 0, 'text', None]},
            'amount_residual_currency': {
                'header': [1, 18, 'text', _render("_('Res. Am. in Curr.')"),
                           None, self.rh_cell_style_right],
                'lines':
                [1, 0,
                 _render(
                     "line.amount_residual_currency and 'number' or 'text'"),
                 _render("line.amount_residual_currency or None"),
                 None, self.aml_cell_style_decimal],
                'totals': [1, 0, 'text', None]},
            'narration': {
                'header': [1, 42, 'text', _render("_('Notes')")],
                'lines': [1, 0, 'text',
                          _render("line.move_id.narration or ''")],
                'totals': [1, 0, 'text', None]},
            'blocked': {
                'header': [1, 4, 'text', _('Lit.'),
                           None, self.rh_cell_style_right],
                'lines': [1, 0, 'text', _render("line.blocked and 'x' or ''"),
                          None, self.aml_cell_style_center],
                'totals': [1, 0, 'text', None]},
            'cta_partner': {
                'header': [1, 18, 'text', _render("_('Cuenta Empresa')"), None,
                           self.rh_cell_style_right],
                'lines': [1, 0, 'number', None, _render("cta_43040")],
                'totals': [1, 0, 'text', None]},
        }

    def generate_xls_report(self, _p, _xs, data, objects, wb):

        wanted_list = _p.wanted_list
        self.col_specs_template.update(_p.template_changes)
        _ = _p._

        debit_pos = 'debit' in wanted_list and wanted_list.index('debit')
        credit_pos = 'credit' in wanted_list and wanted_list.index('credit')
        c43040_pos = 'account' in wanted_list and wanted_list.index('account')
        c43040_ref = 'partner_ref' in wanted_list and wanted_list.index('partner_ref')
        c47740_cod = 'tax_info' in wanted_list and wanted_list.index('tax_info')

        if not (credit_pos and debit_pos) and 'balance' in wanted_list:
            raise orm.except_orm(
                _('Customisation Error!'),
                _("The 'Balance' field is a calculated XLS field requiring \
                the presence of the 'Debit' and 'Credit' fields !"))

        # report_name = objects[0]._description or objects[0]._name
        #report_name = _("Journal Items")
        report_name = _("Asientos")
        ws = wb.add_sheet(report_name[:31])
        ws.panes_frozen = True
        ws.remove_splits = True
        ws.portrait = 0  # Landscape
        ws.fit_width_to_pages = 1
        row_pos = 0

        # set print header/footer
        ws.header_str = self.xls_headers['standard']
        ws.footer_str = self.xls_footers['standard']

        # Title
        cell_style = xlwt.easyxf(_xs['xls_title'])
        c_specs = [
            ('report_name', 1, 0, 'text', report_name),
        ]
        row_data = self.xls_row_template(c_specs, ['report_name'])
        row_pos = self.xls_write_row(
            ws, row_pos, row_data, row_style=cell_style)
        row_pos += 1

        # Column headers
        c_specs = map(lambda x: self.render(
            x, self.col_specs_template, 'header', render_space={'_': _p._}),
            wanted_list)
        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_pos = self.xls_write_row(
            ws, row_pos, row_data, row_style=self.rh_cell_style,
            set_column_size=True)
        ws.set_horz_split_pos(row_pos)

        # account move lines
        for line in objects:
            cta_43040 = rowcol_to_cell(row_pos, c43040_pos)
            #_logger.error('##### AIKO ###### Valor de cuenta para 430: %s' % cta_43040)
            cta_43040ref = rowcol_to_cell(row_pos, c43040_ref)
            cta_47740cod = rowcol_to_cell(row_pos, c47740_cod)
            _logger.error('##### AIKO ###### Valor de tax code: %s' % cta_47740cod)
            cta_43040 = 'If(value(left(' +cta_43040+' ;3))=400;('+cta_43040+'+'+cta_43040ref+');'\
                          'If (value(left(' +cta_43040+' ;3))=410;('+cta_43040+'+'+cta_43040ref+');'\
                          'If (value(left(' +cta_43040+' ;3))=465;('+cta_43040+'+'+cta_43040ref+');'\
                          'If (value(left(' +cta_43040+' ;3))=430;('+cta_43040+'+'+cta_43040ref+');'\
                          'If ((left(' +cta_47740cod+' ;2))="RE";('+cta_43040+'+1);'\
                          'value('+cta_43040+')'\
                          '))))))'

            debit_cell = rowcol_to_cell(row_pos, debit_pos)
            credit_cell = rowcol_to_cell(row_pos, credit_pos)
            bal_formula = debit_cell + '-' + credit_cell
            _logger.debug('dummy call - %s', bal_formula)
            c_specs = map(
                lambda x: self.render(x, self.col_specs_template, 'lines'),
                wanted_list)
            row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
            row_pos = self.xls_write_row(
                ws, row_pos, row_data, row_style=self.aml_cell_style)

        # Totals
        aml_cnt = len(objects)
        debit_start = rowcol_to_cell(row_pos - aml_cnt, debit_pos)
        debit_stop = rowcol_to_cell(row_pos - 1, debit_pos)
        debit_formula = 'SUM(%s:%s)' % (debit_start, debit_stop)
        _logger.debug('dummy call - %s', debit_formula)
        credit_start = rowcol_to_cell(row_pos - aml_cnt, credit_pos)
        credit_stop = rowcol_to_cell(row_pos - 1, credit_pos)
        credit_formula = 'SUM(%s:%s)' % (credit_start, credit_stop)
        _logger.debug('dummy call - %s', credit_formula)
        debit_cell = rowcol_to_cell(row_pos, debit_pos)
        credit_cell = rowcol_to_cell(row_pos, credit_pos)
        bal_formula = debit_cell + '-' + credit_cell
        _logger.debug('dummy call - %s', bal_formula)
        

        c_specs = map(
            lambda x: self.render(x, self.col_specs_template, 'totals'),
            wanted_list)
        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_pos = self.xls_write_row(
            ws, row_pos, row_data, row_style=self.rt_cell_style_right)
        


asb_move_line_xls('report.asb.move.line.list.xls',
              'account.move.line',
              parser=asb_move_line_xls_parser)

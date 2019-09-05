#########################################################################################
#
#    OpenERP, Open Source Management Solution
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#########################################################################################

from openerp import models, fields, api, _
import logging
_logger = logging.getLogger(__name__)


class mct_finca(models.Model):
    _name = 'mct.finca'

    name = fields.Char (string=_('Nombre de la Finca'), required=True)
    lot_code = fields.Char (string=_('Lot Number Code'), required=True)

class mct_campaign(models.Model):
    _name = 'mct.campaign'

    name = fields.Char (string=_('Campaign'), required=True)


# class product_template(models.Model):
#     _inherit = 'product.template'

#     lot_code = fields.Char (string=_('Lot Number Code'))


class product_product(models.Model):
    _inherit = 'product.product'

    lot_code = fields.Char (string=_('Lot Number Code'))


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'


    # @api.multi
    # def onchange_partner_id(self, type, partner_id, date_invoice=False,
    #         payment_term=False, partner_bank_id=False, company_id=False):

    #     res = super(AccountInvoice, self).onchange_partner_id(
    #         type = type, partner_id = partner_id, date_invoice=date_invoice,
    #         payment_term=payment_term, partner_bank_id=partner_bank_id, company_id=company_id)

    #     # _logger.error('##### AIKO ###### Entro en custom mct para un type: %s' % type)

    #     if type in ('in_invoice', 'in_refund'):
    #         sequence_obj = self.env['ir.sequence']
    #         wharehouse = self.env['stock.location']
    #         wh_obj_in = wharehouse.search([('usage','=','supplier')])
    #         wh_obj_out = wharehouse.search([('usage','=','internal')])
    #         partner_obj = self.env['res.partner'].browse(partner_id)
    #         if partner_obj.voucher_seq:
    #             # _logger.error('##### AIKO ###### En custom mct el valor de reference es: %s' % sequence_obj.next_by_id(partner_obj.voucher_seq.id))
    #             res['value']['reference'] = sequence_obj.next_by_id(partner_obj.voucher_seq.id)
    #         if partner_obj.invoice_to_stock:
    #             res['value']['alter_stock']= True
    #         if wh_obj_in:
    #             res['value']['stock_loc_src_id']= wh_obj_in[0].id
    #         if wh_obj_out:
    #             res['value']['stock_loc_dest_id']= wh_obj_out[0].id

    #     return res

    mct_finca_id = fields.Many2one ('mct.finca', string=_('Finca'))

    campaing_id = fields.Many2one ('mct.campaign', string=_('Campaign'))

    cogida_picking = fields.Char(string=_('Working Note'))


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    # @api.multi
    # def product_id_change(self, product, name='',type='in_invoice'):

    #     if product:
    #         _logger.error('##### AIKO ###### Entro en custom mct para un product: %s' % product)
    #         product_obj = self.env['product.product'].browse(product)

    #         if product_obj.product_tmpl_id and product_obj.product_tmpl_id.lot_code:
    #             if self.order_id.mct_finca_id and self.order_id.mct_finca_id.lot_code:
    #                 prod_lot = self.order_id.mct_finca_id.lot_code & product_obj.product_tmpl_id.lot_code
    #                 lot_obj = self.env['stock.production.lot'].search([('product_id','=',product),('name','like',prod_lot)], limit=1)
    #                 if lot_obj:
    #                     self.lot_id = lot_obj.id


class res_partner(models.Model):
    _inherit = 'res.partner'

    voucher_seq = fields.Many2one ('ir.sequence', string=_('Voucher sequence'))
    invoice_to_stock = fields.Boolean (string=_('Invoice to Stock'))



class StockMove(models.Model):
    _inherit = 'stock.move'


    usable_tmpl_ids = fields.Many2many(
        comodel_name='product.template', string=_('Usable templates'),
        compute='_compute_usable')
    usable_product_ids = fields.Many2many(
        comodel_name='product.product', string=_('Usable products'),
        compute='_compute_usable')

    palet_type = fields.Many2one (comodel_name='product.ul', string='Palet',
        related='sale_line_id.sec_pack')

    packet_number = fields.Float(
        string='# Bultos', related='sale_line_id.pri_pack_qty_manual')

    palet_number = fields.Float(
        string='# Palets', related='sale_line_id.sec_pack_qty_manual')

    @api.onchange('picking_type_id')
    @api.depends('picking_type_id')
    def _compute_usable(self):
        res = {}
        product_obj = self.env['product.template']
        for move in self:
            usable_tmpl_ids = False
            if move.picking_type_id:
                if move.picking_type_id.code == 'incoming':
                    suppinfo = self.env['product.product'].search(
                        [('purchase_ok', '=', True)])
                    usable_tmpl_ids = suppinfo.mapped('product_tmpl_id')
                if move.picking_type_id.code == 'outgoing':
                    suppinfo = self.env['product.product'].search(
                        [('purchase_ok', '=', True)])
                    usable_tmpl_ids = suppinfo.mapped('product_tmpl_id')                
            else:
                usable_tmpl_ids = product_obj.search(
                    ['|',('sale_ok', '=', True),('purchase_ok', '=', True)])

            if usable_tmpl_ids:
                move.usable_tmpl_ids = usable_tmpl_ids
                move.usable_product_ids =\
                    move.mapped(
                        'usable_tmpl_ids.product_variant_ids')

        res['domain'] = {'product_id': [('id', 'in', [l.id for l in move.usable_product_ids])]}

        return res


    @api.v7
    def _get_taxes(self, cr, uid, move, context=None):

        fiscal_obj = self.pool.get('account.fiscal.position')

        fpos = False
        res=[]
        # _logger.error('##### AIKO ###### Entro en _get_taxes valor de partner fp: %s' % move.picking_id.partner_id.property_account_position)
        if move.picking_id.partner_id.property_account_position:
            fpos = move.picking_id.partner_id.property_account_position
            # _logger.error('##### AIKO ###### En _get_taxes con una fp: %s' % fpos)

        if move.product_id:
            # _logger.error('##### AIKO ###### En _get_taxes valor de taxes en product: %s' % move.product_id.taxes_id)

            return [tax for tax in fiscal_obj.map_tax(cr, uid,fpos, move.product_id.supplier_taxes_id, context=context)]


        return super(StockMove, self)._get_taxes(cr, uid, move, context=context)



class StockPicking(models.Model):
    _inherit = 'stock.picking'


    mct_finca_id = fields.Many2one ('mct.finca', string=_('Finca'))

    campaing_id = fields.Many2one ('mct.campaign', string=_('Campaign'))

    cogida_picking = fields.Char(string=_('Working Note'))

    product_ul_id = fields.Many2one ('product.ul', string=_('Tipo Palet'))


    @api.model
    def _get_invoice_vals(self, key, inv_type, journal_id, move):

        res = super(StockPicking, self)._get_invoice_vals(key, inv_type, journal_id,move)
        # _logger.error('##### AIKO ###### En custom mct el valor de invoice val: %s' % res)
        # pasa secuencia de proveedor y valores para finca, campaign y albaran
        if inv_type in ('in_invoice', 'in_refund'):
            

            res['mct_finca_id'] = move.picking_id.mct_finca_id.id
            res['campaing_id'] = move.picking_id.campaing_id.id
            res['cogida_picking'] = move.picking_id.cogida_picking
            # _logger.error('##### AIKO ###### En custom mct el valor de res ampliado: %s' % res)
            
            partner = res.get('partner_id')
            # _logger.error('##### AIKO ###### En custom mct el valor de partner: %s' % partner)
            partner_obj = self.env['res.partner'].browse(partner)
            if partner_obj.voucher_seq:
                sequence_obj = self.env['ir.sequence']
                # _logger.error('##### AIKO ###### En custom mct el valor de reference es: %s' % sequence_obj.next_by_id(partner_obj.voucher_seq.id))
                res['reference'] = sequence_obj.next_by_id(partner_obj.voucher_seq.id)

        return res


    @api.onchange('picking_type_id')
    def _onchange_picking_type_id(self):
        if self.picking_type_id:
            self.location_id = self.picking_type_id.default_location_src_id.id
            self.location_dest_id = self.picking_type_id.default_location_dest_id.id



class StockPackOperation(models.Model):
    _inherit = 'stock.pack.operation'

    @api.model
    def create (self, vals):
        if vals.get('product_id') and vals.get('picking_id'):
            picking = self.env['stock.picking'].browse(vals.get('picking_id'))
            # _logger.error('##### AIKO ###### En custom mct el valor de picking en pack: %s' % picking)
            product = self.env['product.product'].browse(vals.get('product_id'))
            # _logger.error('##### AIKO ###### En custom mct el valor de product en pack: %s' % product)
            lot_obj = self.env['stock.production.lot']

            if picking.mct_finca_id:
                lot_finca = picking.mct_finca_id.lot_code
                # _logger.error('##### AIKO ###### En custom mct el valor de lot_finca en pack: %s' % lot_finca)
                
                if product.lot_code:
                    # _logger.error('##### AIKO ###### En custom mct el valor de lot_product en pack: %s' % product.lot_code)
                    lot_number = lot_finca + product.lot_code
                    lote = lot_obj.search([('name','like',lot_number),('product_id','=',vals.get('product_id'))])
                    if lote:
                        vals['lot_id'] = lote.id
                    # si no existe el lote lo creamos
                    else:
                        valote={}
                        valote['name'] = lot_number
                        valote['product_id'] = vals.get('product_id')

                        lote = lot_obj.create (valote)
                        vals['lot_id'] = lote.id

        res_id = super(StockPackOperation, self).create(vals)
        return res_id

class mct_categoria(models.Model):
    _name = 'mct.categoria'

    name = fields.Char (string=_('Categoria'), required=True)
    code = fields.Char (string=_('Code'), required=True)


class mct_calibre(models.Model):
    _name = 'mct.calibre'

    name = fields.Char (string=_('Calibre'), required=True)
    code = fields.Char (string=_('Code'), required=True)

class mct_confeccion(models.Model):
    _name = 'mct.confeccion'

    name = fields.Char (string=_('Confeccion'), required=True)
    code = fields.Char (string=_('Code'), required=True)

class mct_confeccion(models.Model):
    _name = 'mct.marca'

    name = fields.Char (string=_('Marca'), required=True)
    code = fields.Char (string=_('Code'), required=True)


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    categoria_id = fields.Many2one('mct.categoria',string=_('Categoria'), required=True)
    calibre_id= fields.Many2one('mct.calibre',string=_('Calibre'), required=True)
    confeccion_id= fields.Many2one('mct.confeccion',string=_('Confeccion'), required=True)
    marca_id= fields.Many2one('mct.marca',string=_('Marca'), required=True)

    pri_pack_qty_manual = fields.Float(
        string='Manual Pkg 1 Qty.',digits=(12, 2))
    sec_pack_qty_manual = fields.Float(
        string='Manual Pkg 2 Qty.',digits=(12, 2))



    @api.onchange('pri_pack_qty','sec_pack_qty')
    @api.depends('pri_pack_qty','sec_pack_qty')
    def _onchange_pack_qty(self):
        self.pri_pack_qty_manual = self.pri_pack_qty
        self.sec_pack_qty_manual = self.sec_pack_qty



    @api.onchange('categoria_id','calibre_id','confeccion_id','marca_id')
    @api.depends('product_id','categoria_id','calibre_id','confeccion_id','marca_id')
    def _onchange_categoria(self):
        #composicion del codigo de producto
        cd_prod=cd_cat=cd_cal=cd_conf=cd_marc=' '
        if self.product_id.default_code:
            cd_prod = self.product_id.default_code

        #composicion del nombre
        my_cat=my_cal=my_conf=my_marc=' '
        if self.categoria_id:
            my_cat = self.categoria_id.name
            cd_cat = self.categoria_id.code
        if self.calibre_id:
            my_cal = self.calibre_id.name
            cd_cal = self.calibre_id.code
        if self.confeccion_id:
            my_conf = self.confeccion_id.name
            cd_conf = self.confeccion_id.code
        if self.marca_id:
            my_marc = self.marca_id.name
            cd_marc = self.marca_id.code

        if self.product_id.description_sale:
            pr_code = cd_prod+cd_cat+cd_cal+cd_conf+cd_marc
            self.name = pr_code +' - '+self.product_id.description_sale+' '+ my_cat+' '+my_cal+' '+my_conf+' '+my_marc

    #para poner los valores de envases a enteros de la ud. superior
    @api.one
    @api.depends('product_id', 'product_uom_qty',
                 'pri_pack', 'sec_pack', 'attributes_values')
    def _calculate_packages(self):
        super (SaleOrderLine,self)._calculate_packages()

        # if int(self.pri_pack_qty)!= self.pri_pack_qty:
        #     self.pri_pack_qty = int(self.pri_pack_qty)+1

        if int(self.sec_pack_qty)!=self.sec_pack_qty:
            self.sec_pack_qty = int(self.sec_pack_qty)+1

# -*- coding: utf-8 -*-
#################################################################################
# Author      : Acespritech Solutions Pvt. Ltd. (<www.acespritech.com>)
# Copyright(c): 2012-Present Acespritech Solutions Pvt. Ltd.
# All Rights Reserved.
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#################################################################################

from openerp import models, api, fields
import pytz
from datetime import datetime
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
import openerp.addons.decimal_precision as dp

import logging
logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # notes = fields.Text('Notes')
    barcode = fields.Char("Barcode")

    @api.model
    def load_currency(self, company_id):
        if company_id:
            company_obj = self.env['res.company'].browse(company_id)
            if company_obj and company_obj.currency_id:
                return company_obj.currency_id.read()

    @api.model
    def update_so_line(self, line):
        logger.error('Valor de line en update so line %s'%line)
        ids_entrega=[]
        discount = 0
        warehouse=''
        th_tipoent = self.env['st.line.type']

        entregado = line.get('entregado')
        if entregado:
            id_ent = th_tipoent.search([('name','=','Entregado')])
            if id_ent:
                ids_entrega.append(id_ent.id)
            wh = self.env['stock.warehouse'].search([('partner_id', '=', self.env.user.partner_id.id)], limit=1)               
            if wh: 
                warehouse = wh.id
        abono = line.get('abono')
        if abono:
            id_abo = th_tipoent.search([('name','=','Abono')])
            if id_abo:
                ids_entrega.append(id_abo.id)
        cambio = line.get('cambio')
        if cambio:
            discount = 100.0
            id_cam = th_tipoent.search([('name','=','Cambio')])
            if id_cam:
                ids_entrega.append(id_cam.id)
        sincargo = line.get('sin_cargo')
        if sincargo:
            discount = 100.0
            id_sin = th_tipoent.search([('name','=','Sin Cargo')])
            if id_sin:
                ids_entrega.append(id_sin.id)
        if line.has_key('global_discount') and line.get('global_discount')<>0:
            # no se aplica a lineas de cambios o abonos
            if discount < 100 and line.get('quantity') > 0:
                discount += line.get('global_discount')

        if line.has_key('global_discount') and line.get('global_discount')<>0:
            # no se aplica a lineas de cambios o abonos
            if discount < 100 and line.get('quantity') > 0:
                discount = line.get('global_discount')

        line_env = self.env['sale.order.line']
        product_obj = self.env['product.product'].browse(line.get('product_id'))
        sol_exist = line_env.search([('quick_cid','=',line.get('cid')),('order_id','=',line.get('sale_order'))], limit = 1)
        if sol_exist:
            vals={
                'product_uom_qty': line.get('quantity'),
                'price_unit': line.get('price_unit'),
                'discount': discount,
                'line_type': [(6,0, ids_entrega)] or ''
            }
            sol_exist[0].update(vals)
        else:
            # hay que buscar los impuestos aplicables a las nuevas lineas
            # copiamos los de alguna linea anterior
            # pero tenemos que prever que el tipo de pedido no sea sin impuestos
            th_sale = self.env['sale.order'].browse(line.get('sale_order'))
            old_line = line_env.search([('order_id','=',line.get('sale_order'))], limit = 1)

            sale_cond = th_sale.type_id.taxes
            if sale_cond:
                tax_ids =[]
            else:
                taxes = old_line.tax_id
                tax_ids =[]
                for t in taxes:
                    tax_ids.append(t.id)
                # logger.error('Valor taxes en update so %s'%taxes)
            # tambien de una linea anterior tenemos que copiar las comisiones
            agents=[]
            if old_line.agents:
                for ag in old_line.agents:
                    agents.append(ag.id)

            new_line = line_env.create({
                                'product_id': line.get('product_id'),
                                # 'name': product_obj.name,
                                'name': line.get('description') or line.get('product').get('display_name'),
                                'order_id': line.get('sale_order'),
                                'product_uom_qty' : line.get('quantity'),
                                'price_unit' : line.get('price_unit'),
                                'product_uom' : product_obj.uom_id.id,
                                'discount': discount,
                                'line_type': [(6,0, ids_entrega)] or '',
                                'tax_id':[(6,0,tax_ids)],
                                'agents':[(6,0,agents)],
                                'quick_cid': line.get('cid'),
                                'warehouse_id': warehouse
                                })                
            # new_line.product_id_change()

        return line.get('sale_order')

    @api.model
    def update_note(self, vals):
        values = {
            'note': vals.get('note'),
        }
        if vals.get('sale_order_id'):
            order_id = self.browse(vals.get('sale_order_id'))
            order_id.update(values)

            return order_id.id
        else:
            return False

    @api.model
    def remove_line(self, vals):
        logger.error('Valor recibido en remove de vals %s'%vals)
        if vals.get('line_id'):
            line = vals.get('line_id')
            sol_exist = self.env['sale.order.line'].search([('quick_cid','=',line),('order_id','=',vals.get('sale_order_id'))], limit = 1)
            logger.error('Valor en remove para sol_exist %s'%sol_exist)
            if sol_exist:
                sol_exist.unlink()

        return vals.get('sale_order_id')


    @api.model
    def update_discount(self, vals):
        values = {
            'discount': vals.get('discount'),
        }
        if vals.get('sale_order_id'):
            order_id = self.browse(vals.get('sale_order_id'))
            for line in order_id.order_line:
                # no se aplica a lineas de cambios o abonos
                if line.discount < 100 and line.product_uom_qty > 0:
                    line.update(values)

            return order_id.id
        else:
            return False

    @api.model
    def update_payterm(self, vals):
        values = {
            'payment_term': vals.get('payment_term'),
        }
        # order_id = 0
        if vals.get('sale_order_id'):
            order_id = self.browse(vals.get('sale_order_id'))
            order_id.update(values)

            return order_id.id
        else:
            return False

    @api.model
    def update_paymode(self, vals):
        values = {
            'payment_mode_id': vals.get('payment_mode_id'),
        }
        if vals.get('sale_order_id'):
            order_id = self.browse(vals.get('sale_order_id'))
            order_id.update(values)

            return order_id.id
        else:
            return False

    @api.model
    def update_type(self, vals):
        values = {
            'type_id':vals.get('type_id'),
        }
        type_sale = self.env['sale.order.type'].browse(vals.get('type_id'))
        if vals.get('sale_order_id'):
            order_id = self.browse(vals.get('sale_order_id'))
            order_id.update(values)
            if type_sale.taxes:
                for oline in order_id.order_line:
                    oline.tax_id=[(6,0,[])]

            return order_id.id
        else:
            return False

    @api.model
    def create_update_so(self, vals):
        order_lines = []
        # logger.error('Valor recibido de vals %s'%vals)
        for each in vals.get('lines'):

            ids_entrega=[]
            discount = 0
            warehouse=''
            th_tipoent = self.env['st.line.type']

            entregado = each.get('entregado')
            if entregado:
                id_ent = th_tipoent.search([('name','=','Entregado')])
                if id_ent:
                    ids_entrega.append(id_ent.id)
                wh = self.env['stock.warehouse'].search([('partner_id', '=', self.env.user.partner_id.id)], limit=1)               
                if wh: 
                    warehouse = wh.id

            abono = each.get('abono')
            if abono:
                id_abo = th_tipoent.search([('name','=','Abono')])
                if id_abo:
                    ids_entrega.append(id_abo.id)

            cambio = each.get('cambio')
            if cambio:
                discount = 100.0
                id_cam = th_tipoent.search([('name','=','Cambio')])
                if id_cam:
                    ids_entrega.append(id_cam.id)

            sincargo = each.get('sin_cargo')
            if sincargo:
                discount = 100.0
                id_sin = th_tipoent.search([('name','=','Sin Cargo')])
                if id_sin:
                    ids_entrega.append(id_sin.id)

            if vals.has_key('global_discount') and vals.get('global_discount')<>0:
                # no se aplica a lineas de cambios o abonos
                if discount < 100 and each.get('quantity') > 0:
                    discount += vals.get('global_discount')

            # logger.error('Valor de ids_entrega antes de agregar en order_lines %s'%ids_entrega)

            order_lines.append((0, 0, {
                'product_id': each.get('product').get('id'),
                'product_uom_qty': each.get('quantity'),
                'price_unit': each.get('price_unit'),
                'name': each.get('description') or each.get('product').get('display_name'),
                'discount': discount,
                'line_type': [(6,0, ids_entrega)] or '',
                'warehouse_id': warehouse,
                'quick_cid':each.get('cid') or ''
            }))

            # logger.error('Valor de order_lines antes de actualizar el pedido %s'%order_lines)


        values = {
            'partner_id': vals.get('partner_id'),
            # 'notes': vals.get('notes'),
            'note': vals.get('note'),
            'payment_term': vals.get('payment_term'),
            'payment_mode_id': vals.get('payment_mode_id'),
            'global_discount':vals.get('global_discount'),
            'type_id':vals.get('type_id'),
            'order_line': order_lines,
            # 'date_order':vals.get('datetime') or datetime.now(),
        }
        if not vals.get('sale_order_id') and vals.get('partner_id')!= False:
            order_id = self.create(values)
            # si el tipo es sin impuestos en la linea pasamos taxes vacio
            if vals.has_key('type_id') and vals.get('type_id')<>0:
                type_sale = self.env['sale.order.type'].browse(vals.get('type_id'))
                if type_sale.taxes:
                    for oline in order_id.order_line:
                        oline.tax_id=[(6,0,[])]
        else:
            order_id = self.browse(vals.get('sale_order_id'))
            order_id.order_line.unlink()

            if vals.get('lines')==[]:
                order_id.unlink()
                return False
            else:
                order_id.update(values)

        return order_id.id

    @api.model
    def load_sale_order_by_id(self, sale_order_id):
        sale_order = self.browse(sale_order_id)
        sale_order_lines = []
        if sale_order:
            if sale_order.order_line:
                for line in sale_order.order_line:
                    product_obj = line.product_id
                    line = {
                        'line_id':line.id,
                        'quick_cid': line.quick_cid,
                        'product_id':line.read(['product_id'])[0],
                        'display_price':product_obj.list_price,
                        'quantity': line.product_uom_qty,
                        'display_name': product_obj.display_name,
                        'price_unit': line.price_unit,
                        'discount': line.discount,
                        'product': product_obj.read(['name', 'display_name', 'list_price', 'ean13', 'description_sale','virtual_available'])[0],
                        'description':line.name,
                        'entregado':1 if line.line_delivered else 0,
                        'abono':1 if line.line_abonado else 0,
                        'sin_cargo': 1 if line.line_nocharge else 0,
                        'cambio':1 if line.line_cambiado else 0,
                        }
                    sale_order_lines.append(line)
            values = {
                'sale_order_id':sale_order_id,
                'partner_id': sale_order.partner_id.read(['name', 'property_product_pricelist','property_payment_term','customer_payment_mode','credit'])[0],
                'payment_term': sale_order.payment_term.id if sale_order.payment_term else False,
                'payment_discount': sale_order.payment_term.discount if sale_order.payment_term else False,
                'payment_mode_id': sale_order.payment_mode_id.id if sale_order.payment_mode_id else False,
                'global_discount': sale_order.global_discount if sale_order.global_discount else False,
                #'notes': sale_order.notes,
                'note': sale_order.note,
                'type_id':sale_order.type_id.id,
                'lines': sale_order_lines,
                'date_order':self._get_datetime(sale_order.date_order) or '',
            }
            return [values]
        else:
            return False

    @api.multi
    def _get_datetime(self, date_time):
        if self.env.user.tz:
            tz = pytz.timezone(self.env.user.tz)
        else:
            tz = pytz.utc
        date_from = pytz.utc.localize(datetime.strptime(date_time, DEFAULT_SERVER_DATETIME_FORMAT)).astimezone(tz)
        date = date_from.strftime("%d-%m-%Y %H:%M")
        return date

    @api.model
    def load_sale_order_by_query(self, query):
        sale_order = self.search_read(['|', ('barcode','=',query),('name','ilike',query), ['state','=','draft']],['id'])
        if sale_order and sale_order[0] and sale_order[0].get('id'):
            return self.load_sale_order_by_id(sale_order[0].get('id'))
        else:
            return False

    @api.model
    def get_product_price(self, pricelist_id, product_id):
        pricelist = self.env['product.pricelist'].browse(int(pricelist_id))
        res = []
        if pricelist:
            new_price = pricelist.price_get(product_id, 1)
            # logger.error('Valor de new_price en get product price %s'%new_price)
            if new_price:
                res.append({
                    'product_id': product_id,
                    'new_price': new_price.get(int(pricelist_id))
                })
        if res:
            return res
        return False

    @api.model
    def get_product_tax_amount(self, price_unit, quantity, product_id, partner_id):
        val = 0.0
        product_id = self.env['product.product'].browse(product_id)
        partner_id = self.env['res.partner'].browse(partner_id)
        for c in self.pool['account.tax'].compute_all(
                self._cr, self._uid, product_id.taxes_id, float(price_unit), float(quantity),
                product_id, partner_id)['taxes']:
            # logger.error('Valor de c en get product tax amount %s'%c)
            val += c.get('amount', 0.0)
        return {
            'amount': val,
        }

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    quick_cid = fields.Integer(string='CID in quick sale interface')


class ResPartner(models.Model):
    _inherit = 'res.partner'

    property_payment_term_name = fields.Char(related='property_payment_term.name', string='Name of payment term')
    customer_payment_mode_name = fields.Char(related='customer_payment_mode.name', string='Name of payment term')



class ResUsers(models.Model):
    _inherit = 'res.users'

    @api.model
    def load_user_by_id(self, user_id):
        # logger.error('Entro en load_user_by_id con user_id %s'%user_id)
        user = self.browse(user_id)
        if user.groups_id:
            for gid in user.groups_id:
                if gid.name == 'QuickSalePrice':
                    
                    values = {
                        'group_id':gid.id,
                    }
                    # logger.error('Salgo de load_user_by_id con valor %s'%values)
                    return [values]
            # logger.error('Salgo de load_user_by_id con valor False')
            return False
        return False
        


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
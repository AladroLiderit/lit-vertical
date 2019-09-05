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
from openerp import fields, models, api, _
from openerp.tools import float_is_zero
import time

class pos_config(models.Model):
    _inherit = 'pos.order.line'

    prodlot_id = fields.Many2one('stock.production.lot', "Serial No.")
    
class pos_order(models.Model):
    _inherit= 'pos.order'

    @api.v7
    def create_picking(self, cr, uid, ids, context=None):
        """Create a picking for each order and validate it."""
        picking_obj = self.pool.get('stock.picking')
        partner_obj = self.pool.get('res.partner')
        move_obj = self.pool.get('stock.move')

        for order in self.browse(cr, uid, ids, context=context):
            if all(t == 'service' for t in order.lines.mapped('product_id.type')):
                continue
            addr = order.partner_id and partner_obj.address_get(cr, uid, [order.partner_id.id], ['delivery']) or {}
            picking_type = order.picking_type_id
            picking_id = False
            location_id = order.location_id.id
            if order.partner_id:
                destination_id = order.partner_id.property_stock_customer.id
            else:
                if (not picking_type) or (not picking_type.default_location_dest_id):
                    customerloc, supplierloc = self.pool['stock.warehouse']._get_partner_locations(cr, uid, [],
                                                                                                   context=context)
                    destination_id = customerloc.id
                else:
                    destination_id = picking_type.default_location_dest_id.id

            #All qties negative => Create negative
            if picking_type:
                pos_qty = all([x.qty >= 0 for x in order.lines])
                #Check negative quantities
                picking_id = picking_obj.create(cr, uid, {
                    'origin': order.name,
                    'partner_id': addr.get('delivery',False),
                    'date_done' : order.date_order,
                    'picking_type_id': picking_type.id,
                    'company_id': order.company_id.id,
                    'move_type': 'direct',
                    'note': order.note or "",
                    'location_id': location_id if pos_qty else destination_id,
                    'location_dest_id': destination_id if pos_qty else location_id,
                }, context=context)
                self.write(cr, uid, [order.id], {'picking_id': picking_id}, context=context)

            move_list = []
            for line in order.lines:
                if line.product_id and line.product_id.type not in ['product', 'consu']:
                    continue

                line_move = move_obj.create(cr, uid, {
                                'name': line.name,
                                'product_uom': line.product_id.uom_id.id,
                                'picking_id': picking_id,
                                'picking_type_id': picking_type.id,
                                'product_id': line.product_id.id,
                                'product_uom_qty': abs(line.qty),
                                'state': 'draft',
                                'location_id': location_id if line.qty >= 0 else destination_id,
                                'location_dest_id': destination_id if line.qty >= 0 else location_id,
                                'pos_line_id': line.id
                            }, context=context)
                move_list.append(line_move)
            # CUSTOM CODE
            if picking_id:
                picking_obj.action_confirm(cr, uid, [picking_id], context=context)
                picking_obj.force_assign(cr, uid, [picking_id], context=context)
                # Mark pack operations as done
                pick = picking_obj.browse(cr, uid, picking_id, context=context)
                for pack in pick.pack_operation_ids:
                    self.pool['stock.pack.operation'].write(cr, uid, [pack.id], {'qty_done': pack.product_qty},
                                                            context=context)
                picking_brw = picking_obj.browse(cr, uid, picking_id, context=context)
                # We check for the prodlot_id in pos order lines, and check in the pack operations
                # for such product, if we find it we create spol record, which will help in taking the D.O. to Done state
                spol_obj = self.pool.get('stock.pack.operation.lot')
                for each_line in order.lines:
                    if each_line.prodlot_id:
                        for each_op in picking_brw.pack_operation_ids:
                            if each_op.product_id.id == each_line.product_id.id:
                                spol_obj.create(cr, uid, {'lot_name': False, 'qty_todo': 0, 'qty': 1,
                                                          'operation_id': each_op.id, 'lot_id': each_line.prodlot_id.id,
                                                          'plus_visible': True})


                picking_obj.action_done(cr, uid, [picking_id], context=context)
            elif move_list:
                print move_obj.action_confirm(cr, uid, move_list, context=context)
                print move_obj.force_assign(cr, uid, move_list, context=context)
                print move_obj.action_done(cr, uid, move_list, context=context)
        return True

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
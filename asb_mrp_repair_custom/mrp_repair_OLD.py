# -*- encoding: utf-8 -*-
##############################################################################
#    event_advanced
#    Copyright (c) 2016 Francisco Manuel García Claramonte <francisco@garciac.es>
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
##############################################################################
from openerp import models, fields, api, exceptions, _
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
from openerp.osv import fields as old_fields

from datetime import date, datetime
import logging
logger = logging.getLogger(__name__)


class account_invoice(models.Model):
    _inherit = ['account.invoice']

    repair_id = fields.Many2one ('mrp.repair', string='Reparacion')


class stock_picking(models.Model):
    _inherit = ['stock.picking']

    repair_id = fields.Many2one ('mrp.repair', string='Reparacion')


    # ampliamos la funcion para marcar la reparacion como terminada y registrar su factura
    @api.model
    def _create_invoice_from_picking(self, picking, vals):
        res = super(stock_picking, self)._create_invoice_from_picking(
            picking, vals)

        if picking and picking.repair_id and picking.repair_id.state != 'done':
            # logger.error('Entramos en picking create invoice el valor de res %s'%res)
            # logger.error('Entramos en picking create invoice el valor de invoice %s'%picking.repair_id.invoice_id)
            if not picking.repair_id.invoice_id:
                picking.repair_id.invoice_id = res
            picking.repair_id.state = 'done'

        return res


class stock_picking_type(models.Model):
    _inherit = ['stock.picking.type']

    get_price_oninvoicing = fields.Boolean('Get prices from picking when invoicing',default=False)


class stock_move(models.Model):
    _inherit = ['stock.move']

    discount = fields.Float('Discount',digits_compute=dp.get_precision('Account'))

    #para cambiar el criterio al obtener el precio de las lineas de albaran
    def _get_price_unit_invoice(self, cr, uid, move_line, type, context=None):

        # agregamos para que devuelva el price_unit si lo tiene registrado
        # logger.error('Entramos en get price reescrito para el stock move %s'%move_line.id)
        # logger.error('Entramos en get price reescrito con el price unit %s'%move_line.price_unit)
        if move_line.picking_id.picking_type_id.get_price_oninvoicing:
            res =  move_line.price_unit
        else:
            res = super(stock_move, self)._get_price_unit_invoice(cr, uid, move_line, type, context=context)
        # logger.error('Entramos en get price reescrito valor devuelto %s'%res)

        return res




class mrp_repair(models.Model):
    _inherit = ['mrp.repair']

    _order = "fecha_recepcion DESC, name"


    referencia = fields.Char('Referencia', size=100)
    # las fechas ahora las instala mrp_repair_laborales aqui solo damos un default
    # fecha_recepcion = fields.Date(default=fields.Date.today())
    fecha_recepcion = fields.Date(default=lambda self: fields.datetime.now())
    
    # fecha_reparacion = fields.Date(string='Fecha de Reparación')
    fecha_esperar = fields.Date(string='Puesto en espera')
    num_pedido  = fields.Char('Pedido Nº', size=100)
    depart = fields.Char('Depart.', size=100)
    att = fields.Char('ATT.', size=100)
    destino = fields.Char('Destino', size=100)
    # nuevo estado
    state= fields.Selection(selection_add=[('send','Presupuestado')])
    # lote no requerido en reparaciones porque puede ser un historico
    # lot_id = fields.Many2one(required= True)
    accs = fields.One2many(comodel_name='mrp.repair.accs', inverse_name='repair_id', string='accs Lines', readonly=False, 
        states={'done': [('readonly', True)]})
    invoice_method = fields.Selection(selection_add=[('picking','En Albaran'),('warranty','En garantia')],readonly=False,
        states={'done':[('readonly', True)]})
    picking_out = fields.Many2one('stock.picking', string='Picking Out',readonly=True)
    sale_id = fields.Many2one('sale.order', string='Sale Order',readonly=True)

    repaired_by = fields.Many2one('res.users',string='Reparado por')
    con_linea = fields.Boolean(string='Crear línea con aparato reparado', default=True)
    

    def action_repair_start(self, cr, uid, ids, context=None):
        super(mrp_repair, self).action_repair_start(cr, uid, ids, context=context)

        for order in self.browse(cr, uid, ids, context=context):
            val = {}
            val['repair_ready_date'] = datetime.now().date()
            self.write(cr, uid, [order.id], val)
        return True


    def action_repair_end(self, cr, uid, ids, context=None):
        #antes vamos a llamar a un wizard para registrar el tecnico que hizo la reparacion
        for order in self.browse(cr, uid, ids, context=context):
            if not order.repaired_by:
                raise exceptions.Warning(
                    _("No se puede registrar la finalización sin recoger un técnico."))

        #crear albaran de salida como en un repair done
        self.action_repair_done(cr,uid,ids,context=context)

    	super(mrp_repair, self).action_repair_end(cr, uid, ids, context=context)

        for order in self.browse(cr, uid, ids, context=context):
            val = {}
            # val['fecha_reparacion'] = fields.Date.today()
            val['fecha_reparacion'] = datetime.now().date()
            self.write(cr, uid, [order.id], val)
        return True


    def action_cancel(self, cr, uid, ids, context=None):
        super(mrp_repair, self).action_cancel(cr, uid, ids, context=context)

        for order in self.browse(cr, uid, ids, context=context):
            val = {}
            # val['fecha_esperar'] = fields.Date.today()
            val['fecha_esperar'] = datetime.now().date()
            self.write(cr, uid, [order.id], val)
        return True


    def action_cancel_draft(self, cr, uid, ids, *args):
        super(mrp_repair, self).action_cancel_draft(cr, uid, ids, *args)

        for order in self.browse(cr, uid, ids, context=None):
            val = {}
            val['fecha_esperar'] = False
            self.write(cr, uid, [order.id], val)
        return True


    def onchange_location_id(self, cr, uid, ids, location_id=None):
        # evita el cambio de la direccion de entrega cuando cambia la de origen
        super(mrp_repair, self).onchange_location_id(cr, uid, ids, location_id=None)
        return True


    @api.one
    def button_enviado(self):
        self.state = 'send'


    @api.onchange('lot_id')
    def _onchange_lot_id(self):
        if self.lot_id:
            self.product_id = self.lot_id.product_id.id
            self.product_uom = self.lot_id.product_id.uom_id.id
            st_lot = self.env['stock.move'].search([('restrict_lot_id','=',self.lot_id.id)])
            #suponemos un lote asociado a un solo cliente
            if st_lot and st_lot[0].partner_id:
                self.partner_id = st_lot[0].partner_id.id


    # no permitir un dia anterior al de inicio de reparacion
    @api.onchange('fecha_reparacion')
    def _onchange_fecha_reparacion(self):
        if self.fecha_reparacion and self.repair_ready_date:
            if self.repair_ready_date > self.fecha_reparacion:
                raise exceptions.Warning(
             _("No se puede registrar un día de finalización anterior al de inicio de la reparación"))


    def _prepare_stock_picking(self, cr, uid, ids, move, loc_id, context=None):
        StockPickingType = self.pool.get('stock.picking.type')
        stock_move = self.pool.get('stock.move')
        stock_mv = stock_move.browse(cr,uid,move)
        outgoing_type = StockPickingType.search(cr,uid,
            [('code', '=', 'outgoing'),
             #('warehouse_id', '=', stock_mv.warehouse_id.id),
             ('default_location_dest_id','=',loc_id)],limit=1)
        values = {'origin': stock_mv.origin,
                  'company_id': stock_mv.company_id.id,
                  'move_type': stock_mv.group_id.move_type or 'direct',
                  'partner_id': stock_mv.partner_id.id,
                  'picking_type_id': outgoing_type[0],
                  }  
        # logger.error('Values en prepare stock picking %s'%values)
        return values

    # @api.v7
    # def action_repair_done(self, cr, uid, ids, context=None):
        
    #     ir_values = self.pool.get('ir.values')
    #     rep_loc_dest_id = ir_values.get_default(cr,uid,'mrp.config.settings', 'repair_location_dest_id')

    #     if not rep_loc_dest_id:
    #         raise exceptions.Warning(
    #          _("Debe asociar un almacén de destino para reparaciones en la configuración de producción"))

    #     # res = super(mrp_repair, self).action_repair_done()

    #     res = {}
    #     move_obj = self.pool.get('stock.move')
    #     repair_line_obj = self.pool.get('mrp.repair.fee')

    #     StockLocation = self.pool.get('stock.location')
    #     StockPicking = self.pool.get('stock.picking')
        
    #     for repair in self.browse(cr, uid, ids, context=context):
    #         move_ids = []

    #         move_id = move_obj.create(cr, uid, {
    #             'name': "REPARACION "+ repair.product_id.name_template+" "+repair.lot_id.name,
    #             'product_id': repair.product_id.id,
    #             'product_uom': repair.product_uom.id or repair.product_id.uom_id.id,
    #             'product_uom_qty': repair.product_qty,
    #             'partner_id': repair.partner_id and repair.partner_id.id or False,
    #             'location_id': rep_loc_dest_id,
    #             'location_dest_id': rep_loc_dest_id,
    #             'restrict_lot_id': repair.lot_id.id,
    #             'origin': repair.name,
    #             'price_unit': 0.0,
    #             'discount': 0.0,
    #             'sequence': 0,
    #         })
    #         move_ids.append(move_id)

    #         # move_obj.action_done(cr, uid, move_id, context=context)
    #         # val_lot = self._prepare_stock_picking(cr, uid, ids, move_id, rep_loc_dest_id, context=context)
    #         # pick_lot = StockPicking.create(cr,uid,val_lot, context=context)
    #         # move_obj.write(cr,uid,move_id,{'picking_id': pick_lot}, context=context)

    #         mov_seq = 1
    #         for move in repair.fees_lines:
    #             if move.to_invoice:
    #                 mov_id = move_obj.create(cr, uid, {
    #                     'name': move.name,
    #                     'product_id': move.product_id.id,
    #                     'product_uom_qty': move.product_uom_qty,
    #                     'product_uom': move.product_uom.id,
    #                     'partner_id': repair.partner_id and repair.partner_id.id or False,
    #                     'location_id': repair.location_id.id,
    #                     'location_dest_id': rep_loc_dest_id,
    #                     'origin': repair.name,
    #                     'price_unit': move.price_unit,
    #                     'discount':move.discount,
    #                     'sequence': mov_seq
    #                 })
    #                 mov_seq += 1
    #                 move_ids.append(mov_id)
    #                 # repair_line_obj.write(cr, uid, [move.id], {'move_id': move_id, 'state': 'done'}, context=context)
                        
    #         move_obj.action_done(cr, uid, move_ids, context=context)

    #         self.write(cr, uid, [repair.id], {'state': 'done', 'move_id': move_id}, context=context)
    #         res[repair.id] = move_id

           
    #         if repair.partner_id and repair.move_id:
    #             wh_id = StockLocation.get_warehouse(cr, uid, repair.location_dest_id,context)
    #             if not repair.move_id.warehouse_id:
    #                 move_obj.write(cr, uid, move_ids[0], {'warehouse_id': wh_id}, context=context)
    #             values = self._prepare_stock_picking(cr, uid, ids, move_ids[0], rep_loc_dest_id, context=context)
    #             pick = StockPicking.create(cr,uid,values, context=context)
    #             pick_type = StockPicking.browse(cr,uid,pick)
    #             StockPicking.write(cr,uid,pick,{'repair_id':repair.id},context=context)
    #             self.write(cr, uid, [repair.id], {'picking_out': pick}, context=context)
    #             # move_obj.write(cr, uid, [move_id],{'picking_type_id': pick_type.picking_type_id.id,
    #             #     'picking_id': pick}, context=context)

    #             for m in move_ids:
    #                 move_obj.write(cr,uid,m,{'picking_type_id': pick_type.picking_type_id.id,
    #                             'picking_id': pick}, context=context)
    #                 if repair.invoice_method=='picking':
    #                     move_obj.write(cr, uid, m,{'invoice_state': '2binvoiced'}, context=context)
    #                 else:
    #                     move_obj.write(cr, uid, m,{'invoice_state': 'none'}, context=context)

    #     return res


    # cambiamos criterio: creamos un pedido de venta confirmado en lugar de un albaran para gestionar bien precios
    @api.v7
    def action_repair_done(self, cr, uid, ids, context=None):
        
        ir_values = self.pool.get('ir.values')
        rep_loc_dest_id = ir_values.get_default(cr,uid,'mrp.config.settings', 'repair_location_dest_id')

        if not rep_loc_dest_id:
            raise exceptions.Warning(
             _("Debe asociar un almacén de destino para reparaciones en la configuración de producción"))

        res = {}
        move_obj = self.pool.get('stock.move')
        sale_obj = self.pool.get('sale.order')
        line_obj = self.pool.get('sale.order.line')
        repair_line_obj = self.pool.get('mrp.repair.fee')
        StockPicking = self.pool.get('stock.picking')
        procur_obj = self.pool.get('procurement.order')

        template_obj = self.pool.get('product.template').search(cr,uid,[('is_free_text','=',True)])
        
        if not template_obj:
            raise exceptions.Warning(
             _("Debe existir un producto para descripción libre de texto"))

        product_obj = self.pool.get('product.product').search(cr,uid,[('product_tmpl_id','=',template_obj[0])])

        product_text = self.pool.get('product.product').browse(cr,uid,product_obj[0])

        sale_type = self.pool.get('sale.order.type').search(cr,uid,[('order_policy','=','picking')],limit=1)

        if not sale_type:
            raise exceptions.Warning(
             _("Debe existir un tipo de pedido para facturar desde albarán"))

        for repair in self.browse(cr, uid, ids, context=context):
             #solo ejecutamos si no tiene ya un albaran relacionado
            if repair.picking_out:
                continue

            vals_order={}
            vals_order['name'] = repair.name
            vals_order['origin'] = repair.name
            vals_order['state'] = 'sent'
            vals_order['order_policy'] = 'picking'
            vals_order['user_id'] = uid
            vals_order['partner_id']= repair.partner_id.id
            vals_order['type_id'] = sale_type[0] or 1
            vals_order['depart'] = repair.depart
            vals_order['destino'] = repair.destino
            vals_order['att'] = repair.att
            vals_order['client_order_ref'] = repair.num_pedido


            if repair.invoice_method == 'warranty':
                vals_order['payment_mode_id'] = False

            new_sale = sale_obj.create (cr, uid, vals_order,context=context)

            # primero lineas con cargos de secuencia 1 en adelante
            seq = 1
            for fee in repair.fees_lines:
                values = {}
                values['order_id'] = new_sale
                values['sequence'] = fee.sequence
                values['state'] = 'draft'
                values['product_id'] = fee.product_id.id
                values['name'] = fee.name
                values['product_uom'] = fee.product_uom.id
                values['product_uom_qty']= fee.product_uom_qty
                values['price_unit'] = fee.price_unit
                values['discount'] = fee.discount
                values['tax_id'] = [(6, 0, [i.id for i in fee.tax_id])]
                seq+=1
                line_obj.create(cr,uid,values,context=context)
                line_obj.product_id_change(cr, uid, ids, repair.pricelist_id.id, values['product_id'],
                                             qty=values['product_uom_qty'], uom=False, qty_uos=0, uos=False, name='', partner_id=vals_order['partner_id'],
                                             lang=False, update_tax=True, date_order=False, packaging=False, fiscal_position=False, flag=False, context=None)

            # linea con producto de texto libre y sin lote
            # el movimiento de reparacion se registra fuera del pedido facturable
            if repair.con_linea:
                val_rep={}
                val_rep['order_id'] = new_sale
                val_rep['sequence'] = 0
                val_rep['state'] = 'draft'
                val_rep['product_id'] = product_text.id
                # val_rep['lot_id'] = repair.lot_id.id
                val_rep['name'] = "REPARACION "+ repair.product_id.name+" "+repair.lot_id.name
                val_rep['product_uom'] = product_text.uom_id.id
                val_rep['product_uom_qty']= repair.product_qty
                val_rep['price_unit'] = 0.0

                line_obj.create(cr,uid,val_rep,context=context)

                line_obj.product_id_change(cr, uid, ids, repair.pricelist_id.id, val_rep['product_id'],
                                                 qty=val_rep['product_uom_qty'], uom=False, qty_uos=0, uos=False, name='', partner_id=vals_order['partner_id'],
                                                 lang=False, update_tax=True, date_order=False, packaging=False, fiscal_position=False, flag=False, context=None)

            sale_obj.button_dummy(cr, uid, new_sale, context=None)
            sale_obj.action_button_confirm(cr, uid, new_sale, context=None)

            #buscamos el picking generado para asociarlo a la orden de reparacion
            sale_lines = line_obj.search(cr,uid,[('order_id','=',new_sale)])
            group_id = False
            for s in sale_lines:
                proc_group = procur_obj.search(cr,uid,[('sale_line_id','=',s)])
                if proc_group:
                    group_id = procur_obj.browse(cr,uid,proc_group[0]).group_id.id


            self.write(cr, uid, [repair.id], {'state': 'done', 'sale_id':new_sale}, context=context)
            if group_id:
                pick_repair = StockPicking.search(cr,uid,[('group_id','=',group_id)])
                if pick_repair:
                    self.write(cr, uid, [repair.id], {'picking_out': pick_repair[0]}, context=context)
                    StockPicking.write(cr,uid,pick_repair[0],{'repair_id':repair.id})
                    # si la reparacion es en garantia o no facturar lo marcamos como no facturable
                    # y damos salida a las piezas, nadie lo va a mirar si no.
                    if repair.invoice_method == 'warranty' or repair.invoice_method == 'none':
                        StockPicking.write(cr,uid,pick_repair[0],{'invoice_state':'none'})
                    act_move = move_obj.search(cr, uid,[('picking_id','=',pick_repair[0])])
                    for m in act_move:
                        move_obj.action_done(cr, uid, m, context=context)


            # debemos crear el stock.move del producto reparado
            move_id = move_obj.create(cr, uid, {
                'name': "REPARACION "+ repair.product_id.name_template+" "+repair.lot_id.name,
                'product_id': repair.product_id.id,
                'product_uom': repair.product_uom.id or repair.product_id.uom_id.id,
                'product_uom_qty': repair.product_qty,
                'partner_id': repair.partner_id and repair.partner_id.id or False,
                'location_id': rep_loc_dest_id,
                'location_dest_id': rep_loc_dest_id,
                'restrict_lot_id': repair.lot_id.id,
                'origin': repair.name,
            })
            val_lot = self._prepare_stock_picking(cr, uid, ids, move_id, rep_loc_dest_id, context=context)
            pick_lot = StockPicking.create(cr,uid,val_lot, context=context)
            move_obj.write(cr,uid,move_id,{'picking_id': pick_lot}, context=context)

            move_obj.action_done(cr, uid, move_id, context=context)


            res[repair.id] = new_sale

        return res




    # @api.v7
    # def action_invoice_create(self, cr, uid, ids, group=False, context=None):
    #     res = super(mrp_repair, self).action_invoice_create(cr, uid, ids, group=False, context=context)
    #     # logger.error('Valor de res al invoice create %s'%res)
    #     inv_obj = self.pool.get('account.invoice')
    #     rep_journal_id = 1
    #     ir_values = self.pool.get('ir.values')
    #     rep_journal_id = ir_values.get_default(cr,uid,'mrp.config.settings', 'repair_journal_id')
    #     rep_loc_dest_id = ir_values.get_default(cr,uid,'mrp.config.settings', 'repair_location_dest_id')
    #     # logger.error('Valor del rep journal de config %s'%rep_journal_id)
        

    #     if not rep_journal_id:
    #         raise exceptions.Warning(
    #          _("Debe asociar un diario de reparaciones en la configuración de producción"))

    #     if not rep_loc_dest_id:
    #         raise exceptions.Warning(
    #          _("Debe asociar un almacén de destino para reparaciones en la configuración de producción"))

    #     for val in res:
    #         stock_move = self.pool.get('stock.move')
    #         # picking_type = self.pool.get('stock.picking.type')
    #         # search_cond_pick = [('code','like','outgoing'),('default_location_src_id','=',rep_loc_dest_id)]
    #         # picking_type_id = picking_type.search(cr, uid, search_cond_pick)
    #         # if not picking_type_id:
    #         #     raise exceptions.Warning(
    #         #         _("Debe crear un tipo de movimiento en stock para las reparaciones"))

    #         for repair in self.browse(cr, uid, ids, context=context):

    #             # logger.error('Valor del invoice rescatado de res %s'%res[val])
    #             # logger.error('Valor del origen %s'%repair.location_id.id)

    #             # ponemos alter_stock a false porque ahora en el albaran se registran ya los consumos
    #             if repair.company_id:
    #                 company_obj = self.pool.get('res.company').browse(cr,uid,repair.company_id.id)
    #                 inv_obj.write(cr,uid,res[val],{'repair_id': val, 'alter_stock': False,
    #                 'stock_loc_src_id':repair.location_id.id, 'stock_loc_dest_id':rep_loc_dest_id,
    #                 'journal_id':rep_journal_id,'partner_bank_id':company_obj.bank_ids[0].id})
    #             else:
    #                 inv_obj.write(cr,uid,res[val],{'repair_id': val, 'alter_stock': False,
    #                 'stock_loc_src_id':repair.location_id.id, 'stock_loc_dest_id':rep_loc_dest_id,
    #                 'journal_id':rep_journal_id})

    #     return res



    # @api.multi
    # def action_invoice_create(self, group=False):
    #     res = super(mrp_repair, self).action_invoice_create(group)

    #     rep_journal_id = 1
    #     ir_values = self.env['ir.values']
    #     rep_journal_id = ir_values.get_default('mrp.config.settings', 'repair_journal_id')
    #     rep_loc_dest_id = ir_values.get_default('mrp.config.settings', 'repair_location_dest_id')
    #     inv_obj = self.env['account.invoice']

    #     if not rep_journal_id:
    #         raise exceptions.Warning(
    #          _("Debe asociar un diario de reparaciones en la configuración de producción"))

    #     if not rep_loc_dest_id:
    #         raise exceptions.Warning(
    #          _("Debe asociar un almacén de destino para reparaciones en la configuración de producción"))

    #     for repair in self:
    #         operations = repair.operations.filtered('to_invoice')
    #         for op in operations:
    #             op.invoice_line_id.discount = op.discount
    #         if operations:
    #             repair.invoice_id.button_reset_taxes()

    #         fees = repair.fees_lines.filtered('to_invoice')
    #         for f in fees:
    #             f.invoice_line_id.discount = f.discount
    #         if fees:
    #             repair.invoice_id.button_reset_taxes()

    #     for val in res:
    #         for rep in self:
    #             if rep.company_id:
    #                 company_obj = self.env['res.company'].browse(rep.company_id.id)
    #                 inv_obj.browse(res[val]).write({'repair_id': val, 'alter_stock': False,
    #                 'stock_loc_src_id':rep.location_id.id, 'stock_loc_dest_id':rep_loc_dest_id,
    #                 'journal_id':rep_journal_id,'partner_bank_id':company_obj.bank_ids[0].id})
    #             else:
    #                 inv_obj.write(res[val],{'repair_id': val, 'alter_stock': False,
    #                 'stock_loc_src_id':rep.location_id.id, 'stock_loc_dest_id':rep_loc_dest_id,
    #                 'journal_id':rep_journal_id})


    #     return res



    @api.multi
    def action_invoice_create(self, group=False):
        #redefinimos la funcion, ahora solo sera facturar el albaran de salida si existe, si no lo normal:

        for repair in self:
            if repair.picking_out:
                pick_out = self.env['stock.picking'].browse(repair.picking_out.id)
                #si no esta transferido, transferirlo primero
                if repair.picking_out.state not in ('cancel','done'):
                    pick_out.action_done()

                #facturar albaran
                rep_journal_id = 1
                ir_values = self.env['ir.values']
                rep_journal_id = ir_values.get_default('mrp.config.settings', 'repair_journal_id')

                res = pick_out.action_invoice_create(rep_journal_id, group=False, type='out_invoice')

                repair_invoice = self.env['account.invoice'].browse(res[0])
                repair_invoice.write({
                    'repair_id':repair.id,
                    'name':repair.name,
                    'comment': repair.quotation_notes,
                    })

                repair.write({'invoiced': True, 'invoice_id': res[0], 'state':'done'})
            else:
                res = super(mrp_repair, self).action_invoice_create(group)
        return res


    @api.v7
    def _amount_tax(self, cr, uid, ids, field_name, arg, context=None):
        """ Calculates taxed amount with discount on lines.
        @param field_name: Name of field.
        @param arg: Argument
        @return: Dictionary of values.
        """
        res = {}
        #return {}.fromkeys(ids, 0)
        cur_obj = self.pool.get('res.currency')
        tax_obj = self.pool.get('account.tax')
        for repair in self.browse(cr, uid, ids, context=context):
            val = 0.0
            cur = repair.pricelist_id.currency_id
            for line in repair.operations:
                #manage prices with tax included use compute_all instead of compute
                if line.to_invoice:
                    tax_calculate = tax_obj.compute_all(cr, uid, line.tax_id, line.price_unit * (1-(line.discount or 0.0)/100.0), 
                        line.product_uom_qty, line.product_id, repair.partner_id)
                    for c in tax_calculate['taxes']:
                        val += c['amount']

            for fee in repair.fees_lines:
                if fee.to_invoice:
                    # logger.error('##### AIKO ###### El amount_tax en fees_lines con discount:%s'%fee.discount)
                    tax_calculate = tax_obj.compute_all(cr, uid, fee.tax_id, fee.price_unit * (1-(fee.discount or 0.0)/100.0),
                        fee.product_uom_qty, fee.product_id, repair.partner_id)
                    for c in tax_calculate['taxes']:
                        # logger.error('##### AIKO ###### El amount_tax valor a sumar en amount_tax:%s'%c['amount'])
                        val += c['amount']

            res[repair.id] = cur_obj.round(cr, uid, cur, val)
        return res


    _columns = {
        # Must be defined in old API so that we can call super in the compute
        'amount_tax': old_fields.function(
            _amount_tax, string='Taxes',
            digits_compute=dp.get_precision('Account'),
            store= True),
    }



class mrp_repair_fee(models.Model):
    _inherit = ['mrp.repair.fee']

    discount = fields.Float(string='Discount(%)', digits_compute=dp.get_precision('Account'))
    sequence = fields.Integer(string='Sequence', default=50)

    _order = 'sequence, id'

    @api.multi
    def _amount_line(self, field_name, arg):
        res = super(mrp_repair_fee, self)._amount_line(field_name, arg)
        for line in self.filtered('discount'):
            price = res[line.id] * (1 - (line.discount or 0.0) / 100.0)
            res[line.id] = price
        return res

    @api.onchange('product_id')
    def _onchange_product_id(self):
        for s in self:
            if s.repair_id.invoice_method == 'warranty':
                s.discount = 100.0


    _columns = {
        # Must be defined in old API so that we can call super in the compute
        'price_subtotal': old_fields.function(
            _amount_line, string='Subtotal',
            digits_compute=dp.get_precision('Account')),
    }




class mrp_repair_accs(models.Model):
    _name = 'mrp.repair.accs'

    name = fields.Char('Description', required=True)
    repair_id = fields.Many2one('mrp.repair', 'Repair Order Reference', ondelete='cascade', select=True)
    product_id = fields.Many2one('product.product', 'Product')
    product_uom_qty = fields.Float('Quantity', digits_compute=dp.get_precision('Product Unit of Measure'), required=True)


    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.name= self.product_id.name


class mrp_production(models.Model):
    _inherit = ['mrp.production']

    # paramos el uso de lot_id porque vendra de la linea de venta
    # lot_id= fields.Many2one('stock.production.lot', 'Numero serie')
    # utilizamos mrp_sale_info para tener el campo partner_id relacionado con el pedido de venta

    venting = fields.Char('Venting', size=100)
    observaciones_impresion = fields.Char('Observaciones de impresion', size=100)
    referencia = fields.Char('Referencia', size=100)
    #el campo gabinete en la orden de produccion que se refiere al grupo de cliente (paciente, hospital,...)
    gabinete = fields.Many2one(string='Gabinete', related='partner_id.partner_type_id', readonly='True')
    #el campo cliente_de para registrar los pedidos de Oviedo a traves de la etiqueta del cliente
    cliente_de = fields.Many2many(string='Cliente de', related='partner_id.category_id', readonly='True')
    accs = fields.One2many(comodel_name='mrp.production.accs', inverse_name='production_id', string='accs Lines', 
        readonly=False, states={'done': [('readonly', True)]})


    
'''
    @api.onchange('lot_id')
    def _onchange_lot_id(self):
        if self.lot_id:
            self.product_id = self.lot_id.product_id.id
            self.product_uom = self.lot_id.product_id.uom_id.id
'''
# nuevo valor en product para identificar el producto de texto libre
class product_template(models.Model):
    _inherit = ['product.template']

    is_free_text = fields.Boolean('Is Free Text')



class stock_pack_operation(models.Model):
    _inherit = ['stock.pack.operation']


    @api.depends('picking_id','product_id')
    def _get_lot_from_move(self):
        stock_move_obj = self.env['stock.move']
        for s in self:
            stock_mv = stock_move_obj.search([('picking_id','=',s.picking_id.id),('product_id','=',s.product_id.id)])
            for mv in stock_mv:
                if mv.restrict_lot_id:
                    s.lot_id = mv.restrict_lot_id.id

    lot_id = fields.Many2one(compute='_get_lot_from_move')



class mrp_production_accs(models.Model):
    _name = 'mrp.production.accs'

    name = fields.Char('Description', required=True)
    production_id = fields.Many2one('mrp.production', 'Production Order Reference', ondelete='cascade', select=True)
    product_id = fields.Many2one('product.product', 'Product')
    product_uom_qty = fields.Float('Quantity', digits_compute=dp.get_precision('Product Unit of Measure'), required=True)


    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.name= self.product_id.name


class mrp_product_produce(models.TransientModel):
    _inherit = ['mrp.product.produce']


    def _get_lotid(self):

        ids = self.env.context.get('active_ids', [])
        if ids:
            prod = self.env['mrp.production'].browse(ids[0])
            # logger.error('##### AIKO ###### El valor de prod en product.produce al lot_id:%s'%prod)
            if prod.sale_lot_id:
                return prod.sale_lot_id.id

    lot_id = fields.Many2one(default=_get_lotid)



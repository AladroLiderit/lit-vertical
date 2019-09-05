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




class mrp_repair(models.Model):
    _inherit = ['mrp.repair']

    _order = "fecha_recepcion DESC, name"


    referencia = fields.Char('Referencia', size=100)
    # las fechas ahora las instala mrp_repair_laborales aqui solo damos un default
    fecha_recepcion = fields.Date(default=lambda self: fields.datetime.now())
    # nuevo estado
    state= fields.Selection(selection_add=[('send','Presupuestado')])
    invoice_method = fields.Selection(selection_add=[('warranty','En garantia')],readonly=False,
        states={'done':[('readonly', True)]})
    

    def action_repair_start(self, cr, uid, ids, context=None):
        super(mrp_repair, self).action_repair_start(cr, uid, ids, context=context)

        for order in self.browse(cr, uid, ids, context=context):
            val = {}
            val['repair_ready_date'] = datetime.now().date()
            self.write(cr, uid, [order.id], val)
        return True


    def action_repair_end(self, cr, uid, ids, context=None):
        #crear albaran de salida como en un repair done
        self.action_repair_done(cr,uid,ids,context=context)

    	super(mrp_repair, self).action_repair_end(cr, uid, ids, context=context)

        for order in self.browse(cr, uid, ids, context=context):
            val = {}
            val['fecha_reparacion'] = datetime.now().date()
            self.write(cr, uid, [order.id], val)
        return True


    def onchange_location_id(self, cr, uid, ids, location_id=None):
        # evita el cambio de la direccion de entrega cuando cambia la de origen
        super(mrp_repair, self).onchange_location_id(cr, uid, ids, location_id=None)
        return True


    # no permitir un dia anterior al de inicio de reparacion
    @api.onchange('fecha_reparacion')
    def _onchange_fecha_reparacion(self):
        if self.fecha_reparacion and self.repair_ready_date:
            if self.repair_ready_date > self.fecha_reparacion:
                raise exceptions.Warning(
             _("No se puede registrar un día de finalización anterior al de inicio de la reparación"))


    @api.onchange('invoice_method')
    def _onchange_invoice_method(self):
        if self.invoice_method == 'warranty':
            for f in self.fees_lines:
                f.discount = 100.0
        else:
            for f in self.fees_lines:
                if f.discount == 100:
                    f.discount = 0.0


    @api.multi
    def action_invoice_create(self, group=False):

        res = super(mrp_repair, self).action_invoice_create(group)

        repair_invoice = self.env['account.invoice'].browse(res[0])
        repair_invoice.write({
                    'repair_id':repair.id,
                    'name':repair.name,
                    'comment': repair.quotation_notes,
                    })
                
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


    _columns = {
        # Must be defined in old API so that we can call super in the compute
        'price_subtotal': old_fields.function(
            _amount_line, string='Subtotal',
            digits_compute=dp.get_precision('Account')),
    }


    @api.v7
    def onchange_product_id(self, cr, uid, ids, pricelist, product, uom=False,
                          product_uom_qty=0, partner_id=False, guarantee_limit=False, active_id=False, context=None):
        logger.error('##### AIKO ###### En onchange_product_id valor de active_id: %s',active_id)
        res = super(mrp_repair_fee, self).product_id_change(cr,uid,ids,pricelist, product, uom=uom,
            product_uom_qty=product_uom_qty, partner_id=partner_id, guarantee_limit=guarantee_limit,context=context)
        result = res['value']
        warning = res['warning']

        if active_id:
            rep = self.browse(cr, uid, active_id, context=context)
            logger.error('##### AIKO ###### En onchange_product_id valor de rep: %s',rep)
            if rep.repair_id and rep.repair_id.invoice_method == 'warranty':
                logger.error('##### AIKO ###### En onchange_product_id invoice warranty')
                result['discount']= 100.0

        return {'value': result, 'warning': warning}


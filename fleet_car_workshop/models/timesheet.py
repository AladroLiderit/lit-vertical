# -*- coding: utf-8 -*-
##############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#    Copyright (C) 2008-TODAY Cybrosys Technologies(<http://www.cybrosys.com>).
#    Author: Nilmar Shereef(<http://www.cybrosys.com>)
#    you can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    It is forbidden to publish, distribute, sublicense, or sell copies
#    of the Software or modified copies of the Software.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    GENERAL PUBLIC LICENSE (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp import fields, models, api


class PlannedWork (models.Model):
    _name = 'planned.work'

    planned_work = fields.Many2one('product.template', string='Planned work', domain=[('type', '=', 'service')])
    time_spent = fields.Float(string='Estimated Time', default=1)
    work_date = fields.Datetime(string='Date')
    responsible = fields.Many2one('res.users', string='Responsible')
    work_id = fields.Many2one('car.workshop', string="Work id")
    work_price = fields.Float(string="Service Price")
    work_discount = fields.Float(string="Dto.")
    work_cost = fields.Float(string="Service Cost")
    completed = fields.Boolean(string="Completed")
    duration = fields.Float(string='Duration')
    work_date2 = fields.Datetime(string='Date')
    tax_ids = fields.Many2many('account.tax', 'car_work_account_tax_rel',
            'car_work_id', 'tax_id', 'Taxes')

    @api.onchange('planned_work')
    def get_price(self):
        self.work_cost = self.planned_work.lst_price * (1-(self.work_discount/100)) * self.time_spent
        self.work_price = self.planned_work.lst_price
        self.tax_ids = self.planned_work.taxes_id

    @api.onchange('work_discount')
    def get_discount_price(self):
        self.work_cost = self.planned_work.lst_price * (1-(self.work_discount/100)) * self.time_spent
        self.work_price = self.planned_work.lst_price
        self.tax_ids = self.planned_work.taxes_id

    @api.onchange('time_spent')
    def get_spent_price(self):
        self.work_cost = self.planned_work.lst_price * (1-(self.work_discount/100)) * self.time_spent
        self.work_price = self.planned_work.lst_price
        self.tax_ids = self.planned_work.taxes_id


class MaterialUsed (models.Model):
    _name = 'material.used'

    def _get_default_taxes(self):

        if 'default_vehicle_id' in context:
            vehicle = self.pool.get('car.car').browse(cr, uid, context['default_vehicle_id'], context=context)
            if vehicle and vehicle.partner_id:
                return vehicle.partner_id.id
        return False

    material = fields.Many2one('product.template', string='Products')
    description = fields.Char(string='Description', required=True)
    amount = fields.Integer(string='Quantity', default=1)
    price = fields.Float(string='Unit Price')
    discount = fields.Float(string='Dto.')
    material_id = fields.Many2one(string='car.workshop')
    tax_ids = fields.Many2many('account.tax', 'car_material_account_tax_rel',
            'car_material_id', 'tax_id', 'Taxes')

    @api.onchange('material')
    def get_price(self):
        self.price = self.material.lst_price
        self.tax_ids = self.material.taxes_id
        self.description = self.material.name


from openerp import models, fields, api
from openerp.addons import decimal_precision as dp
import logging
logger = logging.getLogger(__name__)

class st_parameters(models.Model):
    _inherit = 'st.parameters'
    line_price_ids = fields.One2many('st.parameters_line_price', 'line_price_id', copy=True, string='Prices lines')
class st_parameters_line_price(models.Model):
    _name = 'st.parameters_line_price'
    _order = 'price_to asc'

    line_price_id = fields.Many2one('st.parameters', string='line price', ondelete='cascade')
    price_to = fields.Float(
        'Price To', digits=dp.get_precision('Product Price'),
        help="Price ladder pvp to apply a retail factor")
    factor = fields.Float(
        'Incremental factor', digits=dp.get_precision('Product Price'),
        help="Factor increasing the price for the retail price list", default = 1)

    _sql_constraints = [('name_uniq', 'unique (price_to)', " Price already exists !")]

    @api.onchange('price_to','factor')
    def _onchange_price_param(self):
        temp_obj = self.env['product.template']

        for temp in temp_obj.search([]):
            temp._amount_final_price_template()


class product_template(models.Model):
    _inherit = 'product.template'
  
    @api.one
    @api.depends('list_price','company_id.st_parameters_ids.line_price_ids')
    def _amount_final_price_template(self): 
        #
        # parameters_obj = self.pool.get('st.parameters') 
        # par00 = parameters_obj.search(self.env.cr, self.env.uid, [('par_name', '=','pa00'), ('company_id', '=', self.company_id.id)], limit=1)
        # par =  parameters_obj.browse(self.env.cr, self.env.uid, par00, context=None)   

        par = self.env['st.parameters'].search([('par_name', '=','pa00'), ('company_id', '=', self.company_id.id)],limit=1)
               
        for p in self:
            p.precio_catalogo = p.list_price
            
            if par and par.line_price_ids:                
                for pr in par.line_price_ids:
                    if p.list_price <= pr.price_to:  
                        p.precio_catalogo = float(p.list_price * pr.factor)
                        break  
            
         
    precio_catalogo = fields.Float(string='Catalogue price', compute='_amount_final_price_template', store=True, default=False)                                         

class res_company(models.Model):
    _inherit = 'res.company'

    st_parameters_ids = fields.One2many (comodel_name='st.parameters', inverse_name='company_id')
import openerp
from openerp import tools, api
from openerp.osv import osv, fields
from openerp.osv.expression import get_unaccent_wrapper
from openerp.tools.translate import _


class res_partner(osv.osv):
    _inherit = "res.partner"

    _columns = {'type': fields.selection([('default', 'Default'), ('invoice', 'Invoice'),
                                   ('delivery', 'Shipping'), ('contact', 'Contact'),
                                   ('advertising',_('Advertising')),
                                   ('commitment',_('Commitment')),
                                   ('other', 'Other')], 'Address Type',
            help="Used to select automatically the right address according to the context in sales and purchases documents.")}
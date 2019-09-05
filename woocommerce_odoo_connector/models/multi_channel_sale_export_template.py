from openerp import api,models,fields
import logging
_logger = logging.getLogger(__name__)

class ExportTemplates(models.TransientModel):
    _inherit = 'export.templates'

    @api.multi
    def submit(self):
        message=''
        if self.operation == 'export':
            message = self.channel_id.action_export_woocommerce_products()
        else:
            message = self.channel_id.action_update_woocommerce_products()
        return message


class ExportCategories(models.TransientModel):
    _inherit = 'export.categories'

    @api.multi
    def submit(self):
        message=''
        if self.operation == 'export':
            message = self.channel_id.export_woocommerce_categories(0)
        else:
            message = self.channel_id.action_export_update_woocommerce_categories()
        return message


class ExportPartners(models.TransientModel):
    _inherit = 'export.partners'

    @api.multi
    def submit(self):
        message=''
        if self.operation == 'export':
            message = self.channel_id.export_woocommerce_customer_value()
        else:
            message = self.channel_id.action_update_woocommerce_customers()
        return message
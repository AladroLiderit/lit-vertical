from openerp import models, api, fields



class WizardUpdateInvoiceSupplierinfo(models.TransientModel):
	 _inherit = 'wizard.update.invoice.supplierinfo'
	 _name='wizard.update.invoice.supplierinfo'
	 @api.multi
	 def update_supplierinfo(self):
		self.ensure_one()
		supplierinfo_obj = self.env['product.supplierinfo']
		partnerinfo_obj = self.env['pricelist.partnerinfo']
		for line in self.line_ids:
			supplierinfo = line.supplierinfo_id
			partnerinfo = line.partnerinfo_id

			# Create supplierinfo if not exist
			if not supplierinfo:
				supplierinfo_vals = line._prepare_supplierinfo()
				supplierinfo = supplierinfo_obj.create(supplierinfo_vals)

			partnerinfo_vals = line._prepare_partnerinfo(supplierinfo)

			# Create partnerinfo if not exist
			if not line.partnerinfo_id:
				partnerinfo_obj.create(partnerinfo_vals)

			# Update partnerinfo, if exist
			else:
				partnerinfo.write(partnerinfo_vals)


			line.product_id.product_tmpl_id.standard_price = line.new_price

		# Mark the invoice as checked
		self.invoice_id.write({'supplierinfo_ok': True})
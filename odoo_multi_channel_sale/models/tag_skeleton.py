# -*- coding: utf-8 -*-
#################################################################################
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>
# Developed By: Jahangir Ahmad
#################################################################################
from openerp import fields ,models, api, _

class ChannelTagMappings(models.Model):

	_name="channel.tag.mappings"
	_inherit = ['channel.mappings']
	_rec_name = "tag_name"

	store_tag_id =  fields.Char(string='Store Tag ID',required=True)
	odoo_tag_id = fields.Integer(string='Odoo Tag ID',required=True)
	tag_name = fields.Many2one('st.type_material',string='Material')
	# leaf_category = fields.Boolean(string='Leaf Category')
	_sql_constraints = [
		('channel_store_store_tag_id_uniq',
		'unique(channel_id, store_tag_id)',
		'Store tag ID must be unique for channel tag mapping!'),
		('channel_odoo_tag_id_uniq',
		'unique(channel_id, odoo_tag_id)',
		'Odoo tag ID must be unique for channel tag mapping!'),
	]

	@api.multi
	def unlink(self):
		for record in self:
			if record.store_tag_id:
				match = record.channel_id.match_tag_feeds(record.store_tag_id)
				if match: match.unlink()
		res = super(ChannelCategoryMappings, self).unlink()
		return  res

	def _compute_name(self):
		for record in self:
			if record.tag_name:
				record.name = record.tag_name.name
			else:
				record.name = 'Deleted'

	@api.onchange('tag_name')
	def change_odoo_id(self):
		self.odoo_tag_id = self.tag_name.id


class ChannelGenderMappings(models.Model):

	_name="channel.gender.mappings"
	_inherit = ['channel.mappings']
	_rec_name = "gender_name"

	store_tag_id =  fields.Char(string='Store Tag ID',required=True)
	odoo_tag_id = fields.Char(string='Odoo Tag ID',required=True)
	gender_name = fields.Char(string='Gender Tag Name',required=True)

	_sql_constraints = [
		('channel_store_store_gender_id_uniq',
		'unique(channel_id, store_tag_id)',
		'Store tag ID must be unique for channel tag mapping!'),
		('channel_odoo_tag_gender_uniq',
		'unique(channel_id, odoo_tag_id)',
		'Odoo tag ID must be unique for channel tag mapping!'),
	]

	# @api.multi
	# def unlink(self):
	# 	for record in self:
	# 		if record.store_tag_id:
	# 			match = record.channel_id.match_tag_feeds(record.store_tag_id)
	# 			if match: match.unlink()
	# 	res = super(ChannelCategoryMappings, self).unlink()
	# 	return  res

	def _compute_name(self):
		for record in self:
			if record.gender_name:
				record.name = record.gender_name
			else:
				record.name = 'Deleted'

	@api.onchange('gender_name')
	def change_odoo_id(self):
		self.odoo_tag_id = self.gender_name

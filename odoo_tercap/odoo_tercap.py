# -*- coding: utf-8 -*-

from openerp import models, api
from openerp.osv import fields, osv

from openerp.tools import (
    drop_view_if_exists,
)


# Clases de tercap_import_export
class payment_mode(osv.osv):
    _inherit = 'payment.mode'
    _columns = { 
        'tercap_sat_cod_modo_pago': fields.selection([  
            ('0', 'Credito'),                              
            ('1', 'Contado')], 'Codigo forma Pago TERCAP:'),    
        }

class account_tax(osv.osv):
    _inherit = 'account.tax'
    _columns = {   
        'tercap_sat_codiva': fields.selection([  
            ('0', 'No se trata en Tercap'),
            ('N', 'Normal'),
            ('R', 'Reducido'),
            ('S', 'Super-Reducido'),
            ('E', 'Exento'),
            ('PRN', 'Porcentaje Recargo Normal'),
            ('PRR', 'Porcentaje Recargo Reducido'),
            ('PRS', 'Porcentaje Recargo Superreducido'),
            ], 'Codigo de iva asignado para interfase TERCAP:'),
        'tercap_retax': fields.many2one('account.tax','Tipo de Recargo')    
        }    
    _defaults = {
        'tercap_sat_codiva': '0'    
     }


class accountfiscalposition(osv.osv):
    _inherit =  'account.fiscal.position'
    _columns = {
        'tercap_sat_tipo_iva': fields.selection([  
            ('N', 'Iva sin recargo'),
            ('E', 'Exento de Iva'),                            
            ('R', 'Iva con recargo')], 'Tipo de Iva en sistema Tercap_SAT:'),     
        }

# Consulta para mostrar Clientes
class odoo_tercap_clientes(osv.osv):
	_name = 'tabla.clientes.tercap'

   	_auto = False

	_columns = {
		'id': fields.integer('id', readonly=True),
		'nombre_comercial': fields.char('Nombre comercial', readondly=True),
		'nombre_fiscal': fields.char('Nombre fiscal', readondly=True),
		'identificacion_fiscal': fields.char('Identificación fiscal', readondly=True),
		'tipo_fiscalidad': fields.char('Tipo fiscalidad', readondly=True),
		'direccion': fields.char('Dirección', readondly=True),
		'poblacion': fields.char('Población', readondly=True),
		'provincia': fields.char('Provincia', readondly=True),
		'telefono': fields.char('Teléfono', readondly=True),
		'codigo_postal': fields.char('Código postal', readondly=True),
		'latitud': fields.float('Latitud', digits=(4, 6), readondly=True),
		'longitud': fields.float('Longitud', digits=(4, 6), readondly=True),
		'observaciones': fields.text('Observaciones', readonly=True),
		'tarifa': fields.integer('Tarifa', readonly=True),
		'forma_pago': fields.char('Forma pago', readonly=True),
		'riesgo': fields.float('Riesgo', digits=(10, 2), readondly=True),
	}

	def init(self, cr):

		drop_view_if_exists(cr, 'tabla_clientes_tercap')

		cr.execute("""
		  CREATE OR REPLACE VIEW tabla_clientes_tercap AS(
		  SELECT 
		  partner.id as id,
		  partner.comercial as nombre_comercial, 
		  partner.name as nombre_fiscal,
          partner.vat as identificacion_fiscal,
          case
          	when fiscal_pos.name ilike 'Recargo de Equivalencia%' then 'R'
          	else 'N'
          	end
          as tipo_fiscalidad,
          partner.street as direccion,
          partner.city as poblacion,
          partner.state_id as provincia,
          partner.phone as telefono,
          partner.zip as codigo_postal,
          0.0 as latitud,
          0.0 as longitud,
          partner.comment as observaciones,
          case
			when p_pricelist.name ilike 'Public Pricelist' or tar.pricelist_id is null then
				(select id from product_pricelist where name ilike 'Public Pricelist')
			else p_pricelist.id
			end
	  	  as tarifa,
	  	  case
			when mod_pago is null then 'Contado'
			else 
			   case when p_mode.tercap_sat_cod_modo_pago = '0' then 'Credito'
			   else 'Contado'
               end
			end
	  	  as forma_pago,
          case
          	when partner.credit_limit=0 or partner.credit_limit is null then 999999
          	else partner.credit_limit
          	end
          as riesgo
          from res_partner as partner
          left join (select cast(split_part(res_id,',',2) as int) as partner_id,
 							cast(split_part(value_reference,',',2) as int) as account_property_id 
 							from ir_property
							where split_part(res_id,',',1) like 'res.partner' and name like 'property_account_position') as fiscal
		  on fiscal.partner_id = partner.id
		  left join account_fiscal_position fiscal_pos
		  on fiscal_pos.id = fiscal.account_property_id
		  left join (select cast(split_part(value_reference,',',2) as int) as pricelist_id, 
							cast(split_part(res_id,',',2) as int) as partner_id 
							from ir_property
							where name ilike 'property_product_pricelist') as tar
       	  on tar.partner_id = partner.id
       	  left join product_pricelist p_pricelist
          on p_pricelist.id = tar.pricelist_id
          left join (select cast(split_part(value_reference,',',2) as int) as pay_mode, 
							cast(split_part(res_id,',',2) as int) as partner_id 
							from ir_property
							where name ilike 'customer_payment_mode') as mod_pago
		  on mod_pago.partner_id = partner.id
          left join payment_mode p_mode
		  on p_mode.id = mod_pago.pay_mode
          where partner.customer=True and partner.active=True and partner.parent_id is null)
		""")


# Consulta para mostrar tarifas
class odoo_tercap_tarifas(osv.osv):
	_name = 'tabla.tarifas.tercap'

   	_auto = False

   	_columns = {
		'id': fields.integer('id', readonly=True),
		'nombre': fields.char('Nombre', readondly=True),
	}

	def init(self, cr):

	  	drop_view_if_exists(cr, 'tabla_tarifas_tercap')

		cr.execute("""
		  CREATE OR REPLACE VIEW tabla_tarifas_tercap AS(
		  SELECT 
		  tarifa.id as id,
		  case
		  	when traduccion.src is null then tarifa.name
		  	else traduccion.value
		  	end
		  as nombre
          from product_pricelist as tarifa
          left join ir_translation traduccion
          on traduccion.src = tarifa.name
          where tarifa.type ilike 'sale' and tarifa.active=True)
		""")


# Consulta para mostrar Direcciones del cliente
class odoo_tercap_direcciones_cliente(osv.osv):
	_name = 'tabla.direccionescliente.tercap'

	_auto = False

	_columns = {
		'id': fields.integer('id', readonly=True),
		'cliente': fields.char('cliente', readonly=True),
		'nombre_direccion': fields.char('Nombre direccion', readonly=True),
		'nombre_contacto': fields.char('Nombre contacto', readonly=True),
		'direccion': fields.char('Direccion', readonly=True),
		'poblacion': fields.char('Poblacion', readonly=True),
		'provincia': fields.char('Provincia', readonly=True),
		'telefono': fields.char('Telefono', readonly=True),
		'email': fields.char('Email', readonly=True),
		'codigo_postal': fields.char('Codigo postal', readonly=True),
		'latitud': fields.float('Latitud', digits=(4, 6), readondly=True),
		'longitud': fields.float('Longitud', digits=(4, 6), readondly=True),
		'observaciones': fields.text('Observaciones', readonly=True),
	}

	def init(self, cr):
		drop_view_if_exists(cr, 'tabla_direccionescliente_tercap')

		cr.execute("""
		  CREATE OR REPLACE VIEW tabla_direccionescliente_tercap AS(
		  SELECT 
		  partner.id as id,
		  partner.parent_id as cliente,
		  partner.name as nombre_direccion,
		  partner.street as direccion,
		  partner.city as poblacion,
          partner.state_id as provincia,
          partner.phone as telefono,
          partner.email as email,
          partner.zip as codigo_postal,
          0.0 as latitud,
          0.0 as longitud,
          partner.comment as observaciones
		  from res_partner partner
		  where customer=True and parent_id is not null)
		""")



# Consulta para mostrar Familias
class odoo_tercap_familias(osv.osv):
	_name = 'tabla.familias.tercap'

	_auto = False

	_columns = {
		'id': fields.integer('id', readonly=True),
		'nombre': fields.char('Nombre', readonly=True),
		'parent': fields.char('Parent', readonly=True),
	}

	def init(self, cr):
		drop_view_if_exists(cr, 'tabla_familias_tercap')

		cr.execute("""
		  CREATE OR REPLACE VIEW tabla_familias_tercap AS(
		  SELECT categoria.id as id,
		  case
		  	when traduccion.src is null then categoria.name
		  	else traduccion.value
		  	end
		  as nombre,
		  categoria.parent_left as parent
		  from product_category as categoria
		  left join ir_translation traduccion
		  on traduccion.src = categoria.name
		  where traduccion.module ilike 'product')
		""")


# Consulta para mostrar Tipos de impuesto
class odoo_tercap_tipos_impuesto(osv.osv):
	_name = 'tabla.tiposimpuesto.tercap'

	_auto = False

	_columns = {
		'id': fields.integer('id', readonly=True),
		'nombre': fields.char('Nombre', readonly=True),
		'tipo_iva': fields.char('Tipo iva', readonly=True),
		'porcentaje_iva': fields.float('Porcentaje iva', digits = (3, 2), readonly=True),
		'porcentaje_recargo': fields.float('Porcentaje recargo', digits = (3, 2), readonly=True),
	}

	def init(self, cr):
		drop_view_if_exists(cr, 'tabla_tiposimpuesto_tercap')

		cr.execute("""
		  CREATE OR REPLACE VIEW tabla_tiposimpuesto_tercap AS(
		  sELECT taxes.id as id,
		  taxes.name as nombre,
		  taxes.tercap_sat_codiva as tipo_iva,
		  (taxes.amount)*100 as porcentaje_iva,
		  (taxesre.amount)*100 as porcentaje_recargo
		  from account_tax taxes
		  join account_tax taxesre on
		  taxes.tercap_retax = taxesre.id
		  where taxes.tercap_sat_codiva != '0')
		""")

# Consulta para mostrar Tarifa productos
class odoo_tercap_tarifa_productos(osv.osv):
	_name = 'tabla.tarifaprod.tercap'

	_auto = False

	_columns ={
		'id': fields.integer('id', readonly=True),
		'tarifa': fields.integer('Tarifa', readonly=True),
		'producto': fields.integer('Producto', readonly=True),
		'precio_bruto': fields.float('Precio bruto', digits = (10, 2), readonly=True),
		'porcentaje_descuento': fields.float('Porcentaje descuento', digits = (2, 3), readonly=True),
		'euros_desccuento': fields.float('Euros descuento', digits = (10, 2), readonly=True),
		'precio_neto': fields.float('Precio neto', digits = (10, 2), readonly=True),
	}

	def init(self, cr):
		drop_view_if_exists(cr, 'tabla_tarifaprod_tercap')

		cr.execute("""
		  CREATE OR REPLACE VIEW tabla_tarifaprod_tercap AS(
		  SELECT  product.id as id,
		  1 as tarifa,
		  product.id as producto,
		  product.list_price as precio_bruto,
		  0.0 as porcentaje_descuento,
		  0.0 as euros_descuento,
		  product.list_price as precio_neto
		  from product_template product
		  where sale_ok=True )
		""")


# Consulta para mostrar Actividades abiertas
class odoo_syg_actividades(osv.osv):
	_name = 'tabla.actividades.syg'

	_auto = False

	_columns = {
		'id': fields.integer('id', readonly=True),
		'nombre': fields.char('Nombre', readonly=True),
		'estado': fields.char('Estado', readonly=True)
	}

	def init(self, cr):
		drop_view_if_exists(cr, 'tabla_productos_tercap')

		cr.execute("""
		  CREATE OR REPLACE VIEW tabla_actividades_syg AS(
		  SELECT 
		  event.id as id,
		  event.name as nombre,
		  event.state as estado
		  from event_event event
          where state='confirm')
		""")

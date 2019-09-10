# -*- coding: utf-8 -*-

from openerp import models, api
from openerp.osv import fields, osv

from openerp.tools import (
    drop_view_if_exists,
)

#ampliar clase alumnos con el valor del dni
class res_partner(models.Model):
    _inherit = 'res.partner'

    _columns = {
    	'dni_num': fields.char('DNI Web', size=25),
    }


#ampliar clase event.registration con el valor de las que son de web
class event_registration(models.Model):
    _inherit = 'event.registration'

    _columns = {
    	'web': fields.boolean('Viene de Web'),
    }



# Consulta para mostrar Clientes
class tabla_alumnos_syg(osv.osv):
	_name = 'tabla.alumnos.syg'

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

		drop_view_if_exists(cr, 'tabla_alumnos_syg')

		cr.execute("""
		  CREATE OR REPLACE VIEW tabla_alumnos_syg AS(
		  SELECT 
		  partner.id as id,
		  partner.name as nombre,
          partner.vat as identificacion_fiscal,
          partner.street as direccion,
          partner.city as poblacion,
          partner.state_id as id_provincia,
          prov.name as provincia,
          partner.phone as telefono,
          partner.zip as codigo_postal,
          partner.comment as observaciones
          from res_partner as partner
          join res_country_state prov
          on prov.id = partner.state_id
          where partner.customer=True and partner.active=True and partner.alumni_boolean=True)
		""")


# Consulta para mostrar Actividades abiertas
class tabla_actividades_syg(osv.osv):
	_name = 'tabla.actividades.syg'

	_auto = False

	_columns = {
		'id': fields.integer('id', readonly=True),
		'nombre': fields.char('Nombre', readonly=True),
		'estado': fields.char('Estado', readonly=True),
		'destino': fields.char('Destino', readonly=True),
		'desde': fields.date('Desde el'),
		'hasta': fields.date('Hasta el'),
		'reserva': fields.float('Reserva', readonly=True),
		'total': fields.float('Total', readonly=True),
		'pais': fields.char('Nombre', readonly=True),
	}

	def init(self, cr):
		drop_view_if_exists(cr, 'tabla_actividades_syg')

		cr.execute("""
		  CREATE OR REPLACE VIEW tabla_actividades_syg AS(
		  SELECT 
		  event.id as id,
		  event.name as nombre,
		  event.state as estado,
		  event.destino_event as destino,
		  event.date_begin as desde,
		  event.date_end as hasta,
		  event.precio_web as reserva,
		  event.precio_total_event as total,
		  event.pais_event as pais
		  from event_event event
          where state='confirm')
		""")


# Consulta para mostrar Colegios con actividades abiertas
class tabla_coles_syg(osv.osv):
	_name = 'tabla.coles.syg'

   	_auto = False

	_columns = {
		'id': fields.integer('id', readonly=True),
		'nombre': fields.char('Nombre colegio', readondly=True),
		'poblacion': fields.char('Población Colegio', readondly=True),
		'actividad': fields.char('Actividad', readondly=True),
		'id_actividad': fields.integer('id actividad', readonly=True),
	}

	def init(self, cr):

		drop_view_if_exists(cr, 'tabla_coles_syg')

		cr.execute("""
		  CREATE OR REPLACE VIEW tabla_coles_syg AS(
		  SELECT 
		  cole.id as id,
		  cole.name as nombre,
          cole.city as poblacion,
          event.name as actividad,
          event.id as id_actividad
          from res_partner as cole
          join syg_colegio syg
          on syg.partner_id = cole.id
          join event_event event
          on event.colegio_event = syg.id
          where cole.active=True and syg.colegio_boolean=True and event.state = 'confirm')
		""")




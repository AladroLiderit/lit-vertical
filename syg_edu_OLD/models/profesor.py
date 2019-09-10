# -*- coding: utf-8 -*-
###############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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
###############################################################################

import openerp
from openerp import SUPERUSER_ID, models
from openerp import tools
import openerp.exceptions
from openerp import api
from openerp.osv import fields, osv, expression

class SygProfesor(osv.osv):
    _name = 'syg.profesor'
    _inherits = {'res.partner': 'partner_id'}


    _columns={
    	'es_profesor' : fields.boolean('Es Personal?'),
        'es_externo' : fields.boolean('Es Profesor externo?'),
    	'partner_id' : fields.many2one(
            'res.partner', 'Partner', required=True, ondelete="cascade"),
    	'alta_date' : fields.date('Fecha de Alta'),
    	'baja_date' : fields.date('Fecha de Baja'),
    	'puesto_id' : fields.many2one('syg.puesto', 'Puesto de trabajo'),
        'trabajos_ids' : fields.one2many('syg.puesto.persona','profesor_id','Puesto de trabajo'),
    	#'programa_id' : fields.many2one('event_advanced.programa_event', 'Programa'),
        'programa_id': fields.many2many ('event_advanced.programa_event','syg_profesor_programa_rel','profesor_id','programa_event_id','Programas'),
    	'reconocimiento' : fields.boolean('Renuncia a reconocimiento anual'),
    	'rec_date' : fields.date('Fecha de renuncia'),
    	'prl' : fields.boolean('Certificado PRL en la empresa'),
    	'prl_date' : fields.date('Fecha de PRL'),
    	'acc_datos' : fields.boolean('Tiene acceso a ficheros de datos'),
    	'acc_equipos' : fields.boolean('Tiene acceso a equipos informáticos'),
    	#'nivelacceso_id' : fields.many2one('syg.nivelacceso', 'Nivel de acceso'),
        'nivelacceso_id': fields.many2many ('syg.nivelacceso','syg_profesor_nivelacceso_rel','profesor_id','nivelacceso_id','Niveles de acceso'),
        'baja_lopd' : fields.date('Fecha de Baja LOPD'),
    	'certificados_ids': fields.one2many('syg.cert','profesor_id','Certificados'),
    	'otros_titulos' : fields.char('Otras titulaciones',size=150),
        'seg_social_num' : fields.char('Nº Seg.Social',size=50),
    	'idioma_ids' : fields.many2many('syg.idioma','syg_profesor_idioma_rel','profesor_id','idioma_id','Idiomas'),
        'email_trabajo' : fields.char('Correo de trabajo',size=150),
        'phone_trabajo' : fields.char('Teléfono de trabajo',size=50),

    }
    
    def onchange_state(self, cr, uid, ids, state_id, context=None):
        partner_ids = [user.partner_id.id for user in self.browse(cr, uid, ids, context=context)]
        return self.pool.get('res.partner').onchange_state(cr, uid, partner_ids, state_id, context=context)

    def onchange_type(self, cr, uid, ids, is_company, context=None):
        """ Wrapper on the user.partner onchange_type, because some calls to the
            partner form view applied to the user may trigger the
            partner.onchange_type method, but applied to the user object.
        """
        partner_ids = [user.partner_id.id for user in self.browse(cr, uid, ids, context=context)]
        return self.pool['res.partner'].onchange_type(cr, uid, partner_ids, is_company, context=context)

    def onchange_address(self, cr, uid, ids, use_parent_address, parent_id, context=None):
        """ Wrapper on the user.partner onchange_address, because some calls to the
            partner form view applied to the user may trigger the
            partner.onchange_type method, but applied to the user object.
        """
        partner_ids = [user.partner_id.id for user in self.browse(cr, uid, ids, context=context)]
        return self.pool['res.partner'].onchange_address(cr, uid, partner_ids, use_parent_address, parent_id, context=context)


    @api.onchange('es_profesor')
    def _on_change_es_profesor(self):
        if self.es_profesor and self.es_externo:
            self.es_externo = False

    @api.onchange('es_externo')
    def _on_change_es_externo(self):
        if self.es_profesor and self.es_externo:
            self.es_profesor = False


    #creates employee and redirects to it
    def create_employee(self, cr, uid, partner_id, context):

        employee_id=self.create_employee_from_partner(cr, uid, partner_id, context)
        
        if not employee_id:
            return False
        else:
            view_id = self.pool.get('ir.ui.view').search(cr, uid, [('model','=','hr.employee'),('type','=','form')], order='id ASC')
            if isinstance(view_id,(list,tuple)):
                view_id=view_id[0]

            return {
                'view_type' : 'form',
                'view_mode' : 'form',
                'view_id'   : view_id,
                'res_model' : 'hr.employee',
                'res_id'    : employee_id,
                'type'      : 'ir.actions.act_window',
                'target'    : 'current',
            }


    #creates employee with partner's data
    def create_employee_from_partner(self, cr, uid, prof_id, context):
        employee_id=False

        if isinstance(prof_id,(list,tuple)):
            prof_partner_id=self.pool.get('syg.profesor').browse(cr, uid, prof_id[0])
            partner_id = prof_partner_id.partner_id.id
 
        if partner_id and not self.partner_has_employee(cr, uid, partner_id):
            # partner_res=self.browse(cr, uid, partner_id)
            partner_res=self.pool.get('res.partner').browse(cr, uid, partner_id)
            if partner_res:
                employee_obj=self.pool.get('hr.employee')
        
                employee={
                        'name'              : partner_res.name,
                        'country_id'        : partner_res.country_id.id,
                        'image'             : partner_res.image,
                        'work_email'        : partner_res.email,
                        'address_home_id'   : partner_id,
                        'identification_id' : partner_res.vat if partner_res.vat else '',
                        'bank_account_id'   : partner_res.bank_ids[0].id if partner_res.bank_ids else '',
                        }
                
                employee_id=employee_obj.create(cr, uid, employee)

                if employee_id:
                    cr.execute('UPDATE res_partner SET employee=TRUE WHERE id=%s' % (partner_id))

                    #Won't create a user:
                    '''
                    #checks for the existence of a user associated to this partner
                    user_obj=self.pool.get('res.users')
                    
                    if not user_obj.search(cr, uid, [('partner_id','=',partner_id)]):

                        #check for the existence of a user with the same email
                        if partner_res.email and user_obj.search(cr, uid, [('email','=',partner_res.email)]):
                            raise osv.except_osv(_('Error!'), _("There's already a user using %s.\nIt will not be possible to create a user." % (partner_res.email)))
                        
                        #there's no user, so, we'll create one
                        user_exists=True
                        while user_exists:        
                            if partner_res.email:
                                user_login=partner_res.email
                            else:
                                user_login=str(uuid.uuid4())[:64]

                            user_exists=user_obj.search(cr, uid, [('login','=',user_login)])
                        
                        user_id=user_obj.create(cr, uid, {
                                                'partner_id' : partner_id,
                                                'company_id' : partner_res.company_id.id,
                                                'login'      : user_login,
                                                })
                                                
                        #now, we put the user in the employee
                        employee_obj.write(cr, uid, employee_id, {'user_id':user_id})
                    '''
        return employee_id
        

    #check for the existance of an employee associated to the partner        
    def partner_has_employee(self, cr, uid, partner_id):
        employee_id=False
        
        if partner_id:
            #is there an employee whose user_id is related to the partner?
            
            partner_user=self.pool.get('res.users').search(cr, uid, [('partner_id','=',partner_id)])
            if partner_user:

                employee_id=self.pool.get('hr.employee').search(cr, uid, [('user_id','=',partner_user)])

                if employee_id:
                    if isinstance(employee_id,(list,tuple)):
                        employee_id=employee_id[0]
    
        #raise osv.except_osv(_('Error!'), _(employee_id))
        return employee_id


class SygPuesto(models.Model):
    _name = 'syg.puesto'

    _columns={
        'name': fields.char('Puesto de trabajo', size=150),
    }

class SygPuestoPersona(models.Model):
    _name = 'syg.puesto.persona'

    _columns={
        'name': fields.many2one('syg.puesto',"Puesto"),
        'profesor_id':fields.many2one('syg.profesor','Personal'),
        'fecha_alta' : fields.date('Fecha de Alta'),
        'fecha_baja' : fields.date('Fecha de Baja'),
        'programa_id' : fields.many2one('event_advanced.programa_event', 'Programa'),
    }


class syg_idioma(osv.osv):
	_name = "syg.idioma"
	_columns = {
		'name' : fields.char('Idioma',size=50),
		'nivel_idioma': fields.selection([('A1','A1'),('A2','A2'),('B1','B1'),('B2','B2'),('C1','C1'),('C2','C2'),('nativo', 'Nativo')], 'Nivel'),
	}

class syg_cert(osv.osv):
	_name = "syg.cert"
	_columns = {
        #'name' : fields.selection(
        #[('D-S', 'Delitos sexuales'), ('M-T-L', 'Monitor de Tiempo Libre'), ('M-N', 'Monitor de Nivel')
        #, ('C-T-L', 'Coordinador de Tiempo Libre'), ('C-N', 'Coordinador de Nivel')],'Certificado'),
        'name': fields.many2one('syg.tipo.cert',"Certificado"),
		'fecha_cert' : fields.date('Fecha certificado'),
        'fecha_caduca' : fields.date('Fecha caducidad'),
        'ccaa_cert' : fields.many2one ('res.partner.ccaa',"CC.AA."),
        #'ccaa_cert' : fields.char('Comunidad Autónoma',size=100),
        'profesor_id':fields.many2one('syg.profesor','Personal'),
	}

class syg_tipo_cert(osv.osv):
    _name = "syg.tipo.cert"
    _columns = {
        'name' : fields.char('Tipo de Certificado', size=150),
    }

class profesor_idiomas_rel(osv.osv):
    _name = "syg.profesor.idioma.rel"
    _rec_name = "profesor_id"
    _columns = {
        'profesor_id': fields.many2one('syg.profesor', 'Personal', ondelete='cascade'),
        'idioma_id': fields.many2one('syg.idioma', 'Idioma', ondelete='cascade'),
    }


class SygNivelAcceso(osv.osv):
    _name = 'syg.nivelacceso'

    _columns={
        'name' : fields.char('Nivel de acceso', size=150),
    }

#ampliamos la clase event.event para asociar un profesor a la actividad
class EventEvent(osv.osv):
    _name = 'event.event'
    _inherit = 'event.event'


    _columns={
        'profesor_id': fields.many2one('syg.profesor', 'Personal'),
        'colegio_event' : fields.many2one('syg.colegio', 'Colegio de actividad'),
        'teacher_ids': fields.many2many ('syg.profesor','syg_teachers_event_rel','event_id','profesor_id','Personal en Actividad'),
        'externos_ids': fields.many2many ('syg.profesor','syg_externos_event_rel','event_id','profesor_id','Profesores Externos en Actividad'),
        'codigo_fotos': fields.char('Código Fotos'),

    }



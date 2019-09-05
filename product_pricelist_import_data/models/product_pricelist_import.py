# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
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
from openerp.osv import osv, fields
from openerp import tools
from datetime import datetime
from openerp import uid
from openerp.tools import ustr

import logging
_logger = logging.getLogger(__name__)

# agregamos un valor nuevo a product_template para almacenar una ref. interna de plantilla
class product_template(osv.osv):
    _inherit = 'product.template'
    #creamos un campo para registrar el precio minimo de venta en productos
    _columns = {
        'ref_interna' :fields.char('Referencia interna'),
        'obsoleto': fields.boolean('Obsoleto'),
        'version': fields.char('Versión de tarifa')
    }


#creamos una clase para tener en una vista los datos a exporta a excel
class product_pricelist_import(osv.osv):
    _name = "product.pricelist.import"
    _columns = {
        'prov_name': fields.char('Nombre Proveedor'),
        'version': fields.char('Version Tarifa'),
        'product_name': fields.char('Artículo'),
        # 'template_defcode': fields.char('Referencia de Artículo'),
        # 'product_defcode_unique': fields.char('Referencia Variante S'),
        'product_defcode_attribute': fields.char('Referencia Variante N'),
        'product_ean': fields.char('EAN Variante'),
        'product_attribute_talla': fields.char('Talla'),
        'product_attribute_numero': fields.char('Numero'),
        'product_attribute_color': fields.char('Color'),
        'purchase_price': fields.float('Precio compra'),
        'purchase_discount': fields.float('Descuento compra'),
        'list_price': fields.float('Precio venta'),
        'error_prov': fields.boolean('Error en proveedor'),
        'error_refs': fields.boolean('Error de referencias'),
        # estos no se van a usar, si no existe se crea el nuevo valor
        # 'error_talla': fields.boolean('Error en talla'),
        # 'error_color': fields.boolean('Error en color'),
        # 'error_num': fields.boolean('Error en número'),
        'cargado': fields.boolean('Producto importado'),
        'a_cargar': fields.boolean('Producto a importar'),
    }


    def _pricelist_import(self, cr, uid, ids, context):
        prov = self.pool.get('res.partner')
        product_obj = self.pool.get('product.product')
        tmpl_obj = self.pool.get('product.template')
        supp_info = self.pool.get('product.supplierinfo')
        price_partner = self.pool.get ('pricelist.partnerinfo')
        attrs = self.pool.get('product.attribute')
        attrs_value = self.pool.get('product.attribute.value')

        pr_att_lines = self.pool.get('product.attribute.line')

        # tomamos los ids de los atributos TALLA, COLOR, NUMERO que tiene que estar antes registrados
        search_condition = [('name', '=', 'TALLA')]
        attr_talla = attrs.search(cr, uid, search_condition)
        if len (attr_talla)==0:
            raise osv.except_osv(('Error!'),('No existe el atributo TALLA'))
        else:
            attr_talla = attr_talla[0]

        search_condition = [('name', '=', 'NUMERO')]
        attr_num = attrs.search(cr, uid, search_condition)
        if len (attr_num)==0:
            raise osv.except_osv(('Error!'),('No existe el atributo NUMERO'))
        else:
            attr_num = attr_num[0]

        search_condition = [('name', '=', 'COLOR')]
        attr_color = attrs.search(cr, uid, search_condition)
        if len (attr_color)==0:
            raise osv.except_osv(('Error!'),('No existe el atributo COLOR'))
        else:
            attr_color = attr_color[0]

        # comprobamos que solo hay una version de tarifa por proveedor
        cr.execute('SELECT distinct prov_name,version from product_pricelist_import where cargado = False order by prov_name')
        version_doble = cr.dictfetchall()
        for v  in range(0,len(version_doble)):
            search_condition = [('version', 'not ilike', version_doble and version_doble[v]['version']),('prov_name','not ilike', version_doble and version_doble[v]['prov_name']),('cargado','=',False)]
            v_duplex = self.search (cr, uid, search_condition)
            if len(v_duplex)>0:
                raise osv.except_osv(('Error!'),('Una sola versión de tarifa por proveedor!!'))


        
        # marcamos los productos seleccionados para identificar los ids a importar
        for prai in ids:
            # recorremos los registros para marcar los que no tienen proveedor reconocido
            reg = self.browse(cr,uid,prai)
            search_condition = [('name', '=', reg.prov_name),('supplier','=', True)]
            prov_value = prov.search (cr,uid, search_condition)
            if len(prov_value) == 0:
                self.write(cr, uid, prai, {'error_prov':True,},context=None)
            else:
                self.write(cr, uid, prai, {'a_cargar':True,},context=None)
            # verificamos que existen valores para los atributos, si no los creamos
            if reg.product_attribute_talla:
                search_condition = [('name', '=', reg.product_attribute_talla),('attribute_id','=', attr_talla)]
                hay_talla = attrs_value.search (cr, uid, search_condition)
                if len (hay_talla)==0:
                    vals={}
                    vals['name'] = reg.product_attribute_talla
                    vals['attribute_id'] = attr_talla
                    attrs_value.create(cr, uid,vals, context=None)
            if reg.product_attribute_numero:
                search_condition = [('name', '=', reg.product_attribute_numero),('attribute_id','=', attr_num)]
                hay_talla = attrs_value.search (cr, uid, search_condition)
                if len (hay_talla)==0:
                    vals={}
                    vals['name'] = reg.product_attribute_numero
                    vals['attribute_id'] = attr_num
                    attrs_value.create(cr, uid,vals, context=None)
            if reg.product_attribute_color:
                search_condition = [('name', '=', reg.product_attribute_color),('attribute_id','=', attr_color)]
                hay_talla = attrs_value.search (cr, uid, search_condition)
                if len (hay_talla)==0:
                    vals={}
                    vals['name'] = reg.product_attribute_color
                    vals['attribute_id'] = attr_color
                    attrs_value.create(cr, uid,vals, context=None)



        # los pasos para crear productos son: crear el template con su proveedor, 
        # luego crear el product.attribute.line con el tmpl_id (zapato), el att_id (numero) 
        # y asociar el value_ids identificando el valor del atributo (num. 40)
        # luego crear el product con su ean y default_code y asociarle el template

        # vamos con los template para ver si existen y si no existen crearlos
        cr.execute('SELECT distinct prov_name,product_name,version,list_price,purchase_price,purchase_discount from product_pricelist_import where a_cargar order by product_name')
        t_a_cargar = cr.dictfetchall()
        _logger.error('##### AIKO ###### En import pricelist valor de t_a_cargar es %s'%t_a_cargar)
        for n  in range(0,len(t_a_cargar)):
            # buscamos el template por nombre, def_code y proveedor
            _logger.error('##### AIKO ###### En import pricelist valor de t_a_cargar [n] es %s'%t_a_cargar[n])
            _logger.error('##### AIKO ###### En import pricelist valor de t_a_cargar prov_name [n] es %s'%t_a_cargar[n]['prov_name'])
            search_condition = [('name', '=', t_a_cargar and t_a_cargar[n]['prov_name']),('supplier','=', True)]
            prov_value = prov.search (cr,uid, search_condition)
            # search_condition = ['&',('seller_id', '=', prov_value[0]),'|',('name', '=ilike', t_a_cargar and t_a_cargar[n]['product_name']),('ref_interna','=', t_a_cargar and t_a_cargar[n]['template_defcode'])]
            search_condition = ['&',('seller_id', '=', prov_value[0]),('name', '=ilike', t_a_cargar and t_a_cargar[n]['product_name'])]
            haytmpl = tmpl_obj.search( cr, uid, search_condition)
            if len (haytmpl)==0:
                # creamos nuevo template
                values = {}
                values['name'] = t_a_cargar and t_a_cargar[n]['product_name']
                values['version'] = t_a_cargar and t_a_cargar[n]['version']
                # values['ref_interna'] = t_a_cargar and t_a_cargar[n]['template_defcode']
                values['available_in_pos'] = False
                values['no_create_variants'] = 'no'
                values['list_price'] = t_a_cargar and t_a_cargar[n]['list_price']
                haytmpl = tmpl_obj.create(cr, uid, values, context=None)
                # asociamos el proveedor creando linea en supplierinfo y su precio
                vals={}
                vals['name'] = prov_value[0]
                vals['product_tmpl_id'] = haytmpl
                valores={}
                valores ['price']= t_a_cargar and t_a_cargar[n]['purchase_price']
                valores ['discount']= t_a_cargar and t_a_cargar[n]['purchase_discount']
                valores ['min_quantity']= 0
                vals['pricelist_ids'] = [(0,0,valores)]
                precio_compra = supp_info.create (cr, uid, vals, context=None)

            else:
                haytmpl = haytmpl[0]
                # y actualizamos precios de venta y de compra
                tmpl_obj.write (cr, uid, haytmpl, {'list_price': t_a_cargar and t_a_cargar[n]['list_price'], 'version':t_a_cargar and t_a_cargar[n]['version']}, context=None)
                act_prod = tmpl_obj.browse(cr, uid, haytmpl)
                for sumi in act_prod.seller_ids:
                    if sumi.name.id == prov_value[0]:
                        for price in sumi.pricelist_ids:
                            valores={}
                            valores ['price']= t_a_cargar and t_a_cargar[n]['purchase_price']
                            valores ['discount']= t_a_cargar and t_a_cargar[n]['purchase_discount']
                            price_partner.write (cr, uid, price.id, valores,context=None)
                    

            # ahora para este template haytmpl creado o actualizado creamos sus atributos
            # para eso actualizamos el registro de a importar

            search_condition = ['&',('prov_name', '=', t_a_cargar and t_a_cargar[n]['prov_name']),'&',('product_name','=', t_a_cargar and t_a_cargar[n]['product_name']),('a_cargar','=',True)]
            reg_imp_ids = self.search(cr,uid,search_condition)
            for imp_id in reg_imp_ids:
                reg_imp = self.browse(cr, uid, imp_id)

                if reg_imp.product_attribute_numero:
                    search_condition = [('product_tmpl_id', '=', haytmpl),('attribute_id','=',attr_num)]
                    haypr_att = pr_att_lines.search(cr, uid, search_condition)
                    if len (haypr_att)==0:
                        vals={}
                        vals ['attribute_id']= attr_num
                        vals ['product_tmpl_id']= haytmpl
                        haypr_att_num_id = pr_att_lines.create(cr, uid, vals,context=None)
                    else:
                        haypr_att_num_id = haypr_att[0]

                    # creamos una lista con sus value_ids
                    num_vl_ids =[]
                    haypr_att_num = pr_att_lines.browse(cr, uid, haypr_att_num_id)
                    _logger.error('##### AIKO ###### En import pricelist valor de value_ids en numero es %s'%haypr_att_num.value_ids)
                    for valor in haypr_att_num.value_ids:
                        num_vl_ids.append (valor.id)

                    # comprobamos que existe el valor para el atributo en la tabla de pr.att.value
                    search_condition = [('name', '=', reg_imp.product_attribute_numero),('attribute_id','=',attr_num)]
                    hayatt_value = attrs_value.search(cr, uid, search_condition)
                    if len(hayatt_value)==0:
                        vals={}
                        vals ['attribute_id']= attr_num
                        vals ['name']= reg_imp.product_attribute_numero
                        hayatt_value_id = attrs_value.create(cr, uid, vals,context=None)
                    else:
                        hayatt_value_id = hayatt_value[0]

                    _logger.error('##### AIKO ###### En import pricelist valor de hayatt_value_id en numero es %s'%hayatt_value_id)
                    if hayatt_value_id not in num_vl_ids:
                        _logger.error('##### AIKO ###### En import pricelist encontrado nuevo valor para numero %s'%reg.product_attribute_numero)
                        num_vl_ids.append(hayatt_value_id)

                    # una vez tenemos la lista de values_id actualizada la escribimos en el product att line
                    valores={}
                    valores['value_ids']= [(6,0,num_vl_ids)]
                    _logger.error('##### AIKO ###### En import pricelist escribiendo valores en att lines %s'%valores)
                    pr_att_lines.write (cr, uid,haypr_att_num_id, valores, context=None)



                #lo mismo para el color
                if reg_imp.product_attribute_color:
                    search_condition = [('product_tmpl_id', '=', haytmpl),('attribute_id','=',attr_color)]
                    haypr_att = pr_att_lines.search(cr, uid, search_condition)
                    if len (haypr_att)==0:
                        vals={}
                        vals ['attribute_id']= attr_color
                        vals ['product_tmpl_id']= haytmpl
                        haypr_att_num_id = pr_att_lines.create(cr, uid, vals,context=None)
                    else:
                        haypr_att_num_id = haypr_att[0]

                    # creamos una lista con sus value_ids
                    num_vl_ids =[]
                    haypr_att_num = pr_att_lines.browse(cr, uid, haypr_att_num_id)

                    for valor in haypr_att_num.value_ids:
                        num_vl_ids.append (valor.id)

                    # comprobamos que existe el valor para el atributo en la tabla de pr.att.value
                    search_condition = [('name', '=', reg_imp.product_attribute_color),('attribute_id','=',attr_color)]
                    hayatt_value = attrs_value.search(cr, uid, search_condition)
                    if len(hayatt_value)==0:
                        vals={}
                        vals ['attribute_id']= attr_color
                        vals ['name']= reg_imp.product_attribute_color
                        hayatt_value_id = attrs_value.create(cr, uid, vals,context=None)
                    else:
                        hayatt_value_id = hayatt_value[0]
                    if hayatt_value_id not in num_vl_ids:
                        num_vl_ids.append(hayatt_value_id)

                    # una vez tenemos la lista de values_id actualizada la escribimos en el product att line
                    valores={}
                    valores['value_ids']= [(6,0,num_vl_ids)]
                    pr_att_lines.write (cr, uid,haypr_att_num_id, valores, context=None)

                #lo mismo para la talla
                if reg_imp.product_attribute_talla:
                    search_condition = [('product_tmpl_id', '=', haytmpl),('attribute_id','=',attr_talla)]
                    haypr_att = pr_att_lines.search(cr, uid, search_condition)
                    if len (haypr_att)==0:
                        vals={}
                        vals ['attribute_id']= attr_talla
                        vals ['product_tmpl_id']= haytmpl
                        haypr_att_num_id = pr_att_lines.create(cr, uid, vals,context=None)
                    else:
                        haypr_att_num_id = haypr_att[0]

                    # creamos una lista con sus value_ids
                    num_vl_ids =[]
                    haypr_att_num = pr_att_lines.browse(cr, uid, haypr_att_num_id)

                    for valor in haypr_att_num.value_ids:
                        num_vl_ids.append (valor.id)

                    # comprobamos que existe el valor para el atributo en la tabla de pr.att.value
                    search_condition = [('name', '=', reg_imp.product_attribute_talla),('attribute_id','=',attr_talla)]
                    hayatt_value = attrs_value.search(cr, uid, search_condition)
                    if len(hayatt_value)==0:
                        vals={}
                        vals ['attribute_id']= attr_talla
                        vals ['name']= reg_imp.product_attribute_talla
                        hayatt_value_id = attrs_value.create(cr, uid, vals,context=None)
                    else:
                        hayatt_value_id = hayatt_value[0]
                    if hayatt_value_id not in num_vl_ids:
                        num_vl_ids.append(hayatt_value_id)

                    # una vez tenemos la lista de values_id actualizada la escribimos en el product att line
                    valores={}
                    valores['value_ids']= [(6,0,num_vl_ids)]
                    pr_att_lines.write (cr, uid,haypr_att_num_id, valores, context=None)


            # llamamos a la funcion que crea las variantes del template creado
            tmpl_obj.create_variant_ids(cr, uid, haytmpl, context=context)

            # ahora tenemos que localizar la variante creada por sus atributos
            # para asi podemos asociar el ean y default code si no los tienen
            for imp_id in reg_imp_ids:
                reg_imp = self.browse(cr, uid, imp_id)
                search_condition = [('product_tmpl_id', '=', haytmpl)]
                prod_tmpl_id = product_obj. search (cr, uid, search_condition)
                if reg_imp.product_attribute_numero and reg_imp.product_attribute_talla and reg_imp.product_attribute_color:
                    search_condition = ['|','&',('attribute_id', '=', attr_num),('name','=',reg_imp.product_attribute_numero),'|','&',
                    ('attribute_id', '=', attr_talla),('name','=',reg_imp.product_attribute_talla),'&',
                    ('attribute_id', '=', attr_color),('name','=',reg_imp.product_attribute_color)]
                elif reg_imp.product_attribute_numero and reg_imp.product_attribute_color:
                    search_condition = ['|','&',('attribute_id', '=', attr_num),('name','=',reg_imp.product_attribute_numero),'&',
                    ('attribute_id', '=', attr_color),('name','=',reg_imp.product_attribute_color)]
                elif reg_imp.product_attribute_talla and reg_imp.product_attribute_color:
                    search_condition = ['|','&',
                    ('attribute_id', '=', attr_talla),('name','=',reg_imp.product_attribute_talla),'&',
                    ('attribute_id', '=', attr_color),('name','=',reg_imp.product_attribute_color)]
                elif reg_imp.product_attribute_numero:
                    search_condition = ['&',('attribute_id', '=', attr_num),('name','=',reg_imp.product_attribute_numero)]
                elif reg_imp.product_attribute_talla:
                    search_condition = ['&',('attribute_id', '=', attr_talla),('name','=',reg_imp.product_attribute_talla)]
                elif reg_imp.product_attribute_color:
                    search_condition = ['&',('attribute_id', '=', attr_color),('name','=',reg_imp.product_attribute_color)]
                else:
                    continue

                att_value_ids = attrs_value.search(cr, uid, search_condition)
                _logger.error('##### AIKO ###### En import pricelist escribiendo valor de la lista att_value_ids %s'%att_value_ids)

                for variants in prod_tmpl_id:
                    prod_id = product_obj.browse(cr, uid, variants)
                    list_atts = []
                    for tt in prod_id.attribute_value_ids:
                        list_atts.append (tt.id)
                    _logger.error('##### AIKO ###### En import pricelist escribiendo valor de la lista list_atts %s para el product_id %s'%(list_atts,prod_id.id))
                    if att_value_ids == list_atts:
                        #este sera el product
                        product_obj.write (cr, uid, variants,{'ean13':reg_imp.product_ean, 'default_code':reg_imp.product_defcode_attribute},context=context)
                        pass



        #por la version cargada, identificar los productos que hay que pasar a obsoletos (cambio nombre y marcar como obsoleto)
        # lo que haremos es filtrar todos los template del proveedor que no tengan como version la cargada y marcarlos como no activos y obsoletos
        # primero de product_supplierinfo todos los productos de los proveedores de los ids cargados
        cr.execute('SELECT distinct prov_name, version from product_pricelist_import where cargado = False order by prov_name')
        provs_to_act = cr.dictfetchall()
        for v  in range(0,len(provs_to_act)):
            search_condition = [('name', '=', provs_to_act and provs_to_act[v]['prov_name']),('supplier','=', True)]
            v_prov = prov.search (cr,uid, search_condition)
            search_condition = [('name', '=', v_prov[0])]
            tmpl_by_supp = supp_info.search(cr, uid, search_condition)
            _logger.error('##### AIKO ###### En import pricelist valores de tmpl a validar %s'%tmpl_by_supp)
            for v_tmpl in tmpl_by_supp:
                # comprobamos la version que tiene registrada el template
                this_suppinfo = supp_info.browse( cr, uid, v_tmpl)
                _logger.error('##### AIKO ###### En import pricelist valor de tmpl in suppinfo %s'%this_suppinfo.product_tmpl_id.id)
                this_tmpl = tmpl_obj.browse (cr, uid, this_suppinfo.product_tmpl_id.id)
                version_tmpl = this_tmpl.version
                _logger.error('##### AIKO ###### En import pricelist comparo version de producto %s'%version_tmpl)
                _logger.error('##### AIKO ###### En import pricelist con version de import %s'%provs_to_act[v]['version'])
                if version_tmpl != provs_to_act[v]['version']:
                    tmpl_obj.write (cr, uid, this_tmpl.id,{'active':False, 'obsoleto':True},context=None)
                

        # antes de acabar recordar desmarcar los productos a_marcar, y marcar como importados los que se pudieron registrar
        for prai in ids:
            self.write(cr, uid, prai, {'a_cargar':False,'cargado':True},context=None)

        return True

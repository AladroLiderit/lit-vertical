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
from openerp import models, fields, api, exceptions
from openerp.tools.translate import _
import glob, os
import logging
_logger = logging.getLogger(__name__)

class product_get_image(models.TransientModel):
    _name = "product.get.image"
    _description = "Get products image"


    directory = fields.Char('Directory where images'
                                     ' are load',
                                     default="/var/aristos/fotos")

    file_type = fields.Selection ([('jpg','.jpg'),('png','.png'),('bmp','.bmp')],default='jpg')


    @api.model
    def _img_asoc(self):
        
        if self.env.context.get('active_model', '') == 'product.template':            
            ids = self.env.context['active_ids']

            p_obj = self.env['product.template']
            p = p_obj.browse(ids)

            img_obj = self.env['base_multi_image.image']

            # _logger.error('##### AIKO ###### En img_asoc con valor de active_ids: %s' % ids)
           
            for d in p:
                # _logger.error('##### AIKO ###### En img_asoc con valor de def_code: %s' % d.default_code)
                if d.default_code == False:
                    continue
                
                num_imgs = img_obj.search([('owner_id','=',d.id),('owner_model','=','product.template')])
                # _logger.error('##### AIKO ###### En img_asoc con valor de image_ids: %s' % len(num_imgs))
                if len(num_imgs) > 0:
                    continue

                file_name = d.default_code+ '.' + self.file_type
                directory = self.directory
                rute_last_char = directory[-1:]
                if rute_last_char == "/":
                    directory = directory[:-1]


                file_path = directory + "/" + file_name


                os.chdir(directory)

                file_type = "*."+str(self.file_type)

                # _logger.error('##### AIKO ###### En img_asoc antes de buscar fichero con datos: path %s' % file_path)
                # _logger.error('##### AIKO ###### En img_asoc antes de buscar fichero con datos: type %s' % file_type)

                for nombre in glob.glob(file_type):
                    # _logger.error('##### AIKO ###### En img_asoc comparando nombre %s' % nombre)
                    # _logger.error('##### AIKO ###### En img_asoc comparando con fichero %s' % file_name)
                    if nombre == file_name:
                        #creamos un base_multi_image.image para el producto
                        vals={}
                        vals['name'] = d.default_code
                        vals['sequence'] = 10
                        vals['storage'] = 'file'
                        vals['owner_model'] = 'product.template'
                        vals['path'] = file_path
                        vals['owner_id'] = d.id

                        # _logger.error('##### AIKO ###### En img_asoc valores para crear image %s' % vals)
                        img_obj.create(vals)


        return {}

    @api.multi
    def p_get_images(self):
        self._img_asoc()
        return     


    # TODO: al cambiar el default_code delproducto eliminar la imagen asociada (sin borrar el fichero) y buscar nueva segun cambio de def_code

    # TODO: Al desactivar productos borrar los ficheros de sus imagenes del servidor  y la imagen vinculada.

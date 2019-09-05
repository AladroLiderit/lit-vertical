function openerp_pos_gift_voucher_models(instance, module){ //module is instance.point_of_sale 
	var QWeb = instance.web.qweb;
    var global_serial_no = new Array();
	var coupon_id = new Array();
	var element = null;
	var _t = instance.web._t;
	var oldOrder = module.Order;
    var round_di = instance.web.round_decimals;
    var round_pr = instance.web.round_precision
    
    function formatDate(value)
    {
       return value.getMonth()+1 + "/" + value.getDate() + "/" + value.getFullYear();
    }

	var _super_ = module.PosModel.prototype.load_server_data;
    module.PosModel.prototype.load_server_data = function() {

		var self = this;
		var loaded = _super_.call(this).then(function(){
		return self.fetch('account.journal',['name','for_gift_coupens','is_loyalty_journal'],[])})
		.then(function(journal){
			self.set('journallists',journal);
                 return self.fetch(
                         'pos.session', 
                         ['id', 'journal_ids','name','user_id','config_id','start_at','stop_at'],
                         [['state', '=', 'opened'], ['user_id', '=', self.session.uid]]
                     );
                 }).then(function(sessions){
                     self.set('pos_session', sessions[0]); 
                 return self.fetch(
                       'gift.voucher',
                       ['id','product_id','voucher_serial_no','source','voucher_name','out','in','date','last_date','amount'],[['in','=',false],['last_date','>', instance.web.date_to_str(new Date())]]);
                 }).then(function(gift_voucher){
                    self.set('gift_voucher',gift_voucher);
                    return self.fetch(
                            'product.template',
                             ['id','name','track_outgoing','coupon','list_price','default_code','property_account_income','ean13','validity'],[]);
                          }).then(function(product_obj){
                         self.set('products',product_obj);         
                 
        });
		
		return loaded;
	}

    var _super_scan_product = module.PosModel.prototype.scan_product;
    module.PosModel.prototype.scan_product = function(parsed_code) {
    	var isinput = $(":focus").is('input');
    	var curElement = $(":focus");
    	if(isinput){
    		curElement.val(parsed_code.code);
    		curElement.trigger($.Event( "keypress", { which: 13 } ));
    		curElement.trigger($.Event( "keyup", { which: 13 } ));
    	}
    	if(parsed_code.type == 'coupon' || parsed_code.type == 'coupon1'){
            var self = this;
            var selectedOrder = this.get('selectedOrder');
            if(parsed_code.encoding === 'ean13'){
                var product = this.db.get_product_by_ean13(parsed_code.base_code);
            }else if(parsed_code.encoding === 'reference'){
                var product = this.db.get_product_by_reference(parsed_code.base_code);
            }else if(parsed_code.encoding === 'code128'){
            	var id;
            	var p;
            	var g=this.get('gift_voucher');
            	for(var i=0;i<g.length;i++){
            		if(g[i].voucher_serial_no == parsed_code.base_code){
            			id = g[i].product_id[0];
            			p=g[i];
            			break; 
            			}
            	}
                var product = this.db.get_product_by_id(id);
            }

            if(!product){
                return false;
            }

            if(parsed_code.type === 'price'){
                selectedOrder.addProduct(product, {price:parsed_code.value});
            }else if(parsed_code.type === 'weight'){
                selectedOrder.addProduct(product, {quantity:parsed_code.value, merge:false});
            }else if(parsed_code.type === 'discount'){
                selectedOrder.addProduct(product, {discount:parsed_code.value, merge:false});
            }else if(parsed_code.type === 'coupon'){
            }else if(parsed_code.type === 'coupon1'){
          }else{
                selectedOrder.addProduct(product);
            }
            return true;
    	}
    	else{
    		var self = this;
            var selectedOrder = this.get('selectedOrder');
            if(parsed_code.encoding === 'ean13'){
                var product = this.db.get_product_by_ean13(parsed_code.base_code);
            }else if(parsed_code.encoding === 'reference'){
                var product = this.db.get_product_by_reference(parsed_code.code);
            }

            if(!product){
                return false;
            }

            if(parsed_code.type === 'product' && product.to_weight && self.config.iface_electronic_scale){
            	self.set('hide_barcode',true)
                self.pos_widget.screen_selector.set_current_screen('scale',{product: product});
            }
            else{
            	return _super_scan_product.call(this,parsed_code);
            }
    	}
    }
    
    var baseOrderline = module.Orderline;
	module.Orderline = module.Orderline.extend({
		initialize:function(attributes,options){
			baseOrderline.prototype.initialize.call(this,attributes,options);
			this.loyalty_card_number = "";
        },
        get_loyalty_card_number: function(){
            return this.discount_comment;
        },
        set_loyalty_card_number : function(comment){
            this.loyalty_card_number = comment;
            this.trigger('change', this);
        },
        export_as_JSON : function(){
        	var Export = baseOrderline.prototype.export_as_JSON.call(this);
        	Export.loyalty_card_number = this.get_loyalty_card_number() || "";
        	return Export;
        },
    });
    
	
    var _super_initialize_ = module.Order.prototype.initialize;
    module.Order.prototype.initialize = function(session, attributes){
         _super_initialize_.call(this, session, attributes);
        this.set({
        	customer_name:	new Array(),
            label:null,
            c_name:null,
        });
        this.cust_name;
        this.coupon_name;
        this.coupon_id=new Array();
        this.serial_nos = new Array();
        this.coupon_redeemed = new Array();
        this.voucher_number = new Array();
        this.coupon_unit_price=new Array();
        this.coupon_qty=new Array();
        this.journal_id;
        
        this.quantity = 1;
        this.quantityStr = '1';
        this.voucher_serial_no = new Date().getTime()+ "0"
        // this.voucher_serial_no = Date.now();
        this.global_serial_no=[];
        this.element = document.getElementById("canv");
    }
	
	var _super_add_product = module.Order.prototype.addProduct;
	module.Order.prototype.addProduct = function(product, options){
		var self = this;
    	start_flag = false;
    	var currentOrderLines = this.pos.get('selectedOrder').get('orderLines');
    	var products=this.pos.get('products');
    	var selected_product_id=product.product_tmpl_id;
    	if(currentOrderLines.length == 0)
    	{
    		start_flag = true;
    		for(product_id in products)
    		{
    		if(products[product_id].id==selected_product_id)	
    		{
    			coupon_id.push(products[product_id].id)
    			if(products[product_id].coupon==true)
				{
    				this.pos.get('selectedOrder').set_coupon_name(true);
					is_coupon_flag=true;
					break;
				}
    			break;
    		}
    		}
    	}
    	else
    	{
    		var is_coupon_flag=false;
    		for(line in currentOrderLines['models'])
			{
    		orderline_product_id = currentOrderLines['models'][line].get_product().product_tmpl_id;
    		selected_product_id=product.product_tmpl_id;
    		for(product_id in products)
    		{
    			if(products[product_id].id==selected_product_id)
    			{
    				if(products[product_id].coupon==true)
    				{
    					is_coupon_flag=true;
    					break;
    				}
    			}
    		}
			}
    		for (product_id in products)
    		{
    			if(products[product_id].id==orderline_product_id)
    			{
    				if(products[product_id].coupon==true && is_coupon_flag==true)
    				{
    					start_flag = true;
    					this.pos.get('selectedOrder').set_coupon_name(true);
    					for(product_id in products)
    					{
    						if(products[product_id].id==selected_product_id)	
    						{
    							coupon_id.push(products[product_id].id)
    							break;
    						}
    					}
    					break;
    				}
    				else if(products[product_id].coupon==false && is_coupon_flag==false)
    				{
    					start_flag = true;
    					this.pos.get('selectedOrder').set_coupon_name(false);
    					for(product_id in products)
    					{
    						if(products[product_id].id==selected_product_id)	
    						{
    							break;
    						}
    					}
    					break;
    				}
    			}
			}
    	}
    	if(start_flag == true)
    		{
    		_super_add_product.call(this,product, options);
    		}
	}
	
	
	var _super_export_as_JSON = module.Order.prototype.export_as_JSON;
	module.Order.prototype.export_as_JSON = function(){
        var Json = _super_export_as_JSON.call(this);
		var d = new Date();
		var creation_date = ""+String(d.getMonth()+1)+"-"+String(d.getDate())+"-"+String(d. getFullYear());
    //if new customer
		if(this.get_client_name()=='')
		{
			Json.coupon_name = this.get_coupon_name(),
			Json.coupon_id = this.get_coupon_id(),

			Json.company = this.pos.company.name,
			Json.shop    = this.pos.shop.name,
			Json.date = creation_date,
			Json.coupon_redeemed = this.get_coupon_redeemed(),
			Json.coupon_qty = this.get_coupon_qty(),
			Json.coupon_unit_price = this.get_coupon_unit_price(),
			Json.coupon_unique_no = this.get_voucher_number()
			return Json;
		}
		else
		{
			Json.coupon_name = this.get_coupon_name(),
			Json.coupon_id = this.get_coupon_id(),

			Json.company = this.pos.company.name,
			Json.shop    = this.pos.shop.name,
			Json.date = creation_date,
			Json.coupon_redeemed = this.get_coupon_redeemed(),
			Json.coupon_qty = this.get_coupon_qty(),
			Json.coupon_unit_price = this.get_coupon_unit_price(),
			Json.coupon_unique_no = this.get_voucher_number()
			return Json;

		}	
	}
	
	var _super_initialize_Orderline = module.Orderline.prototype.initialize;
    module.Orderline.prototype.initialize = function(attr,options){
         _super_initialize_Orderline.call(this, attr,options);
         this.serial_nos = new Array();
         this.voucher_serial_no = new Date().getTime()+ "0"
         this.cust_id;
         this.global_serial_no=[];
    }
    
    var _super_export_as_JSON_Orderline = module.Orderline.prototype.export_as_JSON;
	module.Orderline.prototype.export_as_JSON = function(){
		var orderLineJson = _super_export_as_JSON_Orderline.call(this);
		orderLineJson.voucher_no = this.get('voucher_serial_no')
		return orderLineJson
	}
   

module.Order=module.Order.extend({
        set_voucher_number:function(){
        	global_serial_no.length=0;
        },
        get_voucher_number:function(){
        	return global_serial_no;
        },
      
        set_coupon_name:function(coupon_name){
            	this.set('coupon_name',coupon_name);
          },
          
         get_coupon_name:function(){
           return this.get('coupon_name')	
           },
           
         get_coupon_qty:function(){
             return this.get('coupon_qty')	
             },
             
          set_coupon_qty:function(coupon_qty){
             	this.set('coupon_qty',coupon_qty);
           },
           
           get_coupon_unit_price:function(){
               return this.get('coupon_unit_price')	
               },
               
           set_coupon_unit_price:function(coupon_unit_price){
               	this.set('coupon_unit_price',coupon_unit_price);
             },
         
         set_coupon_redeemed:function(coupon_redeemed){
         	this.set('coupon_redeemed',coupon_redeemed);
       },
       
      get_coupon_redeemed:function(){
        return this.get('coupon_redeemed')	
        },
        
        set_coupon_id:function(coupon_id){
        	this.coupon_id.push(coupon_id)
      },
         
        get_coupon_id:function(){
          return this.coupon_id	
          },
        reset_global_serial_no:function(){
        	  global_serial_no = [];
           }
    });

    var orderline_id = 1;
    module.Orderline = module.Orderline.extend({
    
    uniqueSerialNo: function(i) {
    	this.voucher_serial_no = new Date().getTime()+Math.floor(Math.random()*101)+i.toString()
      	global_serial_no.push(this.voucher_serial_no)
      },
    
     
    getUniqueId:function(){
    	  return this.global_serial_no
      },
     
      
      
	set_serial_no:function(serial_nos){
	this.serial_nos=serial_nos
	},
	
	get_serial_no:function(){
    	return this.serial_nos;
    },
   
  });
}
    
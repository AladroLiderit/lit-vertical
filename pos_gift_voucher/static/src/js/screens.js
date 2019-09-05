function openerp_pos_gift_voucher_screens(instance, module){ 
    var QWeb = instance.web.qweb;
    _t = instance.web._t;
    var round_pr = instance.web.round_precision
    
    var voucher_code_array=new Array();
    var name_template_array=new Array();
    var temp_voucher_array=new Array();
    var updated_sale_price=0.0;
	var sale_price_total=0.0;
	var coupon_id = new Array();
	var coupon_qty = new Array();
	var coupon_unit_price = new Array();
	var cnt = 0;
    
    var _super_initialize_ = module.Order.prototype.initialize;
    module.Order.prototype.initialize = function(session, attributes){
         _super_initialize_.call(this, session, attributes);
         synch=this.pos.get('synch');
         if(synch.state === "disconnected"){
         g = this.pos.get('gift_voucher');
         for(i=0;i<g.length;i++){
        	 for(j=0;j<temp_voucher_array.length;j++){
        		 if(g[i].voucher_serial_no == temp_voucher_array[j]){
        			 g.splice(i, 1);
        		 }
        	 }
         }
         }
    }
    
    var _super_renderElement = module.PaymentScreenWidget.prototype.renderElement;
	module.PaymentScreenWidget.prototype.renderElement = function(){
		_super_renderElement.call(this);
        var self = this;

        self.$('.add-coupon-button').click(function(){
     		self.addgiftVoucher();
     		document.getElementById('gift-coupon').value="";
     		document.getElementById('gift-coupon').focus();

     	});
           
            self.$('.cancel-coupon-button').click(function(){
     		self.cancelgiftVoucher();
     		document.getElementById('gift-coupon').value="";
     		document.getElementById('gift-coupon').focus();

     	});
           self.$('.add-coupon-button').keyup(function(e){
        	   if(e.which == 13){
        		   self.addgiftVoucher();
        		   document.getElementById('gift-coupon').value="";
        		   document.getElementById('gift-coupon').focus();
        		   e.preventDefault();
        	   }
        	});
           self.$('.cancel-coupon-button').keyup(function(e){
        	   if(e.which == 13){
        		   self.cancelgiftVoucher();
        		   document.getElementById('gift-coupon').value="";
        		   document.getElementById('gift-coupon').focus();
        		   e.preventDefault();
        	   }
        	});
}
	
	var _super_addPaymentline = module.Order.prototype.addPaymentline;
	module.Order.prototype.addPaymentline = function(cashregister){
		var flag = false;
		
        var for_gift_coupens = cashregister.journal.for_gift_coupens;
		var currentPaymentLines = (this.pos.get('selectedOrder')).get('paymentLines');
		if(currentPaymentLines.length>0){
			var len = currentPaymentLines.length;
			for(i=0;i<len;i++){
				if(for_gift_coupens){
					flag = true;
					cnt++;
					break;
				}
			}
			if(!flag){
				_super_addPaymentline.call(this,cashregister);
			}
			if(cnt == 1 && flag){
				var len=currentPaymentLines.models.length;
				for(j=0;j<len;j++){
					var is_coupon=currentPaymentLines.models[j].cashregister.journal.for_gift_coupens;
				}
				if(!is_coupon){
				_super_addPaymentline.call(this,cashregister);
				}
			}
		}
		else{
			if(for_gift_coupens){cnt++;}
			_super_addPaymentline.call(this,cashregister);
		}
	}

	var _super_removePaymentline = module.Order.prototype.removePaymentline;
	module.Order.prototype.removePaymentline = function(line){
		var self=this;
		var flag=true;
		var method_detail_gift=self.pos.get('journallists');

		for(i=0;i<method_detail_gift.length;i++){
        	if(method_detail_gift[i].for_gift_coupens){
        		var m_name=method_detail_gift[i].name;
        		if(!line.name.search(m_name)){
        			flag=false;
        			if($('paymentline-delete').click()){
        				flag=true;
        			}
        		}
        	}
        }
 		if(flag){
 			_super_removePaymentline.call(self,line);
			cnt=0; //for addPaymentLine function of payment line
		}
	}
	var _super_barcode_product_action = module.PaymentScreenWidget.prototype.barcode_product_action;
	module.PaymentScreenWidget.prototype.barcode_product_action = function(code){
        var self = this;
        if(self.pos.scan_product(code)){
        	current_screen = self.pos_widget.screen_selector.get_current_screen();
        	if(current_screen == 'payment'){
        		self.pos_widget.screen_selector.set_current_screen('payment');
        		$(".add-coupon-button").focus();
        	}else if(self.barcode_product_screen){ 
                self.pos_widget.screen_selector.set_current_screen(self.barcode_product_screen);
            }
        }
        else{
        	if (!this.pos.get('hide_barcode')){
        	$.msgBox({
					    title: "Warning",
					    content: "Unknown Barcode !!! The Point of Sale couldn't find any product, client, employee and action associated with the scanned barcode.",
					    type: "error",
					    opacity:0.6,
					    buttons: [{ value: "Ok" }],
					});
        	}
        }
		
	}
	
	module.PaymentScreenWidget.prototype.barcode_error_action = function(code){
		if (!this.pos.get('hide_barcode')){
		$.msgBox({
		    title: "Warning",
		    content: "Unknown Barcode !!! The Point of Sale couldn't find any product, client, employee and action associated with the scanned barcode.",
		    type: "error",
		    opacity:0.6,
		    buttons: [{ value: "Ok" }],
		});
		}
	}
	var _sup_back=module.PaymentScreenWidget.prototype.back;
    module.PaymentScreenWidget.prototype.back=function(){
        _sup_back.call(this);
        $("#gift_coupon_desc").hide();
		$("#gift-voucher-code").hide();
    }
	

    var _super_init_ = module.PaymentScreenWidget.prototype.init;
    module.PaymentScreenWidget.prototype.init = function(parent, options){
         _super_init_.call(this, parent, options);
         var self = this;
         var old_handler = this.line_delete_handler;

 		this.line_delete_handler = function(event){

 			var journal=self.pos.get('journallists');
             var node = this;
             while(node && !node.classList.contains('paymentline')){
                 node = node.parentNode;
             }
             if(node){
                 self.pos.get('selectedOrder').removePaymentline(node.line);
                 var linename=String(node.line.name);
                 for(i=0;i<journal.length;i++){
                     if(journal[i].for_gift_coupens){
                         var j_name=journal[i].name;
                         if(!linename.search(j_name)){
                            $('#gift_coupon').val("");
                            $("#gift_coupon_desc").hide();
 							$("#gift-voucher-code").hide();
 							cnt=0; //for addPaymentLine function of payment line
                         }
                     }
                     else if(journal[i].is_loyalty_journal){
                    	 var j_name=journal[i].name;
                         if(!linename.search(j_name)){
                             $('#loyalty-card-code').val("");
                             $("#loyalty_card").hide();
 							 cnt=0; //for addPaymentLine function of payment line
                         }
                     }
                 }
             }
             event.stopPropagation();
			old_handler.call(this,event);
  
         };

     }
    
    module.ActionBarWidget = module.ActionBarWidget.extend({
    	delete_action_button : function(label){
    		for(var i = 0; i < this.button_list.length; i++){
    			if(this.button_list[i].label == label){
    				this.button_list[i].destroy();
    			}
            }
    	},
    });
    
    var _super_show_ = module.PaymentScreenWidget.prototype.show;
    module.PaymentScreenWidget.prototype.show = function(parent, options){
         _super_show_.call(this, parent, options);

         var self = this;
         document.body.removeEventListener('keyup', this.hotkey_handler);

         this.pos_widget.action_bar.delete_action_button('Validate');
         
         this.add_action_button({
                 label: _t('Validate'),
                 name: 'validation',
                 icon: '/point_of_sale/static/src/img/icons/png48/validate.png',
                 click: function(){
               	 var is_coupon_flag=false;
               	 self.validate_order();
               	 updated_sale_price=0.0;

         			// Barcode Generation=============>>
               		var element = document.getElementById("canv")

         			var currentOrderLines = self.pos.get('selectedOrder').get('orderLines');
         			var orderline_product_id;
         			
         			var products=self.pos.get('products');
         			for(line in currentOrderLines['models'])
         			{
         				orderline_product_id = currentOrderLines['models'][line].get_product().product_tmpl_id;
         			}
         			for(product_id in products)
             		{
             			if(products[product_id].id==orderline_product_id)
             			{
             				if(products[product_id].coupon==true)
             				{
             					is_coupon_flag=true;
             					break;
             				}
             				else
             				{
             					is_coupon_flag=false;
             					break;
             				}
             			}
             		}
         			
         			
         			if(is_coupon_flag==true)
         			{
                 	var serial = self.pos.get('selectedOrder').get_voucher_number()
         			for(x in serial)
         			{
         				
         			var canvas_div = document.createElement('div');
         			canvas_div.id = serial[x];
         			var elem = document.createElement('canvas');
         			elem.id= serial[x];

         			var text = serial[x].replace(/^\s+/,'').replace(/\s+$/,'');
         			var elt = symdesc[9];
         			var altx =serial[x].replace(/^\s+/,'').replace(/\s+$/,'');
         			var opts = "includetext parsefnc".replace(/^\s+/,'').replace(/\s+$/,'');
         			var bw = new BWIPJS;

         			// Convert the options to a dictionary object, so we can pass alttext with
         			// spaces.
         			var tmp = opts.split(' '); 
         			opts = {};
         			for (var i = 0; i < tmp.length; i++) {
         				if (!tmp[i])
         					continue;
         				var eq = tmp[i].indexOf('=');
         				if (eq == -1)
         					opts[tmp[i]] = bw.value(true);
         				else
         					opts[tmp[i].substr(0, eq)] = bw.value(tmp[i].substr(eq+1));
         			}

         			// Add the alternate text
         			if (altx)
         				opts.alttext = bw.value(altx);

         			// Add any hard-coded options required to fix problems in the javascript
         			// emulation. 
         			opts.inkspread = bw.value(0);
         			if (needyoffset[elt.sym] && !opts.textxalign && !opts.textyalign &&
         					!opts.alttext && opts.textyoffset === undefined)
         				opts.textyoffset = bw.value(-10);

         			var rot  = 'N';
         			bw.bitmap(new Bitmap);
         			bw.scale("1","1");
         			

         			var div = document.getElementById('output');
         			if (div)
         				div.innerHTML = '';

         			bw.push(text);
         			bw.push(opts);

         			try {
         				
         				bw.call(elt.sym);
         				bw.bitmap().show(elem,rot);
         				
         			} catch(e) {
         				var s = '';
         				if (e.fileName)
         					s += e.fileName + ' ';
         				if (e.lineNumber)
         					s += '[line ' + e.lineNumber + '] ';
         			}
         			canvas_div.appendChild(elem);
         			element.appendChild(canvas_div);
         			}
         			}
         			self.pos.get('selectedOrder').set_voucher_number();
                 },
             });
         
         this.update_payment_summary();
     }
    
    module.PaymentScreenWidget = module.PaymentScreenWidget.extend({
    	
        cancelgiftVoucher : function(){
				coupon_exist_flag=true;
				var products=this.pos.get('products');
				var gift_voucher_obj=this.pos.get('gift_voucher');
				var sale_price = 0.0;
				var sum = 0.0;
				var coup_name = "";
				var coupon_code = document.getElementById("gift-coupon").value;
				if (coupon_code == '')
         	{
         	}
         	else
         	{
         		for (coupon in voucher_code_array)
         		{
         			if (voucher_code_array[coupon]==coupon_code)
         			{
         				var index = voucher_code_array.indexOf(coupon_code);
         				voucher_code_array.splice(index, 1);
         				coupon_exist_flag=true;
         				break;
         			}
         			else
         			{
         				coupon_exist_flag=false;
         			}
         		}
         		if (coupon_exist_flag==false)
         		{
         			$.msgBox({
	 					    title: "Warning",
	 					    content: "We can not cancel this Gift Voucher Code as it is not Added for Redemption",
	 					    type: "error",
	 					    opacity:0.6,
	 					    buttons: [{ value: "Ok" }],
	 					});

         		}
         		else
         		{
         			for (lot in gift_voucher_obj)
         			{
         				if (gift_voucher_obj[lot].voucher_serial_no==coupon_code)
         				{
         					coup_name=gift_voucher_obj[lot].voucher_name;
         					break;
         				}
         			}
         			for (product in products)
         			{
         				var toggle=true; //Require to avoids multiple warning messages
         				for(template in name_template_array)
         				{
         					if (products[product].name==coup_name)
         					{
         						sale_price = products[product].list_price;
         						sum=this.getAmount(updated_sale_price);
         						if(sum == 0.0)
         						{
         							
         							if(toggle==true){
         							$.msgBox({
         	   	 					    title: "Warning",
         	   	 					    content: "No more gift coupon to cancel",
         	   	 					    type: "error",
         	   	 					    opacity:0.6,
         	   	 					    buttons: [{ value: "Ok" }],
         	   	 					});
         							toggle=false;
         							}
         							document.getElementById("gift-coupon").value=""
         						}
         						else
         						{
         							updated_sale_price=sum-sale_price;
         							if(temp_voucher_array.length > 0)
         							{
         								for(voucher in temp_voucher_array)
         								{
         									if(temp_voucher_array[voucher] == coupon_code)
         									{
         										var index = temp_voucher_array.indexOf(coupon_code);
         										temp_voucher_array.splice(index, 1);
         										break;
         									}
         								}
         							}
         							else
         							{
         								$.msgBox({
	         	   	 					    title: "Warning",
	         	   	 					    content: "No such coupon to cancel",
	         	   	 					    type: "error",
	         	   	 					    opacity:0.6,
	         	   	 					    buttons: [{ value: "Ok" }],
	         	   	 					});
         							}
         							this.getAmount(updated_sale_price);
         							this.update_payment_summary();
         							this.renderElement();
         	   	        			$("#gift_coupon_desc").show();
         							$("#gift-voucher-code").show();
         							document.getElementById("gift-coupon").value=""
             						document.getElementById("gift-coupon").focus()
         							$('#coupon-calculated-price').trigger('keyup');
         							break;
         						}
         					}
         				}
         			}
         		}
         	}
			},
			
   			addgiftVoucher	: function() {
   				var flag=true;
   				var scanned_flag = true;
   				var redeemed_flag = true;
   				var valid_voucher_flag = false;
   				var valid_flag =false;
   				var voucher_validity;
   				var products=this.pos.get('products');
   	        	var gift_voucher_obj=this.pos.get('gift_voucher');
   	        	var entered_voucher_code = document.getElementById("gift-coupon").value;
   	        	
   	        	var currentOrder = this.pos.get('selectedOrder');
   	            var paidTotal = currentOrder.getPaidTotal();
   	            var dueTotal = currentOrder.getTotalTaxIncluded();
   	            var remaining = dueTotal > paidTotal ? dueTotal - paidTotal : 0;
   	            
   	        	if (entered_voucher_code == '')
   	        	{
   	        	}
   	        	else
   	        	{
   	        		for (voucher in gift_voucher_obj)
   	        		{
   	        			if(gift_voucher_obj[voucher].voucher_serial_no==entered_voucher_code)
   	        			{
   	        				voucher_source = gift_voucher_obj[voucher].source;
   	        				voucher_name = gift_voucher_obj[voucher].voucher_name;
   	        				creation_date = gift_voucher_obj[voucher].date;
                            // CAMBIO agrego el valor de last_date
                            last_date = gift_voucher_obj[voucher].last_date;
                            // CAMBIO agrego el valor de amount
                            val_amount = gift_voucher_obj[voucher].amount;
                            // CAMBIO: vamos a parar aqui el uso de vales de importe superior a la venta
                            if (val_amount > remaining)
                            {
                                $.msgBox({
                                        title: "Warning",
                                        content: "No se puede utilizar un vale de importe superior a la venta. Valor del vale: "+val_amount,
                                        type: "error",
                                        opacity:0.6,
                                        buttons: [{ value: "Ok" }],
                                });
                                valid_voucher_flag=false;
                            }
                            else
                            {
   	        				    valid_voucher_flag=true;
                                // $.msgBox({
                                //        title: "Warning",
                                //        content: "Coupon "+ entered_voucher_code +" encontrado con valor last_date "+last_date+" y creacion "+creation_date,
                                //        type: "error",
                                //        opacity:0.6,
                                //        buttons: [{ value: "Ok" }],
                                //    });
                            }
   	        				break;
   	        			}
   	        		}
   	        	}

   	        	if(valid_voucher_flag==true)
   	        	{
                    // CAMBIO: no trabajamos con el validity del product si no con el last_date del voucher
       	        	// for (prod in products)
       	        	// {
       	        	//  	if(products[prod].name==voucher_name)
       	        	//  	{
       	        	//  		voucher_validity = products[prod].validity;
       	        	//  		break;
       	        	// 	    }
       	        	// }
       	        	
                    // CAMBIO: no necesitamos el valor de creacion del voucher
       	        	//creation date of voucher(sold date)
       	        	// creation_voucher_date = new Date(creation_date).getDate();
       	        	// creation_voucher_month = (new Date(creation_date).getMonth())+1; //porque devuelve el mes de 0 a 11
       	        	// creation_voucher_year = new Date(creation_date).getFullYear();

       	        	//Today's date
       	        	var date = new Date();
                	year = date.getFullYear();
                    // CAMBIO: cast a entero por si el valor es texto
                    year = parseInt(year);
                	month = (date.getMonth()) + 1 ;
                    month = parseInt(month);
                	date = date.getDate() ;
                    date = parseInt(date);
                    // CAMBIO: no vamos a necesitar esta variable today
                	// var today = year + "-" + month + "-" + date;

                	// Date formed after adding validity days
                    // CAMBIO para usar el last_date del registro
                    // var endDate = new Date(new Date(creation_date).getTime());
                	// endDate.setDate(endDate.getDate()+parseInt(voucher_validity));
       	        	    
                	//endDate_date = endDate.getDate();
                    endDate_date = last_date.split('-')[2];
                    endDate_date = parseInt(endDate_date);
           	        //endDate_month = endDate.getMonth()+1;
                    endDate_month = last_date.split('-')[1];
                    endDate_month = parseInt(endDate_month);
           	       	//endDate_year = endDate.getFullYear();
                    endDate_year = last_date.split('-')[0];
                    endDate_year = parseInt(endDate_year);

                    // eSTA VAR solo se necesita para el msg que no mostramos
           	      	// var valid_date = endDate_year + "-" + endDate_month + "-" + endDate_date;
                    // $.msgBox({
                    //                title: "Warning",
                    //                content: "Last date es "+ valid_date,
                    //              type: "error",
                    //              opacity:0.6,
                    //              buttons: [{ value: "Ok" }],
                    //          });

           	       	if(year == endDate_year)
           	       	{
                        // $.msgBox({
                        //          title: "Warning",
                        //          content: "El año es el mismo",
                        //          type: "error",
                        //          opacity:0.6,
                        //         buttons: [{ value: "Ok" }],
                        //      });
           	       		if(month == endDate_month)
           	       		{
           	       			if(date <= endDate_date)
                            {
                                // $.msgBox({
                                // title: "Warning",
                                //  content: "El mes es el mismo y el dia menor",
                                //  type: "error",
                                //  opacity:0.6,
                                //  buttons: [{ value: "Ok" }],
                                // });
           	       				valid_flag = true;
                            }
           	       			else
                            {
                                // $.msgBox({
                                // title: "Warning",
                                //  content: "Coupon "+ entered_voucher_code +" day is not valid",
                                //  type: "error",
                                //  opacity:0.6,
                                //  buttons: [{ value: "Ok" }],
                                // });
           	       				valid_flag = false;
                            }
           	       		}
           	       		else
           	       		{
                            // CAMBIO
           	       			// if(month <= endDate_month)
                            if(month < endDate_month)
                            {
                                // $.msgBox({
                                // title: "Warning",
                                //  content: "El mes es menor",
                                //  type: "error",
                                //  opacity:0.6,
                                //  buttons: [{ value: "Ok" }],
                                // });
           	       				valid_flag = true;
                            }
           	       			else
                            {
                                // $.msgBox({
                                // title: "Warning",
                                //  content: "Coupon "+ entered_voucher_code +" month " + month +" is not minor than "+endDate_month,
                                //  type: "error",
                                //  opacity:0.6,
                                //  buttons: [{ value: "Ok" }],
                                // });
           	       				valid_flag = false;
                            }
           	       		}
           	       	}
                    // CAMBIO
                    // si el año es menor no hace falta comparar nada mas
                    //el caso de que sea igual esta en el if anterior
           	       	// else if(year <= endDate_year)
                    else if(year < endDate_year)
                    {   
                        // if(month == endDate_month)
                        // {
                        //   if(date <= endDate_date)
                        //     valid_flag = true;
                        //   else
                        //     valid_flag = false;
                        // }
                        // else
                        // {
                        //   if(month >= endDate_month)
                        //     valid_flag = true;
                        //   else
                        //     {
                        //       valid_flag = false;
                        //     }
                        
                        // $.msgBox({
                        //         title: "Warning",
                        //          content: "El año es menor",
                        //          type: "error",
                        //          opacity:0.6,
                        //          buttons: [{ value: "Ok" }],
                        //      });
                        valid_flag = true;
                    }
           	       	else
           	       	{
                        // $.msgBox({
                        // title: "Warning",
                        //  content: "Coupon "+ entered_voucher_code +" year " +year+" is not minor than "+endDate_year,
                        //  type: "error",
                        //  opacity:0.6,
                        //  buttons: [{ value: "Ok" }],
                        // });
           	       		valid_flag = false;
           	       	}
                    // $.msgBox({
                    //             title: "Warning",
                    //              content: "Salgo de valid_voucher_flag con valor valid_flag "+valid_flag,
                    //              type: "error",
                    //              opacity:0.6,
                    //              buttons: [{ value: "Ok" }],
                    //          });
   	        	}	
                // Fin de valid_voucher_flag==true
                // sale con valid_flag = true si la fecha del vale es correcta

       	        	
       	        if(valid_flag == true)
       	        {
   	        	    if (entered_voucher_code == '')
   	        	    {
   	        		    $.msgBox({
   					        title: "Warning",
   					        content: "Falta el número del vale",
   					        type: "error",
   					        opacity:0.6,
   					        buttons: [{ value: "Ok" }],
   					    });
 	        		    flag=false;
   	        	    }
   	        	    else
   	        	    {
   	        		    if (temp_voucher_array.length > 0)
   	        		    {
   	        		        for(sold_voucher in temp_voucher_array)
	        			    {
       	        				if (temp_voucher_array[sold_voucher]==entered_voucher_code)
       	        				{
       	        					$.msgBox({
       	        					    title: "Warning",
       	        					    content: "Este vale ya se ha utilizado",
       	        					    type: "error",
       	        					    opacity:0.6,
       	        					    buttons: [{ value: "Ok" }],
       	        					});
       	        					scanned_flag=false;
       	        					flag = false;
       	        					break;
    	        				}
       	        				else
       	        				{
       	        					flag=true;
       	        				}
	        			    }

   	        			    if(flag==true)
   	        			    {
   	        				    for (voucher in gift_voucher_obj)
   	        	   	            {
   	        	   	        	  if(gift_voucher_obj[voucher].voucher_serial_no==entered_voucher_code)
   	        	   	        	  {
   	        	   	        		is_sold = gift_voucher_obj[voucher].out;
   	        	   	        		is_redeemed = gift_voucher_obj[voucher].in;
   	        	   	        		if (is_redeemed == true)
   	        	   	        		{
   	        	   	        			flag=false;
   	        	   	        			break;
   	        	   	        		}
   	        	   	        		else if(is_sold==true)
   	        	   	        		{
   	        	   	        			voucher_code_array.push(entered_voucher_code)
   	        	   	        			temp_voucher_array.push(entered_voucher_code)
   	        	   	        			name_template = gift_voucher_obj[voucher].voucher_name;
   	        	   	        			name_template_array.push(gift_voucher_obj[voucher].voucher_name)
   	        	   	        			flag=true;
   	        	   	        			break;
   	        	   	        		}
   	        	   	        		else
   	        	   	        		{
       	        	   	        		$.msgBox({
       	   	        					    title: "Warning",
       	   	        					    content: "Este vale no es correcto",
       	   	        					    type: "error",
       	   	        					    opacity:0.6,
       	   	        					    buttons: [{ value: "Ok" }],
       	   	        					});
   	        	   	        			flag=false;
   	        	   	        		}
   	        	   	        	  }
   	        	   	        	  else // Improbable caso que ahora no se encuentre el serial cuando antes se encontro
   	        	   	        	  {
                                    $.msgBox({
                                        title: "Warning",
                                        content: "Este es un vale no correcto",
                                        type: "error",
                                        opacity:0.6,
                                        buttons: [{ value: "Ok" }],
                                    });
   	        	   	        		flag=false;
   	        	   	        	  }
   	        	   	           }
   	        			    }
	        				
   	        		    }
   	        		    else
                        // este else if valid_flag = true (hay un no. de voucher con fecha adecuada) and temp_voucher_array.length == 0
   	        		    {
       	        		  for (voucher in gift_voucher_obj)
       	   	        	  {
           	   	        	if(gift_voucher_obj[voucher].voucher_serial_no==entered_voucher_code)
           	   	        	{
                                // $.msgBox({
                                // title: "Warning",
                                //  content: "En gift_vou_obj encontrado el serial no.",
                                //  type: "error",
                                //  opacity:0.6,
                                //  buttons: [{ value: "Ok" }],
                                // });
           	   	        		is_sold = gift_voucher_obj[voucher].out;
           	   	        		is_redeemed = gift_voucher_obj[voucher].in;
           	   	        		if (is_redeemed == true)
           	        	   	    {
           	   	        			redeemed_flag = false;
           	   	        			flag=false;
           	   	        			$.msgBox({
        	        					    title: "Warning",
        	        					    content: "Este vale ya se ha utilizado",
        	        					    type: "error",
        	        					    opacity:0.6,
        	        					    buttons: [{ value: "Ok" }],
        	        					});
           	   	        			break;
           	        	   	    }
           	        	   	    else if(is_sold==true)
           	        	   	    {
           	        	   	    	voucher_code_array.push(entered_voucher_code)
           	        	   	    	temp_voucher_array.push(entered_voucher_code)
           	        	   	    	name_template = gift_voucher_obj[voucher].voucher_name;
           	        	   	    	name_template_array.push(gift_voucher_obj[voucher].voucher_name)
           	        	   	    	flag=true;
                                    // $.msgBox({
                                    //     title: "Warning",
                                    //      content: "This coupon is_sold",
                                    //      type: "error",
                                    //      opacity:0.6,
                                    //      buttons: [{ value: "Ok" }],
                                    //  });
           	        	   	    	break;
           	   	        		}
           	   	        		else
           	   	        		{
                                    //CAMBIO
                                    $.msgBox({
                                            title: "Warning",
                                            content: "Este vale no se ha utilizado pero no se puede utilizar",
                                            type: "error",
                                            opacity:0.6,
                                            buttons: [{ value: "Ok" }],
                                        });

           	   	        			flag=false;

                                    // CAMBIO
                                    break;
           	   	        		}
           	   	        	} // FIN de if que localiza el voucher serial no.
           	   	        	else
           	   	        	{
           	   	        		flag=false;
                                // CAMBIO este break no puede estar aqui porque entonces solo analiza el primer voucher de la lista
                                // break;
           	   	        	}
       	   	        	  }
   	        		    }
   	        	    } //FIN else entered_voucher_code != ''
       	        } //FIN else valid_flag == true
       	        else
       	        {
                    // $.msgBox({
                    //                title: "Warning",
                    //              content: "Consulte este error con su servicio de mantenimiento",
                    //              type: "error",
                    //              opacity:0.6,
                    //              buttons: [{ value: "Ok" }],
                    //          });
       	        	flag=false;
       	        }
   	        	
   	        	if (flag==false)
   	        	{
   	        		if(scanned_flag == true && redeemed_flag == true)
   	        		{
   	        			$.msgBox({
    					    title: "Warning",
    					    content: "Este vale no se puede utilizar",
    					    type: "error",
    					    opacity:0.6,
    					    buttons: [{ value: "Ok" }],
    					});
   	  	        	}
   	        		
   	        	}
   	        	else
   	        	{
   	        	for (product in products)
   	        	{
   	        		if(products[product].name==name_template)
   	        		{   
   	        			var coupon_price = parseFloat(products[product].list_price);
   	        			
   	        			if(remaining>=coupon_price){
   	        				this.getAmount(updated_sale_price);
   	        				this.update_payment_summary();
   	        				var total=this.getAmount(updated_sale_price);
   	        				updated_sale_price = parseFloat(total) + coupon_price
   	        				this.getAmount(updated_sale_price);
   	        				this.renderElement();
   	        				$("#gift_coupon_desc").show();
   	        				$("#gift-voucher-code").show();
   	        				document.getElementById("gift-coupon").value="";
   	        				document.getElementById("gift-coupon").focus(); 	        			
   	        				break;
   	        			}
   	        			else{
   	        	        	var payment_lines = this.pos.get_order().get('paymentLines');
   	        				if(payment_lines.length<2){
   	        				$.msgBox({
        					    title: "Warning",
        					    content: "El valor del vale no puede ser superior al valor de la venta<br/><br/>Valor del vale: "+this.format_currency(coupon_price,2),
        					    type: "error",
        					    opacity:0.6,
        					    buttons: [{ value: "Ok" }],
        					});
   	        				
   	        				}
   	        				else{
   	        					$.msgBox({
   	        					    title: "Warning",
   	        					    content: "El valor del vale no puede ser superior al pendiente de cobro.</br> Use otro vale o ajuste los cobros<br/><br/>Valor del vale: "+this.format_currency(coupon_price,2),
   	        					    type: "error",
   	        					    opacity:0.6,
   	        					    buttons: [{ value: "Ok" }],
   	        					});
   	        				}
   	        				if (temp_voucher_array.length > 0)
   	    	        		{
   	    	        			for(sold_voucher in temp_voucher_array)
   	    	        			{
   	    	        				if (temp_voucher_array[sold_voucher]==entered_voucher_code)
   	    	        				{
   	    	        					var index = temp_voucher_array.indexOf(entered_voucher_code);
 										temp_voucher_array.splice(index, 1);
 										var code_index = voucher_code_array.indexOf(entered_voucher_code);
 										voucher_code_array.splice(code_index, 1);
 										break;
   	    	        				}
   	    	        			}
   	    	        		}
   	        			}
   	        		}
   	        	}
   	        	}
   	        	this.pos.get('selectedOrder').set_coupon_redeemed(voucher_code_array);
	            return voucher_code_array;
   	        	
   			},
   			
   			getAmount : function(amt){
   				var ret_amt;
   				var method_detail_gift=(this.pos.get('journallists'));
   	        	var paymentlinesss = this.pos.get_order().get('paymentLines');
   							paymentlinesss.each(function(line){
   				        		for(i=0;i<method_detail_gift.length;i++){
   				                	if(method_detail_gift[i].for_gift_coupens){
   				                		var m_name=method_detail_gift[i].name;
   				                		if(!line.name.search(m_name)){
   				                			line.set_amount(amt);
   				                			ret_amt=line.get_amount();
   				                			break;
   				                		}
   				                	}
   				                }
   				        	});
   							return ret_amt;
   				
   			},
   			
    });
    
    var super_ = module.ReceiptScreenWidget.prototype.print
    module.ReceiptScreenWidget.prototype.print = function(){
    	setTimeout(function(){
            window.print();
            },100);
        }
    
    var _super_product_show_ = module.ProductScreenWidget.prototype.show;
    module.ProductScreenWidget.prototype.show = function(){
    	this.pos.set('hide_barcode',false);
    	_super_product_show_.call(this);
    }
    
    var _super_scale_order_product_ = module.ScaleScreenWidget.prototype.order_product;
    module.ScaleScreenWidget.prototype.order_product = function(){
    	this.pos.set('hide_barcode',false);
    	_super_scale_order_product_.call(this);
    	
    }
    
    var _super_scale_get_product_weight_string_ = module.ScaleScreenWidget.prototype.get_product_weight_string;
    module.ScaleScreenWidget.prototype.get_product_weight_string = function(){
    	weightstr = _super_scale_get_product_weight_string_.call(this);
    	new_weightstr = weightstr.replace('Kg','lb(s)')
    	return new_weightstr;
    }
}

openerp.style_aristos_quick_sale = function (instance) {
    var _t = instance.web._t;
    var QWeb = instance.web.qweb;
    var Session = instance.session;
    var user_auth=0;

    var round_di = instance.web.round_decimals;

    instance.web.sale = instance.web.sale || {};

    instance.web.client_actions.add('open_quick_sale', 'instance.web.sale.QuickSaleAction');
    instance.web.sale.QuickSaleAction = instance.web.Widget.extend({
        template: 'QuickSaleAction',
        events: {
            'click .cart-row-item .product-image': 'product_image_click',
            'click .cart-row-item .delete-cart-line':'remove_line',
            'focusout input#in-global-discount':'change_discount',
            'focusout select#sel-payment-term':'change_payment_term',
            'focusout select#sel-payment-mode':'change_payment_mode',
            'focusout select#sel-payment-type':'change_sale_type',
            'focusout textarea#note':'change_note',
            'focusout .cart-row-item .product-qty input.qty':'change_quantity',
            // 'focusout .cart-row-item .product-description .description':'change_product_description',
            'focusout .cart-row-item .product-price input.price_unit':'change_product_price',
            'keyup #customer-name':'customer_name_keyup',
            'keyup input#product-search': 'scan_handler',
            'keyup input#sale_order_search':'sale_order_search',
            'click button.add-variants':'add_variants',
            'click #slidemenubtn':'slidemenubtn',
            'click .new_sale_order':'new_sale_order',
            'click .cart-row-item .abono input.abono':'set_abono',
            'click .cart-row-item .entregado input.entregado':'set_entregado',
            'click .cart-row-item .cambio input.cambio':'set_cambio',
            'click .cart-row-item .sin-cargo input.sin-cargo':'set_sincargo',
            
        },
        init: function(parent, context) {
            this._super(parent);
            if (context.context.sale_order_id) this.sale_order_id = [context.context.sale_order_id];
            this.cid = 0;
            this.cart_lines = [];
            this.variant_products = false;
            this.company_id = Session.company_id;
            // por defecto el precio es readonly, por usuario y grupo cambiamos con $(this).removeAttr("readonly");
            // en el render_orderline
            // console.info("Valor de session: ",Session);
            this.load_price_auth(Session.uid);
            this.account_fiscal_position = false;
            this.load_currency();
            this.load_fiscal_position();
//            Barcode Scan Method Code
            this.code = "";
        	this.timeStamp  = 0;
        	this.onlynumbers = true;
        	this.timeout = null;
        },
        load_price_auth: function(user_id){
            var self = this;
            new instance.web.Model('res.users').call('load_user_by_id',[user_id], {}, {async: false})
            .then(function(user_id){
                // console.info("Valor de user_id: ",user_id);
                if(user_id && user_id[0]){
                    $(this).find(".price_unit").removeAttr("readonly");
                    // console.info("Cambiando el valor de User Auth: ",Session.uid);
                    user_auth = Session.uid;
                }
            });
        },
        new_sale_order: function(){
        	this.destroy_sale_order();
        },
        scan_handler: function(e){
            var self = this;
            if(e.which === 13 || e.wich==9){ //ignore returns
                e.preventDefault();
                // return;
                // console.info("Intro detected: ",self.code);
                self.scan(self.code);
                self.code = "";
                self.onlynumbers = true;
                return;
            }
            // if(self.timeStamp + 50 < new Date().getTime()){
            //     self.code = "";
            //     self.onlynumbers = true;
            // }
            // self.timeStamp = new Date().getTime();
            // clearTimeout(self.timeout);
            if( e.which < 48 || e.which >= 58 ){ // not a number
                self.onlynumbers = false;
            }
            if(e.which != 16){
                // self.code += String.fromCharCode(e.which);
                var keyCode = e.keyCode || e.which;
                if (keyCode >= 96 && keyCode <= 105) {
                    // Numpad keys
                    keyCode -= 48;
                }
                self.code += String.fromCharCode(keyCode);
                // console.info("Code: ",self.code);
            }
            // self.timeout = setTimeout(function(){
            //     self.scan(self.code);
            //     self.code = "";
            //     self.onlynumbers = true;
            // },200);
        },
        scan: function(code){
            var self = this;
            // console.info("Barcode: ",code);
            if(code.length >= 8){
                // fields = ['name', 'display_name', 'list_price', 'ean13', 'description_sale','virtual_available','product_tmpl_id','attribute_line_ids','product_variant_ids'];
                fields = ['name', 'list_price', 'ean13', 'description_sale','virtual_available','product_tmpl_id','product_variant_ids'];
                limit = 200;
                order='description_sale';
                new instance.web.Model("product.product").call('search_read',[['|', ['ean13','=',code],['default_code','=',code]],fields, false, 1], {}, {async: false})
                .then(function(products){
                    // console.info("Products: ",products);
                    if(products && products[0]){
                        var product = products[0];
                        if(product.product_variant_ids.length > 1){
                            //new instance.web.Model("product.product").call('search_read',[['|', ['id','in',product.product_variant_ids],['default_code','=',code]],fields], {}, {async: false}, order='description_sale asc')
                            new instance.web.Model("product.product").call('search_read',[['|', ['id','in',product.product_variant_ids],['default_code','=',code]],fields,false,limit,order], {}, {async: false})
                            .then(function(variant_products){
                                if(variant_products && variant_products.length > 0){
                                    self.variant_products = variant_products;
                                    // var i;
                                    // for (i = 0; i < variant_products.length; i++) {
                                    //   self.prepare_orderline(variant_products[i]);
                                    // } 
                                    
                                    var variant_modal_html = QWeb.render('VariantModal',{
                                        widget:  self,
                                        product: product,
                                        variant_products:variant_products,
                                    });
                                    // $('#product-search').autocomplete('close').val('');
                                    $('#product-search').val('');
                                    $('.oe_quick_sale_view .popup-view').html('');
                                    $('.oe_quick_sale_view .popup-view').html(variant_modal_html);
                                    $('#variant_popup').modal('show');
                                    self.index = 0;
                                    // $('.p_variant_qty')[0].focus();
                                    // $('.p_variant_qty:first').focus();
                                    $('#variant_popup').keydown(_.bind(self.keydown_discount, self));
                                }
                            });
                        }else{
                            self.prepare_orderline(product);
                        }
                    }else{
                        $('#product-search').attr("placeholder", "No product with this code");
                        $('#product-search').val('');
                    }
                });
            }else{
                $('#product-search').attr("placeholder", "Error on product code");
                $('#product-search').val('');
            }
        },
        keydown_discount: function(event){
            event.stopImmediatePropagation();
            var self = this;
            if (event.keyCode == 40) {
                if(self.index >= 0){
                    self.index += 1;
                    var $el = $('.p_variant_qty')[self.index];
                    if($el){
                        $el.focus();
                    }else{
                        self.index -= 1;
                    }
                }
            }
            if (event.keyCode == 38) {
                if(self.index > 0){
                    self.index -= 1;
                    var $el = $('.p_variant_qty')[self.index];
                    $el.focus();
                }
            }
        },
        start: function() {
            self = this;
            this._super();
            $('.oe_leftbar').hide();
            $('#customer-name').focus();
            self.renderElement();
            self.load_pay_types();
            self.load_pay_terms();
            self.load_pay_modes();
            self.update_summary();
            if(this.sale_order_id && this.sale_order_id.length > 0){
                var sale_order = self.get_sale_order_by_id(this.sale_order_id[0]);
                self.fill_sale_order(sale_order);
            }
        },
        prepare_orderline: function(product){
            var line = {
                'product_id': product.id,
                'display_price':product.list_price,
                'quantity':1,
                'display_name':product.display_name,
                'price_unit':product.list_price || 0,
                'product': product,
                'description':product.description_sale,
            };
            $('#product-search').attr('placeholder','Search product with barcode.');
            $('#product-search').val('');
            // $('#product-search').autocomplete('close').val('');
            self.add_orderline(line);
            
        },
        sale_order_search: function(e){
            if(e.which == 13){
            	self.destroy_sale_order();
                var query = $(e.currentTarget).val();
                $(e.currentTarget).val('');
                if(query){
                    var sale_order = self.get_sale_order_by_query(query);
                    if(sale_order){
                    	self.fill_sale_order(sale_order);
                    }else{
                    	self.destroy_sale_order();
                    	return alert("Sale order not found!");
                    }
                }
            }
        },
        fill_sale_order: function(sale_order){
            var self = this;
            if(sale_order && sale_order.partner_id){
                self.set_customer(sale_order.partner_id);
            }
            // if(sale_order && sale_order.notes){
            //     self.$el.find('textarea#notes').val(sale_order.notes);
            // }
            if(sale_order && sale_order.note){
                self.$el.find('textarea#note').val(sale_order.note);
            }
            if(sale_order && sale_order.payment_term){
                self.$el.find('#sel-payment-term').val(sale_order.payment_term);
            }
            if(sale_order && sale_order.payment_mode_id){
                self.$el.find('#sel-payment-mode').val(sale_order.payment_mode_id);
            }
            if(sale_order && sale_order.type_id){
                self.$el.find('#sel-payment-type').val(sale_order.type_id);
            }
            if(sale_order && sale_order.payment_discount > 0){
                self.$el.find('#in-global-discount').val(sale_order.payment_discount);
            }else if(sale_order && sale_order.global_discount){
                self.$el.find('#in-global-discount').val(sale_order.global_discount);
            }
            if(sale_order && sale_order.date_order){
                self.$el.find('input#datetime').val(sale_order.date_order);
            }
            if(sale_order && sale_order.lines){
                self.update_so = false;
                sale_order.lines.map(function(line){
                    self.addnoup_orderline(line);
                });
                self.update_so = true;
            }
        },
        get_sale_order_by_id: function(sale_order_id){
            var self = this;
            if(sale_order_id){
                new instance.web.Model('sale.order').call('load_sale_order_by_id',[sale_order_id], {}, {async: false})
                .then(function(sale_order){
                    if(sale_order && sale_order[0]){
                        self.set_sale_order(sale_order[0]);
                    }
                });
                return self.get_sale_order();
            }
        },
        get_sale_order_by_query: function(query){
            var self = this;
            if(query){
                new instance.web.Model('sale.order').call('load_sale_order_by_query',[query], {}, {async: false})
                .then(function(sale_order){
                    if(sale_order && sale_order[0]){
                        self.set_sale_order(sale_order[0]);
                    }else{
                    	self.destroy_sale_order();
                    }
                });
                return self.get_sale_order();
            }
        },
        set_sale_order: function(sale_order){
        	if(sale_order.sale_order_id){
        		this.sale_order_id = sale_order.sale_order_id;
        	}
            this.sale_order = sale_order;
        },
        get_sale_order: function(){
            return this.sale_order;
        },
        destroy_sale_order: function(){
        	this.set_sale_order(false);
        	this.sale_order = false;
        	this.sale_order_id = false;
        	this.cart_lines = [];
            $('#payment-term').val('');
            $('#in-global-discount').val(0);
            // $('#notes').val('');
            $('#note').val('');
            this.renderElement();
        },
        renderElement: function () {
            this._super();
            var dt = new Date();
            var currentDate = dt.getDate()+ "/" + (dt.getMonth()+1) + "/" + dt.getFullYear();
            var mins = '0'+dt.getMinutes();
            var currentTime = dt.getHours() + ":" + mins.slice(-2);
            var currentDateTime = currentDate +' '+ currentTime;
            $('#datetime').datetimepicker({
	            calendarWeeks: true,
	            changeMonth: true,
                changeYear: true,
                showWeek: true,
                showButtonPanel: true,
	        }).val(currentDateTime);
            $('#customer-name').autocomplete({
                source: function (request, response) {
                    setTimeout(function() {
                        domain = ['|','|',['name','ilike',request.term],['ref','ilike',request.term],['comercial','ilike',request.term]];
                        fields = ['name', 'property_product_pricelist','property_payment_term','customer_payment_mode','credit'];
                        new instance.web.Model("res.partner").call('search_read',[domain,fields, false, 7], {}, {async: false})
                        .then(function(partners){
                            var partners_list = [];
                            self.partners = partners;
                            _.each(partners, function(partner){
                                partners_list.push({
                                    'id':partner.id,
                                    'value':partner.name,
                                    'label':partner.name
                                });
                            });
                            response(partners_list);
                        });
                    }, 500);
                },
                select: function(event, partner){
                    event.stopImmediatePropagation();
                    // event.preventDefault();
                    if(partner.item && partner.item.id){
                        var partner_obj = _.find(self.partners, function(customer) { return customer.id == partner.item.id });
                        if(partner_obj){
                             self.set_customer(partner_obj);
                        }
                    }
                },
                focus: function (event, ui) {
                    event.preventDefault(); // Prevent the default focus behavior.
                },
                close: function (event) {
                    // it is necessary to prevent ESC key from propagating to field
                    // root, to prevent unwanted discard operations.
                    if (event.which === $.ui.keyCode.ESCAPE) {
                        event.stopPropagation();
                    }
                },
                autoFocus: true,
                html: true,
                minLength: 1,
                delay: 1000
            });
            $('#product-search').autocomplete({
                source: function (request, response) {
                    var client_validate = self.client_validation();
                    if(client_validate){
                        return $('#product-search').val('');
                    }
            //         // domain = ['|', '|', ['name','ilike',request.term],['ean13','ilike',request.term],['default_code','ilike',request.term]];
            //         domain = ['|',['ean13','ilike',request.term],['default_code','ilike',request.term]];
            //         // fields = ['name', 'display_name', 'list_price', 'ean13', 'description_sale','virtual_available','product_tmpl_id','attribute_line_ids'];
            //         fields = ['name', 'display_name', 'list_price', 'ean13', 'description_sale','virtual_available','product_tmpl_id'];
            //         new instance.web.Model("product.product").call('search_read',[domain,fields, false, 25], {}, {async: false})
            //         .then(function(products){
            //             var products_list = [];
            //             self.products = products;
            //             if($('#product-search').val!=''){
            //                 _.each(products, function(product){
            //                     products_list.push({
            //                         'id':product.id,
            //                         'value':product.display_name,
            //                         'label':product.display_name
            //                     });
            //                 });
            //                 response(products_list);                            
            //             }else{
            //                 response();
            //             }
            //         });
                 },
            //     select: function(event, product){
            //         event.stopImmediatePropagation();
            //         event.preventDefault();
            //         if(product.item && product.item.id){
            //             var product_obj = _.find(self.products, function(prod) { return prod.id == product.item.id });
            //             if(product_obj){
            //                 self.prepare_orderline(product_obj);
            //             }
            //         }
            //     },
                focus: function (event, ui) {
                    event.preventDefault(); // Prevent the default focus behavior.
                },
                close: function (event) {
                    // it is necessary to prevent ESC key from propagating to field
                    // root, to prevent unwanted discard operations.
                    if (event.which === $.ui.keyCode.ESCAPE) {
                        event.stopPropagation();
                    }
                },
                autoFocus: true,
                html: true,
                minLength: 1,
                delay: 3000
            });
        },
        format_currency: function(amount,precision){
            var currency = (this.currency) ? this.currency : {symbol:'$', position: 'after', rounding: 0.01, decimals: 2};
            var decimals = currency.decimals;

            if (typeof amount === 'number') {
                amount = round_di(amount,decimals).toFixed(decimals);
            }

            if (currency.position === 'after') {
                return amount + ' ' + (currency.symbol || '');
            } else {
                return (currency.symbol || '') + ' ' + amount;
            }
        },
        format_currency_precision: function(amount,precision){
            var currency = (this.currency) ? this.currency : {symbol:'$', position: 'after', rounding: 0.01, decimals: 2};
            var decimals = currency.decimals;

            if (typeof amount === 'number') {
                amount = round_di(amount,decimals).toFixed(decimals);
            }
            return amount
        },
        load_currency: function(){
	    	var self = this;
	    	new instance.web.Model('sale.order').call('load_currency',[self.company_id], {}, {async: false})
            .then(function(currency){
                if(currency && currency[0]){
                    self.currency = currency[0];
                    if (self.currency.rounding > 0) {
                        self.currency.decimals = Math.ceil(Math.log(1.0 / self.currency.rounding) / Math.log(10));
                    } else {
                        self.currency.decimals = 0;
                    }
                }
            });
	    },
        load_fiscal_position: function(){
            var self = this;
            new instance.web.Model("account.payment.term").call('search_read',[[],['name']], {}, {async: false})
            .then(function(records){
                if(records.length > 0){
                    self.account_fiscal_position = records
                }
            });
        },
        load_pay_terms: function(){
            var self = this;
            self.$el.find('#sel-payment-term').empty();
            new instance.web.Model("account.payment.term").call('search_read',[[],['id','name','discount']], {}, {async: false})
            .then(function(records){
                if(records.length > 0){
                    _.each(records, function(record){
                        self.$el.find('#sel-payment-term').append('<option value="0" dis="0"></option>');
                        // console.info("Valor en pay terms para discount: ",record.discount);
                        self.$el.find('#sel-payment-term').append('<option value="'+record.id+'" dis="'+record.discount+'">'+record.name+'</option>');
                    });
                }
            });
        },
        load_pay_modes: function(){
            var self = this;
            self.$el.find('#sel-payment-mode').empty();
            new instance.web.Model("payment.mode").call('search_read',[[],['id','name']], {}, {async: false})
            .then(function(records){
                if(records.length > 0){
                    self.$el.find('#sel-payment-mode').append('<option value="0"></option>');
                    _.each(records, function(record){
                        // console.info("Valor de pay modes: ",record.name);
                        self.$el.find('#sel-payment-mode').append('<option value="'+record.id+'">'+record.name+'</option>');
                    });
                }
            });
        },
        load_pay_types: function(){
            var self = this;
            self.$el.find('#sel-payment-type').empty();
            new instance.web.Model("sale.order.type").call('search_read',[[],['id','name']], {}, {async: false})
            .then(function(records){
                if(records.length > 0){
                    _.each(records, function(record){
                        // console.info("Valor de pay types: ",record.name);
                        self.$el.find('#sel-payment-type').append('<option value="'+record.id+'">'+record.name+'</option>');
                    });
                    self.$el.find('#sel-payment-type').val('1');
                }
            });
        },
        customer_name_keyup: function(event){
            var self = this;
            setTimeout(function() {
                if(!$(event.currentTarget).val()){
                    this.customer = null;
                }
            },2000);
        },
        set_customer: function(customer){
            this.customer = customer;
            if(customer && customer.property_product_pricelist.length > 0){
                this.set_pricelist_id(customer.property_product_pricelist[0]);
            }
            var credit_st = customer.credit+' €';
            this.$el.find('#customer-credit').val(credit_st.replace('.',','));
            if(customer && customer.property_payment_term != false){
                // console.info("Cliente con plazo de pago: ",customer.property_payment_term[0]);
                this.$el.find('#sel-payment-term').val(customer.property_payment_term[0]);
                var discount = $('#sel-payment-term').find(':selected').attr('dis');
                // console.info("Valor de descuento: ",discount);
                if (discount > 0){
                    self.$el.find('#in-global-discount').val(discount);
                }
            }
            if(customer && customer.customer_payment_mode != false){
                // console.info("Cliente con modo de pago: ",customer.customer_payment_mode[0]);
                this.$el.find('#sel-payment-mode').val(customer.customer_payment_mode[0]);
            }
            this.$el.find('#customer-name').val(customer.name);
            $('#product-search').val('');
            $('#product-search').focus();
        },
        set_pricelist_id: function(pricelist_id){
            this.pricelist_id = pricelist_id;
        },
        get_pricelist_id: function(){
            return this.pricelist_id;
        },
        client_validation: function(){
            if(!this.customer){
                dialog = new instance.web.Dialog(this, {
                    title: _t("No Customer Defined!"),
                    size: 'medium',
                    buttons: [
                        {text: _t("Close"), click: function() {
                            this.parents('.modal').modal('hide');
                            self.$el.find('#customer-name').focus();
                        }}
                    ]
                }).open();
                var image = "<div style='text-align: center;'>Before choosing a product, <br/> select a customer in the quick sales interface.</div>";
                dialog.$el.html(image);
                return true;
            }
        },
        add_orderline: function(line){
	    	var self = this;
            var client_validate = self.client_validation();
            if(client_validate){
                return
            }
	    	line['cid'] = self.cid += 1;
	    	var pricelist_id = self.get_pricelist_id();
	    	if(pricelist_id){
	    	    if(line && !line.line_id){
	    	        new instance.web.Model('sale.order').call('get_product_price',[pricelist_id, line.product.id], {}, {async: false})
                    .then(function(pricelist_price){
                        if(pricelist_price && pricelist_price[0]){
                            line['price_unit'] = self.format_currency_precision(pricelist_price[0].new_price)|| 0;
                        }
                    });
	    	    }
	    	}
	    	var line_html = QWeb.render('CardLine',{
                widget:  this,
                line: line,
                image_url:this.get_product_image_url(line.product.id),
            });
	    	// $('.product-lines').append(line_html);
            // con append lo agrega al final, con prepend al principio
            $('.product-lines').prepend(line_html);
	    	self.cart_lines.push(line);
	    	self.render_orderline(line);
	    },
        addnoup_orderline: function(line){
            var self = this;
            var client_validate = self.client_validation();
            if(client_validate){
                return
            }
            line['cid'] = self.cid += 1;
            var pricelist_id = self.get_pricelist_id();
            if(pricelist_id){
                if(line && !line.line_id){
                    new instance.web.Model('sale.order').call('get_product_price',[pricelist_id, line.product.id], {}, {async: false})
                    .then(function(pricelist_price){
                        if(pricelist_price && pricelist_price[0]){
                            line['price_unit'] = self.format_currency_precision(pricelist_price[0].new_price)|| 0;
                        }
                    });
                }
            }
            var line_html = QWeb.render('CardLine',{
                widget:  this,
                line: line,
                image_url:this.get_product_image_url(line.product.id),
            });
            // $('.product-lines').append(line_html);
            // con append lo agrega al final, con prepend al principio
            $('.product-lines').prepend(line_html);
            self.cart_lines.push(line);
            self.rendernoup_orderline(line);
        },
	    get_product_image_url: function(product_id){
	        // return window.location.origin + '/web/binary/image?model=product.product&field=image_medium&id='+product_id;
            return window.location.origin + '/web/binary/image?model=product.product&field=image&id='+product_id;
	    },
	    product_image_click: function(event){
	        var line_id = $(event.currentTarget).parent().data('line-id');
	        var product_id = $(event.currentTarget).data('product-id');
            dialog = new instance.web.Dialog(this, {
                title: _t("Product Large Image"),
                size: 'large',
                buttons: [
                    {text: _t("Close"), click: function() {
                        this.parents('.modal').modal('hide');
                    }}
                ]
            }).open();
            var image = "<div style='text-align: center; width:50em; height:auto;'><img src='"+ this.get_product_image_url(product_id) + "' width='150%' height ='150%'/></div>";
            dialog.$el.html(image);
	    },
	    render_orderline: function(line){
            var self = this;
            var price = self.get_display_price(line);
	    	line.display_price = price;
	    	// var tax_detail = self.get_tax_amount_by_product_id(line.price_unit, line.quantity, line.product.id);
	    	// if(tax_detail){
	    	// 	line.product_tax_amount = tax_detail.total_amount;
	    	// }
	    	_.each($('tr.cart-row-item'), function(element, index){
	    		var line_element = $(element);
	    		var elem_id = Number(line_element.data('line-id'));
	    		if(elem_id === line.cid){
	    			line_element.replaceWith(QWeb.render('CardLine',{
	                    widget:  self,
	                    line: line,
	                    image_url:self.get_product_image_url(line.product.id),
	                }));
	    			_.extend(_.findWhere(self.cart_lines, { cid: line.cid }), line);
	    		}
	    	});
            $('.cart-row-item').each(function(){
                                if(
                                    parseInt($(this).find(".forecasted-qty").text()) < 0 ||
                                    parseInt($(this).find(".forecasted-qty").text())<(Number($(this).find(".qty").val())+0)
                                    ){
                                        if(!$(this).find(".entregado").is(":checked")&&
                                        !$(this).find(".abono").is(":checked")){
                                            $(this).find(".forecasted-qty").css('background-color','red');
                                    }
                                }
                                if(user_auth!=0){
                                    $(this).find(".price_unit").removeAttr("readonly");
                                }
                                // console.info("Valor de forecasted en render: ",$(this).find(".forecasted-qty").text());
                                // console.info("Valor de qty en render: ",$(this).find(".qty").val());
                                // console.info("Valor de user_auth en render: ",this.user_auth);
                            });
	    	// self.update_summary();
            self.update_order(line);
	    },
        rendernoup_orderline: function(line){
            var self = this;
            var price = self.get_display_price(line);
            line.display_price = price;
            _.each($('tr.cart-row-item'), function(element, index){
                var line_element = $(element);
                var elem_id = Number(line_element.data('line-id'));
                if(elem_id === line.cid){
                    line_element.replaceWith(QWeb.render('CardLine',{
                        widget:  self,
                        line: line,
                        image_url:self.get_product_image_url(line.product.id),
                    }));
                    _.extend(_.findWhere(self.cart_lines, { cid: line.cid }), line);
                }
            });
            $('.cart-row-item').each(function(){
                                if(
                                    parseInt($(this).find(".forecasted-qty").text()) < 5 ||
                                    parseInt($(this).find(".forecasted-qty").text())<(Number($(this).find(".qty").val())+5)
                                    ){
                                        if(!$(this).find(".entregado").is(":checked")&&
                                        !$(this).find(".abono").is(":checked")){
                                            $(this).find(".forecasted-qty").css('background-color','red');
                                    }
                                }
                            });
            // self.update_summary();
            self.update_order(line);
        },
	    // get_tax_amount_by_product_id: function(price_unit,quantity,product_id){
	    // 	var self = this;
	    // 	var amount = 0;
	    // 	var tax_ids = [];
	    // 	var price_unit = price_unit
	    // 	var quantity = quantity
	    // 	var company_id = self.company_id;
	    // 	var partner_id = self.customer;
     //        new instance.web.Model('sale.order').call('get_product_tax_amount',[price_unit, quantity, product_id, partner_id.id], {}, {async: false})
     //        .then(function(taxes_details){
     //        	if(taxes_details && taxes_details.amount){
     //        		amount = taxes_details.amount;
     //        	}
     //        });
	    // 	var result = {
	    // 		total_amount:amount,
	    // 	}
	    // 	return result;
	    // },
	    get_display_price: function(line){
            var self = this;
            if (line.cambio==true || line.sin_cargo==true){
                var price = 0;
            }else{   
                var price = ((line.price_unit || 0) * line.quantity);
            }
	    	return self.format_currency_precision(price);
	    },
	    remove_line: function(event){
            var self = this;
            var line_id = $(event.currentTarget).parent().data('line-id');
            if(line_id){
                self.remove_line_by_id(line_id);
            }else{
                alert('Line id not found!');
            }
	    },
	    remove_line_by_id: function(line_id){
            var self = this;
            // primero borrar la linea del pedido de venta
            self.reset_line(line_id);
            // luego quitar de la vista rapida
            _.each($('tr.cart-row-item'), function(element, index){
	    		var line_element = $(element);
	    		var elem_id = Number(line_element.data('line-id'));
	    		if(elem_id === line_id){
	    			line_element.remove();
	    			self.cart_lines = _.without(self.cart_lines, _.findWhere(self.cart_lines, {
	    				cid: line_id,
	    			}));
	    		}
	    	});
	    	// self.update_summary();
            $('#product-search').val('');
            $('#product-search').focus();
	    },
        set_entregado: function(event){
            var self = this;
            var line_id = $(event.currentTarget).parent().parent().data('line-id');
            // console.info("Marcado entregado en linea: ",line_id);
            if(line_id){
                self.set_entregado_by_id(line_id);
            }else{
                alert("Line id not found!");
            }
        },
        set_entregado_by_id: function(line_id){
            var self = this;
            self.cart_lines.map(function(line){
                    if(line && line.cid == line_id){
                        if (line.entregado == true){
                            line.entregado = false;
                        }else{
                            line.entregado = true;
                        }
                        // console.info("Sale de entregado con valor: ",line.entregado);
                        self.render_orderline(line);
                    }
                });

        },
        set_abono: function(event){
            var self = this;
            var line_id = $(event.currentTarget).parent().parent().data('line-id');
            // console.info("Marcado abono en linea: ",line_id);
            if(line_id){
                self.set_abono_by_id(line_id);
            }
        },
        set_abono_by_id: function(line_id){
            var self = this;
            self.cart_lines.map(function(line){
                    if(line && line.cid == line_id){
                        line.quantity *= -1;
                        if (line.abono == true){
                            line.abono = false;
                        }else{
                            line.abono = true;
                        }
                        // console.info("Valor del check abono en linea: ",line.abono);
                        self.render_orderline(line);
                    }
                });
        },
        set_cambio: function(event){
            var self = this;
            var line_id = $(event.currentTarget).parent().parent().data('line-id');
            // console.info("Marcado cambio en linea: ",line_id);
            if(line_id){
                self.set_cambio_by_id(line_id);
            }
        },
        set_cambio_by_id: function(line_id){
            var self = this;
            self.cart_lines.map(function(line){
                    if(line && line.cid == line_id){
                        if (line.cambio == true){
                            line.cambio = false;
                        }else{
                            line.cambio = true;
                        }
                        self.render_orderline(line);
                    }
                });
        },
        set_sincargo: function(event){
            var self = this;
            var line_id = $(event.currentTarget).parent().parent().data('line-id');
            // console.info("Marcado sin cargo en linea: ",line_id);
            if(line_id){
                self.set_sincargo_by_id(line_id);
            }
        },
        set_sincargo_by_id: function(line_id){
            var self = this;
            self.cart_lines.map(function(line){
                    if(line && line.cid == line_id){
                        if (line.sin_cargo == true){
                            line.sin_cargo = false;
                        }else{
                            line.sin_cargo = true;
                        }
                        self.render_orderline(line);
                    }
                });
        },
        change_discount: function(event){
            var self = this;
            var discount = $(event.currentTarget).val();
            // console.info("Valor de descuento: ",discount);
            self.update_discount(discount);
            // aqui solo cambiar en el summary el importe descontado total
            // luego al crear la orden de venta tener en cuenta el valor de este descuento
        },
        change_payment_term: function(event){
            var self = this;
            var payment = Number($(event.currentTarget).val());
            var discount = $('#sel-payment-term').find(':selected').attr('dis');
            // console.info("Valor de descuento: ",discount);
            self.$el.find('#in-global-discount').val(discount);
            self.update_discount(discount);
            self.update_payterm(payment);
            // aqui solo cambiar en el summary el importe descontado total
            // luego al crear la orden de venta tener en cuenta el valor de este descuento
        },
        change_payment_mode: function(event){
            var self = this;
            var payment = Number($(event.currentTarget).val());
            self.update_paymode(payment);
        },
        change_sale_type: function(event){
            var self = this;
            var type = Number($(event.currentTarget).val());
            self.update_type(type);
            var type_id = Number($('#sel-payment-type').val()); 
            // console.info("Valor de type_id en sale type: ",type_id);
            if(type_id==2){
                $('.header-panel').css({'background-color':'hotpink',});
            }else{
                $('.header-panel').css({'background-color':'#e8e8e8',});
            }
        },
        change_note: function(event){
            var note = $(event.currentTarget).val();
            self.update_note(note);
        },
        change_quantity: function(event){
            var self = this;
            var line_id = $(event.currentTarget).parent().parent().data('line-id');
            var qty = $(event.currentTarget).val();
            if(line_id){
                self.cart_lines.map(function(line){
                    if(line && line.cid == line_id){
                        line.quantity = qty || 0;
                        self.render_orderline(line);
                    }
                });
            }else{
                alert("Line id not found!");
            }
	    },
        change_product_price: function(event){
            var self = this;
            var line_id = $(event.currentTarget).parent().parent().data('line-id');
            var price = $(event.currentTarget).val();
            if(line_id){
                self.cart_lines.map(function(line){
                    if(line && line.cid == line_id){
                        line.price_unit = price || 0;
                        self.render_orderline(line);
                    }
                });
            }else{
                alert("Line id not found!");
            }
	    },
     //    change_product_description: function(event){
     //        var self = this;
     //        var line_id = $(event.currentTarget).parent().parent().data('line-id');
     //        var description = $(event.currentTarget).val();
     //        if(line_id){
     //            self.cart_lines.map(function(line){
     //                if(line && line.cid == line_id){
     //                    line.description = description || 0;
     //                    self.render_orderline(line);
     //                }
     //            });
     //        }
	    // },
        reset_line: function(line_id){
            var self = this;
            var vals = {
                'line_id':line_id,
                'sale_order_id': self.sale_order_id,
            }
            new instance.web.Model('sale.order').call('remove_line',[vals], {}, {async: false})
            .then(function(sale_order_id){
                if(sale_order_id){
                    self.sale_order_id = sale_order_id;
                }
            });
        },
        update_type: function(type){
            var self = this;
            var vals = {
                'type_id':type,
                'sale_order_id': self.sale_order_id,
            }
            new instance.web.Model('sale.order').call('update_type',[vals], {}, {async: false})
            .then(function(sale_order_id){
                if(sale_order_id){
                    self.sale_order_id = sale_order_id;
                }
            });
        },
        update_paymode: function(payterm){
            var self = this;
            var vals = {
                'payment_mode_id':payterm,
                'sale_order_id': self.sale_order_id,
            }
            new instance.web.Model('sale.order').call('update_paymode',[vals], {}, {async: false})
            .then(function(sale_order_id){
                if(sale_order_id){
                    self.sale_order_id = sale_order_id;
                }
            });
        },
        update_payterm: function(payterm){
            var self = this;
            var vals = {
                'payment_term':payterm,
                'sale_order_id': self.sale_order_id,
            }
            new instance.web.Model('sale.order').call('update_payterm',[vals], {}, {async: false})
            .then(function(sale_order_id){
                if(sale_order_id){
                    self.sale_order_id = sale_order_id;
                }
            });
        },
        update_discount: function(discount){
            var self = this;
            var vals = {
                'discount':discount,
                'sale_order_id': self.sale_order_id,
            }
            new instance.web.Model('sale.order').call('update_discount',[vals], {}, {async: false})
            .then(function(sale_order_id){
                if(sale_order_id){
                    self.sale_order_id = sale_order_id;
                }
            });
        },
        update_note: function(note){
            var self = this;
            var vals = {
                'note':note,
                'sale_order_id': self.sale_order_id,
            }
            new instance.web.Model('sale.order').call('update_note',[vals], {}, {async: false})
            .then(function(sale_order_id){
                if(sale_order_id){
                    self.sale_order_id = sale_order_id;
                }
            });
        },
        update_order: function(line){
            var self = this;
            var global_discount = Number($('#in-global-discount').val());
            var sale_order_id = self.sale_order_id || 0;
            if (sale_order_id == 0){
                var lines = self.cart_lines || [];
                if(lines.length > 0){
                    self.create_update_so();
                }
            }else{
                line['sale_order'] = sale_order_id;
                line['global_discount'] = global_discount;
                new instance.web.Model('sale.order').call('update_so_line',[line], {}, {async: false})
                .then(function(sale_order_id){
                if(sale_order_id){
                    self.sale_order_id = sale_order_id;
                }
                });
            }
        },
        update_summary: function(){
            var self = this;
            var lines = self.cart_lines || [];
            var sale_order_id = self.sale_order_id || 0;
            var total_products = 0;
	    	var total_quantity = 0;
	    	var order_total = 0;
            var order_total_abono = 0;
            var order_total_discount = 0;
            var order_total_nocharge = 0;
	    	var order_taxes = 0;
	    	var product_id_list = [];
            lines.map(function(line){
                if(line.quantity > 0){
                    total_quantity += Number(line.quantity);
                }
                if(line.display_price > 0){
                    order_total += Number(line.display_price)*(1-((Number($('#in-global-discount').val())/100)));
                    order_total_discount += Number(line.display_price)*(Number($('#in-global-discount').val())/100);
                }else if(line.display_price == 0){
                    // estara a cero el display_price en cambios o lineas sin cargo que se suman a ese descuento
                    order_total_nocharge += (Number(line.price_unit)*Number(line.quantity));
                }else{
                    // tendra valores negativos en el caso de abonos, no se cuenta el posible descuento
                    order_total += Number(line.display_price);
                    order_total_abono += Number(line.display_price);
                }
	    		// if(line.display_price > 0){
	    		// 	order_taxes += (line.product_tax_amount);
	    		// }
                if(($.inArray(line.product.id, product_id_list) == -1)){
                    total_products += 1
                    product_id_list.push(line.product.id);
                }
            });
	    	// order_total += order_taxes;
	    	self.set_order_total(order_total);
	    	$('table.order-details-sidebar').find('.order-total-qty .value').text(total_quantity);
	    	$('table.order-details-sidebar').find('.order-total-products .value').text(total_products);
	    	// $('table.order-details-sidebar').find('.order-total-taxes .value').text(self.format_currency(order_taxes));
            // $('table.order-details-sidebar').find('.order-total .value').text(self.format_currency(order_total));
            $('table.order-details-sidebar').find('.order-total-discount .value').text(self.format_currency(order_total_discount));
            $('table.order-details-sidebar').find('.order-total-nocharge .value').text(self.format_currency(order_total_nocharge));
            $('table.order-details-sidebar').find('.order-total-abono .value').text(self.format_currency(order_total_abono));
            $('table.order-details-sidebar').find('.order-total-net .value').text(self.format_currency(order_total));
	    	// if(lines.length > 0){
	    	//     if(self.update_so || !self.update_so){
	    	//         self.create_update_so();
	    	//     }
	    	// }
	    },
	    set_order_total: function(order_total){
            this.order_total = order_total;
	    },
	    get_order_total: function(){
            return this.order_total || 0;
	    },
	    addZero: function(value){
			if (value < 10) {
    			value = "0" + value;
    	    }
    	    return value;
    	},
	    create_update_so: function(){
	        var self = this;
            var lines = self.cart_lines || [];
            var customer = self.customer;
            var payment_term = Number($('#sel-payment-term').val());
            var payment_mode_id = Number($('#sel-payment-mode').val());
            var global_discount = Number($('#in-global-discount').val());
            // var notes = $('#notes').val();
            var note = $('#note').val();
            var type_id = Number($('#sel-payment-type').val());
            var datetime = $('#datetime').val();
            var vals = {
                'lines':lines,
                'partner_id':customer ? customer.id : false,
                'payment_term': payment_term != 0 ? payment_term : false,
                'payment_mode_id': payment_mode_id != 0 ? payment_mode_id : false,
                'type_id': type_id != 0 ? type_id : false,
                'global_discount': global_discount != 0 ? global_discount : false,
                // 'notes':notes,
                'note':note,
                'sale_order_id': self.sale_order_id,
                'datetime':datetime,
            }
            new instance.web.Model('sale.order').call('create_update_so',[vals], {}, {async: false})
            .then(function(sale_order_id){
                if(sale_order_id){
                    self.sale_order_id = sale_order_id;
                }
            });
	    },
	    add_variants: function(){
	        var self = this;
	        var variants = self.variant_products;
            var total_variant = 0;
            var variant_copy = 0;
            // primero contamos cuantas lineas tienen cantidad seleccionada
            _.each($('div.product-variants table tr'), function(el, index){
                var qty = $(el).find('td .p_variant_qty').val();
                if(qty && qty > 0){
                    total_variant+=1;
                }
            });
            // console.info("Total lineas variantes: ",total_variant);
            _.each($('div.product-variants table tr'), function(el, index){
                var qty = $(el).find('td .p_variant_qty').val();
                if(qty && qty > 0){
                    var id = $(el).data('id');
                    var product = _.find(variants, function(variant){ return variant.id === id });
                    var line = {
                        'product_id': product.id,
                        'display_price':product.list_price,
                        'quantity':qty,
                        'display_name':product.display_name,
                        'price_unit':product.list_price || 0,
                        'product': product,
                        'description':product.description_sale,
                    };
                    variant_copy +=1;
                    // console.info("Valor de variant_copy: ", variant_copy);
                    if (variant_copy==total_variant){
                        // solo actualizamos el total al final de todas las lineas agregadas
                        self.add_orderline(line);
                    }else{
                         self.addnoup_orderline(line);
                    }
                    
                }
            });
            $('#variant_popup').modal('hide');
            $("#variant_popup").unbind('keydown', self.keydown_discount);
            $('#product-search').attr('placeholder','Search product with barcode.');
            $('#product-search').val('');
            $('#product-search').focus();
        },
        slidemenubtn: function(){
            var self = this;
	    	$('#wrapper').removeClass('oe_hidden');
           	$('#wrapper').toggleClass("toggled");
           	$('#wrapper').find('i').toggleClass('fa fa-chevron-left fa fa-chevron-right');
           	if(!$('#wrapper').hasClass('toggled')){
                self.update_summary();
           	    $('.oe_quick_sale_view').css({
           			'width':'77%',
           		});
           		$('#slidemenubtn').css({
           			'right':'275px',
           		});
           	}else{
           	    $('.oe_quick_sale_view').css({
           			'width':'98%',
           		});
           		$('#slidemenubtn').css({
           			'right':'0px',
           		});
           	}
        },
    });
}
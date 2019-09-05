//updated
function openerp_pos_gift_voucher_widgets(instance, module){ //module is instance.point_of_sale
    var QWeb = instance.web.qweb;
    var is_gift_coupon;
    var is_loyalty_journal;
   
    var posmodule = instance.point_of_sale;
    
    var _super_renderElement = module.PaypadButtonWidget.prototype.renderElement;
	module.PaypadButtonWidget.prototype.renderElement = function(){
		_super_renderElement.call(this);
        var self = this;
		this.$el.click(function(){
        	var currentOrderLines = self.pos.get('selectedOrder').get('orderLines');
        	is_gift_coupon=self.cashregister.journal.for_gift_coupens;
        	is_loyalty_journal = self.cashregister.journal.is_loyalty_journal;
        	var order = self.pos.get('selectedOrder');
        	client = self.pos.get('selectedOrder').get_client()
        	
        	if(is_gift_coupon)
            {
        		$("#gift_coupon_desc").show();
        		$("#gift-voucher-code").show();
				document.getElementById("gift-coupon").focus();
            	$('input.paymentline-input').attr('id','coupon-calculated-price');
              	$('input.paymentline-input').attr('readonly','true');
            }
        	else if (is_loyalty_journal){
        		if (client){
	        		$('#loyalty_card').show()
	        		$('#loyalty-card').focus()
	        		$('input.paymentline-input').attr('id','loyalty-calculated-price');
        		}
        		else {
        			$(".paymentline-delete").trigger('click');
        			self.pos_widget.screen_selector.set_current_screen('products');
        			$.msgBox({
 					    title: "Warning",
 					    content: "Please Select Customer",
 					    type: "error",
 					    opacity:0.6,
 					    buttons: [{ value: "Ok" }],
 					});
        		}
        	}
        	else
            {
            	$('#coupon-calculated-price').attr('id','');
            	$('#loyalty-calculated-price').attr('id','');
                
            }
        	
        	
        	
        	////To generate unique serial no.

        	order.reset_global_serial_no();
        	for(line in currentOrderLines['models'])
			{
    		orderline_prod_id = currentOrderLines['models'][line].get_product().id
    		product_qty = currentOrderLines['models'][line].get_quantity()
    		for(i=0;i<product_qty;i++)
    		{
    			var line=order.get('orderLines').at(order.get('orderLines').length -1);
    			
    			line.uniqueSerialNo(i);
    			
    			order.set_coupon_id(orderline_prod_id);
    		}
			}
        	
        });
	}
    
//	module.LoyaltyCardPopUpWidget = module.PopUpWidget.extend({
//        template: 'LoyaltyCardPopUpWidget',
//        show: function(){
////        	this._super()
//        	var self = this;
//        	
//        	this.$el.find('.btnCancel').off('click').click(function(e) {
//                e.stopPropagation();
//                e.preventDefault();
//                self.pos_widget.screen_selector.close_popup();
//            });
//        }
//    });
	
//	module.PosUserWidget = posmodule.PosWidget.include({
//        template: 'PosWidget',
//
//        init: function(parent, options) {
//            this._super(parent);
//            var  self = this;
//        },
//        start: function(){
//            var self = this;
//            this._super().done(function(){
//            	self.screen_selector.show_popup_overall('useridpopup');
//            });
//        },
//        build_widgets: function() {
//            var self = this;
//            this._super();
//
//            this.loyalty_card_popup = new module.LoyaltyCardPopUpWidget(this, {});
//            this.loyalty_card_popup.appendTo(this.$el);
//
//            this.screen_selector.add_popup('loyaltyCard',this.loyalty_card_popup);
//            
//        },
//    });
}
  

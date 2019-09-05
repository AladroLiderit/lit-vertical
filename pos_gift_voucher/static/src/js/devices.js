function openerp_pos_gift_voucher_devices(instance,module){ //module is instance.pos_gift_voucher
	var _t = instance.web._t;

    module.BarcodeReader =  module.BarcodeReader.extend({
        actions:[
            'product',
            'cashier',
            'client',
            'coupon',
            'coupon1',
        ],
    });
    var _super_init = module.BarcodeReader.prototype.init;
	module.BarcodeReader.prototype.init = function(attributes){
		_super_init.call(this, attributes);
		barcode_patterns = {
				'product':  ['xxxxxxxxxxxxx'],
	            'cashier':  ['041xxxxxxxxxx'],
	            'client':   ['042xxxxxxxxxx'],
	            'weight':   ['21xxxxxNNDDDx'],
	            'discount': ['22xxxxxxxxNNx'],
	            'price':    ['23xxxxxNNNDDx'],
				'coupon':  	['xxxxxxxxxxxxxx'],
	            'coupon1':  ['xxxxxxxxxxxxxxx'],
	            };
		this.add_barcode_patterns(attributes.patterns || barcode_patterns);
	};
	
    var _super_barcode_scan = module.BarcodeReader.prototype.scan;
	module.BarcodeReader.prototype.scan = function(code){
		if(code.length === 14 || code.length === 15){
			var parse_result = this.parse_ean(code);
			if(parse_result.type in {'coupon':'', 'coupon1':''}){    //ean is associated to a product
	              if(this.action_callback['coupon']){
	                  this.action_callback['coupon'](parse_result);
	              }
	          }else{
	              if(this.action_callback[parse_result.type]){
	                  this.action_callback[parse_result.type](parse_result);
	              }
	          }
		}else{
			_super_barcode_scan.call(this, code);
		}
	};
	
	var _super_show_screens = module.ScreenWidget.prototype.show;
	module.ScreenWidget.prototype.show = function() {

		function barcode_coupon_action(code){
        }
		_super_show_screens.call(this);
		var self = this;
		var old_callbacks = this.pos.barcode_reader.action_callback;
		old_callbacks['coupon'] = barcode_coupon_action ? function(code){ barcode_coupon_action(code); } : undefined;
		this.pos.barcode_reader.set_action_callback(old_callbacks);
		
	};
	
    var _super_parse_ean = module.BarcodeReader.prototype.parse_ean;
	module.BarcodeReader.prototype.parse_ean = function(ean){
    	var parse_result = _super_parse_ean.call(this, ean);
    		
			if (!this.check_ean(ean)){
	        	if (ean.length === 14){
	        		parse_result = {
	                        encoding: 'code128',
	                        type:'coupon',  
	                        code:ean,
	                        base_code: ean,
	                        value: 0,
	                    };
	        	}
	        	if (ean.length === 15 ){
	        		parse_result = {
	                        encoding: 'code128',
	                        type:'coupon1',  
	                        code:ean,
	                        base_code: ean,
	                        value: 0,
	                    };
	        	}
	        	return parse_result;
	        }
			return parse_result;
	};
}

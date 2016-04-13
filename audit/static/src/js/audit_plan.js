openerp.sys_audit = function(instance){
	var _t = instance.web._t,
        _lt = instance.web._lt;
    var QWeb = instance.web.qweb;
    instance.sys_audit = {};
	
	
	
	/* 	
	function loadOvaplanStandard(type){
		var obj = new openerp.Model('audit.ovaplan.info');
		obj.call('get_ovaplan_standard',[],{type:type}).then(function (result){
			if(result != undefined){
				
			}
		});
	} */
    
    /**
    instance.sys_audit.Standard = instance.web.Widget.extend({
    	template:"Standard",
    	start:function(){
    		this.$el.append("<div>start checkbox tree</div>");
    	},
    	events: {
            'click .std_btn_add':'addSelectedStandard',
            'click .std_btn_del':'removeSelectedStandard',
        },
        addSelectedStandard:function(){
        	alert('click add');
        },
        removeSelectedStandard:function(){
        	alert('click remove');
        },
    });
    instance.web.client_actions.add('audit.plan.standard', 'instance.sys_audit.Standard');
    **/
    
    /**
    instance.sys_audit.StandardWidget = instance.web.form.AbstractField.extend({
    	template = "Standard",
    	init:function(){
    		alert("init");
    	},
    	start:function(){
    	    alert("start");
    	},
    	display_field: function(){
    		alert("display_field");
    	},
    	render_value: function() {
    		alert("render_value");
    	},{}
    });
    
    instance.web.form.widgets.add('standardWidget', 'instance.sys_audit.StandardWidget');
    */
}
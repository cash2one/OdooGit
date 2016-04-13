/**
 * ShowOrHideButton:
 *
 * @param {String} model
 * @param {Object} record
 * 
 */
function ShowOrHideButton(model,record,_t){
	var current_uid = openerp.session.uid;
	
	if(model == 'pm.impl.month.plan'){
		if(record.state == 'suo_confirmed' || (record.state && !record.can_manager_submit && !record.can_suo_approve && !record.can_xm_submit && !record.can_suo_confirm)){
			$(".oe_form_button_edit").hide();
		}else{
			$(".oe_form_button_edit").show();
		}
	}else if(model == 'pm.impl.quarter.plan'){
		if(record.proj_manager && record.proj_manager.length > 0){
			if(current_uid != 1 && current_uid != record.proj_manager[0]){
				$(".oe_form_button_edit").hide();
			}else{
				$(".oe_form_button_edit").show();
			}
		}
	}else if(model == 'pm.impl.organ.month.plan'){
		if(record.state == 'ke_confirmed' || (record.state && !record.can_suo_submit && !record.can_ke_approve && !record.can_dw_submit && !record.can_ke_confirm)){
			$(".oe_form_button_edit").hide();
		}else{
			$(".oe_form_button_edit").show();
		}
	}else if(model == 'pm.impl.task.project'){
		if(record.manager_id && record.manager_id.length > 0){
			if(current_uid != 1 && current_uid != record.manager_id[0]){
				$(".oe_form_button_edit").hide();
			}else{
				$(".oe_form_button_edit").show();
			}
		}
	}else if(model == 'pm.impl.task'){
		if(current_uid != 1 && current_uid != record.manager_id){
			$(".oe_form_button_edit").hide();
		}else{
			$(".oe_form_button_edit").show();
		}
	}else if(model == 'pm.impl.check.result'){
		if(record.create_uid && record.create_uid.length > 0){
			if(current_uid != 1 && current_uid != record.create_uid[0]){
				$(".oe_form_button_edit").hide();
			}else{
				$(".oe_form_button_edit").show();
			}
		}
	}else if(model == 'pm.impl.procedural.document'){
		if(current_uid != 1 && current_uid != record.manager_id){
			$(".oe_form_button_edit").hide();
		}else{
			$(".oe_form_button_edit").show();
		}
	}else if(model == 'pm.impl.file.upload'){
		if(record.state == 'ke_confirmed' || (record.state && !record.can_manager_submit && !record.can_suo_approve && !record.can_ke_confirm)){
			$(".oe_form_button_edit").hide();
		}else{
			$(".oe_form_button_edit").show();
		}
	}else if(model == 'pm.impl.update'){
		if(record.state == 'jia_confirmed' || (record.state && !record.can_manager_submit && !record.can_suo_approve && !record.can_ke_approve && !record.can_jia_approve)){
			$(".oe_form_button_edit").hide();
		}else{
			$(".oe_form_button_edit").show();
		}
	}else if(model == 'pm.impl.staff.baseline'){
		$(".oe_form_button_edit").hide();
	}else if(model == 'pm.impl.plan.baseline'){
		$(".oe_form_button_edit").hide();
	}
	
	if(model == 'pm.purchase.plan'){
		if((record.state == 'suo_stop_accepted' || record.state == 'fzs_stop_accepted' || record.state == 'yzbgh_stop_accepted' || record.state == 'yz_stop_accepted' || record.state == 'yzzgcg_stop_accepted' || record.state == 'jt_accepted') || (record.state && !record.can_manager_submit && !record.can_suo_approve && !record.can_ke_approve && !record.can_cai_approve && !record.can_yb_approve && !record.can_fzs_approve && !record.can_yzzgcg_approve && !record.can_yz_approve && !record.can_yzbgh_approve && !record.can_jt_approve)){
			$(".oe_form_button_edit").hide();
		}else{
			$(".oe_form_button_edit").show();
		}
	}else if(model == 'pm.purchase.result'){
		if((record.state == 'yzzgcg_stop_accepted' || record.state == 'jt_accepted') || (record.state && !record.can_manager_submit && !record.can_suo_approve && !record.can_yb_approve && !record.can_yzzgcg_approve && !record.can_jt_approve)){
			$(".oe_form_button_edit").hide();
		}else{
			$(".oe_form_button_edit").show();
		}
	}else if(model == 'pm.purchase.trace'){
		record.display_name = '采购合同执行信息';
		if(current_uid != 1 && current_uid != record.manager_id){
			$(".oe_form_button_edit").hide();
		}else{
			$(".oe_form_button_edit").show();
		}
	}
	
	//liuhongtai  techservice
	if(model == "pm.techservice.check"){
		//包括管理员，都能看到编辑按钮
		if(current_uid != 1){
			if(current_uid != record.create_uid[0]){
				$(".oe_form_button_edit").hide();
			}
			else{
				$(".oe_form_button_edit").show();
			}
		}
	}
	
	if(model == "pm.techservice.plan"){
		if(record.hasOwnProperty("state") && record.state.indexOf("returned")<0 && (record.state == 'dean_approved' || (record.state && !record.unit_can_approve && !record.rd_can_approve && !record.dean_can_approve))){
			$(".oe_form_button_edit").hide();
		}
		else{
			$(".oe_form_button_edit").show();
		}
	}
	
	if(model == "pm.techservice.init"){
		if(current_uid != 1){
			$(".oe_form_button_edit").hide();
		}
	}
	
	if(model == "pm.techservice.acceptance"){
		if(current_uid != 1){
			if(record.hasOwnProperty("state") && record.state.indexOf("returned")<0 && ((record.contract_account>20 && record.state == 'rd_approved') || (record.state && !record.rd_can_approve))){
				$(".oe_form_button_edit").hide();
			}
			else{
				$(".oe_form_button_edit").show();
			}
		}
	}
	
	//liuhongtai funds
	if(model == "pm.fund.proj.monthplan"){
		if(current_uid!=1 && record.hasOwnProperty("state") && record.state.indexOf("returned")<0 && (record.state == 'fd_approved' || (record.state && !record.unit_can_approve && !record.rd_can_approve && !record.fd_can_approve))){
			$(".oe_form_button_edit").hide();
		}
		else{
			$(".oe_form_button_edit").show();
		}
	}
	
	if(model == "pm.fund.use.apply"){
		if(current_uid!=1 && record.hasOwnProperty("state") && record.state.indexOf("returned")<0 && (record.state == 'validated' || (record.state && !record.pm_can_approve && !record.unit_can_approve))){
			$(".oe_form_button_edit").hide();
		}
		else{
			$(".oe_form_button_edit").show();
		}
	}
	
	if(model == "pm.fund.bc.apply"){
		if(current_uid!=1 && record.hasOwnProperty("state") && record.state.indexOf("returned")<0 && (record.state == 'rd_approved' || (record.state && !record.unit_can_approve && !record.rd_can_approve))){
			$(".oe_form_button_edit").hide();
		}
		else{
			$(".oe_form_button_edit").show();
		}
	}
}




/*
 * jiangpeng 
 * 
 * 控制"删除"按钮
 */
var custom_delete_button_data = {has_default_delete_button:false,model:''};
function control_form_delete_button(model,record,_t,data){
	var current_uid = openerp.session.uid;
	var condition = false;  //condition为true则去掉"删除"按钮
	
	if(model == 'pm.impl.month.plan'){
		condition = (current_uid != 1 && record.state && (record.state != 'draft' || !record.can_manager_submit));
	}else if(model == 'pm.impl.quarter.plan'){
		condition = (current_uid != 1 && record.proj_manager && record.proj_manager.length > 0 && current_uid != record.proj_manager[0]);
	}else if(model == 'pm.impl.organ.month.plan'){
		condition = (current_uid != 1 && record.state && (record.state != 'draft' || !record.can_suo_submit));
	}else if(model == 'pm.impl.task.project'){
		condition = (current_uid != 1 && record.manager_id && record.manager_id.length > 0 && current_uid != record.manager_id[0]);
	}else if(model == 'pm.impl.task'){
		condition = (current_uid != 1 && current_uid != record.manager_id);
	}else if(model == 'pm.impl.check.result'){
		condition = (current_uid != 1 && record.create_uid && record.create_uid.length > 0 && current_uid != record.create_uid[0]);
	}else if(model == 'pm.impl.procedural.document'){
		condition = (current_uid != 1 && current_uid != record.manager_id);
	}else if(model == 'pm.impl.file.upload'){
		condition = (current_uid != 1 && record.state && (record.state != 'draft' || !record.can_manager_submit));
	}else if(model == 'pm.impl.update'){
		condition = (current_uid != 1 && record.state && (record.state != 'draft' || !record.can_manager_submit));
	}else if(model == 'pm.impl.staff.baseline'){
		condition = (current_uid != 1);
	}else if(model == 'pm.impl.plan.baseline'){
		condition = (current_uid != 1);
	}
	
	if(model == 'pm.purchase.plan'){
		condition = (current_uid != 1 && record.state && (record.state != 'draft' || !record.can_manager_submit));
	}else if(model == 'pm.purchase.result'){
		condition = (current_uid != 1 && record.state && (record.state != 'draft' || !record.can_manager_submit));
	}else if(model == 'pm.purchase.trace'){
		condition = (current_uid != 1 && current_uid != record.manager_id);
	}

	common_control_form_delete_button(model,record,_t,data,condition);
}

//公用方法
function common_control_form_delete_button(model,record,_t,data,condition){
	if(custom_delete_button_data.has_default_delete_button && custom_delete_button_data.model == model){
		data.sidebar.items.other.splice(custom_delete_button_data.index,0,custom_delete_button_data.data)
	}
	if(condition){
		var other_items = data.sidebar.items.other;
		for(var i = 0;i < other_items.length;i++){
			if(other_items[i]['label'] == _t("Delete")){
				custom_delete_button_data.has_default_delete_button = true;
				custom_delete_button_data.model = model;
				custom_delete_button_data.index = i;
				custom_delete_button_data.data = other_items[i];
				data.sidebar.items.other.splice(i,1);
				return;
			}
		}
	}
	custom_delete_button_data.has_default_delete_button = false;
	custom_delete_button_data.model = '';
}
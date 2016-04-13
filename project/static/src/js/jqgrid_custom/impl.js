//生成单位月度计划
function impl_create_organ_month_plan(){
	var param_organ_id = $("#param_organ_id").find("input").val();
	var param_year = $("#param_year").find("input").val();
	var param_month = $("#param_month").find("input").val();
	if(!param_organ_id){
		alert("请选择承担单位！");
		return false;
	}
	if(!param_year){
		alert("请选择年份！");
		return false;
	}
	if(!param_month){
		alert("请选择月份！");
		return false;
	}
	var obj = new openerp.web.Model("pm.impl.plan.execution.statistics");
	obj.call("check_before_create_organ_month_plan",[],{'param_organ_id':param_organ_id,'param_year':param_year,'param_month':param_month,context: new openerp.web.CompoundContext()}).then(function(result){
        var total = result['total']
        var has_task_project_amount = result['has_task_project_amount']
        var not_has_task_project_amount = result['not_has_task_project_amount']
        if(has_task_project_amount == 0){
        	alert('该单位共有' + total + '个项目在实施中,其中' + has_task_project_amount + '个项目有工作任务,' + not_has_task_project_amount + '个项目没有工作任务.\n不能生成单位月度计划：');
        	return false;
        }
		flag = confirm('该单位共有' + total + '个项目在实施中,其中' + has_task_project_amount + '个项目有工作任务,' + not_has_task_project_amount + '个项目没有工作任务.\n是否生成单位月度计划：');
		if(flag){
			obj.call("create_organ_month_plan2",[],{'param_organ_id':param_organ_id,'param_year':param_year,'param_month':param_month,context: new openerp.web.CompoundContext()}).then(function(result){
				alert(result);
			});
		}
	});
}

//生成项目月度计划
function impl_create_month_plan(){
	var param_project_id = $("#param_project_id").find("input").val();
	var param_year = $("#param_year").find("input").val();
	var param_month = $("#param_month").find("input").val();
	if(!param_project_id){
		alert("请选择项目！");
		return false;
	}
	if(!param_year){
		alert("请选择年份！");
		return false;
	}
	if(!param_month){
		alert("请选择月份！");
		return false;
	}
	var obj = new openerp.web.Model("pm.impl.plan.execution.statistics");
	obj.call("create_month_plan2",[],{'param_project_id':param_project_id,'param_year':param_year,'param_month':param_month,context: new openerp.web.CompoundContext()}).then(function(result){
		alert(result);
	});
}

//项目任务进展分析
function task_analysis(){
	alert("task_analysis...");
}

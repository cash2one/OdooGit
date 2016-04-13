function createNode(){
  var root = {
    "id" : "0",
    "text" : "root",
    "value" : "86",
    "showcheck" : true,
    complete : true,
    "isexpand" : true,
    "checkstate" : 0,
    "hasChildren" : true
  };
  var arr = [];
  for(var i= 1;i<10; i++){
    var subarr = [];
    for(var j=1;j<10;j++){
      var value = "node-" + i + "-" + j; 
      subarr.push( {
         "id" : value,
         "text" : value,
         "value" : value,
         "showcheck" : true,
         complete : true,
         "isexpand" : false,
         "checkstate" : 0,
         "hasChildren" : false
      });
    }
    arr.push( {
      "id" : "node-" + i,
      "text" : "node-" + i,
      "value" : "node-" + i,
      "showcheck" : true,
      complete : true,
      "isexpand" : false,
      "checkstate" : 0,
      "hasChildren" : true,
      "ChildNodes" : subarr
    });
  }
  root["ChildNodes"] = arr;
  return root; 
}

function loadTreeDataOfOvaForm(type, id){
	if (id == null && id == undefined){
		var obj = new openerp.Model('audit.standard');
		if (type == 'lhsh'){
			type = 114;
		}
		if (type == 'txsh'){
			type = 115;
		}
		if (type == 'zxsh'){
			type = 116;
		}
		obj.call('get_all_standards',[],{type:type}).then(function (result){
			if(result != undefined){
				var l_std_list = result.l_std;
				var l = {showcheck:true};
				l.data = list2tree(l_std_list);
				if ( type == 114 && l_std_list.length > 0){
					$('#ltree_1').treeview(l);
				}
				else if(type == 115 && l_std_list.length > 0){
					$('#ltree_2').treeview(l);
				}
				else if(type == 116 && l_std_list.length > 0){
					$('#ltree_3').treeview(l);
				}
			}
		});
	}
	else{
		var obj = new openerp.Model('audit.ovaplan.standard');
		if (type == 'lhsh'){
			type = 114;
		}
		if (type == 'txsh'){
			type = 115;
		}
		if (type == 'zxsh'){
			type = 116;
		}
		obj.call('get_all_and_ova_standard',[],{type:type, ova_id: id}).then(function (result){
			if(result != undefined){		
				initCheckState(result);
				var r_std_list = result.r_std;
				var l_std_list = result.l_std;
				var l = {showcheck : true};
				l.data = list2tree(l_std_list);			
				var r = {showcheck : true, ltreeUpdate : false};
				r.data = list2tree(r_std_list);
				if(type == 114 && l_std_list.length > 0){
					$('#ltree_1').treeview(l);
					$('#rtree_1').treeview(r);
				}
				else if(type == 115 && l_std_list.length > 0){
					$('#ltree_2').treeview(l);
					$('#rtree_2').treeview(r);
				}
				else if(type == 116 && l_std_list.length > 0){
					$('#ltree_3').treeview(l);
					$('#rtree_3').treeview(r);
				}
			}
		});
	}
}

//added by hl. 03/26. when load an exsit plan
function loadTreeDataOfPlanForm(id){
	if(id != null || id != undefined){
		var obj = new openerp.Model('audit.plan.standard');
		obj.call('get_exsit_plan_form_standard_tree',[],{plan_id: id}).then(function (result){
			if(result != undefined){		
				initCheckState(result);
				var plan_std_list = result.r_std;
				var l_std_list = result.l_std;
				var l = {showcheck : true};
				l.data = list2tree(l_std_list);
				$('#lplantree').treeview(l);
				
				var r = {showcheck : true, ltreeUpdate : false};
				r.data = list2tree(plan_std_list);
				$('#rplantree').treeview(r);
			}
		});
	}
}

function setButtonStatus(isViewMode){
	var buttons = document.getElementsByClassName('std_btn')
	if (buttons != null && buttons != undefined){
		for(var i=0; i<buttons.length; i++){
			buttons[i].disabled= isViewMode;
		}
	}
}

//added by hl 03/28. when create a new plan...
function loadInitTreeDataOfPlanForm(type, ovaplan_id){
	var obj = new openerp.Model('audit.plan.standard');
	obj.call('get_init_plan_form_standard_tree',[],{ovaplan_id: ovaplan_id, type: type}).then(function (result){
		if(result != undefined){		
			initCheckState(result);
			var plan_std_list = result.r_std;
			var l_std_list = result.l_std;
			var l = {showcheck : true};
			l.data = list2tree(l_std_list);
			$('#lplantree').treeview(l);
			
			var r = {showcheck : true, ltreeUpdate : false};
			r.data = list2tree(plan_std_list);
			$('#rplantree').treeview(r);
		}
	});
}

function initCheckState(ret){
	var r_std_list = ret.r_std;
	var l_std_list = ret.l_std;
	if (r_std_list == null || r_std_list == undefined || l_std_list == null || l_std_list == undefined){
		return
	}
	for(var i=0; i < l_std_list.length; i++){
		var std = l_std_list[i];
		for(var j=0; j<r_std_list.length; j++){
			if(std.id == r_std_list[j].id){
				std.checkstate = 1;
			}
		}
	}
	for(var i=0; i<r_std_list.length; i++){
		var r_std = r_std_list[i];
		r_std.checkstate = 0;
	}
}

function list2tree(arr){
	var tree = [];
	var root = {};
	for(var i=0; i<arr.length; i++){
		var item = arr[i];
		var children = [];
		for(var j=0; j<arr.length; j++){
			var oitem = arr[j];
			if(item.id == oitem.id){
				continue;
			}
			if(oitem.parentid == item.id){
				item.hasChildren = true;
				children.push(oitem);
			}
		}
		if(children.length > 0){
			children.sort(sortBySeq);
			item.ChildNodes = children;
		}
		if(item.parentid == null || item.parentid == undefined){
			root = item;
			tree.push(root);
		}
	}
	tree.sort(sortBySeq);
	return tree;
}

function sortBySeq(item1, item2){
	return item1.seq - item2.seq;
}


//Save tree data

function update_ova_std(model_id){
	
	var ova_stds = [];
	var s1 = $('#ltree_1').getTSNs(true);
	if(s1 != null && s1.length > 0){
		for(var i=0; i<s1.length; i++){
			ova_stds.push(s1[i].id)
		}
	}
	var s2 = $('#ltree_2').getTSNs(true);
	if(s2 != null && s2.length > 0){
		for(var i=0; i<s2.length; i++){
			ova_stds.push(s2[i].id)
		}
	}
	var s3 = $('#ltree_3').getTSNs(true);
	if(s3 != null && s3.length > 0){
		for(var i=0; i<s3.length; i++){
			ova_stds.push(s3[i].id)
		}
	}
	var obj = new openerp.web.Model('audit.ovaplan.standard');
	obj.call("updateOvaStd",[],{stds:ova_stds, ova_id : model_id}).then(function(result){
        alert("审核要素保存成功！");
    });
}

function update_plan_std(model_id){
	var s = $('#lplantree').getTSNs(true);
	if(s != null){
		var plan_stds = [];
		for(var i=0; i<s.length; i++){
			plan_stds.push(s[i].id);
		}
		var obj = new openerp.web.Model('audit.plan.standard');
		obj.call("updatePlanStd",[],{stds:plan_stds, plan_id : model_id}).then(function(result){
			alert("Succeed!");
		});
	}
}

treedata = [createNode()];

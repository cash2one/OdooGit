function btn_add_lh(){
	var s=$("#ltree_1").getTSNs(true);
    if(s !=null){
		//view update
		var o = { showcheck: true, ltreeUpdate: false };
		var data = [];
		cloneAndfilterData(data, noRepeatData(s));
		o.data = data;
		$("#rtree_1").treeview(o);
	}	
    else
        alert("NULL");
}

function btn_add_tx(){
	var s=$("#ltree_2").getTSNs(true);
    if(s !=null){
		//view update
		var o = { showcheck: true, ltreeUpdate: false };
		var data = [];
		cloneAndfilterData(data, noRepeatData(s));
		o.data = data;
		$("#rtree_2").treeview(o);
	}	
    else
        alert("NULL");
}

function btn_add_zx(){
	var s=$("#ltree_3").getTSNs(true);
    if(s !=null){
		//view update
		var o = { showcheck: true, ltreeUpdate: false };
		var data = [];
		cloneAndfilterData(data, noRepeatData(s));
		o.data = data;
		$("#rtree_3").treeview(o);
	}	
    else
        alert("NULL");
}

function btn_add_plan(){
	var s=$("#lplantree").getTSNs(true);
    if(s !=null){
		//view update
		var o = { showcheck: true, ltreeUpdate: false };
		var data = [];
		cloneAndfilterData(data, noRepeatData(s));
		o.data = data;
		$("#rplantree").treeview(o);
	}	
    else
        alert("NULL");
}


function onlyShowChecked(data){
	if(data != null){
		for(var item in data){
			if(item.checkstate == 0 || item.checkstate == undefined){
				item.invisible = true;
			}
			if(item.hasChildren){
				onlyShowChecked(data.ChildNodes);
			}
		}
	}
}

function btn_del_lh(){
	var s=$("#rtree_1").getTSNs(false);
    if(s !=null){	
		var data = $("#rtree_1").getTreeData();
		delCheckedItem(data);
		//proFolderNode(data);
		var o = { showcheck: true, ltreeUpdate: false };
		var d = [];
		cloneAndfilterData(d, noRepeatData(data));
		o.data = d;
		$("#rtree_1").treeview(o);
		
		var ldata = $('#ltree_1').getTreeData();
		var list =[];
		tree2list(list, d)
		filterLeftTree(ldata, list2map(list));
		var l = {showcheck:true};
		l.data = ldata;
		$('#ltree_1').treeview(l);
	}
	
    else
        alert("NULL");
}

function tree2list(list, tree){
	for(var i=0; i<tree.length; i++){
		var node = tree[i];
		list.push(node);
		if(node.hasChildren == true){
			tree2list(list, node.ChildNodes);
		}
	}
}
function list2map(list){
	var map ={};
	for(var i=0; i<list.length; i++){
		var node = list[i];
		map[node.id] = node;
	}
	return map;
}
function filterLeftTree(ldata, rmap){
	for(var i=0; i<ldata.length; i++){
		var node = ldata[i];
		if(rmap.hasOwnProperty(node.id)){
			node.checkstate = 1;
		}
		else{
			node.checkstate = 0;
		}
		if(node.hasChildren){
			filterLeftTree(node.ChildNodes, rmap);
		}
	}
}

function btn_del_tx(){
	var s=$("#rtree_2").getTSNs(false);
    if(s !=null){
		//alert(s.join(","));	
		var data = $("#rtree_2").getTreeData();
		delCheckedItem(data);
		//proFolderNode(data);
		var o = { showcheck: true, ltreeUpdate: false };
		var d = [];
		cloneAndfilterData(d, noRepeatData(data));
		o.data = d;
		$("#rtree_2").treeview(o);
		
		var ldata = $('#ltree_2').getTreeData();
		var list =[];
		tree2list(list, d)
		filterLeftTree(ldata, list2map(list));
		var l = {showcheck:true};
		l.data = ldata;
		$('#ltree_2').treeview(l);
	}
	
    else
        alert("NULL");
}

function btn_del_zx(){
	var s=$("#rtree_3").getTSNs(false);
    if(s !=null){
		//alert(s.join(","));	
		var data = $("#rtree_3").getTreeData();
		delCheckedItem(data);
		//proFolderNode(data);
		var o = { showcheck: true, ltreeUpdate: false };
		var d = [];
		cloneAndfilterData(d, noRepeatData(data));
		o.data = d;
		$("#rtree_3").treeview(o);
		
		var ldata = $('#ltree_3').getTreeData();
		var list =[];
		tree2list(list, d)
		filterLeftTree(ldata, list2map(list));
		var l = {showcheck:true};
		l.data = ldata;
		$('#ltree_3').treeview(l);
	}
	
    else
        alert("NULL");
}

function btn_del_plan(){
	var s=$("#rplantree").getTSNs(false);
    if(s !=null){
		//alert(s.join(","));	
		var data = $("#rplantree").getTreeData();
		delCheckedItem(data);
		//proFolderNode(data);
		var o = { showcheck: true, ltreeUpdate: false };
		var d = [];
		cloneAndfilterData(d, noRepeatData(data));
		o.data = d;
		$("#rplantree").treeview(o);
		
		var ldata = $('#lplantree').getTreeData();
		var list =[];
		tree2list(list, d)
		filterLeftTree(ldata, list2map(list));
		var l = {showcheck:true};
		l.data = ldata;
		$('#lplantree').treeview(l);
	}
	
    else
        alert("NULL");
}


function delCheckedItem(data){
	for(var i=0; i<data.length; i++){
		if(data[i].checkstate == 1){
			data[i].checkstate = 0;
		}
		else if(data[i].checkstate == 0 || data[i].checkstate == undefined){
			data[i].checkstate = 1;
		}
		if(data[i].hasChildren){
			var children = data[i].ChildNodes;
			delCheckedItem(children);
		}
	}
}

function proFolderNode(data){
	for(var i=0; i<data.length; i++){
		if(data[i].hasChildren){
			var toKeep = false;
			var children = data[i].ChildNodes;
			for(var j=0; j<children.length; j++){
				if(children[j].checkstate == 1){
					toKeep = true;
					break;
				}
			}
			if(!toKeep){
				data[i].checkstate = 0;
			}
			proFolderNode(children);
		}
	}
}

function getType(o)
{
    var _t;
    return ((_t = typeof(o)) == "object" ? o==null && "null" || Object.prototype.toString.call(o).slice(8,-1):_t).toLowerCase();
}
function extend(destination,source)
{
    for(var p in source)
    {
        if(getType(source[p])=="array"||getType(source[p])=="object")
        {
            destination[p]=getType(source[p])=="array"?[]:{};
            arguments.callee(destination[p],source[p]);
        }
        else
        {
			destination[p]=source[p];
        }
    }
}

function noRepeatData(d){
	var ret = [];
	for(var i=0; i<d.length; i++){
		var isRepeat = false;
		for(var j=0; j<i; j++){
			if(d[i].parentid == null || d[i].parentid == undefined){
				continue;
			}
			if(d[i].parentid == d[j].id){
				isRepeat = true;
			}
		}
		if(isRepeat){
			continue;
		}
		ret.splice(0,0,d[i]);
	}
	return ret;
}

function cloneData(d,o){
	for(var i=0; i<o.length; i++){
		var tmp = {};
		tmp.id = o[i]["id"];
		tmp.text = o[i]["text"];
		tmp.value = o[i]["value"];
		tmp.showcheck = o[i]["showcheck"];
		tmp.complete = o[i]["complete"];
		tmp.isexpand = o[i].isexpand;
		tmp.checkstate = o[i]["checkstate"];
		tmp.hasChildren = o[i]["hasChildren"];
		if(o[i].parent != null && o[i].parent != undefined){
			tmp.parent = o[i].parent;
		}
		d[i] = tmp;
		if(o[i].hasChildren == true){
			var arr = [];
			d[i]["ChildNodes"] = arr;
			cloneData(d[i]["ChildNodes"], o[i]["ChildNodes"]);
		}
	}
}

function cloneAndfilterData(d,o){
	for(var i=0; i<o.length; i++){
		var tmp = {};
		if(o[i].checkstate == 0){
			continue;
		}
		tmp.id = o[i]["id"];
		tmp.text = o[i]["text"];
		tmp.value = o[i]["value"];
		tmp.showcheck = o[i]["showcheck"];
		tmp.complete = o[i]["complete"];
		tmp.isexpand = o[i].isexpand;
		tmp.checkstate = o[i].checkstate;
		// if(tortree){
			// tmp.checkstate = 0;
		// }else{
			// tmp.checkstate = 1;
		// }
		tmp.hasChildren = o[i]["hasChildren"];
		if(o[i].parentid != null && o[i].parentid != undefined){
			tmp.parentid = o[i].parentid;
		}
		d.push(tmp);
		if(o[i].hasChildren == true){
			var arr = [];
			var index_d = d.length - 1;
			d[index_d]["ChildNodes"] = arr;
			cloneAndfilterData(d[index_d]["ChildNodes"], o[i]["ChildNodes"]);
		}
	}
}
/**
 * crate jqGrid:
 *
 * @param {String} model
 * @param {Object} record
 * 
 */
function createJqGrid(model,record,upContext){
	var theGrid = $("#jqGrid");
	var numberTemplate = {formatter: 'number', align: 'right', sorttype: 'number'};
	var colNames = ['detail_id', 'subject_id', 'sn', '', '', '', ''];
	var colModel = [          
                {name: 'detail_id', index: 'subject_id', width: 20, align:'center',hidden:true, sortable:false, editable:false},
                {name: 'subject_id', index: 'subject_id', width: 20, align:'center',hidden:true, sortable:false, editable:false},
				{name: 'sn', index: 'sn', width: 20, align:'center',hidden:true, sortable:false, editable:false},
				{name: 'first', index: 'first', width: 35, align:'center',sortable:false, editable:false, 
				 cellattr: function(rowId, tv, rawObject, cm, rdata) {
                        //合并单元格
                        return 'id=\'first' + rowId + "\'";
                    }
				},
				{name: 'second', index: 'second', width: 40, align:'center',sortable:false, editable:false,
				 cellattr: function(rowId, tv, rawObject, cm, rdata) {
                        //合并单元格
                        return 'id=\'second' + rowId + "\'";
                    }
				},
				{name: 'third', index: 'third', width: 35, align:'center',sortable:false, editable:false,
					 cellattr: function(rowId, tv, rawObject, cm, rdata) {
	                        //合并单元格
	                        return 'id=\'third' + rowId + "\'";
	                    }
				},
				{name: 'subject_name', index: 'subject_name', width: 70, align: 'center', sortable:false, editable:false}
    ];
	/*经费月度计划跟踪页面*/
	if(model=="pm.fund.proj.monthplan"){
		var current_uid = openerp.session.uid;
		var monthplan_id;
		var editable_plan=editable_actual=false;
		if(record.hasOwnProperty("id")){//非新建
			monthplan_id = record.id;
			if((current_uid==1 || current_uid==record.proj_pm_uid) && (record.state == "unit_returned" || record.state == "rd_returned" || record.state == "fd_returned")){
				editable_plan = true;
			}
			if(record.state == "rd_approved" && record.fd_can_approve==true){
				editable_actual = true;
			}
		}
		else{
			monthplan_id = "New";
			editable_plan = true;
		}
		colNames.push("计划");
		colNames.push("实际使用");
		colNames.push("年度累计支出");
		colNames.push("当前余额");
		colNames.push("科目总额");
		colNames.push("已使用总额");
	    colModel.push({name: 'plan_value', index: 'plan_value', width: 50, align:'center', template: numberTemplate, sortable:false, editable:editable_plan}); 
	    colModel.push({name: 'actual_value', index: 'actual_value', width: 50, align:'center', template: numberTemplate, sortable:false, editable:editable_actual});
	    colModel.push({name: 'cost_total', index: 'cost_total', width: 50, align:'center', template: numberTemplate, sortable:false, editable:false});			
	    colModel.push({name: 'left_value', index: 'left_value', width: 50, align:'center', template: numberTemplate, sortable:false, editable:false});
	    colModel.push({name: 'curyear_total', index: 'curyear_total', width: 50, align:'center',hidden:true, template: numberTemplate, sortable:false, editable:false});
	    colModel.push({name: 'curyear_cost', index: 'curyear_cost', width: 50, align:'center',hidden:true, template: numberTemplate, sortable:false, editable:false});
	    if(theGrid.length > 0){
	    	var lastsel;
	    	var obj=new openerp.web.Model("pm.fund.proj.monthplan");
	    	obj.call("getJqGridData",[],{monthplan_id:monthplan_id}).then(function(result) {
			    theGrid.jqGrid({
			        datatype: 'local',
			        data: result["data"],
			        colNames: colNames,
			        colModel: colModel,
			        hidegrid: false,
			        autowidth: true,
					gridview: true,             
					rownumbers: false,
			        rowNum: 50,
			        viewrecords: true,  
			        //caption: '科目明细（单位：万元）',
			        height: '100%',
					onSelectRow : function(id) {
			    			  var rowData =  theGrid.getRowData(id);
					    	  if(upContext.$el.hasClass('oe_form_readonly')||rowData.first=="资本化合计"||rowData.first=="费用化合计"||rowData.first=="合计"){
					    		return;
					    	  }
			    			  //upContext.on_button_edit();
					          if (id && id !== lastsel) {
					        	  //theGrid.jqGrid('saveRow', lastsel, false, 'clientArray');
					        	  theGrid.jqGrid('saveRow',lastsel, 
					        			  { 
					        			      keys : true,
					        			      url: 'clientArray',
					        			      aftersavefunc: function(response) {
								        		 var count = theGrid.getGridParam("reccount");
								        		 getSum(theGrid,count,11);
								        		 if(record.hasOwnProperty("id") && record.state=="rd_approved"){
								        			 //自动计算年度累计支出和当前余额
								        			 var rowData =  theGrid.getRowData(lastsel);
								        			 curyear_cost = parseFloat(rowData.actual_value) + parseFloat(rowData.curyear_cost);
								        			 theGrid.jqGrid('setCell',lastsel,9,curyear_cost);
								        			 curyear_left = parseFloat(rowData.curyear_total) - parseFloat(rowData.actual_value) - parseFloat(rowData.curyear_cost);
								        			 theGrid.jqGrid('setCell',lastsel,10,curyear_left);
									        		 //alert(rowData.curyear_total);
								        		 }
					        			      }
					        			  });
					        	  theGrid.jqGrid('editRow', id, true); 
					              lastsel = id;
					       }
					 },
				    editurl: 'clientArray',
					gridComplete: function () { 
						 MergeJqGrid("jqGrid");
					}
			    });
			    JqReloadAndGroup(theGrid,result);
			});
	   }	
	}
	
	/*预算变更基线页面*/
	if(model=="pm.fund.budget.version" || model=="pm.fund.account"){
		//根据条件构造colNames和colModel
		if(record.hasOwnProperty("id")){//非新建
			record.version_id = record.id;
			if(record.proj_id&&record.proj_id[0]){
				record.proj_id = record.proj_id[0];
			}
			//record.flag = "NoOnChange";
		}
		else{
			record.version_id = "New";
			if(!record.hasOwnProperty("proj_id")){
				record.proj_id = 0;
			}
		}
	    if(theGrid.length > 0){
	    	var lastsel;
	    	current_year = (new Date()).getFullYear();
	    	var obj=new openerp.web.Model("pm.fund.budget.version");
	    	obj.call("getJqGridData",[],{rec_info:record, context: new openerp.web.CompoundContext()}).then(function(result) {
	    		if(result['start_year']!=0){
				    for(var year=result['start_year']; year<=result['end_year'];year++){
				    	colNames.push(year+"年");
				    	if(model=="pm.fund.account"||year<current_year){
				    		colModel.push({name: year, index: year, width: 40, align: 'center', template: numberTemplate, sortable:false, editable:false});
				    	}
				    	else{
				    		colModel.push({name: year, index: year, width: 40, align: 'center', template: numberTemplate, sortable:false, editable:true});
				    	}
				    }
				    colNames.push("合计");
				    if(model=="pm.fund.account"){
				    	colModel.push({name: 'total', index: 'total', width: 40, align: 'center', template: numberTemplate, sortable:false, editable:false});
				    }
				    else{
				    	colModel.push({name: 'total', index: 'total', width: 40, align: 'center', template: numberTemplate, sortable:false, editable:true});
				    }
				    theGrid.jqGrid({
				        datatype: 'local',
				        data: result["data"],
				        colNames: colNames,
				        colModel: colModel,
				        hidegrid: false,
				        autowidth: true,
						gridview: true,             
						rownumbers: false,
				        rowNum: 50,
				        viewrecords: true, 
				        //caption: '科目明细（单位：万元）',
				        height: '100%',
						onSelectRow : function(id) {
						    	  var rowData =  theGrid.getRowData(id);
						    	  if(upContext.$el.hasClass('oe_form_readonly')||rowData.first=="资本化合计"||rowData.first=="费用化合计"||rowData.first=="合计"){
						    		return;
						    	  }
				    			  //upContext.on_button_edit();
						          if (id && id !== lastsel) {
						        	  //theGrid.jqGrid('saveRow', lastsel, false, 'clientArray');
						        	  theGrid.jqGrid('saveRow',lastsel, 
						        			  { 
						        			      keys : true,
						        			      url: 'clientArray',
						        			      aftersavefunc: function(response) {
						        		  			 var count = theGrid.getGridParam("reccount");
						        		  		  	 getSum(theGrid,count,result['end_year']-result['start_year']+8);
						        		  		  	 var cellSum = 0;
						        		  		  	 //循环每一行统计最后一列合计值
						        		  			 for(var r=1;r<=count;r++){
						        		  				for(var col=7;col<result['end_year']-result['start_year']+8;col++){
						        		  					cellSum+= parseFloat(theGrid.jqGrid('getCell',r,col)); 
						        		  				}
						        		  				theGrid.jqGrid('setCell',r,col,cellSum);
						        		  				cellSum = 0;
						        		  			 }
						        			      }
						        			  });
						        	  theGrid.jqGrid('editRow', id, true); 
						              lastsel = id;
						       }
						 },
					    editurl: 'clientArray',
					    gridComplete: function () { 
							 MergeJqGrid("jqGrid");
							 var count = theGrid.getGridParam("reccount");
        		  			 var cellSum = 0;
        		  			//循环每一行统计最后一列合计值
        		  			 for(var r=1;r<=count;r++){
        		  				for(var col=7;col<result['end_year']-result['start_year']+8;col++){
        		  					cellSum+= parseFloat(theGrid.jqGrid('getCell',r,col)); 
        		  				}
        		  				theGrid.jqGrid('setCell',r,col,cellSum);
        		  				cellSum = 0;
        		  			 }
						}
				    });
				    JqReloadAndGroup(theGrid,result);
	    		}
			});
		}
		
	}
	
	   /*立项表经费预算页面*/
    if(model=="pm.init.proj.apply"){
        //根据条件构造colNames和colModel
        if(theGrid.length > 0){
            var lastsel;
            //current_year = (new Date()).getFullYear();
            var obj=new openerp.web.Model("pm.init.proj.apply");
            obj.call("getJqGridData",[],{rec_info:record, context: new openerp.web.CompoundContext()}).then(function(result) {
                if(result['start_year']!=0){
                	var editable = true;
                	if(record.proj_apply_state != "draft" && record.proj_approve_state != "draft"){
                		editable = false;
                	}
                    for(var year=result['start_year']; year<=result['end_year'];year++){
                        colNames.push(year+"年");
                        colModel.push({name: year, index: year, width: 40, align: 'center', template: numberTemplate, sortable:false, editable:editable});
                    }
                    colNames.push("合计");
                    colModel.push({name: 'total', index: 'total', width: 40, align: 'center', template: numberTemplate, sortable:false, editable:editable});
                    theGrid.jqGrid({
                        datatype: 'local',
                        data: result["data"],
                        colNames: colNames,
                        colModel: colModel,
                        hidegrid: false,
                        autowidth: true,
                        gridview: true,             
                        rownumbers: false,
                        rowNum: 50,
                        viewrecords: true, 
                        //caption: '科目明细（单位：万元）',
                        height: '100%',
                        onSelectRow : function(id) {
		                    	  var rowData =  theGrid.getRowData(id);
						    	  if(upContext.$el.hasClass('oe_form_readonly')||rowData.first=="资本化合计"||rowData.first=="费用化合计"||rowData.first=="合计"){
						    		return;
						    	  }
                                  //upContext.on_button_edit();
                                  if (id && id !== lastsel) {
                                      //theGrid.jqGrid('saveRow', lastsel, false, 'clientArray');
                                      theGrid.jqGrid('saveRow',lastsel, 
                                              { 
                                                  keys : true,
                                                  url: 'clientArray',
                                                  aftersavefunc: function(response) {
                                                     var count = theGrid.getGridParam("reccount");
                                                     getSum(theGrid,count,result['end_year']-result['start_year']+8);
                                                     var cellSum = 0;
                                                     //循环每一行统计最后一列合计值
                                                     for(var r=1;r<=count;r++){
                                                        for(var col=7;col<result['end_year']-result['start_year']+8;col++){
                                                            cellSum+= parseFloat(theGrid.jqGrid('getCell',r,col)); 
                                                        }
                                                        theGrid.jqGrid('setCell',r,col,cellSum);
                                                        cellSum = 0;
                                                     }
                                                  }
                                              });
                                      theGrid.jqGrid('editRow', id, true); 
                                      lastsel = id;
                               }
                         },
                        editurl: 'clientArray',
                        gridComplete: function () { 
                             MergeJqGrid("jqGrid");
                             var count = theGrid.getGridParam("reccount");
                             var cellSum = 0;
                            //循环每一行统计最后一列合计值
                             for(var r=1;r<=count;r++){
                                for(var col=7;col<result['end_year']-result['start_year']+8;col++){
                                    cellSum+= parseFloat(theGrid.jqGrid('getCell',r,col)); 
                                }
                                theGrid.jqGrid('setCell',r,col,cellSum);
                                cellSum = 0;
                             }
                        }
                    });
                    JqReloadAndGroup(theGrid,result);
                }
            });
        }
        
    }
}

/**
 * save jqGrid Data:
 *
 * @param {String} model
 * @param {String} id
 * @param {String} flag "NewSave" and "EditSave"
 * 
 */
function saveJqGrid(model,id,flag){
	theGrid = $("#jqGrid");
	//获取最后一次编辑的行号
	var gr = theGrid.jqGrid('getGridParam', 'selrow');
	//取消编辑行状态
	theGrid.saveRow(gr);
	var row_count = theGrid.getGridParam("reccount");
	var data_list = new Array();
	if(model=="pm.fund.proj.monthplan"){
		var obj=new openerp.web.Model("pm.fund.proj.monthplan.detail");	
		//循环获取jqGrid中的数据
		for (var i=1; i<=row_count; i++){
			var rowData =  theGrid.getRowData(i);
			rowData.monthplan_id=id;
			data_list[i-1] = rowData;
		}
		obj.call("saveJqGrid",[],{flag:flag, data:data_list, context: new openerp.web.CompoundContext()}).then(function(result){
			//alert("保存成功！");
		});
	}
	
	if(model=="pm.fund.budget.version"){
		var col = theGrid.getGridParam('colNames');
		var start_year = parseInt(col[7].substr(0,4));
		var end_year = parseInt(col[col.length-2].substr(0,4));
		var obj = new openerp.web.Model("pm.fund.budget.version.detail");
		//循环获取jqGrid中的数据
		for (var i=1; i<=row_count; i++){
			var rowData =  theGrid.getRowData(i);
			rowData.version_id=id;
			data_list[i-1] = rowData;
		}
		obj.call("saveJqGrid",[],{flag:flag, start_year:start_year, end_year:end_year, data:data_list, context: new openerp.web.CompoundContext()}).then(function(result){
			//alert("保存成功！");
		});
	}
	
	   if(model=="pm.init.proj.apply"){
        var col = theGrid.getGridParam('colNames');
        var start_year = parseInt(col[7].substr(0,4));
        var end_year = parseInt(col[col.length-2].substr(0,4));
        var obj = new openerp.web.Model("pm.init.budget");
        //循环获取jqGrid中的数据
        for (var i=1; i<=row_count; i++){
            var rowData =  theGrid.getRowData(i);
            rowData.proj_id=id;
            data_list[i-1] = rowData;
        }
        obj.call("saveJqGrid",[],{id:id, start_year:start_year, end_year:end_year, data:data_list}).then(function(result){
            //alert("保存成功！");
        });
    }
}

/**
 * 编辑完单元格，实现自动合计
 *
 * @param {String} count jqgrid总行数
 * @param {String} interval 统计列数
 * 
 */
function getSum(GridObject, count, interval){
	for(var col=7; col<interval; col++){
	  		 var z_cellSum = f_cellSum= 0;
	  		 var z_count = f_count = 0;
	  		 for(var r=1;r<=count;r++){
	  			var rowData =  GridObject.getRowData(r);
		  		if(rowData.first=="资本化支出"){
		  			z_cellSum+= parseFloat(GridObject.jqGrid('getCell',r,col)); 
				}
	  			if(rowData.first=="资本化合计"){
	  				z_count = r;
	  				GridObject.jqGrid('setCell',r,col,z_cellSum);
	  				f_cellSum = 0;
	  			}
		  		if(rowData.first=="费用化支出"){
		  			f_cellSum+= parseFloat(GridObject.jqGrid('getCell',r,col)); 
				}
		  		if(rowData.first=="费用化合计"){
		  			f_count = r;
		  			GridObject.jqGrid('setCell',r,col,f_cellSum);
	  			}
	  		 }
	  		GridObject.jqGrid('setCell',count,col,z_cellSum + f_cellSum);
	  	 }
}

//将合并归总
function MergeJqGrid(gridName){
	//Merger(gridName, 'show_sn');
	Merger(gridName, 'first');
	Merger(gridName, 'second');
	Merger(gridName, 'third');
	
	MergerCell(gridName,'second','third',1);
	MergerCell(gridName,'second','subject_name',2);
	MergerCell(gridName,'third','subject_name',1);
	MergerCell(gridName,'first','second',3);
}

//全编辑模式
/*function toEditMode(name){
	var count = $("#"+name).getGridParam("reccount");
	for(var i=1;i<count;i++){
		$("#"+name).jqGrid('editRow', i);
	}
	
}*/

//合并表头，重新加载数据
function JqReloadAndGroup(GridObject,result){
	GridObject.jqGrid('destroyGroupHeader');
	GridObject.jqGrid( 'setGroupHeaders' , {
		useColSpanStyle: true,  // 没有表头的列是否与表头列位置的空单元格合并
		groupHeaders: [{
		startColumnName:  'first' ,  // 对应colModel中的name
		numberOfColumns: 4,  // 跨越的列数
		titleText: '项目类型'
		}]
	});
	//将空白表头隐藏
	$(".ui-jqgrid-labels.jqg-third-row-header").hide();
	//reload数据
	GridObject.setGridParam({data: result["data"]});
	GridObject.trigger("reloadGrid");
}

//合并单元格公共调用方法
function Merger(gridName, CellName) {
	//得到显示到界面的id集合
	var mya = $("#" + gridName + "").getDataIDs();
	//当前显示多少条
	var length = mya.length;
	for (var i = 0; i < length; i++) {
		//从上到下获取一条信息
		var before = $("#" + gridName + "").jqGrid('getRowData', mya[i]);
		//定义合并行数
		var rowSpanTaxCount = 1;
		for (j = i + 1; j <= length; j++) {
			//和上边的信息对比 如果值一样就合并行数+1 然后设置rowspan 让当前单元格隐藏
			var end = $("#" + gridName + "").jqGrid('getRowData', mya[j]);
			if (before[CellName] == end[CellName]) {
				rowSpanTaxCount++;
				$("#" + gridName + "").setCell(mya[j], CellName, '', { display: 'none' });
			} else {
				rowSpanTaxCount = 1;
				break;
			}
			
			$("#" + CellName + "" + mya[i] + "").attr("rowspan", rowSpanTaxCount);
		}
	}
}

//公共调用方法
function MergerCell(gridName, CellName1,CellName2,cellnum) {
	//得到显示到界面的id集合
	var mya = $("#" + gridName + "").getDataIDs();
	//当前显示多少条
	var length = mya.length;
	for (var i = 0; i < length; i++) {
		//从上到下获取一条信息
		var rowdata = $("#" + gridName + "").jqGrid('getRowData', mya[i]);
		var colSpanTaxCount = cellnum;
		if(rowdata[CellName1]==rowdata[CellName2]){
			colSpanTaxCount++;
			$("#" + CellName1 + "" + mya[i] + "").attr("colspan", colSpanTaxCount);
			$("#" + gridName + "").setCell(mya[i], CellName2, '', { display: 'none' });
		}
		
	}
}

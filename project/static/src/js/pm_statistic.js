openerp.aqy_project = function(instance) {
    var _t = instance.web._t,
        _lt = instance.web._lt;
    var QWeb = instance.web.qweb;
    instance.aqy_project = {};
    
    instance.web.client_actions.add('pm.statistic.leader.page.tag', 'instance.aqy_project.LeaderPage');
    
    instance.aqy_project.LeaderPage = instance.web.Widget.extend({
    	template: "LeaderPage"
    });
    
    openerp.web_kanban.KanbanRecord.include({
        on_card_clicked: function() {
            if (this.view.dataset.model === 'pm.impl.task.project') {
                this.$('.oe_kanban_project_list a').first().click();
            } else {
                this._super.apply(this, arguments);
            }
        },
    });
}

//开始统计分析
function pm_statistic_analysis(){
	var load_tabs1 = false;
	var load_tabs2 = false;
	var load_tabs3 = false;
	//生成选项卡
	$('#leader_page_tabs').tabs({
		heightStyle: "fill",
		event: 'click',
		activate: function(event, ui){
			if(ui.newPanel.selector == '#leader_page_tabs1' && !load_tabs1){
				load_tabs1_func();
			}else if(ui.newPanel.selector == '#leader_page_tabs2' && !load_tabs2){
				load_tabs2_func();
			}else if(ui.newPanel.selector == '#leader_page_tabs3' && !load_tabs3){
				load_tabs3_func();
			}
		}
	});
	
	load_tabs1_func();
	
	function set_time(){
		var now_time = new Date();
		var now_year = now_time.getFullYear();
		var now_month = now_time.getMonth() + 1;
		var now_date = now_time.getDate();
		var now_hours = now_time.getHours();
		var now_minutes = now_time.getMinutes();
		var now_seconds = now_time.getSeconds();
		
		if(now_month < 10){
			var now_month_str = "0" + now_month;
		}else{
			var now_month_str = "" + now_month;
		}
		if(now_date < 10){
			var now_date_str = "0" + now_date;
		}else{
			var now_date_str = "" + now_date;
		}
		if(now_hours < 10){
			var now_hours_str = "0" + now_hours;
		}else{
			var now_hours_str = "" + now_hours;
		}
		if(now_minutes < 10){
			var now_minutes_str = "0" + now_minutes;
		}else{
			var now_minutes_str = "" + now_minutes;
		}
		if(now_seconds < 10){
			var now_seconds_str = "0" + now_seconds;
		}else{
			var now_seconds_str = "" + now_seconds;
		}
		$("#leader_page_time").text(now_year + "年" + now_month_str + "月" + now_date_str + "日  " + now_hours_str + ":" + now_minutes_str + ":" + now_seconds_str + " 统计数据");
	}
	
	function load_tabs1_func(){
		set_time();
		load_tabs1 = true;
		load_leader_page_tabs1_left_top();//1左上
		load_leader_page_tabs1_right_top();//1右上
		load_leader_page_tabs1_left_bottom();//1左下
		load_leader_page_tabs1_right_bottom();//1右下
	}
	function load_tabs2_func(){
		set_time();
		load_tabs2 = true;
		load_leader_page_tabs2_left_top();//2左上
		load_leader_page_tabs2_right_top();//2右上
		load_leader_page_tabs2_left_bottom();//2左下
		load_leader_page_tabs2_right_bottom();//2右下
	}
	function load_tabs3_func(){
		set_time();
		load_tabs3 = true;
		load_leader_page_tabs3_left_top();//3左上
		load_leader_page_tabs3_right_top();//3右上
		load_leader_page_tabs3_left_bottom();//3左下
		load_leader_page_tabs3_right_bottom();//3右下
	}
	
}

/*
  jqGrid公用方法：
  1.data参数的格式要求:
	{
		'tableId': "生成表的Id",
		'modelName': "调用的后台方法所在的模型名",
		'searchParams': [{key1:value1},{key2:value2}...]
	}
  2.后台模型中添加两个对应的方法
	@api.model
	def getCols(self, searchParams):
		//...
		return {cols: '表的列名，中间以英文逗号隔开'}
  
	@api.model
	def getJqGridData(self, cols, searchParams):
		//...
		return {data: [{列名1: 值1},{列名2: 值2}...]}
 */
function common_jqGrid_method(data){
  	var $table = $("#" + data.tableId);
  	var obj = new openerp.web.Model(data.modelName);
  	obj.call("getCols",[],{'searchParams':data.searchParams, context: new openerp.web.CompoundContext()}).then(function(result){
  		var cols = result.cols.split(",");
  		var colModel = [];
  		for(var i = 0;i < cols.length; i++){
  			colModel.push({name: cols[i], index: cols[i], width: 10, align:'center',hidden:false, sortable:false, editable:false});
  		}
  		if(result){
  			if($table){
  		    	obj.call('getJqGridData',[],{'cols':cols, 'searchParams':data.searchParams, context: new openerp.web.CompoundContext()}).then(function(data_result){
  		    		$table.jqGrid({
  				        datatype: 'local',
  				        data: data_result["data"],
  				        colNames: cols,
  				        colModel: colModel,
  				        hidegrid: false,
  				        autowidth: true,
  						gridview: true,             
  						rownumbers: false,
  				        rowNum: 50,
  				        viewrecords: true,  
  				        height: '100%',
  						gridComplete: function () { 
  						}
  				    });
  		    	});
  			}
  		}
  	});
}

//1左上
function load_leader_page_tabs1_left_top(){
	common_jqGrid_method({
		'tableId': "leader_page_tabs1_left_top",
		'modelName': "pm.statistic.leader.page",
		'searchParams': [{'table_flag' : '1_left_top'}]
	});
}

//1右上
function load_leader_page_tabs1_right_top(){
	
	var myChart = echarts.init($("#leader_page_tabs1_right_top")[0]);
	var option = {
		title: {
			text: "所(中心)项目"
		},
		tooltip: {},
		legend: {
			data: ["项目"]
		},
		xAxis: {
			data: ["HSE信息中心安全所","环保所","检测中心","认证中心","新技术推广中心"]
		},
		yAxis: {},
		series: [{
			name: "项目",
			type: "bar",
			data: [90, 88, 89, 110, 180]
		}]
	};
	option = newline(option, 4, 'xAxis')

	myChart.setOption(option);
}

function newline(option, number, axis){
    option[axis]['axisLabel']={
        interval: 0,
        formatter: function(params){
            var newParamsName = "";
            var paramsNameNumber = params.length;
            var provideNumber = number;
            var rowNumber = Math.ceil(paramsNameNumber / provideNumber);
            if (paramsNameNumber > provideNumber) {
                for (var p = 0; p < rowNumber; p++) {
                    var tempStr = "";
                    var start = p * provideNumber;
                    var end = start + provideNumber;
                    if (p == rowNumber - 1) {
                        tempStr = params.substring(start, paramsNameNumber);
                    } else {
                        tempStr = params.substring(start, end) + "\n";
                    }
                    newParamsName += tempStr;
                }
            } else {
                newParamsName = params;
            }
            return newParamsName
        }
    }
    return option;
}

//1左下
function load_leader_page_tabs1_left_bottom(){
	var myChart1 = echarts.init($("#leader_page_tabs1_left_bottom_1")[0]);
	var option1 = {
		tooltip : {
			formatter: "{a} <br/>{b} : {c}%"
		},
		series: [
			     {
			        name: '总体任务',
			        type: 'gauge',
			        radius: '85%',
			        detail: {formatter:'{value}%'},
			        data: [{value: 80, name: '完成率'}]
			     }
			     ]
	};
	myChart1.setOption(option1);
	
	var myChart2 = echarts.init($("#leader_page_tabs1_left_bottom_2")[0]);
	var option2 = {
		    tooltip : {
		        trigger: 'item',
		        formatter: "{a} <br/>{b} : {c} ({d}%)"
		    },
		    legend: {
		        orient: 'horizontal',
		        top: 'auto',
		        data: ['进展顺利','进度滞后','严重滞后']
		    },
		    series : [
		        {
		            name: '项目进展',
		            type: 'pie',
		            radius : '55%',
		            center: ['50%', '50%'],
		            data:[
		                {value:12, name:'进展顺利'},
		                {value:8, name:'进度滞后'},
		                {value:11, name:'严重滞后'}
		            ],
		            itemStyle: {
		                emphasis: {
		                    shadowBlur: 10,
		                    shadowOffsetX: 0,
		                    shadowColor: 'rgba(0, 0, 0, 0.5)'
		                }
		            }
		        }
		    ]
		};
	myChart2.setOption(option2);
}

//1右下
function load_leader_page_tabs1_right_bottom(){
	common_jqGrid_method({
		'tableId': "leader_page_tabs1_right_bottom",
		'modelName': "pm.statistic.leader.page",
		'searchParams': [{'table_flag' : '1_right_bottom'}]
	});
}

//2左上
function load_leader_page_tabs2_left_top(){
	var myChart1 = echarts.init($("#leader_page_tabs2_left_top_1")[0]);
	var option1 = {
		tooltip : {
			formatter: "{a} <br/>{b} : {c}%"
		},
		series: [
			     {
			        name: '合同收入',
			        type: 'gauge',
			        radius: '85%',
			        detail: {formatter:'{value}%'},
			        data: [{value: 89, name: '完成率'}]
			     }
			     ]
	};
	myChart1.setOption(option1);
	
	var myChart2 = echarts.init($("#leader_page_tabs2_left_top_2")[0]);
	var option2 = {
			tooltip : {
				formatter: "{a} <br/>{b} : {c}%"
			},
			series: [
			         {
			        	 name: '实际收入',
			        	 type: 'gauge',
					     radius: '85%',
			        	 detail: {formatter:'{value}%'},
			        	 data: [{value: 72, name: '完成率'}]
			         }
			         ]
	};
	myChart2.setOption(option2);
}

//2右上
function load_leader_page_tabs2_right_top(){
	common_jqGrid_method({
		'tableId': "leader_page_tabs2_right_top",
		'modelName': "pm.statistic.leader.page",
		'searchParams': [{'table_flag' : '2_right_top'}]
	});
}

//2左下
function load_leader_page_tabs2_left_bottom(){
	var myChart1 = echarts.init($("#leader_page_tabs2_left_bottom_1")[0]);
	var option1 = {
		tooltip : {
			formatter: "{a} <br/>{b} : {c}%"
		},
		series: [
			     {
			        name: '总体',
			        type: 'gauge',
			        radius: '85%',
			        detail: {formatter:'{value}%'},
			        data: [{value: 72, name: '使用率'}]
			     }
			     ]
	};
	myChart1.setOption(option1);
	
	var myChart2 = echarts.init($("#leader_page_tabs2_left_bottom_2")[0]);
	var option2 = {
		    tooltip : {
		        trigger: 'item',
		        formatter: "{a} <br/>{b} : {c} ({d}%)"
		    },
		    legend: {
		        orient: 'horizontal',
		        top: 'auto',
		        data: ['技术研究','技术支持','技术服务']
		    },
		    series : [
		        {
		            name: '项目进展',
		            type: 'pie',
		            radius : '55%',
		            center: ['50%', '50%'],
		            data:[
		                {value:46, name:'技术研究'},
		                {value:30, name:'技术支持'},
		                {value:36, name:'技术服务'}
		            ],
		            itemStyle: {
		                emphasis: {
		                    shadowBlur: 10,
		                    shadowOffsetX: 0,
		                    shadowColor: 'rgba(0, 0, 0, 0.5)'
		                }
		            }
		        }
		    ]
		};
	myChart2.setOption(option2);
}

//2右下
function load_leader_page_tabs2_right_bottom(){
	common_jqGrid_method({
		'tableId': "leader_page_tabs2_right_bottom",
		'modelName': "pm.statistic.leader.page",
		'searchParams': [{'table_flag' : '2_right_bottom'}]
	});
}

//3左上
function load_leader_page_tabs3_left_top(){
	var data = {
			'tableId': "leader_page_tabs3_left_top",
			'modelName': "pm.statistic.leader.page",
			'searchParams': [{'table_flag' : '3_left_top'}]
	};
	
  	var $table = $("#" + data.tableId);
  	var obj = new openerp.web.Model(data.modelName);
  	obj.call("getCols",[],{'searchParams':data.searchParams, context: new openerp.web.CompoundContext()}).then(function(result){
  		var colNames = result.cols.split(",");
  		var cols = ['category', 'project', 'this_year_goal', 'this_year_complete', 'last_year_same', 'this_year_total','last_year_total'];
  		var colModel = [
  		      		{ name: 'category', index: 'category', width: 5, align: 'center', 
  		      			cellattr: function(rowId, tv, rawObject, cm, rdata) {
  		      				return 'id=\'category' + rowId + "\'";
  		      			}
  		      		},
  		      		{ name: 'project', index: 'project', width: 10, align: 'center'},
  		      		{ name: 'this_year_goal', index: 'this_year_goal', width: 6, align: 'center'},
  		      		{ name: 'this_year_complete', index: 'this_year_complete', width: 6, align: 'center'},
  		      		{ name: 'last_year_same', index: 'last_year_same', width: 6, align: 'center'},
  		      		{ name: 'this_year_total', index: 'this_year_total', width: 6, align: 'center', 
  		      			cellattr: function(rowId, tv, rawObject, cm, rdata) {
							return 'id=\'this_year_total' + rowId + "\'";
		    			}
		    		},
  		      		{ name: 'last_year_total', index: 'last_year_total', width: 6, align: 'center', 
		      			cellattr: function(rowId, tv, rawObject, cm, rdata) {
							return 'id=\'last_year_total' + rowId + "\'";
						}
					}
  		      	];
  		if(result){
  			if($table){
  		    	obj.call('getJqGridData',[],{'cols':cols, 'searchParams':data.searchParams, context: new openerp.web.CompoundContext()}).then(function(data_result){
  		    		$table.jqGrid({
  				        datatype: 'local',
  				        data: data_result["data"],
  				        colNames: colNames,
  				        colModel: colModel,
  				        hidegrid: false,
  				        autowidth: true,
  						gridview: true,             
  						rownumbers: false,
  				        rowNum: 50,
  				        viewrecords: true,  
  				        height: '100%',
  						gridComplete: function () {
  							Merger(data.tableId, 'category');
  						}
  				    });
  		    	});
  			}
  		}
  	});
  	
	//公共调用方法
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
					$("#" + gridName + "").setCell(mya[j], 'this_year_total', '', { display: 'none' });
					$("#" + gridName + "").setCell(mya[j], 'last_year_total', '', { display: 'none' });
				} else {
					rowSpanTaxCount = 1;
					break;
				}
				$("#" + CellName + "" + mya[i] + "").attr("rowspan", rowSpanTaxCount);
				$("#" + 'this_year_total' + "" + mya[i] + "").attr("rowspan", rowSpanTaxCount);
				$("#" + 'last_year_total' + "" + mya[i] + "").attr("rowspan", rowSpanTaxCount);
			}
		}
	}
}

//3右上
function load_leader_page_tabs3_right_top(){
	common_jqGrid_method({
		'tableId': "leader_page_tabs3_right_top",
		'modelName': "pm.statistic.leader.page",
		'searchParams': [{'table_flag' : '3_right_top'}]
	});
}

//3左下
function load_leader_page_tabs3_left_bottom(){
	var myChart = echarts.init($("#leader_page_tabs3_left_bottom")[0]);
	option = {
		    tooltip : {
		        trigger: 'axis',
		        axisPointer : {            // 坐标轴指示器，坐标轴触发有效
		            type : 'shadow'        // 默认为直线，可选为：'line' | 'shadow'
		        }
		    },
		    legend: {
		        data:['实用新型专利','发明专利']
		    },
		    grid: {
		        left: '3%',
		        right: '4%',
		        bottom: '3%',
		        containLabel: true
		    },
		    xAxis : [
		        {
		            type : 'category',
		            data : ['2011年','2012年','2013年','2014年','2015年']
		        }
		    ],
		    yAxis : [
		        {
		            type : 'value'
		        }
		    ],
		    series : [
		        {
		            name:'实用新型专利',
		            type:'bar',
		            data:[40, 37, 39, 43, 38]
		        },
		        {
		            name:'发明专利',
		            type:'bar',
		            data:[38, 35, 41, 39, 44]
		        }
		    ]
		};
	myChart.setOption(option);
}

//3右下
function load_leader_page_tabs3_right_bottom(){
	var myChart = echarts.init($("#leader_page_tabs3_right_bottom_1")[0]);
	option = {
			title : {
				text : '奖励'
			},
		    tooltip : {
		        trigger: 'item',
		        formatter: "{a} <br/>{b}"
		    },
//		    legend: {
//		        data : ['国家','部级','局级','其他']
//		    },
		    calculable : true,
		    series : [
		        {
		            name:'奖励',
		            type:'funnel',
		            x : '5%',
		            sort : 'ascending',
		            itemStyle: {
		                normal: {
		                    // color: 各异,
		                    label: {
		                        position: 'right'
		                    }
		                }
		            },
		            data:[
		                {value:8, name:'国家：10个'},
		                {value:24, name:'局级：10个'},
		                {value:16, name:'部级：10个'},
		                {value:32, name:'其他：10个'}
		            ]
		        }
		    ]
		};
		          
		myChart.setOption(option);
	
		var myChart2 = echarts.init($("#leader_page_tabs3_right_bottom_2")[0]);
		option2 = {
				title : {
					text : '标准'
				},
				tooltip : {
					trigger: 'item',
					formatter: "{a} <br/>{b}"
				},
				calculable : true,
				series : [
				          {
				        	  name:'标准',
				        	  type:'funnel',
				        	  x : '5%',
				        	  sort : 'ascending',
				        	  itemStyle: {
				        		  normal: {
				        			  // color: 各异,
				        			  label: {
				        				  position: 'right'
				        			  }
				        		  }
				        	  },
				        	  data:[
				        	        {value:8, name:'国际：10个'},
				        	        {value:24, name:'国家：10个'},
				        	        {value:16, name:'集团：10个'},
				        	        {value:32, name:'企业：10个'}
				        	        ]
				          }
				          ]
		};
		
		myChart2.setOption(option2);
		
}


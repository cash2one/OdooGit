openerp.oa = function(instance, local) {
    var _t = instance.web._t,
        _lt = instance.web._lt;
    var QWeb = instance.web.qweb;
    instance.oa = {};
    
    //引入openerp_oa_notification.js
    openerp_oa_notification(instance);
   
    
    function get_day(year,month) {              
        var new_date = new Date(year,month,1);//取下一个月中的第一天          
        return year + "-" + month + "-" + (new Date(new_date.getTime()-1000*60*60*24)).getDate();//获取当月最后一天日期          
    }
   
    function loadCalendarState(_result,flag){
    	//日历绑定签到状态
    	if(_result!=undefined){
    		 //计算个人月度考勤统计
    	    var result={};
    	    result["normal"]=result["overtime"]=result["late_early"]=result["holiday"]=result["travel"]=result["absenteeism"]=0;
    	    result["normal_day"]=result["overtime_day"]=result["late_early_day"]=result["holiday_day"]=result["travel_day"]=result["absenteeism_day"]="";
    	    result["normal_day_title"]=result["overtime_day_title"]=result["late_early_day_title"]=result["holiday_day_title"]=result["travel_day_title"]=result["absenteeism_day_title"]="";
    	    $(".ui-state-default").each(function(){
    	    	//防止重复(如果从别的页面点击了日历控件，则在考勤页面会多出一个隐藏日历)
    	    	if(this.parentNode.parentNode.parentNode.parentNode.parentNode.id=="ui-datepicker-div"){
    	    		return false;
    	    	}
	        	var self=this;
	        	//获取日期
	        	var month=(new Number($(this).parent().attr("data-month")) + 1).toString();
	        	var _day=$(this).text();
	        	var day;
	        	if(month.length==1){
	        		month="0" + month.toString();
	        	}
	        	if(_day.length==1){
	        		day="0" + _day;
	        	}
	        	else{
	        		day=_day;
	        	}
	        		
	        	var date=$(this).parent().attr("data-year") + "-" + month + "-" + day;
	        	//今天日期
	    	    var today = (new Date()).$format("%Y-%m-%d");
	    	    		
	        	if(date<today){
	        		_day=_day+"日";
	        		switch (_result[date])
	        		{
	        		case "正常":
	        			$(self).parent().attr("class","normal");
	        			result["normal"]++;
	        			break;
	        		case "加班":
	        			$(self).parent().attr("class","overtime");
	        			result["overtime"]++;
	        			if(result["overtime"]<=5){
	        				result["overtime_day"]=result["overtime_day"] + _day + ",";
	        			}
	        			result["overtime_day_title"] =result["overtime_day_title"] + _day + ",";
	        			break;
	        		case "迟到":
	        			$(self).parent().attr("class","leave_early");
	        			result["late_early"]++;
	        			if(result["late_early"]<=5){
	        				result["late_early_day"]=result["late_early_day"] + _day + ",";
	        			}
	        			result["late_early_day_title"] =result["late_early_day_title"] + _day + ",";
	        			break;
	        		case "早退":
	        			$(self).parent().attr("class","leave_early");
	        			result["late_early"]++;
	        			if(result["late_early"]<=5){
	        				result["late_early_day"]=result["late_early_day"] + _day + ",";
	        			}
	        			result["late_early_day_title"] =result["late_early_day_title"] + _day + ",";
	        			break;
	        		case "旷":
	        			$(self).parent().attr("class","absenteeism");
	        			result["absenteeism"]++;
	        			if(result["absenteeism"]<=5){
	        				result["absenteeism_day"]=result["absenteeism_day"] + _day + ",";
	        			}
	        			result["absenteeism_day_title"] =result["absenteeism_day_title"] + _day + ",";
	        			break;
	        		case "假":
	        			$(self).parent().attr("class","holiday");
	        			result["holiday"]++;
	        			if(result["holiday"]<=5){
	        				result["holiday_day"]=result["holiday_day"] + _day + ",";
	        			}
	        			result["holiday_day_title"] =result["holiday_day_title"] + _day + ",";
	        			break;
	        		case "差":
	        			$(self).parent().attr("class","travel");
	        			result["travel"]++;
	        			if(result["travel"]<=5){
	        				result["travel_day"]=result["travel_day"] + _day + ",";
	        			}
	        			result["travel_day_title"] =result["travel_day_title"] + _day + ",";
	        			break;
	        		default:
	        			$(self).parent().attr("class","empty");
	        		}
	        	}
	        });
	    	if(_result["role"]!="领导" && _result["role"]!="管理员"){
	    		result["overtime_day_title"]=result["overtime_day_title"].indexOf(",")>0?result["overtime_day_title"].substr(0,result["overtime_day_title"].length-1):"";
	    		result["late_early_day_title"]=result["late_early_day_title"].indexOf(",")>0?result["late_early_day_title"].substr(0,result["late_early_day_title"].length-1):"";
	    		result["holiday_day_title"]=result["holiday_day_title"].indexOf(",")>0?result["holiday_day_title"].substr(0,result["holiday_day_title"].length-1):"";
	    		result["travel_day_title"]=result["travel_day_title"].indexOf(",")>0?result["travel_day_title"].substr(0,result["travel_day_title"].length-1):"";
	    		result["absenteeism_day_title"]=result["absenteeism_day_title"].indexOf(",")>0?result["absenteeism_day_title"].substr(0,result["absenteeism_day_title"].length-1):"";
	    		
	    		result["overtime_day"]=result["overtime_day"].indexOf(",")>0?result["overtime_day"].substr(0,result["overtime_day"].length-1):"";
	    		result["late_early_day"]=result["late_early_day"].indexOf(",")>0?result["late_early_day"].substr(0,result["late_early_day"].length-1):"";
	    		result["holiday_day"]=result["holiday_day"].indexOf(",")>0?result["holiday_day"].substr(0,result["holiday_day"].length-1):"";
	    		result["travel_day"]=result["travel_day"].indexOf(",")>0?result["travel_day"].substr(0,result["travel_day"].length-1):"";
	    		result["absenteeism_day"]=result["absenteeism_day"].indexOf(",")>0?result["absenteeism_day"].substr(0,result["absenteeism_day"].length-1):"";
	    		
	    		if(result["overtime"]>5){
	    			result["overtime_day"]=result["overtime_day"]+"...";
	    		}
	    		if(result["late_early"]>5){
	    			result["late_early_day"]=result["late_early_day"]+"...";
	    		}
	    		if(result["holiday"]>5){
	    			result["holiday_day"]=result["holiday_day"]+"...";
	    		}
	    		if(result["travel"]>5){
	    			result["travel_day"]=result["travel_day"]+"...";
	    		}
	    		if(result["absenteeism"]>5){
	    			result["absenteeism_day"]=result["absenteeism_day"]+"...";
	    		}
	    		
	    		result["day_num"]=_result["day_num"];
	    		$(".oa_self_statistic_list").remove();
	    		var SelfList = $(QWeb.render("Self_Statistic", {result: result}));	    		
				$(".oa_att_statistic").append(SelfList);
	    	}
	    	
	    	var rec=new openerp.Model('oa.attendance');
	    	
	    	//存在旷工时进行提示
	    	if(result["absenteeism"]>0){
	    		//上次签到记录如果没有填写工作日志，进行提示
		        rec.call('get_tips_info',[],{}).then(function (result) {
		        	if(result['work_summary']==false){
		        		if(result['attendance_date']==false){
		        			result['attendance_date']="上次";
		        		}
			        	layer.tips('1、您本月存在旷工记录，请去补充休假记录或进行特签!</br>2、您' + result['attendance_date'] + '的工作日志没有填写，记得去补充！', '.oa_attendance_statistic', {
			    		    tips: [3, '#3595CC'],
			    		    time: 4000
			    		});
		        	}
	        	});  
	    	}
	    	else{
	    		//上次签到记录如果没有填写工作日志，进行提示
		        rec.call('get_tips_info',[],{}).then(function (result) {
		        	if(result['work_summary']==false){
		        		if(result['attendance_date']==false){
		        			result['attendance_date']="上次";
		        		}
			        	layer.tips('您' + result['attendance_date'] + '的工作日志没有填写，记得去补充！', '#work_title', {
			    		    tips: [1, '#3595CC'],
			    		    time: 2000
			    		});
		        	}
	        	});  
	    	} 		
    	}
    }
    
    instance.oa.AttendanceSign = instance.web.Widget.extend({
    	template: "AttendanceSignPage", 
    	events: {
            'mouseenter .ui-state-default': 'InfoShow',
            'mouseleave .ui-state-default': 'InfoHide',
            'mouseleave .oa_calendar_mini': 'InfoHide',
            'mouseenter .oa_attendance_sign': 'InfoHide',
            'mouseenter .oa_attendance_summary': 'InfoHide',
            'mouseenter .oa_attendance_statistic': 'InfoHide',
            //'mouseenter .oa_attendance_calendar': 'HideflyAddOne',
            //签到调用
            'click .oa_btn_submit':'saveSignInfo',
            'click #a_trip':'ShowDetail',
            'click #a_holiday':'ShowDetail',
        },
       
        ShowDetail:function(e){
        	var rec=new openerp.Model('oa.attendance');
        	var title = "";
        	if(e.currentTarget.parentNode.id=="trip_total"){
        		$("#details_flag").val("trip");
        		title = "员工差旅详细信息";
        	}
        	else{
        		$("#details_flag").val("holidays");
        		title = "员工休假详细信息";
        	}
        	//判断是下属所有员工还是关注的员工
        	var scope = "all";
        	if($("#opt_follow").attr("class").indexOf("active")>0){
        		//关注的所有员工
        		scope = "followers";
        	}
        	rec.call('get_th_details',[],{flag:$("#details_flag").val(),scope:scope}).then(function (result) {
        		var data = JSON.stringify(result["data"]);
        		$("#th_details").val(data);
        		layer.open({
        	        type: 2,
        	        title: title,
        	        fix: false,
        	        maxmin: false,
        	        shadeClose: true, //点击遮罩关闭层
        	        area : ['800px' , '520px'],
        	        content: 'oa/static/src/showHolidays.html'
        	    });
        	});
	        
        },
        
        InfoShow:function(e){
        	var obj=$(e.currentTarget);
        	var month=obj.parent().attr("data-month");
        	var day=obj.text();
        	if((new Number(month) + 1).toString().length==1){
        		month="0"+(new Number(month)+1).toString();
        	}
        	else{
        		month=(new Number(month)+1).toString();
        	}
        	if(day.length==1){
        		day="0"+(new Number(day)).toString();
        	}
        	var date=obj.parent().attr("data-year") + "-" + month + "-" + day;
        	//今天日期
        	var d = new Date();
        	var today = d.$format("%Y-%m-%d");
        	if(date<=today){
        		if(date==today){
        			$("#hide_fly_num").text(new Number($("#hide_fly_num").text())+1);
        			if($("#hide_fly_num").text()>1){
        				rec=new openerp.Model('oa.attendance');
    			        rec.call('get_fly_info_of_date',[],{date:date}).then(function (result) {
    			        	switch(result["state"])
    			        	{
    			        	case "签到":
    			        		$("#oa_work_fly").fadeIn(1300);
    				        	$("#oa_work_fly").css({"overflow":"visible","left":e.pageX-e.offsetX-85+e.currentTarget.offsetWidth/2,"top":e.pageY-(e.offsetY-e.currentTarget.offsetHeight/2)});
    				        	$("#fly_sign_in_time").text("签到时间："+result["sign_in_time"]);
    				        	$("#fly_sign_out_time").text("签退时间："+result["sign_out_time"]);
    				        	$("#fly_sign_in_overtime").text("加班签到时间："+result["sign_in_overtime"]);
    				        	$("#fly_sign_out_overtime").text("加班签退时间："+result["sign_out_overtime"]);
    				        	break;
    			        	case "假":
    			        		$("#oa_holiday_fly").fadeIn(1300);
    				        	$("#oa_holiday_fly").css({"overflow":"visible","left":e.pageX-e.offsetX-85+e.currentTarget.offsetWidth/2,"top":e.pageY-(e.offsetY-e.currentTarget.offsetHeight/2)});
    				        	$("#fly_holiday_type").text("休假类型："+result["holiday_type"]);
    				        	$("#fly_apply_reasons").text("申请事由："+result["apply_reasons"]);
    				        	break;
    			        	case "旷":
    			        		$("#oa_work_fly").fadeIn(1300);
    				        	$("#oa_work_fly").css({"overflow":"visible","left":e.pageX-e.offsetX-85+e.currentTarget.offsetWidth/2,"top":e.pageY-(e.offsetY-e.currentTarget.offsetHeight/2)+12});
    				        	$("#fly_sign_in_time").text("签到时间："+result["sign_in_time"]);
    				        	$("#fly_sign_out_time").text("签退时间："+result["sign_out_time"]);
    				        	$("#fly_sign_in_overtime").text("加班签到时间："+result["sign_in_overtime"]);
    				        	$("#fly_sign_out_overtime").text("加班签退时间："+result["sign_out_overtime"]);
    				        	break;
    				        default:
    				        	break;
    			        	}
    		        	});
        			}
        		}
        		else{
        			$("#hide_fly_num").text(new Number($("#hide_fly_num").text())+1);
		        	rec=new openerp.Model('oa.attendance');
			        rec.call('get_fly_info_of_date',[],{date:date,context: new instance.web.CompoundContext()}).then(function (result) {
			        	switch(result["state"])
			        	{
			        	case "签到":
			        		$("#oa_work_fly").fadeIn(1300);
				        	$("#oa_work_fly").css({"overflow":"visible","left":e.pageX-e.offsetX-85+e.currentTarget.offsetWidth/2,"top":e.pageY-(e.offsetY-e.currentTarget.offsetHeight/2)});
				        	$("#fly_sign_in_time").text("签到时间："+result["sign_in_time"]);
				        	$("#fly_sign_out_time").text("签退时间："+result["sign_out_time"]);
				        	$("#fly_sign_in_overtime").text("加班签到时间："+result["sign_in_overtime"]);
				        	$("#fly_sign_out_overtime").text("加班签退时间："+result["sign_out_overtime"]);
				        	break;
			        	case "假":
			        		$("#oa_holiday_fly").fadeIn(1300);
				        	$("#oa_holiday_fly").css({"overflow":"visible","left":e.pageX-e.offsetX-85+e.currentTarget.offsetWidth/2,"top":e.pageY-(e.offsetY-e.currentTarget.offsetHeight/2)});
				        	$("#fly_holiday_type").text("休假类型："+result["holiday_type"]);
				        	$("#fly_apply_reasons").text("申请事由："+result["apply_reasons"]);
				        	break;
			        	case "旷":
			        		$("#oa_work_fly").fadeIn(1300);
				        	$("#oa_work_fly").css({"overflow":"visible","left":e.pageX-e.offsetX-85+e.currentTarget.offsetWidth/2,"top":e.pageY-(e.offsetY-e.currentTarget.offsetHeight/2)+12});
				        	$("#fly_sign_in_time").text("签到时间："+result["sign_in_time"]);
				        	$("#fly_sign_out_time").text("签退时间："+result["sign_out_time"]);
				        	$("#fly_sign_in_overtime").text("加班签到时间："+result["sign_in_overtime"]);
				        	$("#fly_sign_out_overtime").text("加班签退时间："+result["sign_out_overtime"]);
				        	break;
				        default:
				        	break;
			        	}
		        	});
        		}
        	}
        },
        
        InfoHide:function(e){
        	$("#oa_work_fly").hide();
        	$("#oa_holiday_fly").hide();
        },
        
        start: function() {
    		var self=this;
    		calendar = new instance.oa.Carlendar(this);
    		calendar.appendTo(this.$el.find('.oa_attendance_calendar'));
            this.$small_calendar = self.$el.find(".oa_calendar_mini");
            this.$small_calendar.datepicker({
                onChangeMonthYear : self.ChangeMonthYear(self),
                dayNamesMin : Date.CultureInfo.abbreviatedDayNames,
                monthNames:  Date.CultureInfo.abbreviatedMonthNames,
                firstDay: Date.CultureInfo.firstDayOfWeek,
                showOtherMonths : true,
                onSelect : self.ShowWorkSummary(self),
            });
            
            var Sign = new instance.oa.Sign(this);
            Sign.appendTo(this.$(".oa_attendance_sign"));
            
	        //加载工作日志区域
	        var workSummary = new instance.oa.WorkSummary(this);
	        //保存工作总结事件注册
	        workSummary.on("saveWorkSummary", this, this.saveWorkSummary);
	        workSummary.appendTo(this.$(".oa_attendance_summary"));
	        
	        self.getSignInfo();
	        
	        //统计区
	        var statistic = new instance.oa.statistic(this);
	        statistic.appendTo(this.$(".oa_attendance_statistic"));

        },
        
        ChangeMonthYear:function(context){
        	return function(year,month,obj){
        		var self=this;
        		var last_day=get_day(year,month);
        		var first_day=last_day.substr(0,last_day.length-2) + "01";
        		var rec=new openerp.Model('oa.attendance');
    	        rec.call('get_all_state',[],{start_date:first_day,end_date:last_day}).then(function (result) {
    	        	//日历绑定签到状态
    	        	loadCalendarState(result,0);
            	});
        		
        	};
        }, 
        
        ShowWorkSummary:function(context){
        	return function(dateText, inst){
        		var self=this;
        		sel_date=new Date(dateText).format("%Y-%m-%d");
        		var today = (new Date()).$format("%Y-%m-%d");
        		//如果不是当天，在标题上面加上所选日期
        		if(sel_date!=today){
        			$("#work_title").text("工作日志("+sel_date+")");
        			//给隐藏域赋值，所选日期
            		$("#oa_sel_date").val(sel_date);
        		}
        		else{
        			$("#work_title").text("工作日志");
        			//给隐藏域赋空值
            		$("#oa_sel_date").val("");
        		}
        		
        		rec=new openerp.Model('oa.attendance');
        		rec.call('get_work_summary',[],{date:sel_date}).then(function (result) {
    	        	//显示所选日期的工作日志
        			$(".oa_textarea_summary").val(result["work_summary"]);
            	});
        	};
        },
        
        //查询今天签到记录
        getSignInfo:function(){
        	var self=this;
	        rec=new openerp.Model('oa.attendance');
	        rec.call('get_sign_info',[],{}).then(function (result) {
        	    // do something
	        	self.$el.find(".oa_textarea_summary").text(result["work_summary"]);
	        	self.$el.find(".oa_textarea_summary").val(result["work_summary"]);
	        	self.$el.find("#oa_btn_summary").attr('disabled',false); 
        		//self.$el.find(".oa_btn_submit").text(result["btn_sign_name"]);
	        	self.$el.find("#oa_sign_btn_state").val(result["btn_sign_name"]);
	        	switch(result["btn_sign_name"])
	        	{
		        	case "签到":
		        		self.$el.find(".oa_btn_submit span").text("今日签到");
		        		break;
		        	case "签退":
		        		self.$el.find(".oa_btn_submit span").text("今日签退");
		        		break;
		        	case "加班签到":
		        		self.$el.find(".oa_btn_submit span").text("加班签到");
		        		break;
		        	case "加班签退":
		        		self.$el.find(".oa_btn_submit span").text("加班签退");
		        		break;
		        	default:
		        		self.$el.find(".oa_btn_submit span").text("签到结束");
		        		break;	
	        	}
        		self.$el.find(".oa_input_time").val(result["sign_time"]);
        		if(result["btn_sign_state"]=="disabled")
        			self.$el.find(".oa_btn_submit").attr('disabled',true)
        		self.$el.find(".oa_label_state").text(result["sign_state"]);
        	});
        },
        
        saveSignInfo: function(confirm) {
        	var self = this; 
        	var Attendance = new openerp.Model('oa.attendance');
        	Attendance.call('ConfirmTime',[],{btn_state:self.$el.find("#oa_sign_btn_state").val()}).then(function (ret) {
        		if(ret['state']=="no"){
        			if(window.confirm("还没有到正常下班时间，您确定要签退吗?")){
        				Attendance.call('attendance_sign',[],{btn_state:self.$el.find("#oa_sign_btn_state").val()}).then(function (result) {
                    		self.getSignInfo();
                    		alert(result["sign_state"]);
                    	});
        			}
        			else{
        				return false;
        			}
        		}
        		else{
        			Attendance.call('attendance_sign',[],{btn_state:self.$el.find("#oa_sign_btn_state").val()}).then(function (result) {
                		self.getSignInfo();
                		//领导统计区重新加载
                		loadLeaderStatistic(true,"all");
                		alert(result["sign_state"]);
                	});
        		}
        		
        	});
        	
        },
        
        saveWorkSummary: function(confirm) {
        	var self = this;  
            if (confirm) {
            	var Attendance = new openerp.Model('oa.attendance');
            	Attendance.call('save_attendance_work',[],{date:$("#oa_sel_date").val(), btn_state:self.$el.find("#oa_sign_btn_state").val(),summary:self.$el.find(".oa_textarea_summary").val()})
            	.then(function (result) {
            		alert(result["save_state"])
            	});
            	
            } else {
            	alert("服务器异常");
            }
        },  
    });

    instance.web.client_actions.add('oa.attendance.sign', 'instance.oa.AttendanceSign'); 
    
    instance.oa.Carlendar = instance.web.Widget.extend({
        template: 'Calendar',
        start: function() {
            this._super();
            var self=this;
            var rec=new openerp.Model('oa.attendance');
	        var dat=new Date();
	        var last_day=dat.$format("%Y-%m-%d");
	        var first_day=last_day.substr(0,last_day.length-2) + "01";
	        rec.call('get_all_state',[],{start_date:first_day,end_date:last_day}).then(function (result) {
	        	//页面加载时为日历加上标签
	        	loadCalendarState(result,1);
	        }); 
        }
    });
    
    //签到区域
    instance.oa.Sign = instance.web.Widget.extend({  
        template: "Sign",  
        start: function() {  
            var self = this; 
	    	//时钟
	    	startTime();
	    	//加载九宫格
	    	new openerp.Model('oa.attendance').call('get_every_day_staff',[],{context: new instance.web.CompoundContext()})
	    	.then(function (result) {
	    		result_id=[];
	    		result_name=[];
	    		var count=0;
	    		for(var i = 0; i <= 47; i++){
	    			if(result[i]==undefined||result[i]==""){
	    				if(i<12){
	    					$(".slideBox .bd").append("<li><img class='nine_photo_img' src='/web/static/src/img/placeholder.png' /></li>");
	    				}
	    			}
	    			else{
	    				count++;
	    				result_id[i]=result[i].substr(0,result[i].indexOf(","));
	    	    		$(".slideBox .bd").append("<li><img class='nine_photo_img' src='/web/binary/image?model=oa.staff.basic&amp;id="+result_id[i]+"&amp;field=avatar' /></li>")
	    			}
				}
	    		/*var PhotoList = $(QWeb.render("Nine_Photo", {count:count,result_id: result_id,result_name:result_name}));
				$("#oa_nine_wrap").append(PhotoList);*/
				$(".slideBox .bd li").each(function(h){ jQuery(".slideBox .bd li").slice(h*12,h*12+12).wrapAll("<ul></ul>");});
		        $(".slideBox").slide({mainCell:".bd",autoPlay:true,effect:"left"});
	    	});
	    }, 
    });
    
    instance.oa.WorkSummary = instance.web.Widget.extend({  
        template: "WorkSummary",  
        start: function() {  
            var self = this;
            //保存工作总结事件调用
            this.$el.find("#oa_btn_summary").click(function() {
            	self.trigger("saveWorkSummary", true); 
            });
        },  
    });

    //考勤统计Widget
    instance.oa.statistic = instance.web.Widget.extend({
    	template: "AttendanceStatistic", 
    	events: {
            'click #opt_all':'ShowAll',
            'click #opt_follow':'ShowFollowers',
        },
        ShowAll:function(e){
        	loadLeaderStatistic(true,"all");
        },
        ShowFollowers:function(e){
        	loadLeaderStatistic(true,"followers");
        },
        start: function() {  
            var self = this;
            loadLeaderStatistic(false,"all");
        },  
    });
    
    function loadLeaderStatistic(is_remove,scope){
    	var obj = new openerp.Model('oa.attendance');
        obj.call('get_statistic',[],{scope:scope}).then(function (result) {
    		if (result!=undefined){
    			if(result["role"]=="中心领导"||result["role"]=="项目经理"){
    				//人员过多进行截取
    				result.late_person = result.late_person.substr(0,result.late_person.length-2);
    				if(result.late_person.split(",").length>3){
    					result["late_person_display"]=result.late_person.split(",").slice(0,3).join(",")+"...";
    				}
    				else{
    					result["late_person_display"]=result.late_person;
    				}
    				if(result.no_sign.split(",").length>3){
    					result["no_sign_display"]=result.no_sign.split(",").slice(0,3).join(",")+"...";
    				}
    				else{
    					result["no_sign_display"]=result.no_sign;
    				}
    				if(result.trip_person.split(",").length>3){
    					result["trip_display"]=result.trip_person.split(",").slice(0,3).join(",")+"...";
    				}
    				else{
    					result["trip_display"]=result.trip_person;
    				}
    				if(result.holi_person.split(",").length>3){
    					result["holi_display"]=result.holi_person.split(",").slice(0,3).join(",")+"...";
    				}
    				else{
    					result["holi_display"]=result.holi_person;
    				}
    				if(is_remove==true){
    					$(".oa_leader_statistic_list").remove();
    				}
    				var leaderList = $(QWeb.render("Leader_Statistic", {result: result, scope:scope}));
    				$(".oa_att_statistic").append(leaderList);
    				if(scope=="all"){
    					$("#opt_all").attr("class","btn btn-info btn-sm active");
    				}
    				else{
    					$("#opt_follow").attr("class","btn btn-info btn-sm active");
    				}
    			}
    		}
    	});
    }
    
    //自定义一种展示Datetime字段的widget,只显示和编辑小时：分钟
    instance.oa.OnlyTime = instance.web.form.AbstractField.extend({
    init: function() {
        this._super.apply(this, arguments);
        //this.set("value", new Date().toLocaleString());
        //alert("init " + this.get("value"));
        //alert(this.get("value").constructor==Date)
    },
    
    start: function() {
        this.on("change:effective_readonly", this, function() {
            this.display_field();
            this.render_value();
        });
        this.display_field();
        return this._super();
    },
    
    display_field: function() {
        var self = this;
        this.$el.html(QWeb.render("OnlyTime", {widget: this}));
        if (this.get("effective_readonly")) {
        	//如果是只读，设置空间变灰
            this.$("#hour").attr("readonly", "readonly");
        	this.$("#minute").attr("readonly", "readonly");
        }
        else {
       	 	this.$("#hour").removeAttr("readonly");
        	this.$("#minute").removeAttr("readonly");
        	//绑定两个input的事件处理
        	this.$("input").change(function() {
        		var sHour = self.$("#hour").val();
        		var sMin = self.$("#minute").val();
        		var reg = new RegExp("^[0-9]*$");
        		//小时字段分钟字段都没有填写，将日期设置为null
      			if(!sHour && !sMin) {
      				self.internal_set_value(null);
      			}
      			//小时字段填写了，分钟字段没有填写
      			else if(sHour && !sMin) {
      				if(!reg.test(sHour) || parseInt(sHour, 10) > 23) {
      					self.do_warn("请您按规则填写时间","小时字段填写不合规！");
      					self.$("#hour").val("");
      					self.internal_set_value(null);
      				} else {
      					sMin = "00";
      					var sDt = "1970-01-01 " + sHour + ":" + sMin + ":00";
                self.internal_set_value(sDt);
      				}
      			}
      			else if(!sHour && sMin) {
      				self.do_warn("请您按规则填写时间","小时字段不得为空！");
      				self.$("#minute").val("");
      				self.internal_set_value(null);
      			}
      			else if(sHour && sMin) {
      				if(!reg.test(sHour) || parseInt(sHour, 10) > 23) {
      					self.do_warn("请您按规则填写时间","小时字段填写不合规！");
      					self.$("#hour").val("");
      					self.$("#minute").val("");
      					self.internal_set_value(null);
      					return;
      				}
      				if(!reg.test(sMin) || parseInt(sMin, 10) > 59) {
      					self.do_warn("请您按规则填写时间","分钟字段填写不合规！");
      					self.$("#hour").val("");
      					self.$("#minute").val("");
      					self.internal_set_value(null);
      					return;
      				}
      				// 更新时间，并将日期统一设置为1970-01-01。
      				// 在py中将日期替换为考勤当天日期。
      				//var n_date = new Date("1970", "00", "01", sHour, sMin, "00");
      				var sDt = "1970-01-01 " + sHour + ":" + sMin + ":00";
                  self.internal_set_value(sDt);
      			}
        	});
        }
    },
        
    render_value: function() {
        var dt = this.get("value");
        //alert("render" + dt);
        //alert(dt.constructor==Date);
        if(dt) {
        	//var hour = dt.getHours();
        	//var minute = dt.getMinutes();
        	//alert("render new value");
        	var index = dt.indexOf(":");
        	var hour = dt.substr(index-2, 2);
        	var minute = dt.substr(index+1, 2);
        	this.$("#hour").val(hour);
        	this.$("#minute").val(minute);
         }
         else {
         	//alert("reder clear");
         	this.$("#hour").val("");
        	this.$("#minute").val("");
         }
    },
    });
    
    
    instance.web.form.widgets.add('onlytime', 'instance.oa.OnlyTime');
    
    //考勤统计Widget
    instance.oa.Tobedevelop = instance.web.Widget.extend({
    	template: "TobeDevelop",  
        start: function() {  
            var self = this;
        },  
    });
    
    instance.web.client_actions.add('oa.attendance.statistic', 'instance.oa.Tobedevelop'); //考勤统计
    instance.web.client_actions.add('oa.assess.statistic', 'instance.oa.Tobedevelop'); //绩效统计
    instance.web.client_actions.add('oa.platform.conference.reservation', 'instance.oa.Tobedevelop'); //会议室预订
    instance.web.client_actions.add('oa.platform.research', 'instance.oa.Tobedevelop'); //科研成果
    instance.web.client_actions.add('oa.platform.print', 'instance.oa.Tobedevelop'); //用印管理
    instance.web.client_actions.add('oa.platform.release', 'instance.oa.Tobedevelop'); //文件发布
    instance.web.client_actions.add('oa.online.learn', 'instance.oa.Tobedevelop'); //文件发布
}
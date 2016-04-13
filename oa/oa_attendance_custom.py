# -*- coding: utf-8 -*-
from openerp import models, fields, api
import datetime,calendar
import types


class oa_attendance_custom(models.Model):
    _name = 'oa.attendance.custom'
    _description = u"自定义考勤统计"
    
    def _get_default_param_year(self):
        now_date = datetime.datetime.now()
        return now_date.year
    
    def _get_default_param_month(self):
        now_date = datetime.datetime.now()
        return now_date.month
    
    param_organ = fields.Char(string=u'单位')
    param_year = fields.Integer(string=u'年份',default=_get_default_param_year)
    param_month = fields.Integer(string=u'月份',default=_get_default_param_month)
#     param_organ = fields.Many2one('oa.admin.org',string=u'单位')
#     param_year = fields.Many2one('sys.constant', string=u'年份', domain=[('type', '=', 'year')])
#     param_month = fields.Many2one('sys.constant', string=u'月份', domain=[('type', '=', 'month')])
     
    #获取自定义table表头
    @api.model
    def getCols(self,searchParams):
        #默认查当前月
        now_date = datetime.datetime.now()
        search_year = now_date.year
        search_month = now_date.month
        
        if len(searchParams) > 0:
            for searchParam in searchParams:
                if searchParam and type(searchParam) is types.ListType:
                    if searchParam[0] == u'param_year' and searchParam[2]:
                        search_year = int(searchParam[2])
                    elif searchParam[0] == u'param_month' and searchParam[2]:
                        search_month = int(searchParam[2])
                        
        day_num = calendar.monthrange(search_year,search_month)[1]
        
        cols_str_start = u'姓名,01,02,03,04,05,06,07,08,09,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28'
        cols_str_end = u'正常出勤,迟到,早退,加班,旷工,病假,事假,探亲假,产假,工伤假,婚丧假,年假,换休,献血,公务外出,出差,学习,其它'
        if day_num == 28:
            cols = cols_str_start + u',' + cols_str_end
        elif day_num == 29:
            cols = cols_str_start + u',29,' + cols_str_end
        elif day_num == 30:
            cols = cols_str_start + u',29,30,' + cols_str_end
        elif day_num == 31:
            cols = cols_str_start + u',29,30,31,' + cols_str_end
        return {'cols':cols}
    
    #获取自定义table显示数据
    @api.model
    def getJqGridData(self, cols, searchParams):
        data_list = []
        
        now_date = datetime.datetime.now()
        search_year = now_date.year
        search_month = now_date.month
        search_organ_id = self.env['res.users'].search([('id','=',self.env.uid)]).staff_id.vld_site.id
        
        if len(searchParams) > 0:
            for searchParam in searchParams:
                if searchParam and type(searchParam) is types.ListType:
                    if searchParam[0] == u'param_year' and searchParam[2]:
                        search_year = int(searchParam[2])
                    elif searchParam[0] == u'param_month' and searchParam[2]:
                        search_month = int(searchParam[2])
                    elif searchParam[0] == u'param_organ' and searchParam[2]:
                        organs = self.env['oa.admin.org'].search([('name','like',searchParam[2])])
                        if len(organs) > 0:
                            search_organ_id = organs[0].id
                            
                        
        day_num = calendar.monthrange(search_year,search_month)[1]
        
        first_day = u''
        last_day = u''
        
        if search_month < 10:
            first_day = str(search_year) + '-0' + str(search_month) + '-01'
            last_day = str(search_year) + '-0' + str(search_month) + '-' + str(day_num)
        else:
            first_day = str(search_year) + '-' + str(search_month) + '-01'
            last_day = str(search_year) + '-' + str(search_month) + '-' + str(day_num)
        
        
        #1.查询数据
        sql = '''
            WITH RECURSIVE r AS
              ( SELECT *
               FROM oa_admin_org
               WHERE id = %d
               UNION ALL SELECT oa_admin_org.*
               FROM oa_admin_org,
                    r
               WHERE oa_admin_org.parent_id = r.id )
            SELECT c.id staff_id,
                   c.name,c.org_id,
                   EXTRACT(year from c.oa_day) nian,EXTRACT(month from c.oa_day) yue,EXTRACT(day from c.oa_day) ri,  c.oa_day, c.is_work,count,at.attendance_date,h_t.name,oo.late_state,oo.zt_state,
                   CASE
                       WHEN COUNT=2 THEN '加班'
                       WHEN is_work=0
                            AND at.attendance_date IS NOT NULL THEN '加班'
                       WHEN is_work=0
                            AND at.attendance_date IS NULL THEN '周末节假日'
                       WHEN is_work=1 and at.attendance_date is null and h_t.name is null then '旷工'
                       WHEN h_t.name IS NOT NULL THEN h_t.name
                       WHEN oo.late_state<'00:00:00' THEN '迟到'
                       WHEN oo.zt_state<'00:00:00' THEN '早退'
                       ELSE '正常出勤'
                   END tate
            FROM
              (SELECT b.id,
                      b.name,
                      a.oa_day,
                      a.is_work,b.org_id
               FROM
                 (SELECT oa_day,
                         is_work
                  FROM oa_work_calendar w
                  WHERE w.oa_day >= '%s'
                    AND w.oa_day <= '%s' ) a,
                 (SELECT st.id,
                         st.name,r.id org_id
                  FROM oa_staff_basic st
                  INNER JOIN r ON st.vld_site = r.id
                  WHERE st.working_state = 'on_duty' ) b ) c
            LEFT JOIN
              (SELECT staff_id, attendance_date,COUNT(1) COUNT
               FROM oa_attendance
               WHERE attendance_date >= '%s'
                 AND attendance_date <= '%s'
               GROUP BY staff_id,
                        attendance_date ) AT ON c.id = AT.staff_id
            AND AT.attendance_date = c.oa_day
            LEFT JOIN
              (SELECT o.staff_id,
                      o.attendance_date,
                      o.attendance_type,
                      CASE
                          WHEN sign_in_time IS NOT NULL THEN fixed_stime-sign_in_time
                          ELSE fixed_stime-ori_sign_in_time
                      END late_state,
                      CASE
                          WHEN sign_out_time IS NOT NULL THEN sign_out_time-fixed_etime
                          ELSE ori_sign_out_time-fixed_etime
                      END zt_state
               FROM oa_attendance o
               WHERE o.attendance_type='normal') oo ON c.id=oo.staff_id
            AND oo.attendance_date = c.oa_day
            LEFT JOIN
              (SELECT staff_id,
                      holidays_type_id,
                      CASE
                          WHEN real_start_date IS NOT NULL THEN real_start_date
                          ELSE apply_start_date
                      END apply_start_date,
                      CASE
                          WHEN real_end_date IS NOT NULL THEN real_end_date
                          ELSE apply_end_date
                      END apply_end_date
               FROM oa_holidays_trip) ho ON (c.oa_day BETWEEN ho.apply_start_date - interval '1 day' AND ho.apply_end_date)
            AND ho.staff_id=c.id
            LEFT JOIN oa_holiday_type h_t ON h_t.id=ho.holidays_type_id
            ORDER BY c.id,oa_day
        ''' % (search_organ_id,first_day,last_day,first_day,last_day)
        self.env.cr.execute(sql)
        resultSet = self.env.cr.fetchall()
        
        #2.封装数据
        staff_infos = {}#staff_id : name
        for row in resultSet:
            if not staff_infos.has_key(row[0]):
                staff_infos[row[0]] = row[1]
        #类型        
        day_types = {}
        day_types[u'正常出勤'] = u'√'
        day_types[u'迟到'] = u'迟'
        day_types[u'早退'] = u'早'
        day_types[u'加班'] = u'加'
        day_types[u'旷工'] = u'旷'
        day_types[u'病假'] = u'病'
        day_types[u'事假'] = u'事'
        day_types[u'探亲假'] = u'探'
        day_types[u'产假'] = u'产'
        day_types[u'工伤假'] = u'工'
        day_types[u'婚丧假'] = u'婚'
        day_types[u'年假'] = u'年'
        day_types[u'换休'] = u'换'
        day_types[u'献血'] = u'献'
        day_types[u'公务外出'] = u'公'
        day_types[u'出差'] = u'出'
        day_types[u'学习'] = u'学'
        day_types[u'周末节假日'] = u''
                
        for staff_id in staff_infos:
            data = {}
            data['staff_id'] = staff_id
            data['姓名'] = staff_infos[staff_id]
            
            #统计数字
            normal_num = 0 #正常出勤
            late_num = 0 #迟到
            leave_early_num = 0    # 早退
            over_time_num = 0    # 加班
            absenteeism_num = 0    # 旷工
            sick_num = 0    # 病假
            personal_num = 0    # 事假
            home_leave_num = 0    # 探亲假
            maternity_leave_num = 0    # 产假
            injury_num = 0    # 工伤假
            wedding_funeral_num = 0    # 婚丧假
            year_num = 0    # 年假
            change_num = 0    # 换休
            blood_num = 0    # 献血
            out_num = 0    # 公务外出
            travel_num = 0    # 出差
            study_num = 0    # 学习
            other_num = 0   #其它
            
            for row in resultSet:
                if staff_id == row[0]:
                    day_label = row[6][8:]#str: 2016-02-01
                    day_type = row[13]
                    if day_types.has_key(day_type):
                        data[day_label] = day_types[day_type]
                        if day_type == u'正常出勤':
                            normal_num = normal_num + 1
                        elif day_type == u'迟到':
                            late_num = late_num + 1
                        elif day_type == u'早退':
                            leave_early_num = leave_early_num + 1
                        elif day_type == u'加班':
                            over_time_num = over_time_num + 1
                        elif day_type == u'旷工':
                            absenteeism_num = absenteeism_num + 1
                        elif day_type == u'病假':
                            sick_num = sick_num + 1
                        elif day_type == u'事假':
                            personal_num = personal_num + 1
                        elif day_type == u'探亲假':
                            home_leave_num = home_leave_num + 1
                        elif day_type == u'产假':
                            maternity_leave_num = maternity_leave_num + 1
                        elif day_type == u'工伤假':
                            injury_num = injury_num + 1
                        elif day_type == u'婚丧假':
                            wedding_funeral_num = wedding_funeral_num + 1
                        elif day_type == u'年假':
                            year_num = year_num + 1
                        elif day_type == u'换休':
                            change_num = change_num + 1
                        elif day_type == u'献血':
                            blood_num = blood_num + 1
                        elif day_type == u'公务外出':
                            out_num = out_num + 1
                        elif day_type == u'出差':
                            travel_num = travel_num + 1
                        elif day_type == u'学习':
                            study_num = study_num + 1
                    else:
                        data[day_label] = u'它'
                        other_num = other_num + 1
                        
            data['正常出勤'] = normal_num
            data['迟到'] = late_num
            data['早退'] = leave_early_num
            data['加班'] = over_time_num
            data['旷工'] = absenteeism_num
            data['病假'] = sick_num
            data['事假'] = personal_num
            data['探亲假'] = home_leave_num
            data['产假'] = maternity_leave_num
            data['工伤假'] = injury_num
            data['婚丧假'] = wedding_funeral_num
            data['年假'] = year_num
            data['换休'] = change_num
            data['献血'] = blood_num
            data['公务外出'] = out_num
            data['出差'] = travel_num
            data['学习'] = study_num
            data['其它'] = other_num
                    
            data_list.append(data)
            
        #3.返回数据
        return {'data':data_list}
    
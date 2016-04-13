# -*- coding: utf-8 -*-

from openerp import models, fields, api
from openerp.osv import osv
import datetime,calendar
from __builtin__ import True
from openerp import http
from openerp.http import request
#from serial.tools.list_ports_windows import NULL

# 出勤表1
class attendance(models.Model):
    _name = 'oa.attendance'
    _description = u"出勤"  
   
    # 获取用户名
    def get_user_name(self):
        uid = self.env.uid
        user_name = self.env['oa.staff.basic'].search([('related_user', '=', uid)]).name
        user_id = self.env['res.users'].search([('id', '=', uid)]).login
        if user_name:
            return user_name
        else:
            return user_id
    
    # 获取指定id用户的姓名    
    def get_user_name_by_uid(self, uid):
        user_name = self.env['oa.staff.basic'].search([('related_user', '=', uid)]).name
        user_id = self.env['res.users'].search([('id', '=', uid)]).login
        if user_name:
            return user_name
        else:
            return user_id        
   
    staff_id = fields.Many2one('oa.staff.basic', '姓名', required=True, select=True)
    attendance_date = fields.Date('出勤日期', required=True, default=fields.datetime.now())
    spec_sign_time = fields.Date('特签日期', default=fields.datetime.now(), readonly=True)
    attendance_type = fields.Selection([('normal', '出勤签录'), ('overtime', '加班签录')], '出勤类型', required=True, default='normal')
    sign_in_time = fields.Datetime('特别签录时间', select=True)
    sign_out_time = fields.Datetime('特别签退时间', select=True)
    sign_in_IP = fields.Char('签录IP')
    sign_out_IP = fields.Char('签退IP')
    work_summary = fields.Text('工作总结')
    spec_sign_person = fields.Char(default=get_user_name , string='特签人', readonly=True)
    spec_sign_reason = fields.Text('特签原由')
    fixed_stime = fields.Datetime('固定签录时间')
    fixed_etime = fields.Datetime('固定签退时间')
    org_name = fields.Char(compute='_get_staff_org_name', string='部门')
    ori_sign_in_time = fields.Datetime(string='签录时间', readonly=True)
    ori_sign_out_time = fields.Datetime(string='签退时间', readonly=True)
    
    # 根据人员id获取人员部门
    @api.depends('staff_id')
    def _get_staff_org_name(self):
        if self.staff_id:
            org_id = self.env['oa.staff.basic'].search([('id', '=', self.staff_id.id)]).vld_site.id
            self.org_name = self.env['oa.admin.org'].search([('id', '=', org_id)]).name
    
    # 考勤数据随用户、考勤日期、考勤类型编号而变化        
    @api.onchange('staff_id', 'attendance_date', 'attendance_type')
    def _onchange_filters(self):
        print "on_change"
        self.ori_sign_in_time = None
        self.ori_sign_out_time = None
        self.sign_in_time = None
        self.sign_out_time = None
        self.spec_sign_reason = None
        if(self.staff_id and self.attendance_date and self.attendance_type):
            attendance_obj = self.env['oa.attendance']
            atten_res = attendance_obj.search([('staff_id', '=', self.staff_id.id), ('attendance_date', '=', self.attendance_date), ('attendance_type', '=', self.attendance_type)])
            if(atten_res):
                self.ori_sign_in_time = atten_res[0].ori_sign_in_time
                self.ori_sign_out_time = atten_res[0].ori_sign_out_time
                self.sign_in_time = atten_res[0].sign_in_time
                self.sign_out_time = atten_res[0].sign_out_time
                self.spec_sign_reason = atten_res[0].spec_sign_reason

    # 特签处理
    @api.multi
    def spec_sign(self, vals):
        #print("execute spec_sign!!!")
        # 为了用两个widget显示时间，定制了onlytime wiget，它返回的日期不对，需要调整
        # 将特签签到时间、特签签录时间的日期改为考勤当天日期
        str_date = vals['attendance_date'].encode("utf-8")
        if vals['sign_in_time']:
            vals['sign_in_time'] = vals['sign_in_time'].replace("1970-01-01", str_date)
        if vals['sign_out_time']:    
            vals['sign_out_time'] = vals['sign_out_time'].replace("1970-01-01", str_date)
        #设置特签人和特签日期
        vals['spec_sign_person'] = self.get_user_name_by_uid(vals['uid'])
        vals['spec_sign_time'] = fields.date.today()
        attendance_obj = self.env['oa.attendance']
        atten_res = attendance_obj.search([('staff_id', '=', vals['staff_id']), ('attendance_date', '=', vals['attendance_date']), ('attendance_type', '=', vals['attendance_type'])])
        # 更新记录
        if(atten_res):
            atten_res[0].write({'sign_in_time':vals['sign_in_time'], 'sign_out_time':vals['sign_out_time'], 'spec_sign_person':vals['spec_sign_person'], 'spec_sign_reason':vals['spec_sign_reason'], 'spec_sign_time':vals['spec_sign_time']})
            #print "create-update over"
        # 插入新记录
        else:
            clock_obj = self.env['oa.attendance.clock']
            #str_today = fields.date.today().strftime("%Y-%m-%d")
            str_start_time = str_date + ' ' + clock_obj.search([('id', '!=', False)]).attendance_start_time
            str_end_time = str_date + ' ' + clock_obj.search([('id', '!=', False)]).attendance_end_time
            _start_time = fields.datetime.strptime(str_start_time, "%Y-%m-%d %H:%M:%S")
            _end_time = fields.datetime.strptime(str_end_time, "%Y-%m-%d %H:%M:%S")
            vals['fixed_stime']=_start_time
            vals['fixed_etime']=_end_time
            self.create(vals)
            #sql_insert = "INSERT INTO oa_attendance(staff_id, attendance_date, attendance_type, sign_in_time, sign_out_time, spec_sign_person, spec_sign_reason, spec_sign_time) values(\'{0}\', \'{1}\', \'{2}\', \'{3}\', \'{4}\', \'{5}\', \'{6}\', \'{7}\')"
            #sql_insert = sql_insert.format(vals['staff_id'], vals['attendance_date'], vals['attendance_type'], vals['sign_in_time'], vals['sign_out_time'], vals['spec_sign_person'], vals['spec_sign_reason'], vals['spec_sign_time'])
            #sql_insert = sql_insert.replace("\'False\'", "NULL")
            #self.current_rec_id = self.env.cr.execute(sql_insert)
            #self.env.invalidate_all()
            #print "create-insert over"
    
    # 恢复原签按钮reset_sign事件
    @api.multi
    def reset_sign(self, vals):
        print("execute reset_sign!!!")
        attendance_obj = self.env['oa.attendance']
        atten_res = attendance_obj.search([('staff_id', '=', vals['staff_id']), ('attendance_date', '=', vals['attendance_date']), ('attendance_type', '=', vals['attendance_type'])])
        # 清除特签时间字段
        if(atten_res):
            atten_res[0].write({'sign_in_time':None, 'sign_out_time':None, 'spec_sign_person':None, 'spec_sign_reason':None, 'spec_sign_time':None})
            print "clear sign over"
    
    #添加用户早退提示
    @api.model
    def ConfirmTime(self,btn_state):
        state = 'ok' 
        today = fields.date.today()
        if btn_state==u'签退':
            #判断是否存在记录，如果不存在，则不是当天签退
            rec = self.search([('staff_id.related_user', '=', self.env.uid), ('attendance_date', '=', today), ('attendance_type', '=', 'normal')])
            if rec.exists():
                fixed_etime = self.search([('staff_id.related_user', '=', self.env.uid), ('attendance_date', '=', today), ('attendance_type', '=', 'normal')]).fixed_etime
                if fields.datetime.strptime(fixed_etime, "%Y-%m-%d %H:%M:%S") > fields.datetime.now():
                    state = 'no'
            else:
                raise osv.except_osv('Warning!',"页面信息已过期，请刷新页面！")
        return {'state':state}    
    # 签到
    @api.model
    def attendance_sign(self, btn_state):
        vals = {}
        today = fields.date.today()
        str_today = today.strftime("%Y-%m-%d")
        res_overtime = self.search([('staff_id.related_user', '=', self.env.uid), ('attendance_date', '=', today), ('attendance_type', '=', 'overtime')])
        res_normal = self.search([('staff_id.related_user', '=', self.env.uid), ('attendance_date', '=', today), ('attendance_type', '=', 'normal')])
        # 根据数据库中的值和btn_state进行签到
        if res_overtime:
            #加班已签到，未签退
            if not res_overtime.ori_sign_out_time and res_overtime.ori_sign_in_time and btn_state == u'加班签退':
                vals['ori_sign_out_time'] = fields.datetime.now()
                vals['sign_out_IP'] = request.httprequest.remote_addr
                res_overtime.write(vals)
                sign_state = '加班签退成功'
        elif res_normal:
            #存在签到记录
            if res_normal.ori_sign_out_time and btn_state == u'加班签到':
                #创建加班记录
                staff_id = self.env['oa.staff.basic'].search([('related_user', '=', self.env.uid)]).id
                vals['staff_id'] = staff_id
                vals['ori_sign_in_time'] = fields.datetime.now()      
                vals['attendance_date'] = today
                vals['attendance_type'] = 'overtime'
                vals['sign_in_IP'] = request.httprequest.remote_addr
                new = super(attendance, self).create(vals)
                if new:
                    sign_state = '加班签到成功'
            if res_normal.ori_sign_in_time and not res_normal.ori_sign_out_time and (btn_state == u'签退' or btn_state == u'加班签退'):
                #正常签退
                vals['ori_sign_out_time'] = fields.datetime.now()
                vals['sign_out_IP'] = request.httprequest.remote_addr
                res_normal.write(vals);
                sign_state = '签退成功'    
        else:
            #还未签到
            if btn_state == u'签到' or btn_state==u'加班签到':
                if btn_state == u'签到':
                    vals['attendance_type'] = 'normal'
                if btn_state==u'加班签到':
                    #判断信息是否过期
                    is_work = self.env['oa.work.calendar'].search([('oa_day','=',today)]).is_work
                    tem_normal = self.search([('staff_id.related_user', '=', self.env.uid), ('attendance_date', '=', today), ('attendance_type', '=', 'normal')])
                    if not is_work:
                        vals['attendance_type'] = 'overtime'
                    else:
                        if tem_normal.exists():
                            vals['attendance_type'] = 'overtime' 
                        else:
                            raise osv.except_osv('Warning!',"页面信息已过期，请刷新页面！")  
                staff_id = self.env['oa.staff.basic'].search([('related_user', '=', self.env.uid)]).id
                vals['staff_id'] = staff_id
                vals['ori_sign_in_time'] = fields.datetime.now()      
                vals['attendance_date'] = today
                vals['sign_in_IP'] = request.httprequest.remote_addr
                # 考勤时钟上限和下限
                clock_obj = self.env['oa.attendance.clock']
                clock_res = clock_obj.search([('id', '!=', False)])
                str_start_time = str_today + ' ' + clock_res.attendance_start_time
                str_end_time = str_today + ' ' + clock_res.attendance_end_time
                _start_time = fields.datetime.strptime(str_start_time, "%Y-%m-%d %H:%M:%S")
                _end_time = fields.datetime.strptime(str_end_time, "%Y-%m-%d %H:%M:%S")
                vals['fixed_stime']=_start_time
                vals['fixed_etime']=_end_time
                new = super(attendance, self).create(vals)
                if new:
                    sign_state = '签到成功'
            #liuhongtai 20151126 页面信息过期提示，如昨天签到后页面一直未动，第二天签退情况
            else:
                raise osv.except_osv('Warning!',"页面信息已过期，请刷新页面！")
        return {'sign_state': sign_state}
    
    # 保存工作总结
    @api.model
    def save_attendance_work(self, date, btn_state, summary):
        vals = {}
        vals['work_summary'] = summary
        save_state = ''
        if date:
            #date不为空表示未修改工作日志
            #查询是否借节日(包括周六周天)
            is_work = self.env['oa.work.calendar'].search([('oa_day','=',date)]).is_work
            if is_work==1:
                res_normal = self.search([('staff_id.related_user', '=', self.env.uid), ('attendance_date', '=', date), ('attendance_type', '=', 'normal')])
                res_normal.write(vals);
                save_state = '修改成功'
            else:
                res_overtime = self.search([('staff_id.related_user', '=', self.env.uid), ('attendance_date', '=', date), ('attendance_type', '=', 'overtime')])
                res_overtime.write(vals); 
                save_state = '修改成功'
        else:
            #今天工作日志保存
            today = fields.date.today()
            #查询今日是否借节日(包括周六周天)
            is_work = self.env['oa.work.calendar'].search([('oa_day','=',today)]).is_work
    
            if is_work == 1:
                if btn_state == u'签到':
                    save_state = '还未进行签到，不能进行保存！'
                if btn_state == u'签退' or btn_state == u'加班签到':
                    # 查询需要更新的记录id
                    res_normal = self.search([('staff_id.related_user', '=', self.env.uid), ('attendance_date', '=', today), ('attendance_type', '=', 'normal')])
                    # 更新正常出勤工作总结
                    res_normal.write(vals);
                    save_state = '保存成功'
                if btn_state == u'加班签退' or btn_state == u'加班结束':
                    res_overtime = self.search([('staff_id.related_user', '=', self.env.uid), ('attendance_date', '=', today), ('attendance_type', '=', 'overtime')])
                    res_overtime.write(vals); 
                    save_state = '保存成功'
            else:
                if btn_state == u'加班签到':
                    save_state = '还未进行签到，不能进行保存！'
                else:
                    res_overtime = self.search([('staff_id.related_user', '=', self.env.uid), ('attendance_date', '=', today), ('attendance_type', '=', 'normal')])
                    res_overtime.write(vals); 
                    save_state = '保存成功'
        return {'save_state':save_state}
    
    # 页面刚进入获取当天签到信息
    @api.model
    def get_sign_info(self):
        work_summary = ''
        btn_save_state = ''
        sign_time = ''
        btn_sign_name = ''
        sign_state = ''
        today = fields.date.today()
        # 考勤时钟上限和下限
        '''
        clock_obj = self.pool.get('oa.attendance.clock')
        clock_ids = clock_obj.search(cr, uid, [('id', '!=', False)], context=context)
        str_start_time = str_today + ' ' + clock_obj.browse(cr, uid, clock_ids, context).attendance_start_time
        str_end_time = str_today + ' ' + clock_obj.browse(cr, uid, clock_ids, context).attendance_end_time
        _start_time = fields.datetime.strptime(str_start_time, "%Y-%m-%d %H:%M:%S")
        _end_time = fields.datetime.strptime(str_end_time, "%Y-%m-%d %H:%M:%S")
        '''
        #查询今日是否借节日(包括周六周天)
        is_work = self.env['oa.work.calendar'].search([('oa_day','=',today)]).is_work
        
        res_overtime = self.search([('staff_id.related_user', '=', self.env.uid), ('attendance_date', '=', today), ('attendance_type', '=', 'overtime')])
        res_normal = self.search([('staff_id.related_user', '=', self.env.uid), ('attendance_date', '=', today), ('attendance_type', '=', 'normal')])
        if res_overtime:
            # 加班结束
            if res_overtime.ori_sign_out_time or res_overtime.sign_out_time:
                work_summary = ['', res_overtime.work_summary][ res_overtime.work_summary != False] 
                btn_save_state = 'enabled'
                sign_time = (res_overtime.sign_out_time and res_overtime.sign_out_time[11:]) or res_overtime.ori_sign_out_time[11:]
                btn_sign_name = '加班结束'
                btn_sign_state = 'disabled'
                sign_state = '加班结束'
            # 已加班但未签退    
            if (not res_overtime.ori_sign_out_time and not res_overtime.sign_out_time) and (res_overtime.ori_sign_in_time or res_overtime.sign_in_time):
                work_summary = ['', res_overtime.work_summary][ res_overtime.work_summary != False] 
                btn_save_state = 'enabled'
                sign_time = (res_overtime.sign_in_time and res_overtime.sign_in_time[11:]) or res_overtime.ori_sign_in_time[11:]
                btn_sign_name = '加班签退'
                btn_sign_state = 'enabled'
                sign_state = '正常'
        elif res_normal:
                # 正常签录已完成，等待加班签录 
                if res_normal.ori_sign_out_time or res_normal.sign_out_time:
                    work_summary = ['', res_normal.work_summary][ res_normal.work_summary != False] 
                    btn_save_state = 'enabled'
                    sign_time = (res_normal.sign_out_time and res_normal.sign_out_time[11:]) or res_normal.ori_sign_out_time[11:]
                    sign_out_time=(res_normal.sign_out_time and res_normal.sign_out_time) or res_normal.ori_sign_out_time
                    if is_work == 1:
                        #正常签退下班完毕，保留加班签到
                        btn_sign_name = '加班签到'
                        btn_sign_state = 'enabled'
                        # 计算签退时间和考勤时钟差，得到状态
                        diff_flag = fields.datetime.strptime(sign_out_time, "%Y-%m-%d %H:%M:%S") > fields.datetime.strptime(res_normal.fixed_etime, "%Y-%m-%d %H:%M:%S") 
                        if diff_flag:
                            sign_state = '正常'
                        else:
                            sign_state = '早退'
                    else:
                        #节假日签退完毕，不保留加班签到，直接结束
                        btn_sign_name = '签到结束'
                        btn_sign_state = 'disabled'
                        sign_state = '加班结束'
                # 正常已签到，还未签退            
                if not res_normal.ori_sign_out_time and res_normal.ori_sign_in_time:
                    work_summary = ['', res_normal.work_summary][ res_normal.work_summary != False] 
                    btn_save_state = 'enabled'
                    sign_time = (res_normal.sign_in_time and res_normal.sign_in_time[11:]) or res_normal.ori_sign_in_time[11:]
                    sign_in_time=(res_normal.sign_in_time and res_normal.sign_in_time) or res_normal.ori_sign_in_time
                    if is_work == 1:
                        #正常签退
                        btn_sign_name = '签退'
                        btn_sign_state = 'enabled'
                        # 计算签退时间和考勤时钟差，得到状态
                        diff_flag = fields.datetime.strptime(sign_in_time, "%Y-%m-%d %H:%M:%S") > fields.datetime.strptime(res_normal.fixed_stime, "%Y-%m-%d %H:%M:%S") 
                        if diff_flag:
                            sign_state = '迟到'
                        else:
                            sign_state = '正常' 
                    else:
                        #节假日签退
                        btn_sign_name = '加班签退'
                        btn_sign_state = 'enabled'
                        sign_state = '加班'
        # 未正常签到
        else:
            work_summary = ''
            btn_save_state = 'enabled'
            sign_time = ''
            btn_sign_state = 'enabled'
            sign_state = ''
            if is_work == 1:
                btn_sign_name = '签到' 
            else:
                btn_sign_name = '加班签到'           
        return {'work_summary':work_summary, 'btn_save_state':btn_save_state, 'sign_time':sign_time, 'btn_sign_name':btn_sign_name, 'btn_sign_state':btn_sign_state, 'sign_state':sign_state}
        
    def get_attendance_noti(self, cr, uid, partner_id, context=None):
        noti_obj = self.pool.get('mail.notification')
        ids = noti_obj.search(cr, uid, [('partner_id', '=', partner_id), ('message_id.model', '=', 'oa.assess')], context=context)
        if ids:
            return {'hasValue':'yes'}
        else:
            return {'hasValue':'no'}
    
    def get_res_id(self, cr, uid, message_id, context=None):
        message_obj = self.pool.get('mail.message')
        ids = message_obj.search(cr, uid, [('id', '=', message_id)], context=context)
        res_id = message_obj.browse(cr, uid, ids, context).res_id
        return {'res_id':res_id}

    #签录页面日历显示信息
    def get_calendar_state(self, cr, uid, date, context=None):
        res_ids = self.search(cr, uid, [('staff_id.related_user', '=', uid), ('attendance_date', '=', date), ('attendance_type', '=', 'overtime')], context=context)
        #加班
        if res_ids:
            return {'state':'加班'}
        #没有加班
        else:
            res_normal_ids = self.search(cr, uid, [('staff_id.related_user', '=', uid), ('attendance_date', '=', date), ('attendance_type', '=', 'normal')], context=context)
            #有签到
            if res_normal_ids:
                res_normal = self.browse(cr, uid, res_normal_ids, context)
                if res_normal.ori_sign_out_time or res_normal.sign_out_time:
                    n_sign_out_time= (res_normal.sign_out_time and res_normal.sign_out_time) or res_normal.ori_sign_out_time
                    diff_flag_out = fields.datetime.strptime(n_sign_out_time, "%Y-%m-%d %H:%M:%S") > fields.datetime.strptime(res_normal.fixed_etime, "%Y-%m-%d %H:%M:%S") 
                    if diff_flag_out:
                        return {'state':'正常'}
                    else:
                        return {'state':'早退'}
                else:
                    return{'state':'旷'}
#                 diff_flag_in = fields.datetime.strptime(res_normal.ori_sign_in_time, "%Y-%m-%d %H:%M:%S") <= fields.datetime.strptime(res_normal.fixed_stime, "%Y-%m-%d %H:%M:%S") 
#                 if not diff_flag_in:
#                     return {'state':'迟到'}
            #没有签到(先看是否是工作日，然后看是否有请假)
            else:
                work_day_obj=self.pool.get('oa.work.calendar')
                day_ids=work_day_obj.search(cr, uid, [('oa_day', '=', date)], context=context)
                is_work = work_day_obj.browse(cr, uid, day_ids, context).is_work
                #非工作日
                if is_work==0:
                    return {'state':''}
                else:
                    #是否有请假记录
                    holiday_obj=self.pool.get('oa.holidays.trip')
                    l_date=date + ' 23:59:59'
                    date_t=date + ' 00:00:00'
                    res_holidays_ids=holiday_obj.search(cr, uid, ['&',('staff_id.related_user', '=', uid),'|','&',('apply_start_date','<=',l_date),('apply_end_date','>=',date_t),'&',('real_start_date','<=',l_date),('real_end_date','>=',date_t)], context=context)   
                    #有记录
                    if res_holidays_ids:
                        type = holiday_obj.browse(cr, uid, res_holidays_ids, context).holidays_type_id.type
                        if type=='holiday':  
                            return {'state':'假'}
                        if type=='trip':
                            return {'state':'差'}
                    #无记录
                    else:
                        return {'state':'旷'}
    
    #签录页面悬浮信息
    @api.model
    def get_fly_info_of_date(self, date):
        state=''
        sign_in_time=''
        sign_out_time=''
        sign_in_overtime=''
        sign_out_overtime=''
        holiday_type=''
        apply_reasons=''

        #是否出勤
        res_normal = self.search([('staff_id.related_user', '=', self.env.uid), ('attendance_date', '=', date), ('attendance_type', '=', 'normal')])
        res_overtime = self.search([('staff_id.related_user', '=', self.env.uid), ('attendance_date', '=', date), ('attendance_type', '=', 'overtime')])
        #有签到
        if res_normal:
            state='签到'
            sign_in_time= (res_normal.sign_in_time and res_normal.sign_in_time[11:]) or res_normal.ori_sign_in_time[11:]
            if res_normal.ori_sign_out_time or res_normal.sign_out_time:
                sign_out_time=(res_normal.sign_out_time and res_normal.sign_out_time[11:]) or res_normal.ori_sign_out_time[11:] 
        #是否加班
        if res_overtime:
            state='签到'
            sign_in_overtime=(res_overtime.sign_in_time and res_overtime.sign_in_time[11:]) or res_overtime.ori_sign_in_time[11:]
            if res_overtime.ori_sign_out_time or res_overtime.sign_out_time:
                sign_out_overtime=(res_overtime.sign_out_time and res_overtime.sign_out_time[11:]) or res_overtime.ori_sign_out_time[11:]
        #没有签到(先看是否是工作日，然后看是否有请假)
        if not res_normal and not res_overtime:
            work_day_obj=self.env['oa.work.calendar']
            is_work = work_day_obj.search([('oa_day', '=', date)]).is_work
            #非工作日
            if is_work==0:
                state='周末'
            else:
                #是否有请假记录
                holiday_obj=self.env['oa.holidays.trip']
                l_date=date + ' 23:59:59'
                date_t=date + ' 00:00:00'
                holidays_res=holiday_obj.search(['&',('staff_id.related_user', '=', self.env.uid),'|','&',('apply_start_date','<=',l_date),('apply_end_date','>=',date_t),'&',('real_start_date','<=',l_date),('real_end_date','>=',date_t)],limit=1)   
                #有记录
                if holidays_res:
                    state='假'
                    type=holidays_res.holidays_type_id.type
                    apply_reasons=holidays_res.apply_reasons
                    if type=='holiday':  
                        holiday_type='休假'
                    if type=='trip':
                        holiday_type='出差'
                #无记录
                else:
                    state='旷'
        return {'state':state,'sign_in_time':sign_in_time,'sign_out_time':sign_out_time,'sign_in_overtime':sign_in_overtime,'sign_out_overtime':sign_out_overtime,'holiday_type':holiday_type,'apply_reasons':apply_reasons}
    
    #获取员工签到日历信息
    @api.model
    def get_all_state(self,start_date,end_date):
        result={}
        staff_obj = self.env['oa.staff.basic']
        staff_res = staff_obj.search([('related_user', '=', self.env.uid)])
        project_role = staff_res.project_position.name
        if staff_res:
            staff_id=staff_res.id
        if not project_role and self.env.uid==1:
            project_role=u'管理员'
            staff_id = 0     
        if project_role==u'项目经理' or project_role==u'主管领导' or project_role==u'管理员':
            role='领导'
        else:
            role='普通员工'
        sql='''select distinct(oa_day),
            case when is_work=1 and type is not null and type='trip' then '差' 
            when is_work=1 and type is not null and type='holiday' then '假'
            when (type is null and w_num=2) or (is_work=0 and leave_early is not null) then '加班'
            when is_work=1 and type is null and leave_early is null then '旷'
            when type is null and w_num=1 and late<'00:00:00' then '迟到'
            when type is null and w_num=1 and leave_early>'00:00:00' then '早退' 
            when type is null and w_num=1 and leave_early<'00:00:00' then '正常' 
            else '休'   
            end state 
            from 
            (select oa_day,is_work,att.ori_sign_in_time,att.ori_sign_out_time, 
            (att.fixed_stime-att.ori_sign_in_time) late, 
            (att.fixed_etime-att.ori_sign_out_time) leave_early,w_num, h_t.type 
            from (select * from oa_work_calendar where oa_day>='{1}' and oa_day<='{2}') cal 
            left join (select attendance_date,case when sign_in_time is not null then sign_in_time else ori_sign_in_time end ori_sign_in_time,
            case when sign_out_time is not null then sign_out_time else ori_sign_out_time end ori_sign_out_time,fixed_stime,fixed_etime 
            from oa_attendance  
            where staff_id={0} and attendance_date>='{1}' and attendance_date<='{2}') att 
            on cal.oa_day=att.attendance_date 
            left join (select attendance_date,count(attendance_date) w_num  
            from oa_attendance 
            where staff_id={0} and attendance_date>='{1}' and attendance_date<='{2}' 
            group by attendance_date) sta 
            on cal.oa_day=sta.attendance_date 
            left join (select holidays_type_id,case when real_start_date is not null then real_start_date else apply_start_date end apply_start_date,
                             case when real_end_date is not null then real_end_date else apply_end_date end apply_end_date
                             from oa_holidays_trip where staff_id={0}) holi 
            on cal.oa_day between holi.apply_start_date - interval '1 day' and holi.apply_end_date 
            left join oa_holiday_type h_t on h_t.id=holi.holidays_type_id 
            where cal.oa_day>='{1}' and cal.oa_day<='{2}' 
            ) a order by oa_day '''
        self.env.cr.execute(sql.format(staff_id,start_date,end_date))
        for row in self.env.cr.fetchall():
            result[row[0]]=row[1]
        sql_workday_num='''select count(1) from oa_work_calendar a where a.oa_day>='{0}' and a.oa_day<'{1}' and a.is_work=1'''
        self.env.cr.execute(sql_workday_num.format(start_date,end_date))
        res_daynum = self.env.cr.fetchone()
        result['day_num']=res_daynum[0]
        result['role']=role
        return result
    
    #获取主管领导、项目经理当日考勤统计
    @api.model
    def get_statistic(self,scope):
        str_today = fields.date.today().strftime("%Y-%m-%d")
        is_work = self.env['oa.work.calendar'].search([('oa_day','=',str_today)]).is_work
        attendance_type = 'normal'
        if is_work==0:
            attendance_type = 'overtime'
        #首先获取用户类型(是普通员工还是中心领导)
        staff_obj = self.env['oa.staff.basic']
        staff_id = staff_obj.search([('related_user', '=', self.env.uid)]).id
        if not staff_id:
            staff_id = 0
        project_role = staff_obj.search([('related_user', '=', self.env.uid)]).project_position.name
        if not project_role and self.env.uid==1:
            project_role=u'管理员'  
        if project_role==u'项目经理' or project_role==u'主管领导' or project_role==u'管理员':
            if project_role==u'主管领导' or project_role==u'管理员':
                role='中心领导'
                #统计当天出勤人员情况
                sql_sign='''
                                select att.id,sta.name,attendance_date,
                                case when sign_in_time is not null then sign_in_time else ori_sign_in_time end ori_sign_in_time,
                                case when sign_out_time is not null then sign_out_time else ori_sign_out_time end ori_sign_out_time,fixed_stime,fixed_etime,holi.staff_id holi_flag
                                from (select * from oa_attendance where attendance_date='{0}' and attendance_type='{1}') att
                                        inner join (select st.id,st.name from oa_staff_basic st where st.working_state='on_duty') sta on att.staff_id=sta.id
                                        left join (select ho.staff_id from oa_holidays_trip ho where '{0}' between ho.apply_start_date - interval '1 day' and apply_end_date) holi
                                        on holi.staff_id=att.staff_id
                            '''
                if scope == 'followers':
                    sql_sign='''
                                select att.id,sta.name,attendance_date,
                                case when sign_in_time is not null then sign_in_time else ori_sign_in_time end ori_sign_in_time,
                                case when sign_out_time is not null then sign_out_time else ori_sign_out_time end ori_sign_out_time,fixed_stime,fixed_etime,holi.staff_id holi_flag
                                from (select * from oa_attendance where attendance_date='{0}' and attendance_type='{1}') att
                                        inner join (select st.id,st.name from oa_staff_basic st inner join 
                                                    (select rel.staff_id from oa_myfollowers myfol inner join oa_myfollowers_staff_rel rel on myfol.id=rel.oa_myfollowers_id where myfol.staff_id={2}) fol on st.id=fol.staff_id where st.working_state='on_duty') sta 
                                        on att.staff_id=sta.id
                                    left join (select ho.staff_id from oa_holidays_trip ho where '{0}' between ho.apply_start_date - interval '1 day' and apply_end_date) holi
                                        on holi.staff_id=att.staff_id
                            '''
                if scope == 'followers':
                    sql_sign=sql_sign.format(str_today,attendance_type,staff_id)
                else:
                    sql_sign=sql_sign.format(str_today,attendance_type)
                #今日未签到人员
                sql_no_sign='''
                            select array_to_string(array( 
                            select name from oa_staff_basic where working_state='on_duty' and id not in
                            (select staff_id from oa_attendance where attendance_date='{0}' union 
                            select staff_id from oa_holidays_trip where '{0}' between apply_start_date - interval '1 day' and apply_end_date) order by name  
                            ),', ')
                            '''
                if scope == 'followers':
                    sql_no_sign='''
                            select array_to_string(array( 
                            select st.name from oa_staff_basic st inner join (select rel.staff_id from oa_myfollowers myfol inner join oa_myfollowers_staff_rel rel on myfol.id=rel.oa_myfollowers_id where myfol.staff_id={1}) fol on st.id= fol.staff_id where working_state='on_duty' and st.id not in
                            (select staff_id from oa_attendance where attendance_date='{0}' union 
                            select staff_id from oa_holidays_trip where '{0}' between apply_start_date - interval '1 day' and apply_end_date) order by st.name  
                            ),', ')
                            '''
                if scope == 'followers':
                    sql_no_sign=sql_no_sign.format(str_today,staff_id)
                else:
                    sql_no_sign=sql_no_sign.format(str_today)
                #休假人员
                sql_holiday='''
                            select type,array_to_string(array( 
                            select name 
                            from (select s.name,t.type,
                                case when real_start_date is not null then real_start_date else apply_start_date end apply_start_date,
                                    case when real_end_date is not null then real_end_date else apply_end_date end apply_end_date
                                  from oa_holidays_trip h
                                  inner join oa_holiday_type t
                                  on h.holidays_type_id=t.id
                                  inner join (select id,name from oa_staff_basic where working_state='on_duty') s 
                                  on h.staff_id=s.id) a
                            where '{0}' between apply_start_date - interval '1 day' and apply_end_date and a.type=t.type
                            ),', ') from oa_holiday_type t group by t.type  
            
                        '''
                if scope == 'followers':
                    sql_holiday='''
                            select type,array_to_string(array( 
                            select name 
                            from (select s.name,t.type,
                                case when real_start_date is not null then real_start_date else apply_start_date end apply_start_date,
                                    case when real_end_date is not null then real_end_date else apply_end_date end apply_end_date
                                  from oa_holidays_trip h
                                  inner join oa_holiday_type t
                                  on h.holidays_type_id=t.id
                                  inner join (select st.id,st.name from oa_staff_basic st inner join (select rel.staff_id from oa_myfollowers myfol inner join oa_myfollowers_staff_rel rel on myfol.id=rel.oa_myfollowers_id where myfol.staff_id={1}) fol on st.id= fol.staff_id where st.working_state='on_duty') s 
                                  on h.staff_id=s.id) a
                            where '{0}' between apply_start_date - interval '1 day' and apply_end_date and a.type=t.type
                            ),', ') from oa_holiday_type t group by t.type  
            
                        '''
                if scope == 'followers':
                    sql_holiday=sql_holiday.format(str_today,staff_id)
                else:
                    sql_holiday=sql_holiday.format(str_today)
                #应到总人数
                sql_total='''
                        select count(1) from oa_staff_basic where working_state='on_duty'
                        ''' 
                if scope == 'followers':
                    sql_total='''
                            select count(1) from oa_staff_basic st inner join (select rel.staff_id from oa_myfollowers myfol inner join oa_myfollowers_staff_rel rel on myfol.id=rel.oa_myfollowers_id where myfol.staff_id={0}) fol on st.id= fol.staff_id where st.working_state='on_duty'
                            ''' 
                    sql_total = sql_total.format(staff_id)
            if project_role==u'项目经理':
                role='项目经理'
                project_id = staff_obj.search([('related_user', '=', self.env.uid)]).project_id.id
                if not project_id:
                    project_id=0
                #统计当天出勤人员情况
                sql_sign='''
                            WITH RECURSIVE r AS ( 
                                SELECT * FROM oa_project_org WHERE id = {1}
                                union   ALL
                                SELECT oa_project_org.* FROM oa_project_org, r WHERE oa_project_org.parent_id = r.id 
                            ) 
                            select att.id,sta.name,attendance_date,
                            case when sign_in_time is not null then sign_in_time else ori_sign_in_time end ori_sign_in_time,
                            case when sign_out_time is not null then sign_out_time else ori_sign_out_time end ori_sign_out_time,fixed_stime,fixed_etime,holi.staff_id holi_flag
                            from (select * from oa_attendance where attendance_date='{0}' and attendance_type='{2}') att
                                    inner join (select st.id,st.name from oa_staff_basic st 
                                                    inner join r on st.project_id=r.id where st.working_state='on_duty') sta on att.staff_id=sta.id
                                      left join (select ho.staff_id from oa_holidays_trip ho where '{0}' between ho.apply_start_date - interval '1 day' and apply_end_date) holi
                                    on holi.staff_id=att.staff_id
                        '''
                if scope == 'followers':
                    sql_sign='''
                            WITH RECURSIVE r AS ( 
                                SELECT * FROM oa_project_org WHERE id = {1}
                                union   ALL
                                SELECT oa_project_org.* FROM oa_project_org, r WHERE oa_project_org.parent_id = r.id 
                            ) 
                            select att.id,sta.name,attendance_date,
                            case when sign_in_time is not null then sign_in_time else ori_sign_in_time end ori_sign_in_time,
                            case when sign_out_time is not null then sign_out_time else ori_sign_out_time end ori_sign_out_time,fixed_stime,fixed_etime,holi.staff_id holi_flag
                            from (select * from oa_attendance where attendance_date='{0}' and attendance_type='{2}') att
                                    inner join (select st.id,st.name from oa_staff_basic st 
                                                    inner join (select rel.staff_id from oa_myfollowers myfol inner join oa_myfollowers_staff_rel rel on myfol.id=rel.oa_myfollowers_id where myfol.staff_id={3}) fol on st.id= fol.staff_id 
                                                    inner join r on st.project_id=r.id where st.working_state='on_duty') sta on att.staff_id=sta.id
                                    left join (select ho.staff_id from oa_holidays_trip ho where '{0}' between ho.apply_start_date - interval '1 day' and apply_end_date) holi
                                        on holi.staff_id=att.staff_id                
                        '''
                if scope == 'followers':
                    sql_sign=sql_sign.format(str_today,project_id,attendance_type,staff_id)
                else:
                    sql_sign=sql_sign.format(str_today,project_id,attendance_type)
                #今日未签到人员
                sql_no_sign='''
                            WITH RECURSIVE t AS ( 
                                SELECT * FROM oa_project_org WHERE id = {1}
                                union   ALL
                                SELECT oa_project_org.* FROM oa_project_org, t WHERE oa_project_org.parent_id = t.id 
                            )
                            select array_to_string(array( 
                            select name from (select st.id,st.name from oa_staff_basic st                                                  
                                                inner join t on st.project_id=t.id where st.working_state='on_duty') sta where id not in
                            (select staff_id from oa_attendance where attendance_date='{0}' union 
                            select staff_id from oa_holidays_trip where '{0}' between apply_start_date - interval '1 day' and apply_end_date) order by name  
                            ),', ')
                            '''
                if scope == 'followers':
                    sql_no_sign='''
                            WITH RECURSIVE t AS ( 
                                SELECT * FROM oa_project_org WHERE id = {1}
                                union   ALL
                                SELECT oa_project_org.* FROM oa_project_org, t WHERE oa_project_org.parent_id = t.id 
                            )
                            select array_to_string(array( 
                            select name from (select st.id,st.name from oa_staff_basic st 
                                                inner join (select rel.staff_id from oa_myfollowers myfol inner join oa_myfollowers_staff_rel rel on myfol.id=rel.oa_myfollowers_id where myfol.staff_id={2}) fol on st.id= fol.staff_id 
                                                inner join t on st.project_id=t.id where st.working_state='on_duty') sta where id not in
                            (select staff_id from oa_attendance where attendance_date='{0}' union 
                            select staff_id from oa_holidays_trip where '{0}' between apply_start_date - interval '1 day' and apply_end_date) order by name  
                            ),', ')
                            '''
                if scope == 'followers':
                    sql_no_sign=sql_no_sign.format(str_today,project_id,staff_id)
                else:
                    sql_no_sign=sql_no_sign.format(str_today,project_id)
                #休假人员
                sql_holiday='''
                            WITH RECURSIVE tt AS ( 
                                SELECT * FROM oa_project_org WHERE id = {1}
                                union   ALL
                                SELECT oa_project_org.* FROM oa_project_org, tt WHERE oa_project_org.parent_id = tt.id 
                            )
                            select type,array_to_string(array( 
                            select name 
                            from (select s.name,t.type,
                                case when real_start_date is not null then real_start_date else apply_start_date end apply_start_date,
                                    case when real_end_date is not null then real_end_date else apply_end_date end apply_end_date
                                  from oa_holidays_trip h
                                  inner join oa_holiday_type t
                                  on h.holidays_type_id=t.id
                                  inner join (select st.id,st.name from oa_staff_basic st                        
                                              inner join tt on st.project_id=tt.id where st.working_state='on_duty') s 
                                  on h.staff_id=s.id) a
                            where '{0}' between apply_start_date - interval '1 day' and apply_end_date and a.type=t.type
                            ),', ') from oa_holiday_type t group by t.type  
            
                        '''
                if scope == 'followers':
                    sql_holiday='''
                            WITH RECURSIVE tt AS ( 
                                SELECT * FROM oa_project_org WHERE id = {1}
                                union   ALL
                                SELECT oa_project_org.* FROM oa_project_org, tt WHERE oa_project_org.parent_id = tt.id 
                            )
                            select type,array_to_string(array( 
                            select name 
                            from (select s.name,t.type,
                                case when real_start_date is not null then real_start_date else apply_start_date end apply_start_date,
                                    case when real_end_date is not null then real_end_date else apply_end_date end apply_end_date
                                  from oa_holidays_trip h
                                  inner join oa_holiday_type t
                                  on h.holidays_type_id=t.id
                                  inner join (select st.id,st.name from oa_staff_basic st
                                              inner join (select rel.staff_id from oa_myfollowers myfol inner join oa_myfollowers_staff_rel rel on myfol.id=rel.oa_myfollowers_id where myfol.staff_id={2}) fol on st.id= fol.staff_id 
                                              inner join tt on st.project_id=tt.id where st.working_state='on_duty') s 
                                  on h.staff_id=s.id) a
                            where '{0}' between apply_start_date - interval '1 day' and apply_end_date and a.type=t.type
                            ),', ') from oa_holiday_type t group by t.type  
            
                        '''
                if scope == 'followers':
                    sql_holiday=sql_holiday.format(str_today,project_id,staff_id)
                else:
                    sql_holiday=sql_holiday.format(str_today,project_id)
                #应到总人数
                sql_total='''
                            WITH RECURSIVE tg AS ( 
                                SELECT * FROM oa_project_org WHERE id = {0}
                                union   ALL
                                SELECT oa_project_org.* FROM oa_project_org, tg WHERE oa_project_org.parent_id = tg.id 
                            )
                            select count(1) from oa_staff_basic st inner join tg on st.project_id=tg.id where st.working_state='on_duty'
                          '''
                if scope == 'followers':
                    sql_total='''
                            WITH RECURSIVE tg AS ( 
                                SELECT * FROM oa_project_org WHERE id = {0}
                                union   ALL
                                SELECT oa_project_org.* FROM oa_project_org, tg WHERE oa_project_org.parent_id = tg.id 
                            )
                            select count(1) from oa_staff_basic st 
                                        inner join (select rel.staff_id from oa_myfollowers myfol inner join oa_myfollowers_staff_rel rel on myfol.id=rel.oa_myfollowers_id where myfol.staff_id={1}) fol on st.id= fol.staff_id
                                        inner join tg on st.project_id=tg.id where st.working_state='on_duty'
                          '''
                if scope == 'followers':
                    sql_total=sql_total.format(project_id,staff_id) 
                else:
                    sql_total=sql_total.format(project_id)  
            #执行sql
            sign_total = 0
            late_total = 0
            late_person = ''   
            self.env.cr.execute(sql_sign.format(str_today))
            res = self.env.cr.fetchall()
            for rec in res:
                sign_total+=1
                if is_work==1 and rec[3]>rec[5] and not rec[7]:
                    late_total+=1
                    late_person += rec[1] + ', ' 
                
            #执行sql 
            self.env.cr.execute(sql_no_sign.format(str_today))
            res_no_sign = self.env.cr.fetchone()
            if res_no_sign[0]:
                no_sign = res_no_sign[0]
                no_sign_total = no_sign.count(',') + 1
            else:
                no_sign = '都已签录'
                no_sign_total = 0
            #执行sql 
            self.env.cr.execute(sql_holiday.format(str_today))
            res_h = self.env.cr.fetchall()
            if res_h[0][1]:
                trip_person = res_h[0][1]
                trip_total=res_h[0][1].count(',') + 1
            else:
                trip_person = '无人出差'
                trip_total = 0
            if res_h[1][1]:       
                holi_person = res_h[1][1]
                holi_total=holi_person.count(',') + 1
            else:
                holi_person = '无人请假'
                holi_total =  0
            self.env.cr.execute(sql_total)
            res_should = self.env.cr.fetchone()
            if res_should:
                should_total = res_should[0]
            else:
                should_total = 0
            return {'role':role,'should_total':should_total,'sign_total':sign_total,'late_total':late_total,'late_person':late_person,'trip_person':trip_person,'trip_total':trip_total,'holi_person':holi_person,'holi_total':holi_total,'no_sign_total':no_sign_total,'no_sign':no_sign}
    
    
    #用户点击日历日期后获取工作日志
    @api.model
    def get_work_summary(self, date):
        work_day_obj=self.env['oa.work.calendar']
        is_work = work_day_obj.search([('oa_day', '=', date)]).is_work
        work_summary = ''
        if is_work==1:
            work_summary = self.search([('staff_id.related_user', '=', self.env.uid), ('attendance_date', '=', date), ('attendance_type', '=', 'normal')]).work_summary
        else:
            work_summary = self.search([('staff_id.related_user', '=', self.env.uid), ('attendance_date', '=', date), ('attendance_type', '=', 'overtime')]).work_summary
        work_summary = '' if work_summary==False else work_summary
        return {'work_summary':work_summary}
          
    def get_every_day_staff(self, cr, uid, context=None):
        str_today = (fields.date.today()-datetime.timedelta(days = 1)).strftime("%Y-%m-%d")
        first_day=str_today[0:len(str_today)-2] + '01'
        sql_total='''select count(1) total from oa_work_calendar where oa_day between '{0}' and '{1}' and is_work=1'''
        cr.execute(sql_total.format(first_day,str_today))
        res_total = cr.fetchone()
        if res_total:
            total = res_total[0]
        else:
            total=0
        sql_all_att_staff='''
                            select staff_id,name,sum(flag) total from 
                            (select aa.staff_id,aa.name,aa.oa_day,case when (bb.late>'00:00:00' and bb.leave_early<'00:00:00'  and bb.work_summary is not null) or (h_t.type='trip') then 1 else 0 end flag from 
                            (select b.id staff_id,b.name,a.oa_day from (select * from oa_work_calendar where oa_day between '{0}' and '{1}' and is_work=1) a,oa_staff_basic b) aa
                            left join (select staff_id,case when sign_in_time is not null then fixed_stime-sign_in_time else fixed_stime-ori_sign_in_time end late,                                     
                            case when sign_out_time is not null then fixed_etime-sign_out_time else fixed_etime-ori_sign_out_time end leave_early,
                            work_summary,attendance_date from oa_attendance where attendance_date between '{0}' and '{1}' and attendance_type='normal') bb
                            on aa.oa_day=bb.attendance_date and aa.staff_id=bb.staff_id
                            left join (select staff_id,holidays_type_id,case when real_start_date is not null then real_start_date else apply_start_date end apply_start_date,                                               
                            case when real_end_date is not null then real_end_date else apply_end_date end apply_end_date                                               
                            from oa_holidays_trip) h on (aa.oa_day between h.apply_start_date - interval '1 day' and h.apply_end_date) and h.staff_id=aa.staff_id
                            left join oa_holiday_type h_t on h_t.id=h.holidays_type_id) tem
                            group by staff_id,name order by total desc
                            '''
        cr.execute(sql_all_att_staff.format(first_day,str_today))
        i = 0
        result = {}
        for row in cr.fetchall():
            if row[2]>=total: 
                result[i]=str(row[0]) + ',' + row[1]
                i = i + 1
        return result     
    
    #进入签到页面进行提示工作日志
    @api.model
    def get_tips_info(self):
        today = fields.date.today()
        res = self.search([('staff_id.related_user', '=', self.env.uid),('attendance_date','!=',today),('attendance_type','=','normal')], limit=1, order='attendance_date desc')
        return {'work_summary':res.work_summary,'attendance_date':res.attendance_date}
        
    #获取提醒条数
    def get_notification_num(self, cr, uid, context=None):
        sql=''' select model,count(1) from mail_message m
                inner join mail_notification n
                on m.id=n.message_id
                where n.partner_id=(select partner_id from res_users where id={0}) and n.is_read=false
                group by m.model
            '''
        cr.execute(sql.format(uid))
        result = {}
        for row in cr.fetchall(): 
            result[row[0]]=row[1]
        return result
    
    #获取差旅休假详细信息
    @api.model
    def get_th_details(self, flag, scope):
        """
        :param flag: 出差  and 休假
        :param scope: 下属所有员工 and 我关注的员工
        :returns: json
        """
        str_today = fields.date.today().strftime("%Y-%m-%d")
        #首先获取用户类型(是普通员工还是中心领导)
        staff_obj = self.env['oa.staff.basic']
        staff_id = staff_obj.search([('related_user','=', self.env.uid)]).id
        if not staff_id:
            staff_id = 0
        project_role = staff_obj.search([('related_user','=', self.env.uid)]).project_position.name
        if not project_role and self.env.uid==1:
            project_role=u'管理员'
        else:
            th_rec = False   
        #根据uid查询差旅人信息
        th_obj = self.env['oa.holidays.trip']
        if flag=='trip':
            if project_role==u'主管领导' or project_role==u'管理员':
                #差旅人员
                if scope == 'all':
                    th_res = th_obj.search([('holidays_type_id.type', '=', 'trip'),('apply_start_date','<=',str_today),('apply_end_date','>=',str_today)])
                else:
                    fol_ids = self.env['oa.myfollowers'].search([('staff_id','=',staff_id)]).followers.ids
                    th_res = th_obj.search([('staff_id','in',fol_ids),('holidays_type_id.type', '=', 'trip'),('apply_start_date','<=',str_today),('apply_end_date','>=',str_today)])
                th_rec = th_res.read(['staff_name','holidays_type_id','apply_reasons','address','apply_start_date','apply_end_date','state'])
            if project_role==u'项目经理':
                #差旅人员
                if scope == 'all':
                    th_res = th_obj.search([('holidays_type_id.type', '=', 'trip'),('apply_start_date','<=',str_today),('apply_end_date','>=',str_today),('manager_uid','=',self.env.uid)])
                else:
                    fol_ids = self.env['oa.myfollowers'].search([('staff_id','=',staff_id)]).followers.ids
                    th_res = th_obj.search([('staff_id','in',fol_ids),('holidays_type_id.type', '=', 'trip'),('apply_start_date','<=',str_today),('apply_end_date','>=',str_today),('manager_uid','=',self.env.uid)])
                th_rec = th_res.read(['staff_name','holidays_type_id','apply_reasons','address','apply_start_date','apply_end_date','state'])
                
        #根据uid查询休假人信息
        else:
            if project_role==u'主管领导' or project_role==u'管理员':
                #差旅人员
                if scope == 'all':
                    th_res = th_obj.search([('holidays_type_id.type', '=', 'holiday'),('apply_start_date','<=',str_today),('apply_end_date','>=',str_today)])
                else:
                    fol_ids = self.env['oa.myfollowers'].search([('staff_id','=',staff_id)]).followers.ids
                    th_res = th_obj.search([('staff_id','in',fol_ids),('holidays_type_id.type', '=', 'holiday'),('apply_start_date','<=',str_today),('apply_end_date','>=',str_today)])   
                th_rec = th_res.read(['staff_name','holidays_type_id','apply_reasons','apply_start_date','apply_end_date','state'])
            if project_role==u'项目经理':
                #差旅人员
                if scope == 'all':        
                    th_res = th_obj.search([('holidays_type_id.type', '=', 'holiday'),('apply_start_date','<=',str_today),('apply_end_date','>=',str_today),('manager_uid','=',self.env.uid)])
                else:
                    fol_ids = self.env['oa.myfollowers'].search([('staff_id','=',staff_id)]).followers.ids
                    th_res = th_obj.search([('staff_id','in',fol_ids),('holidays_type_id.type', '=', 'holiday'),('apply_start_date','<=',str_today),('apply_end_date','>=',str_today),('manager_uid','=',self.env.uid)])
                th_rec = th_res.read(['staff_name','holidays_type_id','apply_reasons','apply_start_date','apply_end_date','state'])
        return {'data':th_rec}

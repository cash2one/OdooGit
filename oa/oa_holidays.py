# -*- coding: utf-8 -*-

from openerp import models, fields, api
from openerp.osv import osv
import openerp
import datetime

# 休假统计表a
class holidays_static(models.Model):
    _name = 'oa.holidays.static'
    _description = u"休假统计"
    
    staff_id = fields.Many2one('oa.staff.basic', '姓名', required=True, select=True)
    holidays_type_id = fields.Many2one('oa.holiday.type', '休假类型', required=True)
    holidays_sum = fields.Integer('休假总天数')
    holidays_left = fields.Integer('休假剩余天数')

# 请假/差旅申请表
class holidays_trip(models.Model):
    _name = 'oa.holidays.trip'
    #继承mail.thread(消息提醒用)
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = u"休假和差旅申请表" 
    
    #获取人员id
    def _get_staff_id(self):
        uid= self.env.uid
        staff_obj=self.env['oa.staff.basic'].search([('related_user','=',uid)])
        if staff_obj:
            staff_id=self.env['oa.staff.basic'].search([('related_user','=',uid)]).id
        else:
            staff_id=''
        return staff_id
    
    #获取用户名
    def _get_user_name(self):
        uid= self.env.uid
        staff_obj=self.env['oa.staff.basic'].search([('related_user','=',uid)])
        user_name=''
        if staff_obj:
            user_name=staff_obj.name
        else:
            user_name=self.env['res.users'].search([('id','=',uid)]).partner_id.name
        return user_name
    
    #获取当前日期
    def _get_current_date(self):
        return fields.date.today()
    
    @api.depends('staff_id')
    def _get_user_role(self):
        uid=self.env.uid
        role_id=self.env['oa.staff.basic'].search([('related_user','=',uid)]).project_position.id
        self.user_role = self.env['oa.project.role'].search([('id','=',role_id)]).name
    
    #获取用户id
    @api.depends('staff_id')
    def _if_same_uid(self):
        if self.create_uid.id and self.create_uid.id==self.env.uid:
            self.same_uid=True
        else:
            self.same_uid=False    
    
    @api.depends('double_validation')
    def _is_first_invisible(self):
        role_name=self.env['oa.staff.basic'].search([('related_user','=',self.env.uid)]).project_position.name
        if self.double_validation:
            #两级审批，流程肯定是普通员工--组长--项目经理
            if role_name!=u'组长':
                self.is_invisible=True
            else:
                self.is_invisible=False
        else:
            #一级审批，流程可能为普通员工--项目经理；组长--项目经理；项目经理--主管领导
            if self.staff_id.project_position.name == u'项目经理':
                #项目经理创建，则由项目主管审批
                if self.manager_uid == self.env.uid:
                    #当前用户为当前记录所属项目的主管领导
                    self.is_invisible=False
                else:
                    self.is_invisible=True
            elif self.staff_id.project_position.name != u'主管领导':
                #创建者为组长或开发等人员
                if role_name==u'项目经理':
                    self.is_invisible=False
                else:
                    self.is_invisible=True
                        
    #获取名称
    @api.depends('staff_id')
    def _get_name_title(self):
        if self.staff_id:
            self.name = self.env['oa.staff.basic'].search([('id','=', self.staff_id.id)]).name + u'的差旅休假申请'
    
    #获取是否差旅类型
    @api.depends('holidays_type_id')
    def _get_is_trip(self):
        if self.holidays_type_id.type=='trip':
            self.is_trip = True
        else:
            self.is_trip = False
                    
    staff_id = fields.Many2one('oa.staff.basic', '姓名', required=True, select=True,default=_get_staff_id) 
    staff_name=fields.Char('姓名',default=_get_user_name)
    name=fields.Char(compute='_get_name_title',string='名称',default='差旅休假申请',recursive=True)
    holidays_type_id = fields.Many2one('oa.holiday.type', '申请类型', required=True, )  
    apply_reasons = fields.Text('申请事由', required=True)
    apply_date = fields.Date('申请日期', required=True,default=_get_current_date)
    apply_start_date = fields.Datetime('开始时间', required=True)
    apply_end_date = fields.Datetime('结束时间', required=True)
    real_start_date = fields.Datetime('实际开始日期')
    real_end_date = fields.Datetime('实际结束日期')
    state = fields.Selection([('refused', '已拒绝'), ('returned1', '已退回'), ('submitted', '已提交'), ('returned2', '已退回'),('first_accepted', '一级已通过'), ('last_accepted', '审批通过'),('resumpted','已销假'),('validated','确认')], '审批状态')
    proxy_person = fields.Char('代理申请人')
    finally_approver = fields.Char('最终审批人')
    leader_uid=fields.Integer('上级组长id') 
    manager_uid=fields.Integer('项目经理考核人id') 
    double_validation=fields.Boolean('是否两级流程')
    user_role=fields.Char(compute='_get_user_role',string='当前用户项目角色名',recursive=True)
    same_uid=fields.Boolean(compute='_if_same_uid',string='用户id与create_uid是否相同',recursive=True)
    is_invisible=fields.Boolean(compute='_is_first_invisible',string='一级按钮对于项目经理是否可见',recursive=True)
    #增加字段(出差地点)
    address = fields.Char('出差地点',size=100)
    is_trip = fields.Boolean(compute='_get_is_trip', string='是否差旅类型',recursive=True)
    
    # 计算时长
    holidays_duration = fields.Char(compute='_get_holidays_duration', string='计算时长',store=True,recursive=True)
    real_holidays_duration = fields.Char(compute='_get_holidays_duration', string='实际计算时长',store=True,recursive=True)
    holidays_left=fields.Char(compute='_get_left_holidays',string='剩余年假天数',recursive=True)
    compensation_left=fields.Char(compute='_get_left_compensation',string='剩余倒休天数',recursive=True)
    
    @api.multi
    def write(self, vals):
        #判断实际日期不能相同或结束日期不能小于开始日期
        DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
        if vals.has_key('real_end_date') and vals.has_key('real_start_date'):
            from_dt = datetime.datetime.strptime(vals['real_start_date'], DATETIME_FORMAT)
            to_dt = datetime.datetime.strptime(vals['real_end_date'], DATETIME_FORMAT)
            if to_dt <= from_dt:
                raise osv.except_osv('Warning!',"申请开始时间不能早于结束时间！")
        return models.Model.write(self, vals)
    
    def unlink(self, cr, uid, ids, context=None):
        res = self.browse(cr, uid, ids, context)
        is_exist = False 
        for record in res: 
            if record.state not in ('returned1','returned2') or record.create_uid.id!=uid:
                is_exist = True
                break
        if is_exist:
            raise osv.except_osv('提示',"您不能删除!")
        else:
            return models.Model.unlink(self, cr, uid, ids, context=context)
    
    @api.depends('staff_id')
    def _get_left_holidays(self):
        self.holidays_left='0 天'
        if self.staff_id:
            cost_sum=0.0
            #今年开始和结束时间
            cur_date_min=fields.date.today().strftime("%Y")+'-01-01'
            cur_date_max=fields.date.today().strftime("%Y")+'-12-31'
            _date_min=fields.datetime.strptime(cur_date_min, "%Y-%m-%d")
            _date_max=fields.datetime.strptime(cur_date_max, "%Y-%m-%d")
            recs=self.search([('staff_id','=',self.staff_id.id),('holidays_type_id.name','=',u'年假'),('apply_date','>=',_date_min),('apply_date','<=',_date_max),('holidays_duration','!=',u'0.5 天'),('state','not in',('returned1','returned2','refused','submitted'))])
            for rec in recs:
                duration='0'
                if rec.real_start_date and rec.real_end_date:
                    duration=rec.real_holidays_duration[0:len(rec.real_holidays_duration)-2]
                else:
                    duration=rec.holidays_duration[0:len(rec.holidays_duration)-2]
                cost_sum+=float(duration)
            #获取该员工年假总天数
            staff_seniority=self.env['oa.staff.basic'].search([('id','=',self.staff_id.id)]).staff_seniority
            if staff_seniority:
                diff_year=fields.date.today().year-staff_seniority
                if diff_year<1:
                    self.holidays_left = '0 天'
                elif diff_year>=1 and diff_year<10:
                    self.holidays_left = str(5-cost_sum) + ' 天'
                elif diff_year>=10 and diff_year<20:
                    self.holidays_left = str(10-cost_sum) + ' 天'  
                elif diff_year>=20:
                    self.holidays_left = str(20-cost_sum) + ' 天'        
            
    @api.depends('staff_id')         
    def _get_left_compensation(self):
        self.compensation_left='0 天'
        if self.staff_id:
            cost_sum=0.0
            #今年开始和结束时间
            cur_date_min=fields.date.today().strftime("%Y")+'-01-01'
            cur_date_max=fields.date.today().strftime("%Y")+'-12-31'
            _date_min=fields.datetime.strptime(cur_date_min, "%Y-%m-%d")
            _date_max=fields.datetime.strptime(cur_date_max, "%Y-%m-%d")
            recs=self.search([('staff_id','=',self.staff_id.id),('holidays_type_id.name','=','换休'),('apply_date','>=',_date_min),('apply_date','<=',_date_max),('state','not in',('returned1','returned2','refused','submitted'))])
            for rec in recs:
                duration='0'
                if rec.real_start_date and rec.real_end_date:
                    duration=rec.real_holidays_duration[0:len(rec.real_holidays_duration)-2]
                else:
                    duration=rec.holidays_duration[0:len(rec.holidays_duration)-2]
                cost_sum+=float(duration)
            #获取该员工可换休总天数
            sum_compensation=0.0
            compensation_recs=self.env['oa.compensation.records'].search([('staff_id','=',self.staff_id.id),('compensation_year','=',fields.date.today().year)])
            for rec in compensation_recs:
                sum_compensation+=rec.compensation_num
            if sum_compensation:
                self.compensation_left = str(sum_compensation-cost_sum)+' 天'
                
    #在create方法中调用，vals中增加对应字段
    def _save_super_uid(self,vals):
        #获取用户项目角色名
        _role_name = self.env['oa.staff.basic'].search([('id','=',vals['staff_id'])]).project_position.name
        #获取用户项目组织机构名(是否有上级单位)
        _org_id=self.env['oa.staff.basic'].search([('id','=',vals['staff_id'])]).project_id.id
        _pid= self.env['oa.project.org'].search([('id','=', _org_id)]).parent_id
        need_org_id=0
        if _pid:
            need_org_id=_pid.id
        else:
            need_org_id=_org_id
        #获取需要发送信息的所有上级用户
        leader_uid=0
        manager_uid=0
        # 上级单位不是根单位
        if _pid:
            # 组长
            if _role_name==u"组长":
                leader_uid=self.env.uid
                _group_manager_id=self.env['oa.project.role'].search([('name','=',u'项目经理')]).id
                double_validation=False
                #manager_uid=self.env['oa.staff.basic'].search([('project_id','=',need_org_id),('project_position','=',_group_manager_id)]).related_user.id
                #使用insert插入人员id
                str_sql = "select related_user from oa_staff_basic where project_id={0} and project_position={1}"
                self.env.cr.execute(str_sql.format(need_org_id,_group_manager_id))
                res_uid = self.env.cr.fetchone()
                manager_uid = res_uid[0]
            # 普通成员(寻找相同单位的组长)
            else:
                # 获取组长的rold_id
                _group_leader_id=self.env['oa.project.role'].search([('name','=',u'组长')]).id
                _group_manager_id=self.env['oa.project.role'].search([('name','=',u'项目经理')]).id
                leader_uid=self.env['oa.staff.basic'].search([('project_id','=',_org_id),('project_position','=',_group_leader_id)]).related_user.id
                manager_uid=self.env['oa.staff.basic'].search([('project_id','=',need_org_id),('project_position','=',_group_manager_id)]).related_user.id
                double_validation=True   
        # 上级单位为根单位
        else:
            # 上级单位为根单位
            double_validation=False 
            leader_uid = self.env.uid  
            if _role_name == u'项目经理':
                #如果角色为项目经理，则manager_uid为项目主管
                #manager_uid = self.env['oa.project.org'].search([('id','=',need_org_id)]).supervisor.related_user.id
                str_sql = """ select b.related_user from oa_project_org a
                               inner join oa_staff_basic b on b.id=a.supervisor where a.id={0}"""
                self.env.cr.execute(str_sql.format(need_org_id))
                res_uid = self.env.cr.fetchone()
                manager_uid = res_uid[0]
            else:
                #如果角色不是项目经理(组长或普通员工),只记录manager_uid
                _group_manager_id=self.env['oa.project.role'].search([('name','=',u'项目经理')]).id
                #使用insert插入人员id
                str_sql = "select related_user from oa_staff_basic where project_id={0} and project_position={1}"
                #manager_uid=self.env['oa.staff.basic'].search([('project_id','=',need_org_id),('project_position','=',_group_manager_id)]).related_user.id
                self.env.cr.execute(str_sql.format(need_org_id,_group_manager_id))
                res_uid = self.env.cr.fetchone()
                manager_uid = res_uid[0]
            
        vals['leader_uid']=leader_uid
        vals['manager_uid']=manager_uid
        vals['double_validation']=double_validation
        return vals
    
    @api.model
    @api.returns('self', lambda value:value.id)
    def create(self, vals):
        if vals['staff_id']:
            project_id = self.env['oa.staff.basic'].search([('id','=',vals['staff_id'])]).project_id
            if project_id:
                #如果存在所属项目，则说明为不是中心主任
                vals['apply_date']=fields.date.today()
                vals['state']='submitted'
                if vals.has_key('holidays_type_id') and self.env['oa.holiday.type'].search([('id','=',vals['holidays_type_id'])]).type=='trip':
                    if not vals.has_key('address') or not vals['address']:
                        raise osv.except_osv('Warning!',"差旅地点不能为空！")
                self._save_super_uid(vals)
                #向上级发送通知
                new_id=super(holidays_trip,self).create(vals)
                return new_id
            else:
                #如果不存在所属项目，则说明为中心主任，只有保存功能即可
                new_id=super(holidays_trip,self).create(vals)
                return new_id
        else:
            raise osv.except_osv('Warning!',"没有对应的人员信息，请检查！")
        
    #更新消息状态
    def update_message_state(self,res_id,msg,subject,record_name,partner_id,is_read):
        message_id=self.env['mail.message'].search([('model','=','oa.holidays.trip'),('res_id','=',res_id),('type','=','comment'),('parent_id','=',False)]).id
        if message_id:
            new_author_id=self.env['res.users'].search([('id','=',self.env.uid)]).partner_id.id
            sql_update_mess=u'update mail_message set body=\'{0}\',subject=\'{1}\',record_name=\'{2}\',author_id={3} where id = {4}'.format(msg,subject,record_name,new_author_id,message_id)
            self.env.cr.execute(sql_update_mess)
            sql_update_noti=u'update mail_notification set partner_id={0},is_read={1} where message_id = {2}'.format(partner_id,is_read,message_id)
            self.env.cr.execute(sql_update_noti)
            sql_update_rel=u'update mail_message_res_partner_rel set res_partner_id={0} where mail_message_id = {1}'.format(partner_id,message_id)
            self.env.cr.execute(sql_update_rel)
        else:
            if self.double_validation:
                partner_ids = list(set(u.partner_id.id for u in self.env['res.users'].browse([self.leader_uid])))
            else:
                partner_ids = list(set(u.partner_id.id for u in self.env['res.users'].browse([self.manager_uid])))    
            openerp.noti_message.insert_message(res_id,self,[],msg,record_name,subject,partner_ids)    
    
    #工作流到达草稿状态执行的动作
    def state_reset(self):
        #判断是新建保存还是return
        if self.state in ['submitted','returned2']:
            self.write({'state':'returned1'})
            #向申请人发送消息
            apply_type=self.env['oa.holiday.type'].search([('id','=',self.holidays_type_id.id)]).name
            msg= (u"{0}申请{1}到{2} {3}被退回，请前去查看").format(self.staff_name,self.apply_start_date,self.apply_end_date,apply_type)
            subject=u"点击查看"
            record_name=(u"{0} {1}到{2} {3}申请被退回").format(self.staff_name,self.apply_start_date,self.apply_end_date,apply_type)
            staff_uid=self.env['oa.staff.basic'].search([('id','=',self.staff_id.id)]).related_user.id
            partner_id = self.env['res.users'].browse([staff_uid]).partner_id.id
            self.update_message_state(self.id,msg,subject,record_name,partner_id,False)
            
    #工作流到达已提交状态执行的动作
    def submit(self):
        if self.state in ['submitted','returned1']:
            self.write({'state':'submitted'})
            if self.double_validation:
                #向上级发送消息
                apply_type=self.env['oa.holiday.type'].search([('id','=',self.holidays_type_id.id)]).name
                msg= (u"{0}申请{1}到{2} {3}，请前去审批").format(self.staff_name,self.apply_start_date,self.apply_end_date,apply_type)
                subject=u"点击审批"
                record_name=(u"{0} {1}到{2} {3}申请").format(self.staff_name,self.apply_start_date,self.apply_end_date,apply_type)
                partner_id = self.env['res.users'].browse([self.leader_uid]).partner_id.id
                if partner_id:    
                    self.update_message_state(self.id,msg,subject,record_name,partner_id,False)
            else:
                #向上级发送消息
                apply_type=self.env['oa.holiday.type'].search([('id','=',self.holidays_type_id.id)]).name
                msg= (u"{0}申请{1}到{2} {3}，请前去审批").format(self.staff_name,self.apply_start_date,self.apply_end_date,apply_type)
                subject=u"点击审批"
                record_name=(u"{0} {1}到{2} {3}申请").format(self.staff_name,self.apply_start_date,self.apply_end_date,apply_type)
                partner_id = self.env['res.users'].browse([self.manager_uid]).partner_id.id   
                if partner_id:
                    self.update_message_state(self.id,msg,subject,record_name,partner_id,False)
                   
        if self.state=='first_accepted':
            self.write({'state':'returned2'})
            #向一级审批人发送消息
            apply_type=self.env['oa.holiday.type'].search([('id','=',self.holidays_type_id.id)]).name
            msg= (u"{0}申请{1}到{2} {3}被退回，请前去查看").format(self.staff_name,self.apply_start_date,self.apply_end_date,apply_type)
            subject=u"点击查看"
            record_name=(u"{0} {1}到{2} {3}申请被退回").format(self.staff_name,self.apply_start_date,self.apply_end_date,apply_type)
            partner_id = self.env['res.users'].browse([self.leader_uid]).partner_id.id    
            self.update_message_state(self.id,msg,subject,record_name,partner_id,False)
            
    #工作流到达一级已审批状态执行的动作
    def first_accept(self):
        self.write({'state':'first_accepted'})
        #向上级发送消息
        apply_type=self.env['oa.holiday.type'].search([('id','=',self.holidays_type_id.id)]).name
        leader_name=self.env['oa.staff.basic'].search([('related_user','=',self.leader_uid)]).name
        msg= (u"{0}通过了{1}{2}到{3} {4}申请，请前去审批").format(leader_name,self.staff_name,self.apply_start_date,self.apply_end_date,apply_type)
        subject=u"点击审批"
        record_name=(u"{0}通过了{1} {2}到{3} {4}申请").format(leader_name,self.staff_name,self.apply_start_date,self.apply_end_date,apply_type)
        partner_id = self.env['res.users'].browse([self.manager_uid]).partner_id.id    
        if partner_id:
            self.update_message_state(self.id,msg,subject,record_name,partner_id,False)
    
    #工作流到达审批通过状态执行的动作
    def last_accept(self):
        self.write({'state':'last_accepted'})
        apply_type=self.env['oa.holiday.type'].search([('id','=',self.holidays_type_id.id)]).name
        msg= (u"{0}申请{1}到{2} {3}通过，请前去销假").format(self.staff_name,self.apply_start_date,self.apply_end_date,apply_type)
        subject=u"点击查看"
        record_name=(u"{0} {1}到{2} {3}申请通过").format(self.staff_name,self.apply_start_date,self.apply_end_date,apply_type)
        staff_uid=self.env['oa.staff.basic'].search([('id','=',self.staff_id.id)]).related_user.id
        partner_id = self.env['res.users'].browse([staff_uid]).partner_id.id    
        self.update_message_state(self.id,msg,subject,record_name,partner_id,False)
    
    #流程到达拒绝状态执行的动作
    def refuse(self):
        self.write({'state':'refused'})
        #向申请人发送消息
        apply_type=self.env['oa.holiday.type'].search([('id','=',self.holidays_type_id.id)]).name
        msg= (u"{0}申请{1}到{2} {3}被拒绝，请前去查看").format(self.staff_name,self.apply_start_date,self.apply_end_date,apply_type)
        subject=u"点击查看"
        record_name=(u"{0} {1}到{2} {3}申请被拒绝").format(self.staff_name,self.apply_start_date,self.apply_end_date,apply_type)
        staff_uid=self.env['oa.staff.basic'].search([('id','=',self.staff_id.id)]).related_user.id
        partner_id = self.env['res.users'].browse([staff_uid]).partner_id.id        
        self.update_message_state(self.id,msg,subject,record_name,partner_id,False)
    
    #流程到达销假状态执行的动作
    def resumpt(self):
        self.write({'state':'resumpted'})
        #向申请人发送消息
        apply_type=self.env['oa.holiday.type'].search([('id','=',self.holidays_type_id.id)]).name
        msg= (u"{0}申请{1}到{2} {3}已经销假，请前去确认").format(self.staff_name,self.apply_start_date,self.apply_end_date,apply_type)
        subject=u"点击查看"
        record_name=(u"{0} {1}到{2} {3}申请已经销假").format(self.staff_name,self.apply_start_date,self.apply_end_date,apply_type)
        partner_id = self.env['res.users'].browse([self.manager_uid]).partner_id.id        
        self.update_message_state(self.id,msg,subject,record_name,partner_id,False)
    
    #流程到达确认状态执行的动作
    def validated(self):
        self.write({'state':'validated'})
        #向项目经理发送确认销假消息
        apply_type=self.env['oa.holiday.type'].search([('id','=',self.holidays_type_id.id)]).name
        msg= (u"{0}申请{1}到{2} {3}已经确认").format(self.staff_name,self.apply_start_date,self.apply_end_date,apply_type)
        subject=u"点击查看"
        record_name=(u"{0} {1}到{2} {3}申请已经确认").format(self.staff_name,self.apply_start_date,self.apply_end_date,apply_type)
        partner_id = self.env['res.users'].browse([self.manager_uid]).partner_id.id        
        if partner_id:
            self.update_message_state(self.id,msg,subject,record_name,partner_id,True)
               
    # 获取时长
    @api.depends('apply_start_date', 'apply_end_date','real_start_date','real_end_date')
    def _get_holidays_duration(self):        
        DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
        if self.apply_start_date and self.apply_end_date:
            from_dt = datetime.datetime.strptime(self.apply_start_date, DATETIME_FORMAT)
            to_dt = datetime.datetime.strptime(self.apply_end_date, DATETIME_FORMAT)
            if to_dt <= from_dt:
                raise osv.except_osv('Warning!',"申请开始时间不能早于结束时间！")
            else:
                timedelta = to_dt - from_dt
                seconds = timedelta.total_seconds()
                #diff_days = timedelta.days
                #diff_hours = round((timedelta.total_seconds() - diff_days * 24 * 60 * 60) / 3600, 0)
                if timedelta:
                    if seconds >= 4*60*60:
                        self.holidays_duration = str(timedelta.days + 1)+' 天'
                    if seconds > 0 and seconds < 4*60*60:
                        self.holidays_duration = '0.5 天'       
        else:
            self.holidays_duration = '0 天 ' 
        #实际请假时长
        if self.real_start_date and self.real_end_date:
            real_from_dt = datetime.datetime.strptime(self.real_start_date, DATETIME_FORMAT)
            real_to_dt = datetime.datetime.strptime(self.real_end_date, DATETIME_FORMAT)
            if real_to_dt < real_from_dt:
                raise osv.except_osv('Warning!',"实际申请开始时间不能早于实际结束时间！")
            else:
                real_timedelta = real_to_dt - real_from_dt
                real_seconds = real_timedelta.total_seconds()
                #real_diff_days = real_timedelta.days
                #real_diff_hours = round((real_timedelta.total_seconds() - real_diff_days * 24 * 60 * 60) / 3600, 0)
                if real_seconds:
                    if real_seconds >= 4*60*60:
                        self.real_holidays_duration = str(real_timedelta.days + 1)+' 天'
                    if real_seconds > 0 and real_seconds < 4*60*60:
                        self.real_holidays_duration = '0.5 天'        
        else:
            self.real_holidays_duration = '0 天 '     
    
    def get_holi_noti(self, cr, uid, partner_id, context=None):
        noti_obj=self.pool.get('mail.notification')
        ids=noti_obj.search(cr,uid,[('partner_id','=',partner_id),('message_id.model','=','oa.holidays.trip')],context=context)
        if ids:
            return {'hasValue':'yes'}
        else:
            return {'hasValue':'no'}
    
    def get_res_id(self, cr, uid, message_id, context=None):
        message_obj=self.pool.get('mail.message')
        ids=message_obj.search(cr,uid,[('id','=',message_id)],context=context)
        res_id=message_obj.browse(cr, uid,ids, context).res_id
        return {'res_id':res_id}

class oa_holidays_scheduler(osv.osv):
    _auto = False
    _name = "oa.holidays.scheduler"

    def run_scheduler(self, cr, uid, args,context=None):
        #如果差旅修改三天还未审批，默认通过
        today = fields.datetime.now()
        holi_type_obj = self.pool.get('oa.holiday.type')
        staff_obj = self.pool.get('oa.staff.basic')        
        holi_obj = self.pool.get('oa.holidays.trip')
        holi_ids = holi_obj.search(cr, uid, [('state','=','submitted')], context=context)
        holi_res = holi_obj.browse(cr, uid, holi_ids, context)
        for r in holi_res:
            #查找当前记录对应的inst_id
            ins_sql = 'select id from wkf_instance where res_id=%d'%(r.id)
            cr.execute(ins_sql)
            ins_res = cr.fetchone()
            ins_id = ins_res[0]
            apply_date = fields.datetime.strptime(r.apply_date,'%Y-%m-%d')
            if (today - apply_date).days > 3:
                #申请日期超过三天，记录自动转为审批通过
                holi_obj.write(cr, uid, r.id, {'state':'last_accepted'}, context=context)
                
                type_ids = holi_type_obj.search(cr, uid, [('id','=',r.holidays_type_id.id)], context=context)
                apply_type = holi_type_obj.browse(cr, uid, type_ids, context=context).name
                msg= (u"{0}申请{1}到{2} {3}通过，请前去销假").format(r.staff_name,r.apply_start_date,r.apply_end_date,apply_type)
                subject=u"点击查看"
                record_name=(u"{0} {1}到{2} {3}申请通过").format(r.staff_name,r.apply_start_date,r.apply_end_date,apply_type)
                staff_ids = staff_obj.search(cr, uid, [('id','=',r.staff_id.id)], context=context)
                staff_uid = staff_obj.browse(cr, uid, staff_ids, context=context).related_user.id
                partner_id = self.pool.get('res.users').browse(cr, uid,[staff_uid], context=context).partner_id.id    
                r.update_message_state(r.id,msg,subject,record_name,partner_id,False)
                #更新wkf_workitem
                act_sql = """select id from wkf_activity where name='oa.holidays.act.last.accepted'"""
                cr.execute(act_sql)
                act_res = cr.fetchone()
                act_id = act_res[0]
                item_sql = 'update wkf_workitem set act_id=%d where inst_id=%d'%(act_id,ins_id)
                cr.execute(item_sql)
# 允许倒休天数记录表
class compensation_records(models.Model):
    _name = 'oa.compensation.records'
    _description = u"倒休记录(有几天可倒休)"
    
    staff_id = fields.Many2one('oa.staff.basic', '姓名', required=True)
    compensation_num = fields.Integer('授权倒休天数')
    compensation_reason = fields.Char('授权倒休原因')
    compensation_year=fields.Selection([('2014','2014'),('2015','2015'),('2016','2016'),('2017','2017'),('2018','2018'),('2019','2019'),('2020','2020'),('2021','2021')],'倒休年度',required=True)                             
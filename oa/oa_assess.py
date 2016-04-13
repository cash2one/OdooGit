# -*- coding: utf-8 -*-

from openerp import models, fields, api
import openerp
from openerp.osv.fields import datetime, related
from openerp.osv import osv
from openerp.fields import Date

# 月度考核表
class assess(models.Model):
    _name='oa.assess'
    #继承mail.thread(消息提醒用)
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description=u"月度考核"
    _sql_constraints = [
        ('unique_key', 'UNIQUE (staff_id,assess_year,assess_month)',  '已存在本月度考核 !')
    ]
        
    # 根据人员角色id获取角色名称
    @api.depends('staff_id')
    def _get_staff_role_name(self):
        if self.staff_id:
            _project_role_id=self.env['oa.staff.basic'].search([('id','=', self.staff_id.id)]).project_position
            if _project_role_id:
                self.staff_role_name=self.env['oa.project.role'].search([('id','=', _project_role_id.id)]).name
    
    # 根据用户id获取用户角色名称
    @api.depends('staff_id')
    def _get_user_role_name(self):
        uid= self.env.context['uid']
        #通过uid获取人员的project_role_id
        _role_id=self.env['oa.staff.basic'].search([('related_user','=',uid)]).project_position.id
        #通过_role_id获取角色名
        role_name=self.env['oa.project.role'].search([('id','=', _role_id)]).name
        self.user_role_name = role_name
    
    # 计算字段获取上级组织机构id，如果上级组织机构id不存在，赋值'null'
    @api.depends('staff_id')
    def _get_staff_parent_org_id(self):
        if self.staff_id:
            _project_org_id=self.env['oa.staff.basic'].search([('id','=', self.staff_id.id)]).project_id
            if _project_org_id:
                _pid= self.env['oa.project.org'].search([('id','=', _project_org_id.id)]).parent_id
                if _pid:
                    self.staff_parent_org_id = _pid.id              
                else:
                    self.staff_parent_org_id='null'
               
   
    #获取人员名
    @api.depends('staff_id')
    def _get_name_title(self):
        if self.staff_id:
            self.name = self.env['oa.staff.basic'].search([('id','=', self.staff_id.id)]).name + u'的考核'
    
    #获取所属科室
    @api.depends('staff_id')
    def _get_admin_org_name(self):
        if self.staff_id:
            _admin_org_id=self.env['oa.staff.basic'].search([('id','=', self.staff_id.id)]).vld_site
            if _admin_org_id:
                self.admin_org_name=self.env['oa.admin.org'].search([('id','=', _admin_org_id.id)]).name
    
    #获取所属项目组
    @api.depends('staff_id')
    def _get_project_org_name(self):
        if self.staff_id:
            _project_org_id=self.env['oa.staff.basic'].search([('id','=', self.staff_id.id)]).project_id
            if _project_org_id:
                self.project_org_name=self.env['oa.project.org'].search([('id','=', _project_org_id.id)]).name
    
    #获取外协公司名
    @api.depends('staff_id')
    def _get_outsourcing_org_name(self):
        if self.staff_id:
            _outsourcing_org_id=self.env['oa.staff.basic'].search([('id','=', self.staff_id.id)]).outsourcing_org_id
            if _outsourcing_org_id:
                self.outsourcing_name=self.env['oa.outsourcing.org'].search([('id','=', _outsourcing_org_id.id)]).name
    
    #获取技术等级
    @api.depends('staff_id')
    def _get_technology_level(self):
        if self.staff_id:
            self.technology_level=self.env['oa.staff.basic'].search([('id','=', self.staff_id.id)]).technical_grade
    
    #获取人员id
    def _get_staff_id(self):
        uid= self.env.context['uid']
        staff_obj=self.env['oa.staff.basic'].search([('related_user','=',uid)])
        staff_id=''
        if staff_obj:
            staff_id=self.env['oa.staff.basic'].search([('related_user','=',uid)]).id
        else:
            staff_id=''
        return staff_id
    
    #获取用户id
    def _get_uid(self):
        self.user_id=self.env.uid 
    
    #获取用户名
    def _get_user_name(self):
        uid= self.env.context['uid']
        staff_obj=self.env['oa.staff.basic'].search([('related_user','=',uid)])
        user_name=''
        if staff_obj:
            user_name=staff_obj.name
        else:
            user_name=self.env['res.users'].search([('id','=',uid)]).partner_id.name
        return user_name
    
    #获取人员用工性质
    @api.depends('staff_id')
    def _get_staff_type(self):
        if self.staff_id:
            self.staff_type=self.env['oa.staff.basic'].search([('id','=', self.staff_id.id)]).staff_type
    
    #则默认显示考核人和考核时间
    @api.depends('staff_id','project_assess_person','admin_assess_person')
    def _get_default_assess_info(self):
        if self.staff_id:
            if self.project_assess_person:
                self.project_assess_person_comp=self.project_assess_person
                self.project_assess_date_comp=self.project_assess_date
            else:    
                uid= self.env.context['uid']
                staff_obj=self.env['oa.staff.basic'].search([('id','=',self.staff_id.id)])
                if uid != staff_obj.related_user.id:
                    #获取当前用户角色
                    user_staff_obj=self.env['oa.staff.basic'].search([('related_user','=',uid)])
                    user_prole_id=user_staff_obj.project_position.id
                    user_role_name=self.env['oa.project.role'].browse([user_prole_id]).name
                    if user_role_name==u"组长":
                        self.project_assess_person_comp=user_staff_obj.name
                        self.project_assess_date_comp=datetime.now()
            if self.admin_assess_person:
                self.admin_assess_person_comp=self.admin_assess_person
                self.admin_assess_date_comp=self.admin_assess_date
            else:    
                uid= self.env.context['uid']
                staff_obj=self.env['oa.staff.basic'].search([('id','=',self.staff_id.id)])
                if uid != staff_obj.related_user.id:
                    #获取当前用户角色
                    user_staff_obj=self.env['oa.staff.basic'].search([('related_user','=',uid)])
                    user_prole_id=user_staff_obj.project_position.id
                    user_role_name=self.env['oa.project.role'].browse([user_prole_id]).name
                    if user_role_name==u"项目经理":
                        self.admin_assess_person_comp=user_staff_obj.name
                        self.admin_assess_date_comp=datetime.now()           
    
    #如果为3 6 9 12 则返回1，其他返回0
    @api.depends('assess_month')
    def _get_month_type(self):
        _month=self.assess_month
        if _month=='3' or _month=='6' or _month=='9' or _month=='12':
            self._month_type=True
        else:
            self._month_type=False    

    def _get_is_same(self):
        self.is_same=False
        if self.env.uid==self.staff_id.related_user.id:
            self.is_same=True
            
    
    staff_id=fields.Many2one('oa.staff.basic',string='姓名',default=_get_staff_id)
    staff_name=fields.Char('姓名',default=_get_user_name)
    related_user=fields.Many2one(related='staff_id.project_position',string='人员角色id')
    admin_org_name= fields.Char(compute='_get_admin_org_name', string='所属科室')
    project_org_name= fields.Char(compute='_get_project_org_name', string='所属项目组')
    outsourcing_name=fields.Char(compute='_get_outsourcing_org_name',string='外协公司')
    technology_level=fields.Char(compute='_get_technology_level',string='技术等级')
    assess_year=fields.Selection([('2014','2014'),('2015','2015'),('2016','2016'),('2017','2017'),('2018','2018'),('2019','2019'),('2020','2020'),('2021','2021')],'考核年度',required=True)
    assess_month=fields.Selection([('1','1'),('2','2'),('3','3'),('4','4'),('5','5'),('6','6'),('7','7'),('8','8'),('9','9'),('10','10'),('11','11'),('12','12')],'考核月度',required=True)
    work_complete=fields.Text('本月完成工作', required=True)
    work_nextmonth=fields.Text('下月工作计划', required=True)
    project_suggest=fields.Text('考核意见')
    project_scores=fields.Float('考核分值')
    project_sug_level=fields.Selection([('A','A'),('B','B'),('C','C'),('D','D')],'建议考核档级')
    project_tec_level=fields.Selection([('H1','H1'),('H2','H2'),('H3','H3'),('H4','H4'),('H5','H5'),('H6','H6')],'建议技术等级')
    project_assess_date=fields.Date('考核日期')
    project_assess_date_comp=fields.Date(compute='_get_default_assess_info',string='考核日期')
    project_assess_person=fields.Char('考核人')
    project_assess_person_comp=fields.Char(compute='_get_default_assess_info',string='考核人')
    admin_suggest=fields.Text('考核意见')
    admin_scores=fields.Float('考核分值')
    admin_tec_level=fields.Selection([('H1','H1'),('H2','H2'),('H3','H3'),('H4','H4'),('H5','H5'),('H6','H6')],'技术等级')
    admin_sug_level=fields.Selection([('A','A'),('B','B'),('C','C'),('D','D')],'考核档级')
    admin_assess_date=fields.Date('考核日期')
    admin_assess_date_comp=fields.Date(compute='_get_default_assess_info',string='考核日期')
    admin_assess_person=fields.Char('考核人')
    admin_assess_person_comp=fields.Char(compute='_get_default_assess_info',string='考核人')
    related_user=fields.Many2one(related='staff_id',relation='oa.staff.basic', string='User', store=True)
    user_id=fields.Char(compute='_get_uid',string='用户id')
    leader_uid=fields.Integer('上级组长id') 
    manager_uid=fields.Integer('项目经理考核人id')           
    #考核人员的角色名
    staff_role_name=fields.Char(compute='_get_staff_role_name',string='项目岗位')
    #用户的角色名
    user_role_name=fields.Char(compute='_get_user_role_name',string='用户项目角色')
    #考核人员的上级项目组
    staff_parent_org_id=fields.Char(compute='_get_staff_parent_org_id',string='考核人员上级项目组')
    #用户的
    name=fields.Char(compute='_get_name_title',string='考核人员姓名',default='人员考核')
    #用工形式
    staff_type=fields.Char(compute='_get_staff_type',string='用工形式')
    #当前月份类型
    _month_type=fields.Boolean(compute='_get_month_type',string='考核月')
    is_same = fields.Boolean(compute='_get_is_same', string='是否创建者')
    
    # 字段根据人员id进行联动变化
    @api.onchange('staff_id')
    def _check_change(self):
        if self.staff_id:
            _admin_org_id=self.env['oa.staff.basic'].search([('id','=', self.staff_id.id)]).vld_site
            if _admin_org_id:
                self.admin_org_name=self.env['oa.admin.org'].search([('id','=', _admin_org_id.id)]).name
            _project_org_id=self.env['oa.staff.basic'].search([('id','=', self.staff_id.id)]).project_id
            if _project_org_id:
                self.project_org_name=self.env['oa.project.org'].search([('id','=', _project_org_id.id)]).name
            _outsourcing_org_id=self.env['oa.staff.basic'].search([('id','=', self.staff_id.id)]).outsourcing_org_id
            if _outsourcing_org_id:
                self.outsourcing_name=self.env['oa.outsourcing.org'].search([('id','=', _outsourcing_org_id.id)]).name
            _project_role_id=self.env['oa.staff.basic'].search([('id','=', self.staff_id.id)]).project_position
            if _project_role_id:
                self.staff_role_name=self.env['oa.project.role'].search([('id','=', _project_role_id.id)]).name
            self.technology_level=self.env['oa.staff.basic'].search([('id','=', self.staff_id.id)]).technical_grade
            self.staff_type=self.env['oa.staff.basic'].search([('id','=', self.staff_id.id)]).staff_type
    
    #在create方法中调用，vals中增加对应字段
    def _save_super_uid(self,vals):
        #获取用户项目角色名
        uid= self.env.context['uid']
        _role_id=self.env['oa.staff.basic'].search([('related_user','=',uid)]).project_position.id
        _role_name=self.env['oa.project.role'].search([('id','=', _role_id)]).name
        #获取用户项目组织机构名(是否由上级单位)
        _org_id=self.env['oa.staff.basic'].search([('related_user','=',uid)]).project_id.id
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
                leader_uid=uid
                _group_manager_id=self.env['oa.project.role'].search([('name','=','项目经理')]).id
                #manager_uid=self.env['oa.staff.basic'].search([('project_id','=',need_org_id),('project_position','=',_group_manager_id)]).related_user.id
                str_sql = "select related_user from oa_staff_basic where project_id={0} and project_position={1}"
                self.env.cr.execute(str_sql.format(need_org_id,_group_manager_id))
                res_uid = self.env.cr.fetchone()
                manager_uid = res_uid[0]
            # 普通成员(寻找相同单位的组长)
            else:
                # 获取组长的rold_id
                _group_leader_id=self.env['oa.project.role'].search([('name','=','组长')]).id
                _group_manager_id=self.env['oa.project.role'].search([('name','=','项目经理')]).id
                leader_uid=self.env['oa.staff.basic'].search([('project_id','=',_org_id),('project_position','=',_group_leader_id)]).related_user.id
                manager_uid=self.env['oa.staff.basic'].search([('project_id','=',need_org_id),('project_position','=',_group_manager_id)]).related_user.id   
        # 上级单位为根单位
        else:
            # 上级单位为根单位
            _group_manager_id=self.env['oa.project.role'].search([('name','=','项目经理')]).id
            manager_uid=self.env['oa.staff.basic'].search([('project_id','=',need_org_id),('project_position','=',_group_manager_id)]).related_user.id   
        vals['leader_uid']=leader_uid
        vals['manager_uid']=manager_uid
        return vals
    
    #返回需要提醒的上级用户
    def _notify_uids(self):
        #获取用户项目角色名
        uid= self.env.context['uid']
        _role_id=self.env['oa.staff.basic'].search([('related_user','=',uid)]).project_position.id
        _role_name=self.env['oa.project.role'].search([('id','=', _role_id)]).name
        #获取用户项目组织机构名(是否由上级单位)
        _org_id=self.env['oa.staff.basic'].search([('related_user','=',uid)]).project_id.id
        _pid= self.env['oa.project.org'].search([('id','=', _org_id)]).parent_id
        need_org_id=0
        if _pid:
            need_org_id=_pid.id
        else:
            need_org_id=_org_id
        #获取需要发送信息的所有上级用户
        user_ids=[]
        # 上级单位不是根单位
        if _pid:
            # 组长
            if _role_name==u"组长":
                _group_leader_id=self.env['oa.project.role'].search([('name','=','项目经理')]).id
                #staff_ids=self.env['oa.staff.basic'].search([('project_id','=',need_org_id),('project_position','=',_group_leader_id)]).ids
                str_sql = "select related_user from oa_staff_basic where project_id={0} and project_position={1}"
                self.env.cr.execute(str_sql.format(need_org_id,_group_leader_id))
                #res_uid = self.env.cr.fetchall()
                for row in self.env.cr.fetchall():
                    user_ids.append(row[0])
            # 普通成员(寻找相同单位的组长)
            else:
                # 获取组长的role_id
                _group_leader_id=self.env['oa.project.role'].search([('name','=','组长')]).id
                #staff_ids=self.env['oa.staff.basic'].search([('project_id','=',_org_id),('project_position','=',_group_leader_id)]).ids 
                str_sql = "select related_user from oa_staff_basic where project_id={0} and project_position={1}"
                self.env.cr.execute(str_sql.format(_org_id,_group_leader_id))
                #res_uid = self.env.cr.fetchall()
                for row in self.env.cr.fetchall():
                    user_ids.append(row[0])  
        # 上级单位为根单位
        else:
            # 上级单位为根单位
            _group_leader_id=self.env['oa.project.role'].search([('name','=','项目经理')]).id
            #staff_ids=self.env['oa.staff.basic'].search([('project_id','=',need_org_id),('project_position','=',_group_leader_id)]).ids  
            str_sql = "select related_user from oa_staff_basic where project_id={0} and project_position={1}"
            self.env.cr.execute(str_sql.format(need_org_id,_group_leader_id))
            #res_uid = self.env.cr.fetchall()
            for row in self.env.cr.fetchall():
                user_ids.append(row[0])   
        
        #user_ids=list(set(u.related_user.id for u in self.env['oa.staff.basic'].browse(staff_ids))) 
        return user_ids
       
    #创建时向上级添加提醒
    @api.model
    @api.returns('self', lambda value:value.id)
    def create(self, vals):
        if vals['staff_id']:
            #写入人员的技术等级
            tec_level=self.env['oa.staff.basic'].search([('id','=', vals['staff_id'])]).technical_grade
            vals['project_tec_level']=tec_level
            vals['admin_tec_level']=tec_level
            vals=self._save_super_uid(vals)
            new_id=super(assess,self).create(vals)
            #获取人员名
            staff_obj=self.env['oa.staff.basic']
            staff_name=staff_obj.browse([vals['staff_id']]).name
            msg= (u"{0}已经完成{1}月度考核报告，请前去审批").format(staff_name,vals['assess_month'])
            subject=u"点击审核 "
            record_name=(u"{0}{1}月度考核").format(staff_name,vals['assess_month'])
            user_ids=self._notify_uids()
            res_users=self.env['res.users']
            #获取partner_ids
            partner_ids = list(set(u.partner_id.id for u in res_users.browse(user_ids)))
            openerp.noti_message.insert_message(new_id,self,vals,msg,record_name,subject,partner_ids)
            return new_id 
        else:
            raise osv.except_osv('Warning!',"没有对应的人员信息，请检查！")
    
    @api.multi
    def write(self, vals):
        #获取用户项目角色名
        uid= self.env.context['uid']
        _role_name=self.env['oa.staff.basic'].search([('related_user','=',uid)]).project_position.name
        res_users=self.env['res.users']
        staff_uid=self.env['oa.staff.basic'].search([('id','=',self.staff_id.id)]).related_user.id
        user_part_id=res_users.search([('id','=',uid)]).partner_id.id
        author_id=res_users.search([('id','=',staff_uid)]).partner_id.id
        if _role_name==u"组长":
            #用于判断是否发送过消息
            is_send_mess_id=self.env['mail.message'].search([('res_id','=',self.id),('author_id','=',user_part_id),('type','=','comment')]).id
            #获取用户项目组织机构名(是有上级单位)
            _org_id=self.env['oa.staff.basic'].search([('related_user','=',uid)]).project_id.id
            _pid= self.env['oa.project.org'].search([('id','=', _org_id)]).parent_id
            if _pid and not is_send_mess_id:
                u_name=self.env['oa.staff.basic'].search([('related_user','=',uid)]).name
                staff_name=self.env['oa.staff.basic'].search([('id','=',self.staff_id.id)]).name
                msg= (u"{0}已经完成{1}{2}的月度考核审核，请前去审批").format(u_name,staff_name,self.assess_month)
                subject=u"点击审核 "
                record_name=(u"{0}{1}月度考核").format(staff_name,self.assess_month)
                #staff_ids=self.env['oa.staff.basic'].search([('project_id','=',_pid.id)]).ids
                #user_ids=list(set(u.related_user.id for u in self.env['oa.staff.basic'].browse(staff_ids))) 
                user_ids = []
                str_sql = "select a.related_user from oa_staff_basic a inner join oa_project_role b on a.project_position=b.id where project_id={0} and b.name='项目经理'"
                self.env.cr.execute(str_sql.format(_pid.id))
                #res_uid = self.env.cr.fetchall()
                for row in self.env.cr.fetchall():
                    user_ids.append(row[0])        
            
                #获取partner_ids
                partner_ids = list(set(u.partner_id.id for u in res_users.browse(user_ids)))
                openerp.noti_message.insert_message(self.id,self,vals,msg,record_name,subject,partner_ids)
                
                #修改接收到的消息状态
                mess_id=self.env['mail.message'].search([('res_id','=',self.id),('author_id','=',author_id),('type','=','comment')]).id
                sql_update_state='update mail_notification set is_read=True where message_id={0} and partner_id={1}'.format(mess_id,user_part_id)
                self.env.cr.execute(sql_update_state)
        if _role_name==u"项目经理":
            #修改接收到的消息状态
            _role_name=self.env['oa.staff.basic'].search([('related_user','=',staff_uid)]).project_position.id
            #获取用户项目组织机构名(是否有上级单位)
            _org_id=self.env['oa.staff.basic'].search([('related_user','=',staff_uid)]).project_id.id
            _pid= self.env['oa.project.org'].search([('id','=', _org_id)]).parent_id
            # 上级单位不是根单位
            if _pid:
                # 组长
                if _role_name!=u"组长":
                    # 获取组长的rold_id
                    _group_leader_id=self.env['oa.project.role'].search([('name','=','组长')]).id
                    related_user=self.env['oa.staff.basic'].search([('project_id','=',_org_id),('project_position','=',_group_leader_id)]).related_user.id
                    author_id=author_id=res_users.search([('id','=',related_user)]).partner_id.id 
            mess_id=self.env['mail.message'].search([('res_id','=',self.id),('author_id','=',author_id),('type','=','comment')]).id            
            sql_update_state='update mail_notification set is_read=True where message_id={0} and partner_id={1}'.format(mess_id,user_part_id)
            self.env.cr.execute(sql_update_state)  
                                          
        #将默认值存入  vals 
        if self.project_assess_person_comp:          
            vals['project_assess_person']=self.project_assess_person_comp
            vals['project_assess_date']=self.project_assess_date_comp
        if self.admin_assess_person_comp:
            vals['admin_assess_person']=self.admin_assess_person_comp
            vals['admin_assess_date']=self.admin_assess_date_comp
                         
        return models.Model.write(self, vals)
    
    #非空限制    
    @api.multi
    @api.constrains('project_suggest','project_scores','project_tec_level','project_sug_level','admin_suggest','admin_scores','admin_tec_level','admin_sug_level')
    def _check_null(self):
        #进行非空验证
        #1.组长考核
        uid= self.env.context['uid']
        staff_obj=self.env['oa.staff.basic'].search([('id','=',self.staff_id.id)])
        if uid != staff_obj.related_user.id:
            #获取当前用户角色
            user_staff_obj=self.env['oa.staff.basic'].search([('related_user','=',uid)])
            user_prole_id=user_staff_obj.project_position.id
            user_role_name=self.env['oa.project.role'].browse([user_prole_id]).name
            if user_role_name==u"组长":
                #如果是外协员工
                if not self.project_suggest:
                    raise osv.except_osv('Warning!',"组长考核意见不能为空！")
                if not self.project_scores:
                    raise osv.except_osv('Warning!',"组长考核分值不能为0或空！")
                if not self.project_sug_level:
                    raise osv.except_osv('Warning!',"建议考核档级不能为空！")
                staff_type_temp=self.env['oa.staff.basic'].search([('id','=', self.staff_id.id)]).staff_type
                if staff_type_temp=='outsourcing':
                    if not self.project_tec_level:
                        raise osv.except_osv('Warning!',"建议技术等级不能为空！")
            if user_role_name==u"项目经理":
                #如果是外协员工
                if not self.admin_suggest:
                    raise osv.except_osv('Warning!',"项目经理考核意见不能为空！")
                if not self.admin_scores:
                    raise osv.except_osv('Warning!',"项目经理考核分值不能为0或空！")
                if not self.admin_sug_level:
                    raise osv.except_osv('Warning!',"建议考核档级不能为空！")
                staff_type_temp=self.env['oa.staff.basic'].search([('id','=', self.staff_id.id)]).staff_type
                if staff_type_temp=='outsourcing':
                    if not self.admin_tec_level:
                        raise osv.except_osv('Warning!',"建议技术等级不能为空！")
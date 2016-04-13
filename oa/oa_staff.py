# -*- coding: utf-8 -*-
##############################################################################
#    人员信息
#    Created on 2015年7月9日
#    @author: LY
#    Last edit on 2015年7月13日
#    Last edit by  LY
##############################################################################

import time
import logging

from openerp import models, fields,api,exceptions,SUPERUSER_ID

_logger = logging.getLogger(__name__)



class oa_staff_basic(models.Model):
    """
        人员基本信息表 
    """
    
    _name="oa.staff.basic"
    _description=u"人员基本信息"
    
    @api.depends('vld_site')
    def _get_top_vld_site(self):
        parent_site_id = self.vld_site
        while parent_site_id.parent_id:
            parent_site_id = parent_site_id.parent_id
        self.top_vld_site = parent_site_id
    
    name=fields.Char('姓名',size=10,required=True)
    gender=fields.Selection([('male', '男'), ('female', '女')], '性别',required=True,default='female')#,required=True
    birthday=fields.Date('出生日期')
    identify_id=fields.Char('身份证号',size=18,required=True)#,required=True
    avatar=fields.Binary('照片',searchable=False)
    staff_number=fields.Char('员工编号',size=200)
    phone_number=fields.Char('手机号码',size=12,required=True)#,required=True
    telephone_number=fields.Char('固定电话',size=13)
    office_room_number=fields.Char('办公室',size=15)
    email=fields.Char('电子邮箱',size=50,required=True)    #,required=True
    nationality=fields.Char('国籍',size=50)#,required=True
    nation=fields.Char('民族',size=10,required=True)#,required=True
    political_status=fields.Selection([('ccp_member','中共党员'),('ccp_pre_member','预备中共党员'),('league_member','共青团员'),('pre_league_member','预备共青团员'),('masses','群众'),('other','其它')],'政治面貌',required=True)#,required=True
    home_address=fields.Char('家庭住址',size=100,required=True)#,required=True
    emergency_contacter=fields.Char('紧急联系人',size=10,required=True)#,required=True
    emergency_contact_phone=fields.Char('紧急联系电话',required=True)#,required=True
    e_signature=fields.Binary(string=u'电子签名')
    #modify by liuhongtai 2016-03-23 改为必填          
    vld_site=fields.Many2one('oa.admin.org',string='所属单位',required=True)
    administrative_post_id=fields.Many2one('oa.admin.role',string='行政职务',required=True)      #.Integer()#
    staff_type=fields.Selection([('contract','合同化'),('marketization','市场化'),('outsourcing','外协')],'用工形式')
    outsourcing_org_id=fields.Many2one('oa.outsourcing.org','外协公司')     #.Integer()
    technical_grade=fields.Selection([('H1','H1'),('H2','H2'),('H3','H3'),('H4','H4'),('H5','H5'),('H6','H6')],'技术等级')
    hire_date=fields.Date('入职时间')
    working_state=fields.Selection([('on_duty','在职'),('off_duty','离职')],'在职状态')
    quit_time=fields.Date('离职时间')
    project_id=fields.Many2one('oa.project.org','所属项目')
    project_position=fields.Many2one('oa.project.role','项目岗位')
    project_position_start_time=fields.Date('任现职位开始时间')
    project_position_end_time=fields.Date('任职岗位结束时间')
              
    education_experience_id=fields.One2many('oa.education.experience','staff_id','教育经历')       
    training_experience_id=fields.One2many('oa.training.experience','staff_id','培训经历')
    work_experience_id=fields.One2many('oa.work.experience','staff_id','工作经历')
    certificate_info_id=fields.One2many('oa.certificate.info','staff_id','资质取证')
    staff_seniority=fields.Integer(u'工龄起始年份',size=4)
    
    related_user=fields.Many2one('res.users','关联用户')

    #added by liuhongtai 2016-02-27 获取员工的顶层所在单位
    top_vld_site = fields.Many2one('oa.admin.org',compute='_get_top_vld_site',sring='顶层所属单位',store=True, recursive=True)
    
    _sql_constraints = [
        ('phone_number_key', 'UNIQUE (phone_number)',  '手机号码已被注册 !'),
        ('email_key', 'UNIQUE (email)',  '电子邮箱已被注册 !')
    ]
        
    @api.model
    @api.returns('self', lambda value:value.id)
    def create(self, vals):
        """
        创建人员的同时向res.partner表和res.users表插入记录，同时获取user表的id，将二者进行关联
        """
        
        uid=self.env().context['uid']
        res_parter_rec=self.env['res.partner'].create({'name':vals['name'],'display_name':vals['name'],'image':vals['avatar'],'email':vals['email'],'mobile':vals['phone_number'],'notify_email':'always','active':True,'create_uid':uid,'customer':False})
        res_user_rec=self.env['res.users'].create({'login':vals['email'],'company_id':1,'partner_id':res_parter_rec.id,'alias_id':1,'create_uid':uid,'password_crypt':'$pbkdf2-sha512$19000$8T5HCAEAoDSGEML4Pydk7A$qF2EvrMXK4MLo/k1UOkEiGSjYz2UvEaejkeEA.CpO3t0rQt7h4h9GxfKkr6BAbqDAkt9iyz0MXUe9XvFj765EA'})
        vals['related_user']=res_user_rec.id
        return models.Model.create(self, vals)  
        
    @api.multi
    def write(self, vals):
        """
        如果更改姓名，同步更改res.partner表和res.users里对应的姓名和登陆名
        """
        parter_id=str(self.env['res.users'].search([('id','=',self.related_user.id)]).partner_id.id)
        if vals.get('name'):
            self.env.cr.execute('update res_partner set name = \''+vals['name']+'\',display_name = \''+vals['name']+'\' where id = '+parter_id)
            #self.env['res.users'].search([('id','=',self.related_user.id)]).write({'name':vals['name'],'display_name':vals['name']})  
        if vals.get('avatar'):
            self.env.cr.execute('update res_partner set image = \''+vals['avatar']+'\' where id = '+parter_id)
        if vals.get('phone_number'):
            self.env.cr.execute('update res_partner set mobile = \''+vals['phone_number']+'\' where id = '+parter_id)
        if vals.get('email'):   
            self.env['res.users'].search([('id','=',self.related_user.id)]).write({'login':vals['email']})
        if vals.get('working_state'):
            if vals.get('working_state') == 'off_duty':
                self.env['res.users'].search([('id','=',self.related_user.id)]).write({'active':False})
            if vals.get('working_state') == 'on_duty':
                self.env['res.users'].search([('id','=',self.related_user.id)]).write({'active':True})
        return models.Model.write(self, vals)       
         
    def unlink(self, cr, uid, ids, context=None):
        """
        删除人员时，同步删除与人员相关其它表的记录
        """
        
        user_ids=[]
        wizzard_ids=[]
        cpu_ids=[]      #change_password_user_ids
        res_partner_ids=[]
        res_users_model=self.pool.get('res.users')
        cpu_model=self.pool.get('change.password.user')     #change_user_passwor_model
        #根据员工id获取用户id
        for staff in self.browse(cr,uid,ids,context=context):
            if staff.related_user.id:
                user_ids.append(staff.related_user.id)
        #根据用户id获取change_password_user表内的id
        for cpu_id in cpu_model.search(cr,uid,[('user_id','in',user_ids)]):
            if cpu_id:
                cpu_ids.append(cpu_id)
        #根据change_password_user表内的id获取change_password_wizard的id
        for wizzard in cpu_model.browse(cr,uid,cpu_ids,context=context):
            if wizzard.id:
                wizzard_ids.append(wizzard.id)
        #根据用户id获取res_partner的id
        for user in res_users_model.browse(cr,uid,user_ids,context=context):
            if user.partner_id.id:
                res_partner_ids.append(user.partner_id.id) 
        if len(cpu_ids)>0:
            cpu_model.unlink(cr,uid,cpu_ids,context=context)               
        if len(wizzard_ids)>0:
            self.pool.get('change.password.wizard').unlink(cr,uid,wizzard_ids,context=context)        
        #通过模型的unlink方法无法删除user表内的记录，报关联错误，但可以直接在数据库内删除，因此采用直接执行sql语句的方法来做
        if len(user_ids) > 0:
            cr.execute('delete from res_users where id in '+str(user_ids).replace('[', '(').replace(']',')'))
        #res_users_model.unlink(cr,uid,user_ids,context=context)
        if len(res_partner_ids)>0:
            self.pool.get('res.partner').unlink(cr,uid,res_partner_ids,context=context)
        return models.Model.unlink(self, cr, uid, ids, context=context)      
    
    @api.onchange('identify_id')
    def _verify_identify_id(self):
        """
        字段发生改变时，对身份证位数进行 检查
        """
        
        warning={}
        if(self.identify_id):
            if(len(self.identify_id) != 18):                
                warning = {
                           'title': '提示',
                           'message' : '身份证号码位数不正确!'
                }
                #raise models.except_orm('error','not mentioned')
                return {'warning': warning, 'value': self.identify_id}
    
    @api.one
    @api.constrains('identify_id')
    def _verify_identify_id_on_save(self):
        """
        保存时对身份证位数进行检查
        """
        
        if self.identify_id and len(self.identify_id)!=18:
            raise exceptions.ValidationError('身份证号码位数不正确!')
        
    '''def copy(self, cr, uid, id, default=None, context=None):
        rec=self.browse(cr,uid,[id])
        rec.write({'email':(rec.email + u'-复制')})
        return super(oa_staff_basic, self).copy(cr, uid, id, default, context)
        #return models.Model.copy(self, cr, uid, id, default=default, context=context)'''



class oa_education_experience(models.Model):
    """
    员工教育经历表
    """
    
    _name="oa.education.experience"
    _description=u"教育经历"
    
    education_history=fields.Selection(
                                    [('shortcycle_courses','专科'),
                                    ('normal_courses','本科'),
                                    ('master','硕士研究生'),
                                    ('doctor','博士研究生')],'学历')
    education_degree=fields.Selection([('bachelor_degree','学士'),('master_degree','硕士'),('doctor_degree','博士')],'学位')
    education_start_time=fields.Date('开始日期')
    education_end_time=fields.Date('结束日期')
    education_note=fields.Char('备注',size=200)
    education_major=fields.Char('专业',size=50)
    staff_id=fields.Many2one('oa.staff.basic','员工姓名')

    
    
class oa_training_experience(models.Model):
    """
    培训经历表
    """
    
    _name="oa.training.experience"
    _description=u"培训经历"
    
    training_organization=fields.Char('培训机构',size=100)
    training_content=fields.Char('培训内容',size=200)
    training_start_time=fields.Date('开始日期')
    training_end_time=fields.Date('结束日期')
    training_note=fields.Char('备注',size=200)
    staff_id=fields.Many2one('oa.staff.basic','员工姓名')

    

class oa_work_experience(models.Model):
    """
    工作经历表
    """
    
    _name="oa.work.experience"
    _description=u"工作经历"
    
    work_organization=fields.Char('工作机构',size=100)
    work_position=fields.Char('职务',size=200)
    work_content=fields.Char('主要工作内容',size=200)
    work_start_time=fields.Date('开始日期')
    work_end_time=fields.Date('结束日期')
    work_note=fields.Char('备注',size=200)
    staff_id=fields.Many2one('oa.staff.basic','员工姓名')

    

class oa_certificate_info(models.Model):
    """
    员工证书信息
    """
    
    _name="oa.certificate.info"
    _description=u"资质及证书信息"
    
    certificate_name=fields.Char('证书名称',size=100)
    certificate_organization=fields.Char('发证单位',size=200)
    certificate_number=fields.Char('证书编号',size=100)
    certificate_get_time=fields.Date('发证日期')
    certificate_validity=fields.Integer('有效期限')
    staff_id=fields.Many2one('oa.staff.basic','员工姓名')



class oa_task(models.Model):
    """
    任务信息
    """
    _name='oa.task'
    _description=u'任务'
    _inherit = ['mail.thread'] #,'ir.needaction_mixin'
    
    name=fields.Char('任务名称',size=100)
    task_description=fields.Text('任务描述')
    task_creater=fields.Many2one('oa.staff.basic','发起人')
    task_leader=fields.Many2many('oa.staff.basic','负责人')
    task_teamer=fields.Many2many('oa.staff.basic','参与人')
    task_end_time=fields.Date('截止时间')
    task_priority=fields.Selection([('high_level1','非常紧急'),('high_level2','紧急'),('high_level3','普通')],'优先级')
    task_state=fields.Many2one('oa.task.state','状态',default=1)
    task_project=fields.Many2one('oa.project.org','所属项目') 
    task_user_role=fields.Integer(compute='_get_task_role',string=u'任务角色')    
  
    '''@api.model
    @api.returns('self', lambda value:value.id)
    def create(self, vals):
        if vals.get('task_teamer') and len(vals.get('task_teamer'))>0:
            vals['task_teamer']=[(6,0,vals['task_teamer'])]
        if vals.get('task_leader') and len(vals.get('task_leader'))>0:
            vals['task_leader']=[(6,0,vals['task_leader'])]
        vals['task_creater']=self.get_staff_id() 
        rid=models.Model.create(self, vals)
        self.message_post(self.env.cr,self.env.uid,[rid.id],body="测试创建消息",context=None)        
        #self.write_message(, uid, body, rid, attachment_ids)
        return models.Model.create(self, vals)'''
    
    def create(self, cr, uid, values, context=None):
        if values.get('task_teamer') and len(values.get('task_teamer'))>0:
            values['task_teamer']=[(6,0,values['task_teamer'])]
        if values.get('task_leader') and len(values.get('task_leader'))>0:
            values['task_leader']=[(6,0,values['task_leader'])]
        values['task_creater']=self.get_staff_id(cr,uid)             
        context['mail_create_nolog']=True;
        rid=super(oa_task, self).create(cr, uid, values, context=context)   
        bodys=u"%s 创建任务  %s" % (self.get_staff(cr, uid)[0].get('name'),values.get('name')) 
        self.message_post(cr,uid,[rid],body=bodys,partner_ids=self.notificate_staff(cr, uid, rid, context),context=context)
        return rid
    
    def write(self, cr, uid, ids, vals, context=None):        
        if vals.get('task_teamer') and len(vals.get('task_teamer'))>0:
            if vals.get('action') and vals['action'] == 'delStaff':
                vals['task_teamer']=[(3,vals['task_teamer'][0])]
                vals.pop('action')
            elif vals.get('action') and vals['action'] == 'addStaff':
                vals.pop('action')
                r=''
                for t in vals['task_teamer']:
                    vals['task_teamer']=[(4,t)]
                    r=super(oa_task, self).write(cr, uid, ids, vals, context=context)
                #vals['task_teamer']=[(4,vals['task_teamer'][0])]
                return r
            else:
                vals['task_teamer']=[(6,0,vals['task_teamer'])]
        if vals.get('task_leader') and len(vals.get('task_leader'))>0:
            if vals.get('action') and vals['action'] == 'delStaff':
                vals['task_leader']=[(3,vals['task_leader'][0])]
                vals.pop('action')
            else:                
                vals['task_leader']=[(6,0,vals['task_leader'])]
        if vals.get('task_creater'):
            vals.pop('task_creater')
        if vals.get('task_state'):        
            bodys=u"%s 将任务状态变更为  %s" % (self.get_staff(cr, uid)[0].get('name'),self.pool['oa.task.state'].search_read(cr,uid,[('id','=',vals.get('task_state'))],fields=['name'])[0].get('name'))    
            self.message_post(cr,uid,ids,body=bodys,partner_ids=self.notificate_staff(cr, uid, ids[0], context),context=None)    
        else:
            bodys=u"%s 更新了任务信息" % (self.get_staff(cr, uid)[0].get('name')) 
            self.message_post(cr,uid,ids,body=bodys,partner_ids=[],context=None)  
        res = super(oa_task, self).write(cr, uid, ids, vals, context=context)
        return res
    '''@api.multi
    def write(self, vals):
        if vals.get('task_teamer') and len(vals.get('task_teamer'))>0:
            if vals.get('action') and vals['action'] == 'delStaff':
                vals['task_teamer']=[(3,vals['task_teamer'][0])]
                vals.pop('action')
            elif vals.get('action') and vals['action'] == 'addStaff':
                vals.pop('action')
                r=''
                for t in vals['task_teamer']:
                    vals['task_teamer']=[(4,t)]
                    r=models.Model.write(self, vals)
                #vals['task_teamer']=[(4,vals['task_teamer'][0])]
                return r
            else:
                vals['task_teamer']=[(6,0,vals['task_teamer'])]
        if vals.get('task_leader') and len(vals.get('task_leader'))>0:
            if vals.get('action') and vals['action'] == 'delStaff':
                vals['task_leader']=[(3,vals['task_leader'][0])]
                vals.pop('action')
            else:
                vals['task_leader']=[(6,0,vals['task_leader'])]
        if vals.get('task_creater'):
            vals.pop('task_creater')     
                           
        return models.Model.write(self, vals)'''
    
    def get_staff_id(self,cr,uid):   
        related_user=self.pool['oa.staff.basic'].search(cr,uid,[('related_user','=',uid)])
        if len(related_user) == 0:
            raise exceptions.Warning(u'当前账户没有人员与之对应，请先添加人员并关联后再进行此操作。')
            return;
        return related_user[0]
    
    def get_staff(self,cr,uid):
        return self.pool['oa.staff.basic'].search_read(cr,uid,[('related_user','=',uid)])
    
    def get_partner_ids_by_staff_ids(self,cr,uid,ids):
        res = self.pool['oa.staff.basic'].search_read(cr, uid, [('id','in',ids)],fields=['related_user'],context=None)
        if res and len(res) > 0:
            if res != 0:
                uids=[]
                for elem in res:
                    uids.append(elem.get('id'))
                if len(uids)>0:  
                    pids=[]
                    for pid in self.pool['res.users'].search_read(cr, uid, [('id','in',uids)],fields=['partner_id'],context=None):
                        pids.append(pid.get('id'))
                        return pids

    def _get_task_role(self):
        """
        根据用户id判断用户在任务中的角色,从而控制字段的可编辑与否
        返回结果：1--任务创建者
         2--负责人
         3--执行人
        """
        if self.env.uid==1: 
            self.task_user_role=0
            return
        create_ids=[]
        for c in self.task_creater:
            if c.related_user.id:
                create_ids.append(c.related_user.id)
        if self.env.uid in create_ids:
            self.task_user_role=1
            return
        leader_ids=[]
        for l in self.task_leader:
            if l.related_user.id:
                leader_ids.append(l.related_user.id)
        if self.env.uid in leader_ids:
            self.task_user_role=2
            return
        self.task_user_role=3
    
    def _read_group_stage_ids(self, cr, uid, ids, domain, read_group_order=None, access_rights_uid=None, context=None):
        """
        重写model的方法，去除项目相关的内容，所有选项卡的fold设置为false；
        """
        access_rights_uid = access_rights_uid or uid
        stage_obj = self.pool.get('oa.task.state')
        order = stage_obj._order

        if read_group_order == 'task_state desc':
            order = "%s desc" % order
        stage_ids = stage_obj._search(cr, uid, [], order=order, access_rights_uid=access_rights_uid, context=context)
        result = stage_obj.name_get(cr, access_rights_uid, stage_ids, context=context)
        result.sort(lambda x,y: cmp(stage_ids.index(x[0]), stage_ids.index(y[0])))

        fold = {}
        for stage in stage_obj.browse(cr, access_rights_uid, stage_ids, context=context):
            fold[stage.id] = (stage.fold if ('fold' in stage.fields_get_keys()) else False) or False
        return result,fold
    
    _group_by_full = {
        'task_state': _read_group_stage_ids
    }
    
    def check_draggable(self,cr,uid,rid,new_group_id,old_group_id,context=None):
        """
        拖动任务时，检查是否可拖动，条件：
        1、任务执行者不可改变进度；
        2、任务负责人可以改变进度，但不能关闭任务
        3、任务创建人可关闭任务；
        4、已关闭任务不可重开
        """
        if old_group_id == 4:
            return False
        current_record=self.browse(cr,uid,[rid])
        if current_record.task_creater.related_user.id and current_record.task_creater.related_user.id == uid or uid == 1:
            return True;
        teamer_uids=[]
        for i in current_record.task_leader:
            teamer_uids.append(i.related_user.id)
        if len(teamer_uids) > 0 and uid in teamer_uids and new_group_id < 4:
            return True;
        return False;
    
    def write_message(self,cr,uid,body,rid,attachment_ids):
        new_id=self.message_post(cr,uid,[rid],body="%s"%(body),context=None)
        if attachment_ids and len(attachment_ids) > 0:        
            for attachment_id in attachment_ids:
                cr.execute('insert into message_attachment_rel(message_id, attachment_id) values(%s, %s)' %(new_id,attachment_id))
            #self.pool('mail.thread').search(cr,uid,[new_id]).write({'attachment_ids':attachment_ids});
        return new_id
    
    def read(self, cr, user, ids, fields=None, context=None, load='_classic_read'):
        val=models.Model.read(self, cr, user, ids, fields=fields, context=context, load=load)
        if(type(val) == dict):
            ids=val.get('message_ids')
            if(ids):
                m_val=self.pool['mail.message'].read(cr, user, ids,fields=['body','write_uid','write_date','attachment_ids']) 
            #if(m_val)
                val['messages']=m_val       
        return val

    def notificate_staff(self,cr,uid,ids,context=None):
        '''
    获取本条记录所涉及到的员工对应partner表内的id，用于工作提醒、通知等发出
        '''
        staff_to_notification=[]
        if(isinstance(ids,int)):
            res=self.search_read(cr, uid, [('id','=',ids)],context=context,fields=['task_creater','task_leader','task_teamer'])
            if res and len(res) > 0:
                res=res[0]
                temp=res.get('task_creater')
                if(temp):
                    staff_to_notification.append(temp[0])
                temp=res.get('task_leader')
                if(isinstance(temp, int)):
                    if(temp != 0):
                        staff_to_notification.append(temp)
                else:
                    for elem in temp:
                        staff_to_notification.append(elem)
                temp=res.get('task_teamer')
                if(isinstance(temp, int)):
                    if(temp != 0):
                        staff_to_notification.append(temp)
                else:
                    for elem in temp:
                        staff_to_notification.append(elem)
        staff_to_notification=list(set(staff_to_notification))
        temp=self.pool['oa.staff.basic'].search_read(cr, uid, [('id','in',staff_to_notification)],context=context,fields=['related_user'])
        user_ids=[]
        partner_ids=[]
        if(len(temp)>0):
            for elem in temp:
                user_ids.append(elem.get('related_user')[0])
        if(len(user_ids)>0):
            temp=self.pool['res.users'].search_read(cr, uid, [('id','in',user_ids)],fields=['partner_id'],context=context)    
            if temp and len(temp) > 0:
                for elem in temp:
                    partner_ids.append(elem.get('partner_id')[0])
        return partner_ids
        
    def unlink(self, cr, uid, ids, context=None):
        staff_to_notification=self.notificate_staff(cr, uid, ids, context)
        if len(staff_to_notification)>0:
            who=''
            if uid==1:
                who='超级管理员'
            else:
                who=self.get_staff(cr, uid)[0].get('name')
            whens=time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
            bodys=u"%s 于 %s时 删除任务  '%s'。" % (who,whens,self.search_read(cr,uid,[('id','=',ids)],fields=['name'])[0].get('name'))
            self.message_post(cr,uid,ids,body=bodys,partner_ids=staff_to_notification,context=context)       
        return models.Model.unlink(self, cr, uid, ids, context=context)
    
    def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
        #if view_type == 'form' or view_type == 'tree':
            #view_type = 'kanban'
        res=models.Model.fields_view_get(self, cr, uid, view_id=view_id, view_type=view_type, context=context, toolbar=toolbar, submenu=submenu)
        return res
    
    def delete_attachment(self,cr,uid,message_id,attach_id):        
        try:
            #附件有和消息已经结合时，先删除联合表里的信息
            if message_id:
                cr.execute('delete from message_attachment_rel where message_id = %s and attachment_id = %s' %(message_id,attach_id));
            cr.execute('delete from ir_attachment where id = %s' %(attach_id));
        except:
            return False
        return True
    
    '''@api.v7
    def create(self, cr, uid, vals, context=None):
        new_id = super(oa_task, self).create(cr, uid, vals, context=context)
        self.message_post(cr,uid,new_id,body="%s"%('任务已创建'),context=None)
        return new_id'''
    


class oa_task_type(models.Model):  
    """
    任务类型
    """ 
    _name='oa.task.type' 
    
    name=fields.Char('任务类型',required=True)    
    
    
    
class oa_task_state(models.Model):
    """
    任务状态,四种状态，待处理、推进中、已提交、已关闭
    """
    _name='oa.task.state'
    
    name=fields.Char('状态',required=True)
    next_state_id=fields.Many2one('oa.task.state','下一步',select=True)
    
    
    
class res_users(models.Model):
    """
    继承res_users模型，重写write方法，实现与人员的关联
    """
    
    _name = 'res.users'
    _inherit = ['res.users']
    
    def write(self, cr, uid, ids, values, context=None):
        """
        由于在修改人员时调用了res_users的write方法，因此如果再使用人员的write方法时，会触发无限循环，
        故此处直接用sql修改。
        但此处仍存在一个问题，即在修改人员信息的时候，同样也会触发本函数，导致人员表和partner表重复更新，通过什么方式来判断避免呢？
        """
        if not hasattr(ids, '__iter__'):
            ids = [ids]
        if ids == [uid]:
            for key in values.keys():
                if not (key in self.SELF_WRITEABLE_FIELDS or key.startswith('context_')):
                    break
            else:
                if 'company_id' in values:
                    user = self.browse(cr, SUPERUSER_ID, uid, context=context)
                    if not (values['company_id'] in user.company_ids.ids):
                        del values['company_id']
                uid = 1 # safe fields only, so we write as super-user to bypass access rights
        rec=self.browse(cr, uid, ids, context=context)
        rec_id=rec.id
        if values.has_key('login') and values['login']:
            cr.execute('update oa_staff_basic set email = \''+values['login']+'\' where related_user = '+str(rec_id))
            cr.execute('update res_partner set email = \''+values['login']+'\' where id = '+str(rec.partner_id.id))
        if values.has_key('name') and values['name']:
            cr.execute('update oa_staff_basic set name = \''+values['name']+'\' where related_user = '+str(rec_id))
            cr.execute('update res_partner set name = \''+values['name']+'\' ,display_name = \''+values['name']+'\' where id = '+str(rec.partner_id.id))      
        return super(res_users, self).write(cr, uid, ids, values, context=context)



#class view_test(self):
    
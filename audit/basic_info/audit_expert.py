# -*- coding: utf-8 -*-

from openerp import models, fields, api
from docutils.nodes import title

class audit_expert_info(models.Model):
    _name = 'audit.expert.info'
    _description = u"专家个人信息表"
    
    
    vld_site = fields.Many2one('audit.vld.site', related='name.site_id', required=True, string='单位')
    workstation = fields.Many2one('sys.constant', domain=[('type','=','audit_org')], string=u'工作站')
    sex = fields.Selection([('male',u'男'),('fmale',u'女')], u'性别')
    birthday = fields.Date(u'出生日期')
    cell_phone = fields.Char(u'手机', size=11)
    email = fields.Char(u'邮箱', size=30)
    profession_title = fields.Selection([('professor',u'教授级职称'),('senior',u'高级职称'),('medium',u'中级职称'),('primary',u'初级职称'),('technician',u'技术员级职称'),('unrated',u'未定级')], u'职称')    
    duty = fields.Char(u'职务', size=50)
    office_phone = fields.Char(u'办公电话', size=11)
    address = fields.Char(u'通讯地址', size=200)
    apply_date = fields.Date(u'申报日期')
    level = fields.Selection([('jt',u'集团咨询师'),('bk',u'板块咨询师'),('qy',u'企业咨询师')], u'咨询师类型')
    good_business = fields.Selection([('gczz',u'过程组织'),('shfx',u'审核发现'),('bgbx',u'报告编写')], u'擅长业务')
    major = fields.Selection([('aq',u'安全'),('yw',u'运维'),('js',u'技术')], u'专业')
    name=fields.Many2one('res.users','姓名')
    
    education_experience_ids = fields.One2many('audit.expert.education.experience','expert_id','教育经历')       
    work_experience_ids = fields.One2many('audit.expert.work.experience','expert_id','工作经历')
    qualification_ids = fields.One2many('audit.expert.qualification','expert_id','HSE相关资质')
    hsework_ids = fields.One2many('audit.expert.hsework','expert_id','HSE工作记录')
    hsetrain_ids = fields.One2many('audit.expert.hsetrain','expert_id','HSE培训记录')
    audit_plan_expert_ids = fields.One2many('audit.plan.expert', 'audit_expert_id', '审核计划成员专家')
    audit_score_expert_ids = fields.One2many('audit.score.info', 'expert_id', '打分专家')
    
    #workflow related fields
    state = fields.Selection([('draft','草稿'),('submitted','已提交'),('enterprise_approved','企业已确认'),('board_approved','板块已审核'),('enterprise_returned','企业已退回'),('board_returned','板块已退回')], string='审批状态', default='draft')
    enterprise_sug_person = fields.Many2one('res.users', string='审批人')
    enterprise_sug_date = fields.Date(u'审批时间')
    board_sug_person = fields.Many2one('res.users', string='审批人')
    board_sug_date = fields.Date(u'审批时间')
    comp_enterprise_sug_person = fields.Char(compute='_get_can_apporve',string='审批人', readonly=True)
    comp_enterprise_sug_date = fields.Date(compute='_get_can_apporve',string='审批时间', readonly=True)
    comp_board_sug_person = fields.Char(compute='_get_can_apporve',string='审批人', readonly=True)
    comp_board_sug_date = fields.Date(compute='_get_can_apporve',string='审批时间', readonly=True)
    enterprise_can_approve = fields.Boolean(compute='_get_can_apporve',string='企业是否可以确认')
    board_can_approve = fields.Boolean(compute='_get_can_apporve', string='板块是否可以审核')
    is_create_uid = fields.Boolean(compute='_get_is_create_uid', string='是否发起人')
    
    #根据所选用户自动添加用户其他属性
    @api.onchange('name')
    def _get_expert_info(self):
        if self.name and self.name.site_id:
            site_id = 0
            if self.name.site_id.enterprise:
                site_id = self.name.site_id.enterprise.id
            else:
                site_id = self.name.site_id.id
            print site_id
            site_workstation_relation = self.env['audit.vld.site.workstation.relation'].search([('audit_vld_site_id','=',site_id)])
            if site_workstation_relation:
                self.workstation = site_workstation_relation.workstation_id.id
    
    #判断当前用户是否发起人
    @api.depends()
    def _get_is_create_uid(self):
        if self.create_uid.id == self.env.context['uid']:
            self.is_create_uid = True
        else:
            self.is_create_uid = False
            
    #根据状态和当前用户是否在审批组中，判断当前用户是否可以审批
    @api.depends('state')
    def _get_can_apporve(self):
        self.comp_enterprise_sug_person = self.enterprise_sug_person.partner_id.name
        self.comp_enterprise_sug_date = self.enterprise_sug_date
        self.comp_board_sug_person = self.board_sug_person.partner_id.name
        self.comp_board_sug_date = self.board_sug_date
        self.enterprise_can_approve = self.board_can_approve = self.fd_can_approve = False
        #获取当前用户是否与项目中分管领导为同一人，如果是，则可以审批，返回true，否则返回false
        if self.state == 'submitted':
            g_res = self.env.ref('sys_audit.group_enterprise_administrator')
            if g_res:
                self.env.cr.execute('select count(1) from res_groups_users_rel where uid={0} and gid={1}'.format(self.env.context['uid'],g_res.id))
                res = self.env.cr.fetchone()
                if res and res[0]>0: 
                    self.enterprise_can_approve = True
                    if not self.enterprise_sug_person:    
                        self.comp_enterprise_sug_person = self.env['res.users'].search([('id','=',self.env.context['uid'])]).partner_id.name
                    if not self.enterprise_sug_date:     
                        self.comp_enterprise_sug_date = fields.Date.today()
                        
            
        if self.state =='enterprise_approved':
            g_res = self.env.ref('sys_audit.group_board_administrator')
            if g_res:
                self.env.cr.execute('select count(1) from res_groups_users_rel where uid={0} and gid={1}'.format(self.env.context['uid'],g_res.id))
                res = self.env.cr.fetchone()
                if res and res[0]>0: 
                    self.board_can_approve = True
                    if not self.board_sug_person:    
                        self.comp_board_sug_person = self.env['res.users'].search([('id','=',self.env.context['uid'])]).partner_id.name
                    if not self.board_sug_date:     
                        self.comp_board_sug_date = fields.Date.today()
    
    #创建同时提交工作流表单
    @api.model
    @api.returns('self', lambda value:value.id)
    def create(self, vals):
        if self.state:
            vals['state'] = 'draft'
        return models.Model.create(self, vals)
    
    #草稿
    def draft(self):
        self.write({'state':'draft'})
    
    #提交事件
    def submit(self):
        self.write({'state':'submitted'})
    
    #企业确认
    def enterprise_approve(self):
        self.write({'state':'enterprise_approved','enterprise_sug_person':self.env.uid,'enterprise_sug_date':fields.Date.today()})
    
    #板块审核
    def board_approve(self):
        self.write({'state':'board_approved','board_sug_person':self.env.uid,'board_sug_date':fields.Date.today()})
    
    #企业退回
    def enterprise_return(self):
        self.write({'state':'enterprise_returned','enterprise_sug_person':self.env.uid,'enterprise_sug_date':fields.Date.today()})
    
    #板块退回
    def board_return(self):
        self.write({'state':'board_returned','board_sug_person':self.env.uid,'board_sug_date':fields.Date.today()})

class audit_expert_education_experience(models.Model):
    _name="audit.expert.education.experience"
    _description=u"教育经历"
    
    start_time = fields.Date('开始日期')
    end_time = fields.Date('结束日期')
    school = fields.Char('学校', size=100)
    major = fields.Char('专业', size=100)
    education_background = fields.Selection(
                                    [('junior_college','专科'),
                                    ('bachelor','本科'),
                                    ('master','硕士研究生'),
                                    ('doctor','博士研究生')],'学历')
    expert_id = fields.Many2one('audit.expert.info','姓名')
    
class audit_expert_work_experience(models.Model):
    _name="audit.expert.work.experience"
    _description=u"工作经历"
    
    start_time = fields.Date('开始日期')
    end_time = fields.Date('结束日期')
    work_vld = fields.Char('工作单位', size=100)
    work_position = fields.Char('工作岗位', size=100)
    work_content = fields.Char('工作内容', size=500)
    expert_id = fields.Many2one('audit.expert.info', '姓名')

class audit_expert_qualification(models.Model):
    _name="audit.expert.qualification"
    _description=u"HSE相关资质"
    
    name = fields.Char('资质名称', size=100)
    qualification_num = fields.Char('资质证书号', size=30)
    start_time = fields.Date('开始日期')
    end_time = fields.Date('结束日期')
    expert_id = fields.Many2one('audit.expert.info', '姓名')

class audit_expert_hsework(models.Model):
    _name="audit.expert.hsework"
    _description=u"HSE工作记录"
    
    start_time = fields.Date('开始日期')
    end_time = fields.Date('结束日期')
    work_vld = fields.Char('工作单位', size=100)
    work_task = fields.Char('工作任务', size=100)
    work_evaluate = fields.Char('工作评价', size=50)
    expert_id = fields.Many2one('audit.expert.info', '姓名')
    
class audit_expert_hsetrain(models.Model):
    _name="audit.expert.hsetrain"
    _description=u"HSE培训记录"
    
    start_time = fields.Date('开始日期')
    end_time = fields.Date('结束日期')
    train_address = fields.Char('培训地点', size=100)
    sponsor = fields.Char('主办方', size=100)
    train_course = fields.Char('培训课程', size=50)
    train_content = fields.Char('培训内容', size=200)
    expert_id = fields.Many2one('audit.expert.info', '姓名')
    
class audit_expert_achievement(models.Model):
    _name = 'audit.expert.achievement'
    _description = u"专家业绩基本信息表"
        
    name = fields.Char(u'申报人', required=True)
    vld_site = fields.Char(u'单位', required=True)
    apply_date = fields.Date(u'申报日期')
    email = fields.Char(u'申报人邮箱')
    phone = fields.Char(u'申报人手机')
    state = fields.Selection([('draft',u'填报'),('submitted',u'已提交待确认'),('enterprise_approved',u'企业确认'),('enterprise_returned',u'企业退回')], u'申报状态')
    workstation = fields.Selection([('bj',u'北京工作站'),('db',u'东北工作站'),('xb',u'西北工作站'),('xn',u'西南工作站')], u'工作站')
    
    achievement_details_ids = fields.One2many('audit.expert.achievement.details','expert_achievement_id',u'专家业绩详细信息')
    
    enterprise_sug_person = fields.Many2one('res.users', string='审批人')
    enterprise_sug_date = fields.Date(u'审批时间')
    comp_enterprise_sug_person = fields.Char(compute='_get_can_apporve',string='审批人', readonly=True)
    comp_enterprise_sug_date = fields.Date(compute='_get_can_apporve',string='审批时间', readonly=True)
    enterprise_can_approve = fields.Boolean(compute='_get_can_apporve',string='企业是否可以确认')
    is_create_uid = fields.Boolean(compute='_get_is_create_uid', string='是否发起人')
    
    #判断当前用户是否发起人
    @api.depends()
    def _get_is_create_uid(self):
        if self.create_uid.id == self.env.context['uid']:
            self.is_create_uid = True
        else:
            self.is_create_uid = False
    
    #根据状态和当前用户是否在审批组中，判断当前用户是否可以审批
    @api.depends('state')
    def _get_can_apporve(self):
        self.comp_enterprise_sug_person = self.enterprise_sug_person.partner_id.name
        self.comp_enterprise_sug_date = self.enterprise_sug_date
        self.enterprise_can_approve = False
        #获取当前用户是否与项目中分管领导为同一人，如果是，则可以审批，返回true，否则返回false
        if self.state == 'submitted':
            g_res = self.env.ref('sys_audit.group_enterprise_administrator')
            if g_res:
                self.env.cr.execute('select count(1) from res_groups_users_rel where uid={0} and gid={1}'.format(self.env.context['uid'],g_res.id))
                res = self.env.cr.fetchone()
                if res and res[0]>0: 
                    self.enterprise_can_approve = True
                    if not self.enterprise_sug_person:    
                        self.comp_enterprise_sug_person = self.env['res.users'].search([('id','=',self.env.context['uid'])]).partner_id.name
                    if not self.enterprise_sug_date:     
                        self.comp_enterprise_sug_date = fields.Date.today()
            
    #创建同时提交工作流表单
    @api.model
    @api.returns('self', lambda value:value.id)
    def create(self, vals):
        if self.state:
            vals['state'] = 'draft'
        return models.Model.create(self, vals)
    
    #草稿
    def draft(self):
        self.write({'state':'draft'})
    
    #提交事件
    def submit(self):
        self.write({'state':'submitted'})
    
    #企业确认
    def enterprise_approve(self):
        self.write({'state':'enterprise_approved','enterprise_sug_person':self.env.uid,'enterprise_sug_date':fields.Date.today()})
    
    #企业退回
    def enterprise_return(self):
        self.write({'state':'enterprise_returned','enterprise_sug_person':self.env.uid,'enterprise_sug_date':fields.Date.today()})
    
class audit_expert_achievement_details(models.Model):
    _name = 'audit.expert.achievement.details'
    _description = u"专家业绩详细信息表"
        
    type = fields.Selection([('shpg',u'审核评估'),('pxsk',u'培训授课'),('zxzd',u'咨询指导'),('zxjc',u'专项检查'),('xmps',u'项目评审')], u'申报类型', required=True)
    description = fields.Char(u'申报描述', required=True)
    attachment = fields.Integer(u'证明材料')
    remarks = fields.Char(u'备注')
    expert_achievement_id = fields.Many2one('audit.expert.achievement', u'专家业绩基本信息')
    
class audit_expert_group(models.Model):
    _name = 'audit.expert.group'
    _description = u"我的小组信息表"
    
    name = fields.Char(u'小组名称', size=100, required=True)
    vld_site = fields.Char(u'单位')
    creater = fields.Char(u'创建者')
    contact_phone = fields.Char(u'联系电话')
    group_member = fields.Char(u'小组成员')
    remarks = fields.Char(u'备注')
    member_ids = fields.One2many('audit.expert.group.member','group_id','我的小组成员')
    
class audit_expert_group_member(models.Model):
    _name = 'audit.expert.group.member'
    _description = u"我的小组成员表"
    
    name = fields.Many2one('audit.expert.info', u'姓名', required=True)
    vld_site = fields.Many2one('audit.vld.site',related='name.vld_site', string=u'单位', readonly=True)
    good_busibess = fields.Selection(related='name.good_business', string=u'擅长专业', readonly=True)
    birthday = fields.Date(related='name.birthday', string=u'出生日期', readonly=True)
    profession_title = fields.Selection(related='name.profession_title', string=u'职称', readonly=True)
    cell_phone = fields.Char(related='name.cell_phone', string=u'手机', readonly=True)
    email = fields.Char(related='name.email', string=u'邮箱', readonly=True)
    workstation = fields.Many2one('sys.constant',related='name.workstation', string=u'工作站', readonly=True)
    group_id = fields.Many2one('audit.expert.group', u'我的小组')
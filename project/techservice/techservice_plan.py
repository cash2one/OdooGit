# -*- coding: utf-8 -*-
##############################################################################
#    外协计划管理
#    Created on 2016年1月14
#    @author: liuhongtai
#    Last edit on 2016年1月14
#    Last edit by  liuhongtai
##############################################################################

from openerp import models, fields, api
from openerp.osv import osv

class pm_techservice_plan(models.Model):
    _name = 'pm.techservice.plan'
    _description = u"外协计划管理"
    
    #获取默认的填报人
    def _get_default_report_person(self):
        user_name = self.env['res.users'].search([('id','=',self.env.context['uid'])]).partner_id.name
        return user_name
    
    #获取默认的填报日期
    def _get_default_report_date(self):
        return fields.Date.today()   
    
    """
               根据条件判断所走流程
    wf_flag=1代表流程为：提交--所(中心)审批--科研处审批
    wf_flag=2代表流程为：提交--所(中心)审批--科研处审批--院领导审批
              也作为流程结束标志
    """
    @api.depends('budget_account')
    def _get_which_wf(self):
        if self.budget_account<50:
            self.wf_flag = 1
        else:
            self.wf_flag = 2
    
    #判断当前用户是否发起人
    @api.depends()
    def _get_is_create_uid(self):
        if self.create_uid.id == self.env.uid:
            self.is_create_uid = True
        else:
            self.is_create_uid = False
    
    #根据状态和当前用户是否在审批组中，判断当前用户是否可以审批
    @api.depends('state')
    def _get_can_apporve(self):
        self.comp_unit_sug_person = self.unit_sug_person.partner_id.name
        self.comp_unit_sug_date = self.unit_sug_date
        self.comp_rd_sug_person = self.rd_sug_person.partner_id.name
        self.comp_rd_sug_date = self.rd_sug_date
        self.unit_can_approve = self.rd_can_approve = False
        #获取当前用户是否与项目中分管领导为同一人，如果是，则可以审批，返回true，否则返回false
        if (self.state =='submitted' and self.parent_proj.proj_reply_leaders.related_user.id == self.env.context['uid']) or (self.state =='submitted' and self.env.uid==1):
            self.unit_can_approve = True
            #如果审批人存在(已审批过)则显示数据库中审批人，否则显示当前用户,审批时间相同逻辑
            if not self.unit_sug_person:    
                self.comp_unit_sug_person = self.env['res.users'].search([('id','=',self.env.context['uid'])]).partner_id.name
            if not self.unit_sug_date:     
                self.comp_unit_sug_date = fields.Date.today()
        if self.state =='unit_approved':
            g_res = self.env.ref('aqy_project.group_techservice_rd_approve')
            if g_res:
                self.env.cr.execute('select count(1) from res_groups_users_rel where uid={0} and gid={1}'.format(self.env.context['uid'],g_res.id))
                res = self.env.cr.fetchone()
                if res and res[0]>0: 
                    self.rd_can_approve = True
                    if not self.rd_sug_person:    
                        self.comp_rd_sug_person = self.env['res.users'].search([('id','=',self.env.context['uid'])]).partner_id.name
                    if not self.rd_sug_date:     
                        self.comp_rd_sug_date = fields.Date.today()
        if self.state =='rd_approved':
            g_res = self.env.ref('aqy_project.group_techservice_research_dean_approve')
            if g_res:
                self.env.cr.execute('select count(1) from res_groups_users_rel where uid={0} and gid={1}'.format(self.env.context['uid'],g_res.id))
                res = self.env.cr.fetchone()
                if res and res[0]>0: 
                    self.dean_can_approve = True
                    if not self.dean_sug_person:    
                        self.comp_dean_sug_person = self.env['res.users'].search([('id','=',self.env.context['uid'])]).partner_id.name
                    if not self.dean_sug_date:     
                        self.comp_dean_sug_date = fields.Date.today()
    
    def get_project_id_domain(self):
        if self.env.uid == 1:
            return "[('proj_periods.name','=',u'实施中')]"
        return "[('proj_periods.name','=',u'实施中'),('proj_pm_uid','=',uid)]"
            
    name = fields.Char('外协任务名称', size=100, required=True) 
    parent_proj = fields.Many2one('pm.init.proj.apply', string='外协任务所属项目', required=True, domain=get_project_id_domain)
    client = fields.Many2one('oa.admin.org', related='parent_proj.proj_vld', string="委托单位", store=True)
    is_important = fields.Selection([('yes','是'),('no','否')], string='是否重大外协项目', required=True, default='no')
    attach_meeting = fields.Integer(string='会议纪要附件') 
    proj_background = fields.Text("项目背景简介")
    content = fields.Text("研究内容")
    achievement = fields.Text("成果指标")
    start_time = fields.Date("项目开始时间", required=True)
    end_time = fields.Date("项目结束时间", required=True)
    report_person = fields.Char(string="填报人", readonly=True, default=_get_default_report_person)
    report_date = fields.Date("填报时间", readonly=True, default=_get_default_report_date)
    hasno_budget = fields.Many2one('sys.constant', string='合同中有无外协预算', required=True, domain=[('type','=','HAS_NO')])
    budget_account = fields.Float('预算金额', required=True)
    reason = fields.Text('申请外协原因')
    qualification = fields.Text('外协资质要求')
    schedule = fields.Text('时间计划安排')
    other_require = fields.Text('其他要求')
    atta_requirebook = fields.Binary('外协项目技术要求书')
    state = fields.Selection([('unit_returned','草稿'),('rd_returned','草稿'),('dean_returned','草稿'),('submitted','已提交'),('unit_approved','所(中心)已审批'),('rd_approved','科研处已审批'),('dean_approved','主管院长已审批')], string='审批状态', default='submitted')
    unit_suggest = fields.Text('所(中心)审批意见')
    unit_sug_person = fields.Many2one('res.users',string='审批人')
    unit_sug_date = fields.Date('审批时间')
    comp_unit_sug_person = fields.Char(compute='_get_can_apporve',string='审批人', readonly=True)
    comp_unit_sug_date = fields.Date(compute='_get_can_apporve',string='审批时间', readonly=True)
    rd_suggest = fields.Text('科研处审批意见')
    rd_sug_person = fields.Many2one('res.users',string='审批人')
    comp_rd_sug_person = fields.Char(compute='_get_can_apporve',string='审批人', readonly=True)
    comp_rd_sug_date = fields.Date(compute='_get_can_apporve',string='审批时间', readonly=True)
    rd_sug_date = fields.Date('审批时间')
    dean_suggest = fields.Text('院领导审批意见')
    dean_sug_person = fields.Many2one('res.users',string='审批人')
    dean_sug_date = fields.Date('审批时间')
    comp_dean_sug_person = fields.Char(compute='_get_can_apporve',string='审批人', readonly=True)
    comp_dean_sug_date = fields.Date(compute='_get_can_apporve',string='审批时间', readonly=True)
    wf_flag = fields.Integer(compute='_get_which_wf', string='走哪个流程')
    unit_can_approve = fields.Boolean(compute='_get_can_apporve',string='所(中心)领导是否可以审批')
    rd_can_approve = fields.Boolean(compute='_get_can_apporve', string='科研处是否可以审批')
    dean_can_approve = fields.Boolean(compute='_get_can_apporve', string='院领导是否可以审批')
    is_create_uid = fields.Boolean(compute='_get_is_create_uid', string='是否发起人')
    is_over = fields.Boolean('是否审批完成', default=False)
    is_selected_init = fields.Boolean('是否已立项', default=False)
    
    #选择无预算时进行提示
    @api.onchange('hasno_budget')
    def check_onchange_hasno_budget(self):
        if self.hasno_budget.name==u'无':
            raise osv.except_osv('提示',"合同中没有外协预算原则上不允许外协!")
    
    @api.model
    @api.returns('self', lambda value:value.id)
    def create(self, vals):
        if vals.has_key('is_important') and vals['is_important']=='yes':
            if not vals.has_key('attach_meeting') or not vals['attach_meeting']:
                raise osv.except_osv('警告',"重大外协项目必须上传会议纪要附件!")
        return models.Model.create(self, vals)
    
    #提交事件
    def submit(self):
        self.write({'state':'submitted'})
    
    #所(中心)审批事件
    def unit_approve(self):
        self.write({'state':'unit_approved','unit_sug_person':self.env.uid,'unit_sug_date':fields.Date.today()})
        
    #科研处审批事件
    def rd_approve(self):
        if self.wf_flag==1:
            self.write({'state':'rd_approved','rd_sug_person':self.env.uid,'rd_sug_date':fields.Date.today(),'is_over':True})
        else:
            self.write({'state':'rd_approved','rd_sug_person':self.env.uid,'rd_sug_date':fields.Date.today()})
    
    #财务处审批事件
    def dean_approve(self):
        if self.wf_flag==2:
            self.write({'state':'dean_approved','dean_sug_person':self.env.uid,'dean_sug_date':fields.Date.today(),'is_over':True})
    
    #所(中心)退回事件
    def unit_return(self):
        self.write({'state':'unit_returned','unit_sug_person':self.env.uid,'unit_sug_date':fields.Date.today()})
    
    #科研处退回事件
    def rd_return(self):
        self.write({'state':'rd_returned','rd_sug_person':self.env.uid,'rd_sug_date':fields.Date.today()})
    
    #财务处退回事件
    def dean_return(self):
        self.write({'state':'dean_returned','dean_sug_person':self.env.uid,'dean_sug_date':fields.Date.today()})
    
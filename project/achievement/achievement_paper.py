# -*- coding: utf-8 -*-

from openerp import models, fields, api

class pm_achievement_paper(models.Model):
    _name = 'pm.achievement.paper'
    _description = u"论文表"
    
    #根据状态和当前用户是否在审批组中，判断当前用户是否可以审批
    @api.depends('state')
    def _get_can_apporve(self):
        self.unit_can_approve = False
        #获取当前用户是否与项目中分管领导为同一人，如果是，则可以审批，返回true，否则返回false
        if self.state =='submitted' and self.proj_id.proj_reply_leaders.related_user.id == self.env.context['uid'] or self.env.uid==1:
            self.unit_can_approve = True
    
    #判断当前用户是否发起人
    @api.depends()
    def _get_is_create_uid(self):
        if self.create_uid.id == self.env.context['uid']:
            self.is_create_uid = True
        else:
            self.is_create_uid = False
    
    @api.depends('author_ids')
    def _get_author(self):
        self.author = ''
        for rec in self.author_ids:
            self.author += rec.name.name + ','
        if self.author:
            self.author =  self.author[0:len(self.author)-1]
    
    name = fields.Char('论文名称', size=500, required=True)
    public_date = fields.Date('发表日期', required=True)
    proj_id = fields.Many2one('pm.init.proj.apply', string='所属项目', required=True, domain=[('proj_periods.name','=','实施中')])
    proj_vld = fields.Many2one('oa.admin.org',related='proj_id.proj_vld', string="所属单位", store=True)
    publications = fields.Char('发表刊物', size=100, required=True)
    publishing_house = fields.Char('出版社', size=100, required=True)
    retrieve = fields.Char('论文检索', size=100)
    description = fields.Text('论文描述')
    attachment = fields.Integer('论文附件')
    state = fields.Selection([('unit_returned','草稿'),('submitted','已提交'),('unit_approved','所(中心)已审批')], string='审批状态', default='submitted')
    unit_can_approve = fields.Boolean(compute='_get_can_apporve',string='所(中心)领导是否可以审批')
    is_create_uid = fields.Boolean(compute='_get_is_create_uid', string='是否发起人')
    author_ids = fields.One2many('pm.achievement.paper.author', 'paper_id', string="论文作者")
    author = fields.Char(compute='_get_author', string='论文作者',recursive=True)
    
    #创建同时提交工作流表单
    @api.model
    @api.returns('self', lambda value:value.id)
    def create(self, vals):
        if self.state:
            vals['state'] = 'submitted'
        return models.Model.create(self, vals)
    
    #提交事件
    def submit(self):
        self.write({'state':'submitted'})
    
    #所(中心)审批事件
    def unit_approve(self):
        self.write({'state':'unit_approved'})
    
    #财务处退回事件
    def unit_return(self):
        self.write({'state':'unit_returned'})
        
class pm_achievement_paper_author(models.Model):
    _name = 'pm.achievement.paper.author'
    _description = u"论文作者" 
    
    name = fields.Many2one('oa.staff.basic', string='姓名', required=True)
    serial = fields.Integer('排名(第几作者)', required=True)
    paper_id = fields.Many2one('pm.achievement.paper', string="论文信息")        
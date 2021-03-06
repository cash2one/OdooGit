# -*- coding: utf-8 -*-

from openerp import models, fields, api

class pm_achievement_award(models.Model):
    _name = 'pm.achievement.award'
    _description = u"获奖表"
    
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
    
    name = fields.Char('奖项名称', size=100, required=True)
    award_level = fields.Many2one('sys.constant',string='获奖级别', required=True, domain=[('type','=','AWARD_LEVEL')])
    proj_id = fields.Many2one('pm.init.proj.apply', string='所属项目', required=True, domain=[('proj_periods.name','=','实施中')])
    proj_vld = fields.Many2one('oa.admin.org',related='proj_id.proj_vld', string="所属单位", store=True)
    award_date = fields.Date('获奖日期', required=True)
    authority = fields.Char('发证单位', size=100, required=True)
    description = fields.Text('获奖描述')
    attachment = fields.Integer('获奖附件')
    state = fields.Selection([('unit_returned','草稿'),('submitted','已提交'),('unit_approved','所(中心)已审批')], string='审批状态', default='submitted')
    personlist_ids = fields.One2many('pm.achievement.award.personlist', 'award_id', string="获奖名单")
    unit_can_approve = fields.Boolean(compute='_get_can_apporve',string='所(中心)领导是否可以审批')
    is_create_uid = fields.Boolean(compute='_get_is_create_uid', string='是否发起人')
    
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


class pm_achievement_award_personlist(models.Model):
    _name = 'pm.achievement.award.personlist'
    _description = u"获奖名单" 
    
    name = fields.Many2one('oa.staff.basic', string='姓名', required=True)
    serial = fields.Integer('排名', required=True)
    award_id = fields.Many2one('pm.achievement.award', string="获奖信息")
# -*- coding: utf-8 -*-

from openerp import models, fields, api

class pm_techservice_check(models.Model):
    _name = 'pm.techservice.check'
    _description = u"外协评审检查"
    
    @api.depends('proj_id')
    def _get_name(self):
        for record in self:
            record.name = record.proj_id.name.ht_id.plan_id.wx_plan_check_result.name + '-' + u'评审检查'     
        
    name = fields.Char(compute='_get_name', string='外协评审检查名称')    
    proj_id = fields.Many2one('pm.techservice.init', string='外协任务名称', required=True)
    parent_proj = fields.Many2one(related='proj_id.name.ht_id.plan_id.wx_plan_check_result.parent_proj', string='外协任务所属项目', readonly=True, store=True)
    proj_num = fields.Char(related='proj_id.proj_num', string='外协任务编号', readonly=True, store=True)
    client = fields.Many2one(related='proj_id.client', string="委托单位", store=True, readonly=True) 
    bear_vld = fields.Char(related='proj_id.bear_vld', string='承担单位', store=True, readonly=True)
    start_time = fields.Date(related='proj_id.start_time', string='项目开始时间', readonly=True)
    end_time = fields.Date(related='proj_id.end_time', string='项目结束时间', readonly=True) 
    check_vld = fields.Many2one('oa.admin.org', string='组织单位')
    check_type = fields.Many2one('sys.constant', string='检查类型', domain=[('type','=','TECHSERVICE_CHECK_TYPE')])
    check_time = fields.Date('检查日期')
    check_address = fields.Char('检查地点', size=50)
    participant = fields.Char('参与人员列表', size=200)
    check_result = fields.Many2one('sys.constant', string='检查结论', domain=[('type','=','TECHSERVICE_CHECK_RESULT')])
    check_suggest = fields.Text('检查意见')
    attachment_ids = fields.One2many('pm.techservice.check.attachment', 'check_id', string='外协评审检查附件')
    
class pm_techservice_check_attachment(models.Model):
    _name = 'pm.techservice.check.attachment'
    _description = u"外协检查评审附件"
     
    name = fields.Char(string='附件名称', size=50)
    seq = fields.Integer('序号')
    attachment = fields.Integer('附件', required=True)
    content = fields.Text('文档说明')
    check_id = fields.Many2one('pm.techservice.check', string='外协评审检查')
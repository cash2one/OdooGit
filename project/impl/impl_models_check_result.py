# -*- coding: utf-8 -*-

from openerp import models, fields, api
from openerp.osv.fields import related

'''
菜单名：检查结果
'''
#月度计划信息表
class pm_impl_check_result(models.Model):
    _name = 'pm.impl.check.result'
    _description = u'检查结果'
        
    name = fields.Char('名称', size=100, default='检查结果信息')
    check_plan_id = fields.Many2one('pm.impl.check.plan',string='检查计划',required=True)
    check_type =  fields.Many2one('sys.constant',string='检查类型',required=True,domain=[('type','=','impl_check_type')])
    check_mode =  fields.Many2one('sys.constant',string='检查形式',required=True,domain=[('type','=','impl_check_mode')])
    check_time =  fields.Date(string='检查日期',required=True)
    expert_group = fields.Char(string='专家组')
    suggest = fields.Text('评审意见',required=True)
    result = fields.Many2one('sys.constant',string='检查结论',domain=[('type','=','impl_result')],required=True)
    check_result_attach_record_id = fields.One2many('pm.impl.check.result.attach','check_result_id',string='附件')
    
    #取检查计划中对应的值作为默认值，但是可以编辑
    @api.onchange('check_plan_id')
    def _get_default_check_type(self):
        for record in self:
            record.check_type = record.check_plan_id.check_type
            record.check_mode = record.check_plan_id.check_mode
            record.check_time = record.check_plan_id.check_time
            record.expert_group = record.check_plan_id.expert_group
    

    
#检查结果附件表
class pm_impl_check_result_attach(models.Model):
    _name = 'pm.impl.check.result.attach'
    _description = u'检查结果附件表'
    
    name = fields.Char('名称', size=100, default='检查结果附件')
    check_result_id = fields.Many2one('pm.impl.check.result',string='检查结果')
    name = fields.Char('附件名称',required=True)
    attach = fields.Integer('附件',required=True)
    

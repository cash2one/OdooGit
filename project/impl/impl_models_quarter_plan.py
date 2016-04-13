# -*- coding: utf-8 -*-

from openerp import models, fields, api

'''
菜单名：季度计划跟踪
'''
#季度计划信息表
class pm_impl_quarter_plan(models.Model):
    _name = 'pm.impl.quarter.plan'
    _description = u'季度计划基本信息'
    
    name = fields.Char('名称', size=100, default='季度计划信息')
    project_id = fields.Many2one('pm.init.proj.apply',string='项目',required=True,readonly=True,domain=[('proj_periods.name','=','实施中')])
    source = fields.Char(related='project_id.proj_first_party',string='项目来源',required=True,readonly=True)
    cd_organ_id = fields.Many2one(related='project_id.proj_vld',string='承担单位',required=True,readonly=True)
    proj_manager = fields.Many2one('res.users',string='项目经理',readonly=True)
    start_time = fields.Date(related='project_id.proj_start_date',string='开始时间',required=True,readonly=True)
    end_time = fields.Date(related='project_id.proj_end_date',string='结束时间',required=True,readonly=True)
    quarter_plan_record_id = fields.One2many('pm.impl.plan.baseline.version','quarter_plan_gz_id',required=True,string='季度计划',domain=[('plan_baseline_id.active_state.name','=','当前有效')])

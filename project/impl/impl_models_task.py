# -*- coding: utf-8 -*-

from openerp import models, fields, api
from openerp.tools.translate import _
from openerp.osv import osv

'''
菜单名：阶段任务跟踪
'''
#阶段任务信息表
class pm_impl_task(models.Model):
    _name = 'pm.impl.task'
    _description = u'阶段任务信息'
    _inherit = 'mail.thread'
    
    name = fields.Char('任务名称',required=True)
    task_project_id = fields.Many2one('pm.impl.task.project',string='项目',required=True)
    project_id = fields.Many2one(related='task_project_id.name',string='项目')
    manager_id = fields.Integer(related='project_id.proj_pm_uid',string=u'项目经理id',readonly=True)
    responsible_person_id = fields.Many2one('res.users','负责人',required=True)
    participant = fields.Char('参与人')
    start_time = fields.Date('开始日期',required=True)
    end_time = fields.Date('结束日期',required=True)
    priority = fields.Selection([('low','低'),('middle','中'),('high','高')],'优先级')
    description = fields.Text('任务描述')
    state = fields.Selection([('before_start','未开始'),('execute','进行中'),('complete','已完成')],'执行状态')
    task_stage = fields.Many2one('pm.impl.task.stage',string='任务阶段',domain="[('task_project_record_id', '=', task_project_id),('task_project_record_id', '!=', False)]",required=True)
    
    @api.onchange('start_time')
    def change_start_time(self):
        for record in self:
            if record.start_time and record.end_time:
                if record.start_time > record.end_time:
                    record.start_time = False
                    #raise osv.except_osv(u'提示!',u'结束日期不能早于开始日期！')
    
    @api.onchange('end_time')
    def change_end_time(self):
        for record in self:
            if record.start_time and record.end_time:
                if record.start_time > record.end_time:
                    record.end_time = False
                    #raise osv.except_osv(u'提示!',u'结束日期不能早于开始日期！')
    
#任务阶段
class pm_impl_task_stage(models.Model):
    _name = 'pm.impl.task.stage'
    _description = u'任务阶段'
    _sql_constraints = [
        ('unique_key', 'UNIQUE (name)',  '阶段名称已存在!')
    ]
    
    name = fields.Char(string='阶段名称',required=True)
    sequence = fields.Integer(string='阶段序列')
    task_project_record_id = fields.Many2many('pm.impl.task.project','pm_impl_task_project_stage','task_stage_id','task_project_id',string='项目')

    
#项目信息表
class pm_impl_task_project(models.Model):
    _name = 'pm.impl.task.project'
    _description = u'项目信息表'
    _sql_constraints = [
        ('unique_key', 'UNIQUE (name)', '所选项目已设置阶段!')
    ]
    
    @api.depends('task_record_id')
    def _get_task_count(self):
        for record in self:
            record.task_count = len(record.task_record_id)
            
    @api.onchange('name')
    def change_name(self):
        for record in self:
            proj_pm_uid = record.name.proj_pm_uid
            if proj_pm_uid:
                record.manager_id = self.env['res.users'].search([('id','=',proj_pm_uid)])
                record.comp_manager_id = record.manager_id.partner_id.name
                

    def get_project_id_domain(self):
        if self.env.uid == 1:
            return "[('proj_periods.name','=',u'实施中')]"
        return "[('proj_periods.name','=',u'实施中'),('proj_pm_uid','=',uid)]"
    
    name = fields.Many2one('pm.init.proj.apply',string='项目',required=True,domain=get_project_id_domain)
    organ_id = fields.Many2one(related='name.proj_vld',string='承担单位',readonly=True)
    manager_id = fields.Many2one('res.users',string='项目经理')
    comp_manager_id = fields.Char(compute='change_name',string='项目经理')
    start_time = fields.Date(related='name.proj_start_date',string='开始时间',readonly=True)
    end_time = fields.Date(related='name.proj_end_date',string='结束时间',readonly=True)
    task_count = fields.Integer(compute='_get_task_count',string='任务数量')
    task_stage_record_id = fields.Many2many('pm.impl.task.stage','pm_impl_task_project_stage','task_project_id','task_stage_id',string='项目阶段')
    task_record_id = fields.One2many('pm.impl.task','task_project_id',string='阶段任务')
    
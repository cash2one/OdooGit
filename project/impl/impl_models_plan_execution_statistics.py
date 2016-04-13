# -*- coding: utf-8 -*-

'''
菜单名：计划执行统计
'''
#计划执行统计

from openerp import models, fields, api
from openerp.tools.translate import _
from openerp.osv import osv


class pm_impl_plan_execution_statistics(models.Model):
    _name = 'pm.impl.plan.execution.statistics'
    _description = u'计划执行统计'

    def get_project_id_domain(self):
        if self.env.uid == 1:
            return "[('proj_periods.name','=',u'实施中')]"
        return "[('proj_periods.name','=',u'实施中'),('proj_pm_uid','=',uid)]"
    
    name = fields.Char('名称', size=100, default='生成月度计划')
    project_id = fields.Many2one('pm.init.proj.apply', string='项目',domain=get_project_id_domain)
    organ_id = fields.Many2one('oa.admin.org', string='承担单位')
    year = fields.Many2one('sys.constant', string='年份', domain=[('type', '=', 'year')])
    month = fields.Many2one('sys.constant', string='月份', domain=[('type', '=', 'month')])
    year_value = fields.Integer('年份值')
    month_value = fields.Integer('月份值')
    
    #设置年份值
    @api.onchange('year')
    def set_year_value(self):
        for record in self:
            record.year_value = int(record.year.name)
    
    #设置月份值
    @api.onchange('month')
    def set_month_value(self):
        for record in self:
            record.month_value = int(record.month.name)
    
    #判断目标年月是否在标准的时间段内, 标准时间的格式：yyyy-MM-dd
    def check_time(self, standard_start_time, standard_end_time, goal_year, goal_month):
        standard_start_year = int(standard_start_time[0:4])
        standard_start_month = int(standard_start_time[5:7])
        standard_end_year = int(standard_end_time[0:4])
        standard_end_month = int(standard_end_time[5:7])
        if standard_start_year == standard_end_year:
            if standard_start_year == goal_year and standard_start_month <= goal_month and goal_month <= standard_end_month:
                return True
        elif standard_start_year < standard_end_year:
            if standard_start_year == goal_year and standard_start_month <= goal_month:
                return True
            elif standard_start_year < goal_year and goal_year < standard_end_year:
                return True
            elif standard_end_year == goal_year and goal_month <= standard_end_month:
                return True
        return False
    
    #生成单位月度计划前先检查目标单位下哪些项目能生成计划，哪些不能生成计划
    def check_before_create_organ_month_plan(self, cr, uid, param_organ_id, param_year, param_month, context=None):
        real_param_year_id = self.pool.get('sys.constant').search(cr, uid, [('type','=','year'),('name', '=', param_year)], context=context)[0]
        real_param_month_id = self.pool.get('sys.constant').search(cr, uid, [('type','=','month'),('name', '=', param_month)], context=context)[0]
        real_param_organ_id = self.pool.get('oa.admin.org').search(cr, uid, [('name', '=', param_organ_id)], context=context)[0]
        real_project_ids = self.pool.get('pm.init.proj.apply').search(cr, uid, [('proj_vld', '=', real_param_organ_id),('proj_periods.name','=','实施中')], context=context)
        has_task_month_plan_ids = self.pool.get('pm.impl.month.plan').search(cr, uid, [('project_id', 'in', real_project_ids),('year', '=', real_param_year_id),('month', '=', real_param_month_id),('state', '=', 'suo_confirmed')], context=context)
        data = {}
        data['total'] = len(real_project_ids)
        data['has_task_project_amount'] = len(has_task_month_plan_ids)
        data['not_has_task_project_amount'] = len(real_project_ids) - len(has_task_month_plan_ids)
        return data
    
    #使用<input type="button"/>控件生成单位月度计划
    def create_organ_month_plan2(self, cr, uid, param_organ_id, param_year, param_month, context=None):
        real_param_year_id = self.pool.get('sys.constant').search(cr, uid, [('type','=','year'),('name', '=', param_year)], context=context)[0]
        real_param_month_id = self.pool.get('sys.constant').search(cr, uid, [('type','=','month'),('name', '=', param_month)], context=context)[0]
        real_param_organ_id = self.pool.get('oa.admin.org').search(cr, uid, [('name', '=', param_organ_id)], context=context)[0]
        real_project_ids = self.pool.get('pm.init.proj.apply').search(cr, uid, [('proj_vld', '=', real_param_organ_id),('proj_periods.name','=','实施中')], context=context)
        has_task_month_plan_ids = self.pool.get('pm.impl.month.plan').search(cr, uid, [('project_id', 'in', real_project_ids),('year', '=', real_param_year_id),('month', '=', real_param_month_id),('state', '=', 'suo_confirmed')], context=context)
        has_task_month_plans = self.pool.get('pm.impl.month.plan').browse(cr, uid, has_task_month_plan_ids, context)
        if len(has_task_month_plans) > 0:
            organ_month_plan_id = self.pool.get('pm.impl.organ.month.plan').create(cr, uid, {'organ_id' : real_param_organ_id, 'year' : real_param_year_id, 'month' : real_param_month_id}, context)
            for has_task_month_plan in has_task_month_plans:
                month_plan_project_id = has_task_month_plan.project_id.id
                month_contents = has_task_month_plan.month_content_record_id
                xuhao = 1
                content = ''
                for month_content in month_contents:
                    content = content + str(xuhao) + u'、' + month_content.task + u'\n'
                    xuhao = xuhao + 1
                self.pool.get('pm.impl.organ.plan.content').create(cr, uid, {'dwydjh_id' : organ_month_plan_id, 'project_id' : month_plan_project_id,'content' : content}, context)
                return u'单位月度计划已生成，请到单位月度计划跟踪菜单下查看！'
    
                
    #使用<input type="button"/>控件生成项目月度计划
    def create_month_plan2(self, cr, uid, param_project_id, param_year, param_month, context=None):
        real_param_project_id = self.pool.get('pm.init.proj.apply').search(cr, uid, [('name', '=', param_project_id)], context=context)[0]
        real_param_project = self.pool.get('pm.init.proj.apply').browse(cr, uid, real_param_project_id, context)
        task_project_id = self.pool.get('pm.impl.task.project').search(cr, uid, [('name', '=', real_param_project_id)], context=context)
        task_project = self.pool.get('pm.impl.task.project').browse(cr, uid, task_project_id, context)
        if len(task_project) == 0:
            return u'项目"' +param_project_id + u'"在' + param_year + u'年' + param_month + u'月没有任务,不能生成项目月度计划！'
        for record in task_project:
            tasks = record.task_record_id
            xuhao = 1
            month_plan_id = 0
            for task in tasks:
                check_time_result = self.check_time(task.start_time, task.end_time, int(param_year), int(param_month))
                if check_time_result:
                    if xuhao == 1:
                        real_param_year_id = self.pool.get('sys.constant').search(cr, uid, [('type','=','year'),('name', '=', param_year)], context=context)[0]
                        real_param_month_id = self.pool.get('sys.constant').search(cr, uid, [('type','=','month'),('name', '=', param_month)], context=context)[0]
                        month_plan_id = self.pool.get('pm.impl.month.plan').create(cr, uid, {'project_id':real_param_project_id, 'manager_id':real_param_project.proj_pm_uid, 'year':real_param_year_id, 'month':real_param_month_id}, context=context)
                    self.pool.get('pm.impl.month.content').create(cr, uid, {'month_plan_id':month_plan_id, 'sequence_number':xuhao, 'task':task.description}, context=context)
                    xuhao = xuhao + 1
            if xuhao == 1:
                return u'项目"' +param_project_id + u'"在' + param_year + u'年' + param_month + u'月没有任务,不能生成项目月度计划！'
            else:
                return u'项目月度计划已生成，请到月度计划跟踪菜单下查看！'
            
    #项目任务进展分析
    
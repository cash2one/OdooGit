# -*- coding: utf-8 -*-

from openerp import models, fields, api
from openerp.osv.fields import related

'''
菜单名：月度计划跟踪
'''
#月度计划信息表
class pm_impl_month_plan(models.Model):
    _name = 'pm.impl.month.plan'
    _description = u'月度计划信息'
    _sql_constraints = [
        ('unique_key', 'UNIQUE (project_id,year,month)',  '所选项目已存在该月的月度计划!')
    ]
    
    @api.onchange('project_id')
    def change_project_id(self):
        for record in self:
            record.year = False
            record.month = False
            proj_pm_uid = record.project_id.proj_pm_uid
            if proj_pm_uid:
                record.manager_id = self.env['res.users'].search([('id','=',proj_pm_uid)])
                record.comp_manager_id = record.manager_id.partner_id.name
                
    @api.onchange('year')
    def change_year(self):
        for record in self:
            if record.start_time and record.end_time and record.year:
                start_time_str =  str(record.start_time)
                end_time_str =  str(record.end_time)
                start_year = int(start_time_str[0:4])
                start_month = int(start_time_str[5:7])
                end_year = int(end_time_str[0:4])
                end_month = int(end_time_str[5:7])
                param_year = int(record.year.name)
                if param_year < start_year:
                    record.year = False
                elif param_year == start_year:
                    if record.month and int(record.month.name) < start_month:
                        record.year = False
                        
                if param_year > end_year:
                    record.year = False
                elif param_year == end_year:
                    if record.month and int(record.month.name) > end_month:
                        record.year = False
                
    @api.onchange('month')
    def change_month(self):
        for record in self:
            if record.start_time and record.end_time and record.year and record.month:
                start_time_str =  str(record.start_time)
                end_time_str =  str(record.end_time)
                start_year = int(start_time_str[0:4])
                start_month = int(start_time_str[5:7])
                end_year = int(end_time_str[0:4])
                end_month = int(end_time_str[5:7])
                param_year = int(record.year.name)
                if  param_year == start_year:
                    if int(record.month.name) < start_month:
                        record.month = False
                        
                if param_year == end_year:
                    if int(record.month.name) > end_month:
                        record.month = False
                        
    def get_project_id_domain(self):
        if self.env.uid == 1:
            return "[('proj_periods.name','=',u'实施中')]"
        return "[('proj_periods.name','=',u'实施中'),('proj_pm_uid','=',uid)]"
       
    name = fields.Char('名称', size=100, default='月度计划信息')
    project_id = fields.Many2one('pm.init.proj.apply',string='项目',required=True,domain=get_project_id_domain)
    source = fields.Char(related='project_id.proj_first_party',string='项目来源',readonly=True)
    organ_id = fields.Many2one(related='project_id.proj_vld',string='承担单位',required=True,readonly=True)
    manager_id = fields.Many2one('res.users',string='项目经理')
    comp_manager_id = fields.Char(compute='change_project_id',string='项目经理',readonly=True)
    start_time = fields.Date(related='project_id.proj_start_date',string='开始时间',required=True,readonly=True)
    end_time = fields.Date(related='project_id.proj_end_date',string='结束时间',required=True,readonly=True)
    year = fields.Many2one('sys.constant',string='计划 年份',domain=[('type','=','year')],required=True)
    month = fields.Many2one('sys.constant',string='计划 月份',domain=[('type','=','month')],required=True)
    month_content_record_id = fields.One2many('pm.impl.month.content','month_plan_id',string='计划内容')
    suo_suggest = fields.Text('审批意见')
    suo_verifier_id = fields.Many2one('res.users',string='审批人')
    suo_time = fields.Date('日期')
    performance = fields.Text('完成情况')
    operator_id = fields.Many2one('res.users',string='录入人')
    operate_time = fields.Date('日期')
    suo_confirm_suggest = fields.Text('意见')
    suo_confirm_verifier_id = fields.Many2one('res.users',string='确认人')
    suo_confirm_time = fields.Date('日期')
    state = fields.Selection([('draft','草稿'),('submitted', '已提交'),('suo_accepted', '所(中心)已审批'),('xm_accepted', '项目组已填写执行情况'),('suo_confirmed','所(中心)已确认')] ,'审批状态')
    
    def _get_comp_value(self):
        self.comp_suo_verifier_id = self.suo_verifier_id.name
        self.comp_suo_time = self.suo_time
        self.comp_operator_id = self.operator_id.name
        self.comp_operate_time = self.operate_time
        self.comp_suo_confirm_verifier_id = self.suo_confirm_verifier_id.name
        self.comp_suo_confirm_time = self.suo_confirm_time
    
    
    @api.depends('state')
    def _get_can_approve(self):
        for record in self:
            record.can_manager_submit = False
            record.can_suo_approve = False
            record.can_xm_submit = False
            record.can_suo_confirm = False
            
            record.comp_suo_verifier_id = self.suo_verifier_id.name
            record.comp_suo_time = self.suo_time
            record.comp_operator_id = self.operator_id.name
            record.comp_operate_time = self.operate_time
            record.comp_suo_confirm_verifier_id = self.suo_confirm_verifier_id.name
            record.comp_suo_confirm_time = self.suo_confirm_time
            
            if record.state == 'draft':
                if self.env.uid == 1 :
                    record.can_manager_submit = True
                    
                if self.is_user_in_group('aqy_project.group_proj_manager') and record.project_id.proj_pm_uid == self.env.uid:
                    record.can_manager_submit = True
            elif record.state == 'submitted':
                if self.env.uid == 1 :
                    record.can_suo_approve = True
                    
                if self.is_user_in_group('aqy_project.group_unit_leaders') and record.project_id.proj_reply_leaders.related_user.id == self.env.uid:
                    record.can_suo_approve = True
                    
                if record.can_suo_approve:
                    record.comp_suo_verifier_id = self.env['res.users'].search([('id','=',self.env.uid)]).partner_id.name
                    record.comp_suo_time = fields.Date.today()
                else:
                    if not record.suo_suggest:
                        record.comp_suo_verifier_id = False
                        record.comp_suo_time = False
                    else:
                        record.comp_suo_verifier_id = record.suo_verifier_id.partner_id.name
                        record.comp_suo_time = record.suo_time
                    
            elif record.state == 'suo_accepted':
                if self.env.uid == 1 :
                    record.can_xm_submit = True
                
                if self.is_user_in_group('aqy_project.group_proj_manager') and record.project_id.proj_pm_uid == self.env.uid:
                    record.can_xm_submit = True
                    
                if record.can_xm_submit:
                    record.comp_operator_id = self.env['res.users'].search([('id','=',self.env.uid)]).partner_id.name
                    record.comp_operate_time = fields.Date.today()
                else:
                    if not record.performance:
                        record.comp_operator_id = False
                        record.comp_operate_time = False
                    else:
                        record.comp_operator_id = record.operator_id.partner_id.name
                        record.comp_operate_time = record.operate_time
                    
            elif record.state == 'xm_accepted':
                if self.env.uid == 1 :
                    record.can_suo_confirm = True
                    
                if self.is_user_in_group('aqy_project.group_unit_leaders') and record.project_id.proj_reply_leaders.related_user.id == self.env.uid:
                    record.can_suo_confirm = True
                    
                if record.can_suo_confirm:
                    record.comp_suo_confirm_verifier_id = self.env['res.users'].search([('id','=',self.env.uid)]).partner_id.name
                    record.comp_suo_confirm_time = fields.Date.today()
                else:
                    if not record.suo_confirm_suggest:
                        record.comp_suo_confirm_verifier_id = False
                        record.comp_suo_confirm_time = False
                    else:
                        record.comp_suo_confirm_verifier_id = record.suo_confirm_verifier_id.partner_id.name
                        record.comp_suo_confirm_timee = record.suo_confirm_time
                    
    #判断当前用户是否是指定的权限组内
    def is_user_in_group(self,group_str):
        g_res = self.env.ref(group_str)
        if g_res:
            self.env.cr.execute('select count(1) from res_groups_users_rel where uid={0} and gid={1}'.format(self.env.uid,g_res.id))
            res = self.env.cr.fetchone()
            if res and res[0]>0:
                return True
        return False
    
    can_manager_submit = fields.Boolean(compute='_get_can_approve',string='项目经理可提交')
    can_suo_approve = fields.Boolean(compute='_get_can_approve',string='所(中心)可审批')
    can_xm_submit = fields.Boolean(compute='_get_can_approve',string='项目组可提交')
    can_suo_confirm = fields.Boolean(compute='_get_can_approve',string='所(中心)可确认')
    
    comp_suo_verifier_id = fields.Char(compute='_get_can_approve',string='审批人',readonly=True)
    comp_suo_time = fields.Date(compute='_get_can_approve',string='日期',readonly=True)
    comp_operator_id = fields.Char(compute='_get_can_approve',string='录入人',readonly=True)
    comp_operate_time = fields.Date(compute='_get_can_approve',string='日期',readonly=True)
    comp_suo_confirm_verifier_id = fields.Char(compute='_get_can_approve',string='确认人',readonly=True)
    comp_suo_confirm_time = fields.Date(compute='_get_can_approve',string='日期',readonly=True)
    
    def draft(self):
        if self.can_suo_approve:
            self.write({'state':'draft','suo_verifier_id':self.env.uid,'suo_time':fields.Date.today()})
        else:
            self.write({'state':'draft'})
        
    def submitted(self):
        self.write({'state':'submitted'})
        
    def suo_accepted(self):
        if self.can_suo_confirm:
            self.write({'state':'suo_accepted','suo_confirm_verifier_id':self.env.uid,'suo_confirm_time':fields.Date.today()})
        else:
            self.write({'state':'suo_accepted','suo_verifier_id':self.env.uid,'suo_time':fields.Date.today()})
        
#     def return1(self):
#         self.write({'state':'draft'})
        
    def xm_accepted(self):
        self.write({'state':'xm_accepted','operator_id':self.env.uid,'operate_time':fields.Date.today()})
        
    def suo_confirmed(self):
        self.write({'state':'suo_confirmed','suo_confirm_verifier_id':self.env.uid,'suo_confirm_time':fields.Date.today()})
        
#     def return2(self):
#         self.write({'state':'draft'})
        
    @api.model
    @api.returns('self', lambda value:value.id)
    def create(self, vals):
        manager_id = self.env['pm.init.proj.apply'].search([('id','=',vals['project_id'])])[0].proj_pm_uid
        vals['manager_id'] = manager_id
        return models.Model.create(self, vals)
    
    @api.multi
    def write(self, vals):
        return models.Model.write(self, vals)    
    
#计划内容信息表
class pm_impl_month_content(models.Model):
    _name = 'pm.impl.month.content'
    _description = u'计划内容'
    _sql_constraints = [
        ('unique_key', 'UNIQUE (month_plan_id,sequence_number)',  '序号不能重复!')
    ]
    
    name = fields.Char('名称', size=100, default='月度计划内容信息')
    month_plan_id = fields.Many2one('pm.impl.month.plan',string='月度计划')
    sequence_number = fields.Integer('序号',required=True)
    task = fields.Char('任务',required=True)
    is_additional = fields.Selection([('yes','是'),('no','否')],string='计划外任务',default='no')
    percentage = fields.Float('完成率')
    remark = fields.Text('备注')
    main_state = fields.Char(compute='_get_main_state',string='主表审批状态',store=False)
    
    @api.onchange('sequence_number')
    def change_sequence_number(self):
        for record in self:
            if record.sequence_number < 0:
                record.sequence_number = False

    @api.depends()
    def _get_main_state(self):
        #print u'获取主表审批状态'
        for record in self:
            record.main_state = record.month_plan_id.state
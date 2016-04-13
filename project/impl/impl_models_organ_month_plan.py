# -*- coding: utf-8 -*-

from openerp import models, fields, api

'''
菜单名：单位月度计划跟踪
'''
#单位月度计划跟踪
class pm_impl_organ_month_plan(models.Model):
    _name = 'pm.impl.organ.month.plan'
    _description = u'单位月度计划信息'
    _sql_constraints = [
        ('unique_key', 'UNIQUE (organ_id,year,month)',  '所选单位已存在该月的月度计划!')
    ]

    name = fields.Char('名称', size=100, default='单位月度计划信息')
    organ_id = fields.Many2one('oa.admin.org','单位',required=True)
    year = fields.Many2one('sys.constant',string='年份',domain=[('type','=','year')],required=True)
    month = fields.Many2one('sys.constant',string='月份',domain=[('type','=','month')],required=True)
    organ_plan_content_record_id = fields.One2many('pm.impl.organ.plan.content','dwydjh_id',string='单位月度计划内容',required=True)
    ke_suggest = fields.Text('审批意见')
    ke_verifier_id = fields.Many2one('res.users',string='审批人')
    ke_time = fields.Date('日期')
    ke_confirm_suggest = fields.Text('审批意见')
    ke_confirm_verifier_id = fields.Many2one('res.users',string='审批人')
    ke_confirm_time = fields.Date('日期')
    state = fields.Selection([('draft','已退回'),('submitted', '已提交'),('ke_accepted','科研处已审批'),('dw_accepted','单位已填写完成情况'),('ke_confirmed','科研处已确认')] ,string='审批状态')
    
    @api.depends('state')
    def _get_can_approve(self):
        for record in self:
            record.can_suo_submit = False
            record.can_ke_approve = False
            record.can_dw_submit = False
            record.can_ke_confirm = False
            
            record.comp_ke_verifier_id = record.ke_verifier_id.name
            record.comp_ke_time = record.ke_time
            record.comp_ke_confirm_verifier_id = record.ke_confirm_verifier_id.name
            record.comp_ke_confirm_time = record.ke_confirm_time
            if record.state == 'draft':
                if self.env.uid == 1 :
                    record.can_suo_submit = True
                    
                if self.is_user_in_group('aqy_project.group_unit_leaders'):
                    record.can_suo_submit = True
            elif record.state == 'submitted':
                if self.env.uid == 1 :
                    record.can_ke_approve = True
                    
                if self.is_user_in_group('aqy_project.group_impl_ky_approve'):
                    record.can_ke_approve = True
                    
                if record.can_ke_approve:
                    record.comp_ke_verifier_id = self.env['res.users'].search([('id','=',self.env.uid)]).partner_id.name
                    record.comp_ke_time = fields.Date.today()
                else:
                    if not record.ke_suggest:
                        record.comp_ke_verifier_id = False
                        record.comp_ke_time = False
                    else:
                        record.comp_ke_verifier_id = record.ke_verifier_id.partner_id.name
                        record.comp_ke_time = record.ke_time
                        
            elif record.state == 'ke_accepted':
                if self.env.uid == 1 :
                    record.can_dw_submit = True
                
                if self.is_user_in_group('aqy_project.group_unit_leaders'):
                    record.can_dw_submit = True
            elif record.state == 'dw_accepted':
                if self.env.uid == 1 :
                    record.can_ke_confirm = True
                    
                if self.is_user_in_group('aqy_project.group_impl_ky_approve'):
                    record.can_ke_confirm = True
                    
                if record.can_ke_confirm:
                    record.comp_ke_confirm_verifier_id = self.env['res.users'].search([('id','=',self.env.uid)]).partner_id.name
                    record.comp_ke_confirm_time = fields.Date.today()
                else:
                    if not record.ke_confirm_suggest:
                        record.comp_ke_confirm_verifier_id = False
                        record.comp_ke_confirm_time = False
                    else:
                        record.comp_ke_confirm_verifier_id = record.ke_confirm_verifier_id.partner_id.name
                        record.comp_ke_confirm_time = record.ke_confirm_time
    
    #判断当前用户是否是指定的权限组内
    def is_user_in_group(self,group_str):
        g_res = self.env.ref(group_str)
        if g_res:
            self.env.cr.execute('select count(1) from res_groups_users_rel where uid={0} and gid={1}'.format(self.env.uid,g_res.id))
            res = self.env.cr.fetchone()
            if res and res[0]>0:
                return True
        return False
    
    can_suo_submit = fields.Boolean(compute='_get_can_approve',string='所(中心)可提交')
    can_ke_approve = fields.Boolean(compute='_get_can_approve',string='科研处可审批')
    can_dw_submit = fields.Boolean(compute='_get_can_approve',string='单位可提交')
    can_ke_confirm = fields.Boolean(compute='_get_can_approve',string='科研处可确认')
    
    comp_ke_verifier_id = fields.Char(compute='_get_can_approve',string='审批人',readonly=True)
    comp_ke_time = fields.Date(compute='_get_can_approve',string='日期',readonly=True)
    comp_ke_confirm_verifier_id = fields.Char(compute='_get_can_approve',string='审批人',readonly=True)
    comp_ke_confirm_time = fields.Date(compute='_get_can_approve',string='日期',readonly=True)
    
    def draft(self):
        if self.can_ke_approve:
            self.write({'state':'draft','ke_verifier_id':self.env.uid,'ke_time':fields.Date.today()})
        else:
            self.write({'state':'draft'})
        
    def submitted(self):
        self.write({'state':'submitted'})
        
    def ke_accepted(self):
        if self.can_ke_confirm:
            self.write({'state':'ke_accepted','ke_confirm_verifier_id':self.env.uid,'ke_confirm_time':fields.Date.today()})
        else:
            self.write({'state':'ke_accepted','ke_verifier_id':self.env.uid,'ke_time':fields.Date.today()})
        
    def dw_accepted(self):
        self.write({'state':'dw_accepted'})
        
    def ke_confirmed(self):
        self.write({'state':'ke_confirmed','ke_confirm_verifier_id':self.env.uid,'ke_confirm_time':fields.Date.today()})
        
            
#单位月度计划内容
class pm_impl_organ_plan_content(models.Model):
    _name = 'pm.impl.organ.plan.content'
    _description = u'单位月度计划内容'

    name = fields.Char('名称', size=100, default='单位月度计划内容信息')
    dwydjh_id = fields.Many2one('pm.impl.organ.month.plan',string='单位月度计划跟踪')
    organ_id = fields.Many2one(related='dwydjh_id.organ_id',string='承担单位')
    project_id = fields.Many2one('pm.init.proj.apply',string='项目名称')
    project_num = fields.Char(related='project_id.proj_num',string='项目编号',readonly=True)
    project_category = fields.Many2one(related='project_id.proj_category',string='项目类别',readonly=True)
    start_time = fields.Date(related='project_id.proj_start_date',string='开始时间',readonly=True)
    end_time = fields.Date(related='project_id.proj_end_date',string='结束时间',readonly=True)
    jia_organ = fields.Char(related='project_id.proj_first_party',string='甲方单位',readonly=True)
    start_end_time = fields.Char(compute='_get_start_end_time',string='约定起止时间',readonly=True)
    responsible_person = fields.Char('项目负责人')
    content = fields.Text('工作内容')
    performance = fields.Text('本月完成情况')
    remark = fields.Text('备注')
    
    #获取约定起止时间 
    @api.depends('start_time','end_time')
    def _get_start_end_time(self):
        for record in self:
            record.start_end_time = record.start_time + '至' + record.end_time
    
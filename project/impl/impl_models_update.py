# -*- coding: utf-8 -*-

from openerp import models, fields, api
from openerp.osv.fields import related

'''
菜单名：实施变更
'''
#实施变更
class pm_impl_update(models.Model):
    _name = 'pm.impl.update'
    _description = u'实施变更'

    def get_project_id_domain(self):
        if self.env.uid == 1:
            return "[('proj_periods.name','=',u'实施中')]"
        return "[('proj_periods.name','=',u'实施中'),('proj_pm_uid','=',uid)]"

    name = fields.Char('变更名称',required=True)
    project_id = fields.Many2one('pm.init.proj.apply',string='项目',required=True,domain=get_project_id_domain)
    sq_organ = fields.Many2one('oa.admin.org','变更申请单位',required=True)
    change_type = fields.Many2one('sys.constant',string='变更类别',domain=[('type','=','impl_change_type')],required=True)
    change_content = fields.Text('变更内容',required=True)
    change_program = fields.Text('变更方案')
    suo_suggest = fields.Text('审批意见')
    suo_verifier_id = fields.Many2one('res.users',string='审批人')
    suo_time = fields.Date('日期')
    ke_suggest = fields.Text('审批意见')
    ke_verifier_id = fields.Many2one('res.users',string='审批人')
    ke_time = fields.Date('日期')
    jia_suggest = fields.Text('甲方意见')
    jia_attach = fields.Integer('附件')
    jia_agree = fields.Boolean('甲方是否同意')
    jia_operator = fields.Many2one('res.users',string='录入人')
    jia_time = fields.Date('日期')
    state = fields.Selection([('draft','已退回'),('submitted', '已提交'),('suo_accepted', '所(中心)已审批'),('ke_accepted', '科研处已审批'),('jia_confirmed','甲方意见已录入')] ,'审批状态')
    
    @api.depends('state')
    def _get_can_approve(self):
        for record in self:
            record.can_manager_submit = False
            record.can_suo_approve = False
            record.can_ke_approve = False
            record.can_jia_approve = False
            
            record.comp_suo_verifier_id = record.suo_verifier_id.name
            record.comp_suo_time = record.suo_time
            record.comp_ke_verifier_id = record.ke_verifier_id.name
            record.comp_ke_time = record.ke_time
            record.comp_jia_operator = record.jia_operator.name
            record.comp_jia_time = record.jia_time
            if record.state == 'draft':
                if self.env.uid == 1 :
                    record.can_manager_submit = True
                    
                if self.is_user_in_group('aqy_project.group_proj_manager'):
                    record.can_manager_submit = True
            elif record.state == 'submitted':
                if self.env.uid == 1 :
                    record.can_suo_approve = True
                    
                if self.is_user_in_group('aqy_project.group_unit_leaders'):
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
                    record.can_jia_approve = True
                    
                if self.is_user_in_group('aqy_project.group_proj_manager'):
                    record.can_jia_approve = True
                    
                if record.can_jia_approve:
                    record.comp_jia_operator = self.env['res.users'].search([('id','=',self.env.uid)]).partner_id.name
                    record.comp_jia_time = fields.Date.today()
                else:
                    if not record.jia_suggest:
                        record.comp_jia_operator = False
                        record.comp_jia_time = False
                    else:
                        record.comp_jia_operator = record.jia_operator.partner_id.name
                        record.comp_jia_time = record.jia_time
    
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
    can_ke_approve = fields.Boolean(compute='_get_can_approve',string='科研处可审批')
    can_jia_approve = fields.Boolean(compute='_get_can_approve',string='甲方意见可录入')
    
    comp_suo_verifier_id = fields.Char(compute='_get_can_approve',string='审批人',readonly=True)
    comp_suo_time = fields.Date(compute='_get_can_approve',string='日期',readonly=True)
    comp_ke_verifier_id = fields.Char(compute='_get_can_approve',string='审批人',readonly=True)
    comp_ke_time = fields.Date(compute='_get_can_approve',string='日期',readonly=True)
    comp_jia_operator = fields.Char(compute='_get_can_approve',string='录入人',readonly=True)
    comp_jia_time = fields.Date(compute='_get_can_approve',string='日期',readonly=True)
    
    def draft(self):
        if self.can_suo_approve:
            self.write({'state':'draft','suo_verifier_id':self.env.uid,'suo_time':fields.Date.today()})
        elif self.can_ke_approve:
            self.write({'state':'draft','ke_verifier_id':self.env.uid,'ke_time':fields.Date.today()})
        else:
            self.write({'state':'draft'})
        
    def submitted(self):
        self.write({'state':'submitted'})
        
    def suo_accepted(self):
        self.write({'state':'suo_accepted','suo_verifier_id':self.env.uid,'suo_time':fields.Date.today()})
        
#     def return1(self):
#         self.write({'state':'draft'})
        
    def ke_accepted(self):
        self.write({'state':'ke_accepted','ke_verifier_id':self.env.uid,'ke_time':fields.Date.today()})
        
#     def return2(self):
#         self.write({'state':'draft'})
        
    def jia_confirmed(self):
        self.write({'state':'jia_confirmed','jia_operator':self.env.uid,'jia_time':fields.Date.today()})
        
    
    

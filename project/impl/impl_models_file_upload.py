# -*- coding: utf-8 -*-

from openerp import models, fields, api

'''
菜单名：资料上传
'''
#资料上传信息表
class pm_impl_file_upload(models.Model):
    _name = 'pm.impl.file.upload'
    _description = u'资料上传信息'

    @api.onchange('check_plan_id')
    def set_project_id_domain(self):
        project_ids = []
        if self.check_plan_id:
            project_list = self.env['pm.impl.project.list'].search([('check_plan_id','=',self.check_plan_id.id)])
            for p in project_list:
                project_ids.append(p.project_id.id)
            
        if self.env.uid == 1:
            return {'domain':{'project_id':"[('id','in',"+str(project_ids)+"),('proj_periods.name','=',u'实施中')]"}}
        return {'domain':{'project_id':"[('id','in',"+str(project_ids)+"),('proj_periods.name','=',u'实施中'),('proj_pm_uid','=',uid)]"}}
            
    name = fields.Char('名称', size=100, default='资料上传信息')
    check_plan_id = fields.Many2one('pm.impl.check.plan',string='检查计划',required=True)
    project_id = fields.Many2one('pm.init.proj.apply',string='所属项目',required=True)
    file_attach_record_id = fields.One2many('pm.impl.file.attach','file_upload_id',string='附件资料')
    suo_suggest = fields.Text('审批意见')
    suo_verifier_id = fields.Many2one('res.users',string='审批人')
    suo_time = fields.Date('日期')
    ke_suggest = fields.Text('审批意见')
    ke_verifier_id = fields.Many2one('res.users',string='审批人')
    ke_time = fields.Date('日期')
    state = fields.Selection([('draft','已退回'),('submitted', '已提交'),('suo_accepted', '所(中心)已审批'),('ke_confirmed','科研处已审批')] ,string='审批状态')

    @api.depends('state')
    def _get_can_approve(self):
        for record in self:
            record.can_manager_submit = False
            record.can_suo_approve = False
            record.can_ke_confirm = False
            
            record.comp_suo_verifier_id = record.suo_verifier_id.name
            record.comp_suo_time = record.suo_time
            record.comp_ke_verifier_id = record.ke_verifier_id.name
            record.comp_ke_time = record.ke_time
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
                    record.can_ke_confirm = True
                    
                if self.is_user_in_group('aqy_project.group_impl_ky_approve'):
                    record.can_ke_confirm = True
                    
                if record.can_ke_confirm:
                    record.comp_ke_verifier_id = self.env['res.users'].search([('id','=',self.env.uid)]).partner_id.name
                    record.comp_ke_time = fields.Date.today()
                else:
                    if not record.ke_suggest:
                        record.comp_ke_verifier_id = False
                        record.comp_ke_time = False
                    else:
                        record.comp_ke_verifier_id = record.ke_verifier_id.partner_id.name
                        record.comp_ke_time = record.ke_time
    
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
    can_ke_confirm = fields.Boolean(compute='_get_can_approve',string='科研处可确认')
    
    comp_suo_verifier_id = fields.Char(compute='_get_can_approve',string='审批人',readonly=True)
    comp_suo_time = fields.Date(compute='_get_can_approve',string='日期',readonly=True)
    comp_ke_verifier_id = fields.Char(compute='_get_can_approve',string='审批人',readonly=True)
    comp_ke_time = fields.Date(compute='_get_can_approve',string='日期',readonly=True)

    def draft(self):
        if self.can_suo_approve:
            self.write({'state':'draft','suo_verifier_id':self.env.uid,'suo_time':fields.Date.today()})
        elif self.can_ke_confirm:
            self.write({'state':'draft','ke_verifier_id':self.env.uid,'ke_time':fields.Date.today()})
        else:
            self.write({'state':'draft'})
        
    def submitted(self):
        self.write({'state':'submitted'})
        
    def suo_accepted(self):
        self.write({'state':'suo_accepted','suo_verifier_id':self.env.uid,'suo_time':fields.Date.today()})
        
    def ke_confirmed(self):
        self.write({'state':'ke_confirmed','ke_verifier_id':self.env.uid,'ke_time':fields.Date.today()})
     
    
#资料附件表
class pm_impl_file_attach(models.Model):
    _name = 'pm.impl.file.attach'
    _description = u'资料附件'
    
    name = fields.Char('资料名称')
    attach = fields.Integer('附件')
    remark = fields.Text('说明')
    file_upload_id = fields.Many2one('pm.impl.file.upload',string='资料上传信息')


# -*- coding: utf-8 -*-

from openerp import models, fields, api

'''
菜单名：归档结果
'''
#归档结果
class pm_archives_project_archives(models.Model):
    _name = 'pm.archives.project.archives'
    _description = u'归档结果'
    
    
    @api.onchange('project_id')
    def change_project_id(self):
        for record in self:
            proj_pm_uid = record.project_id.proj_pm_uid
            if proj_pm_uid:
                record.manager_id = self.env['res.users'].search([('id','=',proj_pm_uid)])
                record.comp_manager_id = record.manager_id.partner_id.name

    def get_project_id_domain(self):
        if self.env.uid == 1:
            return "[('proj_periods.name','=',u'实施中')]"
        return "[('proj_periods.name','=',u'实施中'),('proj_pm_uid','=',uid)]"
    
    name = fields.Char('名称', size=100, default='项目归档信息')
    project_id = fields.Many2one('pm.init.proj.apply',string=u'项目',required=True,domain=get_project_id_domain)
    source = fields.Char(related='project_id.proj_first_party',string=u'项目来源',readonly=True)
    organ_id = fields.Many2one(related='project_id.proj_vld',string=u'承担单位',required=True,readonly=True)
    manager_id = fields.Many2one('res.users',string=u'项目经理')
    comp_manager_id = fields.Char(compute='change_project_id',string=u'项目经理',readonly=True)

    archives_transfer_paper = fields.Integer(string=u'档案交接文据')
    
    title = fields.Char(string=u'题名')
    archives_number = fields.Char(string=u'档号')
    file_number = fields.Char(string=u'文件编号')
    copies_number = fields.Integer(string=u'份数')
    pages_number = fields.Integer(string=u'页数')
    responsible = fields.Many2one('oa.admin.org',string=u'责任者')
    date = fields.Date(string=u'日期')
    security_level = fields.Char(string=u'密级')
    deadline = fields.Char(string=u'期限')
    electronic_document_number = fields.Integer(string=u'电子文件数')
    remark = fields.Text(string=u'备注')
    
    state = fields.Selection([('draft',u'草稿'),('submitted', u'已提交'),('suo_accepted', u'所(中心)已审批')],u'审批状态')
    
    @api.model
    @api.returns('self', lambda value:value.id)
    def create(self, vals):
        return models.Model.create(self, vals)
    
    @api.multi
    def write(self, vals):
        return models.Model.write(self, vals)
    
    @api.depends('state')
    def _get_can_approve(self):
        for record in self:
            record.can_manager_submit = False
            record.can_suo_approve = False
            
            record.comp_suo_verifier_id = record.suo_verifier_id.name
            record.comp_suo_time = record.suo_time
            if record.state == 'draft':
                if self.env.uid == 1:
                    record.can_manager_submit = True
                    
                if self.is_user_in_group('aqy_project.group_proj_manager') and record.project_id.proj_pm_uid == self.env.uid:
                    record.can_manager_submit = True
            elif record.state == 'submitted':
                if self.env.uid == 1:
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
    
    comp_suo_verifier_id = fields.Char(compute='_get_can_approve',string=u'审批人',readonly=True)
    comp_suo_time = fields.Date(compute='_get_can_approve',string=u'日期',readonly=True)

    
#所(中心)审批
    suo_suggest = fields.Text(u'审批意见')
    suo_verifier_id = fields.Many2one('res.users',string=u'审批人')
    suo_time = fields.Date(u'日期')
    
    
    def draft(self):
        if self.can_suo_approve:
            self.write({'state':'draft','suo_verifier_id':self.env.uid,'suo_time':fields.Date.today()})
        else:
            self.write({'state':'draft'})
         
    def submitted(self):
        self.write({'state':'submitted'})
         
    def suo_accepted(self):
        self.write({'state':'suo_accepted','suo_verifier_id':self.env.uid,'suo_time':fields.Date.today()})
 
    
    
    
class pm_archives_project_archives_directory(models.Model):
    _name = 'pm.archives.project.archives.directory'
    _description = u'企业档案目录'
    
    project_archives_id = fields.Many2one('pm.archives.project.archives',string=u'项目归档')
    title = fields.Char(string=u'题名')
    archives_number = fields.Char(string=u'档号')
    file_number = fields.Char(string=u'文件编号')
    copies_number = fields.Integer(string=u'份数')
    pages_number = fields.Integer(string=u'页数')
    responsible = fields.Many2one('oa.admin.org',string=u'责任者')
    date = fields.Date(string=u'日期')
    security_level = fields.Char(string=u'密级')
    deadline = fields.Char(string=u'期限')
    electronic_document_number = fields.Integer(string=u'电子文件数')
    remark = fields.Text(string=u'备注')
    

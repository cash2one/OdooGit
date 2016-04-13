# -*- coding: utf-8 -*-

from openerp import models, fields, api
from openerp.tools.translate import _
from openerp.osv import osv

'''
菜单名：检查计划
'''
#检查计划信息表
class pm_impl_check_plan(models.Model):
    _name = 'pm.impl.check.plan'
    _description = u'检查计划'
    
    def get_show_notice_button(self):
        for record in self:
            record.show_notice_button = False
            for a in record.inform_officer_record_id:
                if a.name.id == self.env.uid:
                    if a.receive == False:
                        record.show_notice_button = True
                    break
    
    name = fields.Char('检查计划名称',required=True)
    check_type = fields.Many2one('sys.constant',string='检查类型',domain=[('type','=','impl_check_type')],required=True)
    check_time = fields.Date('检查日期',required=True)
    check_mode = fields.Many2one('sys.constant',string='检查形式',domain=[('type','=','impl_check_mode')],required=True)
    expert_group = fields.Char('专家组')
    other_requirement = fields.Text('其他要求')
    project_list_record_id = fields.One2many('pm.impl.project.list','check_plan_id',string='项目清单',required=True)
    check_file_record_id = fields.One2many('pm.impl.file.list','check_plan_id',string='资料清单',required=True)
    inform_officer_record_id = fields.One2many('pm.impl.inform.officer','check_plan_id',string='通知人员',required=True)
    show_notice_button = fields.Boolean(compute='get_show_notice_button',string='是否显示收到通知按钮',default=False)
    @api.multi
    def confirm_receive(self,vals):
        uid = vals['uid']
        self.env.cr.execute('update pm_impl_inform_officer set receive = True where name = \'' + str(uid) + '\'')
    
    @api.model
    @api.returns('self', lambda value:value.id)
    def create(self, vals):
        if len(vals['project_list_record_id']) == 0:
            raise osv.except_osv(_('Error!'), _('项目清单不能为空！'))
        return models.Model.create(self, vals)
    
    @api.multi
    def write(self, vals):
        res = models.Model.write(self, vals)
        if len(self.project_list_record_id) == 0:
            raise osv.except_osv(_('Error!'), _('项目清单不能为空！'))
        return res
#项目清单
class pm_impl_project_list(models.Model):
    _name = 'pm.impl.project.list'
    _description = u'项目清单'
    
    name = fields.Char('名称', size=100, default='项目清单')
    check_plan_id = fields.Many2one('pm.impl.check.plan','检查计划')
    project_id = fields.Many2one('pm.init.proj.apply','项目',domain=[('proj_periods.name','=','实施中')])
    
#资料清单
class pm_impl_file_list(models.Model):
    _name = 'pm.impl.file.list'
    _description = u'资料清单'
    
    name = fields.Char('名称', size=100, default='资料清单')
    check_plan_id = fields.Many2one('pm.impl.check.plan','检查计划')
    name = fields.Char('资料名称')
    requirement = fields.Char('要求')
    template = fields.Integer('模板')
    
#通知人员
class pm_impl_inform_officer(models.Model):
    _name = 'pm.impl.inform.officer'
    _description = u'通知人员'
    
    name = fields.Char('名称', size=100, default='通知人员')
    check_plan_id = fields.Many2one('pm.impl.check.plan','检查计划')
    name = fields.Many2one('res.users',string='姓名')
    receive = fields.Boolean('是否收到',readonly=True)
    
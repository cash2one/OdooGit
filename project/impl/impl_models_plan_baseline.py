# -*- coding: utf-8 -*-

'''
菜单名：计划基线
'''
#检查计划信息表

import time

from openerp import models, fields, api
from openerp.tools.translate import _
from openerp.osv import osv
from lxml import etree


class pm_impl_plan_baseline(models.Model):
    _name = 'pm.impl.plan.baseline'
    _description = u'计划基线'
    _sql_constraints = [
        ('unique_key', 'UNIQUE (project_id,version_number)',  '版本号已被使用!')
    ]
    
    def _get_default_active_state(self):
        return self.env['sys.constant'].search([('type','=','impl_active_state'),('name','=','当前有效')])
    
    @api.onchange('project_id')
    def _get_default_version_info(self):
        for record in self:
            latest_version_info = self.env['pm.impl.plan.baseline.version'].search([('quarter_plan_gz_id.project_id','=',record.project_id.id),('plan_baseline_id.active_state.name','=',u'当前有效')])
            record.plan_baseline_version_info_record_id = latest_version_info

    def get_project_id_domain(self):
        if self.env.uid == 1:
            return "[('proj_periods.name','=',u'实施中')]"
        return "[('proj_periods.name','=',u'实施中'),('proj_pm_uid','=',uid)]"
    
    name = fields.Char('名称', size=100, default='计划基线信息')
    project_id = fields.Many2one('pm.init.proj.apply',string='项目',required=True,domain=get_project_id_domain)
    version_number = fields.Char('版本号',required=True)
    active_state = fields.Many2one('sys.constant',string='使用状态',domain=[('type','=','impl_active_state')],default=_get_default_active_state,readonly=True)
    version_yj = fields.Many2one('pm.impl.update',string='版本依据',domain="[('state','=','jia_confirmed'),('project_id','=',project_id),('change_type.name','=','计划变更')]")
    plan_baseline_version_info_record_id = fields.One2many('pm.impl.plan.baseline.version','plan_baseline_id',string='版本详细信息',required=True)
    flag = fields.Boolean(string='用于判断create的方式',default=False)
    
    
    def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
        res =  models.Model.fields_view_get(self, cr, uid, view_id=view_id, view_type=view_type, context=context, toolbar=toolbar, submenu=submenu)
        if uid != 1 and res['type']=="form" :  
            if self.is_user_in_group(cr,uid,'aqy_project.group_unit_leaders',context):  
                doc = etree.XML(res['arch'])  
                doc.xpath("//form")[0].set("edit","false")
                doc.xpath("//form")[0].set("create","false")
                doc.xpath("//form")[0].set("delete","false")
                res['arch']=etree.tostring(doc) 
        if uid != 1 and res['type']=="tree" :  
            if self.is_user_in_group(cr,uid,'aqy_project.group_unit_leaders',context):  
                doc = etree.XML(res['arch'])  
                doc.xpath("//tree")[0].set("edit","false")
                doc.xpath("//tree")[0].set("create","false")
                doc.xpath("//tree")[0].set("delete","false")
                res['arch']=etree.tostring(doc) 
        return res
    
    
    #判断当前用户是否是指定的权限组内
    @api.model
    def is_user_in_group(self,group_str):
        g_res = self.env.ref(group_str)
        if g_res:
            self.env.cr.execute('select count(1) from res_groups_users_rel where uid={0} and gid={1}'.format(self.env.uid,g_res.id))
            res = self.env.cr.fetchone()
            if res and res[0]>0:
                return True
        return False
    
    @api.model
    @api.returns('self', lambda value:value.id)
    def create(self, vals):
        if vals['flag']:
            return models.Model.create(self, vals)
        else:
            history_active_state = self.env['sys.constant'].search([('type','=','impl_active_state'),('name','=','历史版本')])
            new_active_state = self.env['sys.constant'].search([('type','=','impl_active_state'),('name','=','当前有效')])
            #创建新的基本信息
            new_project_id = vals['project_id']
            new_version_number = vals['version_number']
            new_version_yj = vals['version_yj']
            
            old_plan_baseline = self.env['pm.impl.plan.baseline'].search([('project_id','=',new_project_id),('active_state','=',new_active_state.id)])
            old_plan_baseline.write({'active_state':history_active_state.id})
            
            new_main = self.env['pm.impl.plan.baseline'].create({'project_id':new_project_id,'version_number':new_version_number,'version_yj':new_version_yj,'active_state':new_active_state.id,'flag':True})
            
            #版本信息
            version_info = vals['plan_baseline_version_info_record_id']
            #[[4, 1, False], [4, 50, False]]
            has_no_change = True
            for param_list in version_info:
                id = param_list[1]
                value = param_list[2]
                #修改原记录状态为"历史版本"
                old_record = self.env['pm.impl.plan.baseline.version'].search([('id','=',id)])
                if value:
                    #复制修改原记录得到新记录
                    self.env['pm.impl.plan.baseline.version'].create({'quarter_plan_gz_id':old_record.quarter_plan_gz_id.id,'plan_baseline_id':new_main.id,'year':old_record.year.id,'quarter':old_record.quarter.id,'plan_content':value['plan_content'],'performance':old_record.performance,'remark':old_record.remark})
                    has_no_change = False
                else:
                    self.env['pm.impl.plan.baseline.version'].create({'quarter_plan_gz_id':old_record.quarter_plan_gz_id.id,'plan_baseline_id':new_main.id,'year':old_record.year.id,'quarter':old_record.quarter.id,'plan_content':old_record.plan_content,'performance':old_record.performance,'remark':old_record.remark})
            if has_no_change:
                raise osv.except_osv(_('Error!'), _('计划内容没有更改！'))
            #保存版本详细信息
            return new_main
            
    
    
#版本详细信息
class pm_impl_plan_baseline_version(models.Model):
    _name = 'pm.impl.plan.baseline.version'
    _description = u'版本详细信息'
    
    #只能当前系统时间以后的季度可以变更基线
    @api.depends('year','quarter')
    def check_year_quarter(self):
        for record in self:
            if record.year and record.quarter:
                sys_time = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(time.time()))
                sys_year = int(sys_time[0:4])
                sys_month = int(sys_time[5:7])
                edit_year = int(record.year.name)
                edit_quarter = record.quarter.name
                if edit_year < sys_year:
                    record.can_edit = False
                elif edit_year == sys_year:
                    if sys_month <= 3:
                        if edit_quarter == u'第一季度':
                            record.can_edit = False
                        else:
                            record.can_edit = True
                    elif sys_month <=6:
                        if edit_quarter == u'第一季度' or edit_quarter == u'第二季度':
                            record.can_edit = False
                        else:
                            record.can_edit = True
                    elif sys_month <=9:
                        if edit_quarter == u'第一季度' or edit_quarter == u'第二季度' or edit_quarter == u'第三季度':
                            record.can_edit = False
                        else:
                            record.can_edit = True
                    elif sys_month <=12:
                        record.can_edit = False
                else:
                    record.can_edit = True
    
    quarter_plan_gz_id = fields.Many2one('pm.impl.quarter.plan',string='季度计划主信息')
    plan_baseline_id = fields.Many2one('pm.impl.plan.baseline',string='计划基线')
    year = fields.Many2one('sys.constant',string='年份',domain=[('type','=','year')],required=True,readonly=True)
    quarter = fields.Many2one('sys.constant',string='季度',domain=[('type','=','quarter')],required=True,readonly=True)
    plan_content = fields.Text('研究内容',required=True)
    performance = fields.Text('完成情况')
    remark = fields.Text('备注')
    can_edit = fields.Boolean(compute='check_year_quarter',string='是否可编辑')
    
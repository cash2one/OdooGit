# -*- coding: utf-8 -*-

from openerp import models, fields, api
from openerp.tools.translate import _
from openerp.osv import osv
from lxml import etree

'''
菜单名：人员基线
'''
#检查计划信息表
class pm_impl_staff_baseline(models.Model):
    _name = 'pm.impl.staff.baseline'
    _description = u'人员基线'
    _sql_constraints = [
        ('unique_key', 'UNIQUE (project_id,version_number)',  '版本号已被使用!')
    ]
    
    def _get_default_active_state(self):
        return self.env['sys.constant'].search([('type','=','impl_active_state'),('name','=','当前有效')])

    @api.onchange('project_id')
    def _get_default_version_info(self):
        for record in self:
            latest_version_info = self.env['pm.impl.staff.baseline.version'].search([('staff_baseline_id.project_id','=',record.project_id.id),('staff_baseline_id.active_state.name','=',u'当前有效')])
            record.staff_baseline_version_info_record_id = latest_version_info
        

    def get_project_id_domain(self):
        if self.env.uid == 1:
            return "[('proj_periods.name','=',u'实施中')]"
        return "[('proj_periods.name','=',u'实施中'),('proj_pm_uid','=',uid)]"
    
    name = fields.Char('名称', size=100, default='人员基线信息')
    project_id = fields.Many2one('pm.init.proj.apply',string='项目',required=True,domain=get_project_id_domain)
    version_number = fields.Char('版本号',required=True)
    active_state = fields.Many2one('sys.constant',string='使用状态',domain=[('type','=','impl_active_state')],default=_get_default_active_state,readonly=True)
    version_yj = fields.Many2one('pm.impl.update',string='版本依据',domain="[('state','=','jia_confirmed'),('project_id','=',project_id),('change_type.name','=','人员变更')]")
    staff_baseline_version_info_record_id = fields.One2many('pm.impl.staff.baseline.version','staff_baseline_id',string='版本详细信息',required=True)
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
            
            #修改原记录状态为"历史版本"
            old_staff_baseline = self.env['pm.impl.staff.baseline'].search([('project_id','=',new_project_id),('active_state','=',new_active_state.id)])
            old_staff_baseline.write({'active_state':history_active_state.id})
            
            new_main = self.env['pm.impl.staff.baseline'].create({'project_id':new_project_id,'version_number':new_version_number,'version_yj':new_version_yj,'active_state':new_active_state.id,'flag':True})
            
            #版本信息
            version_info = vals['staff_baseline_version_info_record_id']
            
            has_no_change = True
            pm_id=self.env['oa.project.role'].search([('name','=',u'项目经理')]).id
            find_manager = False
            for param_list in version_info:
                id = param_list[1]
                value = param_list[2]
                old_record = self.env['pm.impl.staff.baseline.version'].search([('id','=',id)])
                new_staff_id = old_record.staff.id
                new_role_id = old_record.role.id
                if value:
                    #复制修改原记录得到新记录
                    if value.has_key('staff'):
                        new_staff_id = value['staff']
                        
                    if value.has_key('role'):
                        new_role_id = value['role']
                        
                    if not find_manager and new_role_id == pm_id:
                        find_manager = True
                        self.env.cr.execute('update pm_init_proj_apply set proj_pm_uid = ' + str(new_staff_id) + ' where id = ' + str(new_project_id))
                        
                    self.env['pm.impl.staff.baseline.version'].create({'staff_baseline_id':new_main.id,'staff':new_staff_id,'role':new_role_id})
                    has_no_change = False
                else:
                    if param_list[0] == 4:
                        self.env['pm.impl.staff.baseline.version'].create({'staff_baseline_id':new_main.id,'staff':new_staff_id,'role':new_role_id})
                        
                        if not find_manager and new_role_id == pm_id:
                            find_manager = True
                            self.env.cr.execute('update pm_init_proj_apply set proj_pm_uid = ' + str(new_staff_id) + ' where id = ' + str(new_project_id))
                    else:
                        has_no_change = False
            
            if not find_manager:
                raise osv.except_osv(_('Error!'), _('人员信息中没有项目经理！'))
                
            if has_no_change:
                raise osv.except_osv(_('Error!'), _('人员信息没有更改！'))
            return new_main
    
#版本详细信息
class pm_impl_staff_baseline_version(models.Model):
    _name = 'pm.impl.staff.baseline.version'
    _description = u'版本详细信息'
    
    staff_baseline_id = fields.Many2one('pm.impl.staff.baseline',string='人员基线')
    project_id = fields.Many2one(related='staff_baseline_id.project_id',string='项目',store=True)
    staff = fields.Many2one('res.users',string='参与人员',required=True)
    role = fields.Many2one('oa.project.role', string='项目角色')

# -*- coding: utf-8 -*-

from openerp import models, fields, api
from docutils.nodes import comment

# 项目组织机构
class project_org(models.Model):

    _name='oa.project.org'
    _description=u"项目组织机构表"
    _order='complete_name asc'
    
    def _dept_name_get_fnc(self, cr, uid, ids, prop, unknow_none, context=None):
        res = self.name_get(cr, uid, ids, context=context)
        return dict(res)
    
    def name_get(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        if not ids:
            return []
        reads = self.read(cr, uid, ids, ['name','parent_id'], context=context)
        res = []
        for record in reads:
            name = record['name']
            if record['parent_id']:
                name = record['parent_id'][1]+' / '+name
            res.append((record['id'], name))
        return res
        
    name= fields.Char('项目组', required=True)
    #complete_name= fields.Char(compute='_dept_name_get_fnc', string='全路径', store=True)
    parent_id= fields.Many2one('oa.project.org', '上级项目组', select=True)
    child_ids= fields.One2many('oa.project.org', 'parent_id', '下级项目组')
    supervisor = fields.Many2one('oa.staff.basic', string='主管领导')
    
    _columns={
        'complete_name': fields.fields.function(_dept_name_get_fnc, type="char", string='全路径',store=True),
        }

# 项目角色
class project_role(models.Model):
    _name='oa.project.role'
    _description=u"项目角色表"
    
    name= fields.Char('项目角色名称', required=True)

# 行政组织机构
class admin_org(models.Model):
    _name='oa.admin.org'
    _description=u"行政组织机构表"
    _order='complete_name asc'
    
    def _admin_org_name_get_fnc(self, cr, uid, ids, prop, unknow_none, context=None):
        res = self.name_get(cr, uid, ids, context=context)
        return dict(res)
    
    name= fields.Char('行政组织机构名称', required=True)
    #complete_name= fields.Char(compute='_admin_org_name_get_fnc', string='全路径')
    parent_id= fields.Many2one('oa.admin.org', '上级行政组织机构', select=True)
    child_ids= fields.One2many('oa.admin.org', 'parent_id', '下级行政组织机构')

    _columns={
        'complete_name': fields.fields.function(_admin_org_name_get_fnc, type="char", string='全路径',store=True),
        }
     
    def name_get(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        if not ids:
            return []
        reads = self.read(cr, uid, ids, ['name','parent_id'], context=context)
        res = []
        for record in reads:
            name = record['name']
            if record['parent_id']:
                name = record['parent_id'][1]+' / '+name
            res.append((record['id'], name))
        return res
    
# 行政组织角色
class admin_role(models.Model):
    _name='oa.admin.role'
    _description=u"行政组织角色表"
    
    name= fields.Char('行政角色名称', required=True)
 
# 外协组织机构
class outsourcing_org(models.Model):
    _name='oa.outsourcing.org'
    _description=u"外协组织机构表"
    
    name= fields.Char('外协名称', required=True)
    outsourcing_contact_ids= fields.One2many('oa.outsourcing.contact', 'outsourcing_id', string="外协联系方式")
 
# 外协联系方式
class outsourcing_contact(models.Model):
    _name='oa.outsourcing.contact' 
    _description=u"外协联系方式表"
    
    contacter= fields.Char('联系人',required=True)
    email=fields.Char('邮箱')
    contacter_phone=fields.Char('联系人手机')
    contacter_landline=fields.Char('联系人座机')    
    outsourcing_id=fields.Many2one('oa.outsourcing.org',string='外协')

#会议室配置
class boardroom(models.Model):
    _name='oa.boardroom'
    _description=u"会议室配置" 
    
    name=fields.Char('会议室房间号',size=100,required=True)
    
#院科研生产管理系统科目表
class pm_common_subject(models.Model):
    _name='pm.common.subject'
    _description=u"经费科目表"
    
    sn = fields.Integer('排序序号')
    #show_sn = fields.Integer('表格显示序号')
    name = fields.Char('科目名称', size=50, required=True)
    #type = fields.Selection([('use_apply','使用申请科目'),('gj','国家级科研项目预算科目'),('jtgf','集团股份科研项目预算科目'),('xx','集团统建信息科研项目预算科目')], string="科目类型", required=True)
    parent_id = fields.Many2one('pm.common.subject', '上级科目')
    is_leaf = fields.Boolean('是否叶子节点')

#常量表 
class sys_constant(models.Model):
    _name = 'sys.constant'
    _description = u'常量表'
    _sql_constraints = [
        ('unique_key', 'UNIQUE (name,type)',  '常量重复，请检查!')
    ]
    
    name = fields.Char('常量名称', size=50)
    type = fields.Char('常量类型', size=50)
    parent_id = fields.Many2one('sys.constant', '父常量')
    comment = fields.Char('描述', size=200)        
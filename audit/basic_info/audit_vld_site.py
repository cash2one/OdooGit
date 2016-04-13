# -*- coding: utf-8 -*-

from openerp import models, fields, api

class audit_vld_site(models.Model):
    _name = 'audit.vld.site'
    _description = u"组织机构表"
        
    name = fields.Char(u'单位名称', required=True)
    code = fields.Char(u'单位编码', required=True)
    enterprise = fields.Many2one('audit.vld.site', u'所属企业')
    parent_id = fields.Many2one('audit.vld.site', u'上级单位')
    child_ids= fields.One2many('audit.vld.site', 'parent_id', u'下级单位')
    state = fields.Selection([('active',u'活动'),('inactive',u'不活动'),('deleted',u'已删除'),('merged',u'已合并')], u'状态')
    duty = fields.Text(u'部门职能')
    audit_plan_ids = fields.One2many('audit.plan.info', 'enterprise_id', u'审核计划')
    
    #获取所有组织机构（单位）列表
    #created by wangkui
    def get_Site(self):
        
        site = self.search([('parent_id','=', False)])
        result = []
        for rec in site:
            id = rec.id
            obj = {}
            obj['SITE_ID'] = rec.id
            obj['SITE_NAME'] = rec.name
            obj['PARENT_ID'] = ''
            obj['rows'] = self.get_subSite(id)
            result.append(obj)
        return result
    
    def get_subSite(self, parent_id):
        site = self.search([('parent_id','=', parent_id)])
        rows = []
        for rec in site:
            id = rec.id
            obj = {}
            obj['SITE_ID'] = rec.id
            obj['SITE_NAME'] = rec.name
            obj['PARENT_ID'] = ''
            obj['rows'] = self.get_subSite(id)
            rows.append(obj)
        return rows
        
class audit_vld_site_workstation_relation(models.Model):
    _name = 'audit.vld.site.workstation.relation'
    _description = u'组织结构与工作站关系表'
    
    audit_vld_site_id = fields.Many2one('audit.vld.site', u'单位')
    workstation_id = fields.Many2one('sys.constant', domain=[('type','=','audit_org')], string=u'工作站')
        
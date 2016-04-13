# -*- coding: utf-8 -*-

from openerp import models, fields, api
from openerp.osv.fields import related

'''
菜单名：过程文档
'''
#月度计划信息表
class pm_impl_procedural_document(models.Model):
    _name = 'pm.impl.procedural.document'
    _description = u'过程文档'

    def get_project_id_domain(self):
        if self.env.uid == 1:
            return "[('proj_periods.name','=',u'实施中')]"
        return "[('proj_periods.name','=',u'实施中'),('proj_pm_uid','=',uid)]"
    
    name = fields.Char('文档名称',required=True)
    project_id = fields.Many2one('pm.init.proj.apply',string='所属项目',required=True,domain=get_project_id_domain)
    manager_id = fields.Integer(related='project_id.proj_pm_uid',string=u'项目经理id',readonly=True)
    document_type = fields.Many2one('sys.constant',string='文档类型',domain=[('type','=','impl_document_type')],required=True)
    content_zy = fields.Text('内容摘要')
    document_version_record_id = fields.One2many('pm.impl.version.info','procedural_document_id',string='版本信息')

    
#版本信息
class pm_impl_version_info(models.Model):
    _name = 'pm.impl.version.info'
    _description = u'版本信息'
    
    number = fields.Char('版本号',required=True)
    operator = fields.Many2one('res.users',string='修改人',required=True)
    remark = fields.Text('修改说明')
    attach = fields.Integer('附件')
    procedural_document_id = fields.Many2one('pm.impl.procedural.document',string='过程文档')

# -*- coding: utf-8 -*-

from openerp import models, fields, api

class pm_techservice_document(models.Model):
    _name = 'pm.techservice.document'
    _description = u"外协文档管理"
    _sql_constraints = [
        ('unique_key', 'UNIQUE (name,proj_id)',  '外协项目已存在!')
    ]
    
    #获取最后一次修改时间
    @api.depends()
    def _get_last_modify_info(self):
        for record in self:
            for version in record.version_ids:
                if record.last_modify_time<=version.modify_date:
                    record.last_modify_time = version.modify_date
                    record.latest_version = version.version_num
        
    name = fields.Char('文档名称', size=50, required=True)
    proj_id = fields.Many2one('pm.techservice.init', string='外协任务名称', required=True)
    parent_proj = fields.Many2one(related='proj_id.name.ht_id.plan_id.wx_plan_check_result.parent_proj', string='外协任务所属项目', readonly=True, store=True)
    client = fields.Many2one(related='proj_id.client', string="委托单位", store=True, readonly=True) 
    bear_vld = fields.Char(related='proj_id.bear_vld', string='承担单位', store=True, readonly=True) 
    document_type = fields.Many2one('sys.constant', string='文档类型', domain=[('type','=','impl_document_type')])
    content = fields.Text('内容摘要')
    version_ids = fields.One2many('pm.techservice.document.version', 'document_id', string='外协文档版本')
    last_modify_time = fields.Date(compute='_get_last_modify_info', string='最后修改时间')
    latest_version = fields.Float(compute='_get_last_modify_info', string='最新版本')
    
class pm_techservice_document_version(models.Model):
    _name = 'pm.techservice.document.version'
    _description = u"外协文档版本"
    _sql_constraints = [
        ('unique_key', 'UNIQUE (version_num,document_id)', '版本已存在!')
    ]
     
    #获取默认的修改人
    def _get_default_modify_person(self):
        return self.env.uid
     
    def _get_default_modify_date(self):
        return fields.date.today()
     
    version_num = fields.Float('版本号', digits=(3,1), required=True)
    modify_person = fields.Many2one('res.users', string='修改人', default=_get_default_modify_person)
    modify_date = fields.Date('修改日期', default=_get_default_modify_date)
    modify_content = fields.Text('修改说明')
    attachment = fields.Integer('附件', required=True)
    document_id = fields.Many2one('pm.techservice.document', string='外协项目文档')
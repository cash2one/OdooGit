# -*- coding: utf-8 -*-

from openerp import models, fields, api

class audit_standard(models.Model):
    _name = 'audit.standard'
    _description = u"审核标准表"
        
    name = fields.Char(u'名称', required=True)
    type = fields.Many2one('sys.constant', domain=[('type','=','audit_type')], string=u'审核类型')
    parent_id = fields.Many2one('audit.standard', u'上级审核项')
    child_ids= fields.One2many('audit.standard', 'parent_id', u'下级审核项')
    is_valid = fields.Many2one('sys.constant', domain=[('type','=','audit_standard_validation')], string=u'是否有效')
    score = fields.Integer(u'分值')
    level_name=fields.Char(u'层级名称')
    seq = fields.Integer(u'同层节点顺序')
    level = fields.Integer(u'节点层级', readyonly=True)
    description = fields.Char(u'说明')
    
    audit_standard_ovaplan_ids = fields.One2many('audit.ovaplan.standard', 'standard_id', u'审核方案标准')
    audit_standard_plan_ids = fields.One2many('audit.plan.standard', 'standard_id', u'审核计划标准')
    score_standard_ids = fields.One2many('audit.score.info', 'standard_id', u'评分标准')
    
    @api.onchange('parent_id')
    def _on_change_parent_id(self):
        if (self.parent_id):
            self.level = self.env['audit.standard'].search([('id','=',self.parent_id.id)]).level + 1
        else:
            self.level = 1
    #获取层级信息
    #def _get_standard_level(self):
    #    if self.parent_id:
     #       self.level = self.env['audit.standard'].search([('id','=',self.parent_id.id)]).level + 1
     #   else:
     #       self.level = 1
    
    #获取同级次序
    #@api.depends('parent_id')
    #def _get_seq(self):
    #    if not self.seq:
    #        self.seq = len(self.env['audit.standard'].search([('parent_id','=',self.parent_id.id)]))
     #   else:
     #       self.seq = self.seq
    
    #获取所有审核标准元素（内容）
    @api.model
    def get_all_standards(self, type):
        sql_std_by_type = '''
                        select id, name, level_name, parent_id, seq from audit_standard where type='{0}'
                          '''
        sql_std_by_type = sql_std_by_type.format(type)
        self.env.cr.execute(sql_std_by_type)
        ret_std = []
        for row in self.env.cr.fetchall():
            item = {}
            item['id'] = row[0]
            item['text'] = row[1]
            item['levelname'] = row[2]
            item['parentid'] = row[3]
            item['seq'] = row[4]
            item['value'] = 0
            item['showcheck'] = True
            item['complete'] = True
            item['isexpand'] = False
            item['checkstate'] = 0
            item['hasChildren'] = False
            ret_std.append(item)
        
        ret = {}
        ret["l_std"] = ret_std
        return ret 
    
    def get_all_std_to_tree(self):
        standards = self.search([('parent_id','=', False)])
        result = []
        for rec in standards:
            id = rec.id
            obj = {}
            obj['CATEGORY_ID'] = str(rec.id)
            obj['CATEGORY_NAME'] = rec.name
            obj['PARENT_ID'] = ''
            obj['rows'] = self._get_child_std(id)
            result.append(obj)
        return result
    
    def _get_child_std(self,parent_id):
        site = self.search([('parent_id','=', parent_id)])
        rows = []
        for rec in site:
            id = rec.id
            obj = {}
            obj['CATEGORY_ID'] = str(rec.id)
            obj['CATEGORY_NAME'] = rec.name
            obj['PARENT_ID'] = str(parent_id)
            obj['rows'] = self._get_child_std(id)
            rows.append(obj)
        return rows
    
    #获取标准的树形结构数据
    def get_all_standard_to_tree(self, type):
        standards = self.search([('parent_id','=', False),('type','=',type)])
        result = []
        for rec in standards:
            id = rec.id
            obj = {}
            obj['CATEGORY_ID'] = str(rec.id)
            obj['CATEGORY_NAME'] = rec.name
            obj['PARENT_ID'] = ''
            obj['rows'] = self._get_child_standards(id, type)
            result.append(obj)
        return result
    
    def _get_child_standards(self,parent_id, type):
        site = self.search([('parent_id','=', parent_id),('type','=',type)])
        rows = []
        for rec in site:
            id = rec.id
            obj = {}
            obj['CATEGORY_ID'] = str(rec.id)
            obj['CATEGORY_NAME'] = rec.name
            obj['PARENT_ID'] = str(parent_id)
            obj['rows'] = self._get_child_standards(id, type)
            rows.append(obj)
        return rows
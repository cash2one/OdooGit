# -*- coding: utf-8 -*-

'''
Created on 2016-3-30

@author: WangKui
'''

from openerp import http
from openerp import models, fields
import audit_record

class audit_record_category_relation(models.Model):
    _name = 'audit.record.category.relation'
    _description = u'问题记录与类型的关联表'
    
    quecategory_id = fields.Char(u'归类表code')
    record_id = fields.Many2one('audit.record', u'问题记录id')
    category_id = fields.Many2one('audit.standard', u'问题类型id')
    
    
    #获取当前人员所有问题记录列表
    #created by wangkui
    def get_Record_Category_Relation(self, user_id, plan_id):
        result = []
        record_list = audit_record.audit_record.get_Recordlist(http.request.env['audit.record'],user_id, plan_id)
        for record_id in record_list:
            site = self.search([('record_id','=', record_id)])
            for rec in site:
                obj = {}
                obj['QUECATEGORY_ID'] = rec.quecategory_id
                obj['CATEGORY_ID'] = str(rec.category_id.id)
                obj['RECORD_ID'] = rec.record_id.record_id
                obj['RowActionState'] = '2'
                result.append(obj)
        return result
    
    #新建编辑问题分类
    #created by wangkui
    def set_CategoryList(self, category_list):
        for item in category_list:
            if item.has_key("QUECATEGORY_ID") \
            and item.has_key("CATEGORY_ID") and item["CATEGORY_ID"].isdigit()\
            and item.has_key("RECORD_ID") \
            and item.has_key("RowActionState") and item["RowActionState"].isdigit():
                record_id = self.env['audit.record'].search([('record_id', '=', item["RECORD_ID"])]).id
                if not record_id:
                    continue
                data = {}
                data["quecategory_id"] = item["QUECATEGORY_ID"]
                data["category_id"] = int(item["CATEGORY_ID"])
                data["record_id"] = record_id
                if item["RowActionState"] == "2":
                    org_data = self.search([('quecategory_id','=', item["QUECATEGORY_ID"])])
                    org_data.write(data)
                elif item["RowActionState"] == "1":
                    self.create(data)
                elif item["RowActionState"] == "3":
                    org_data = self.search([('quecategory_id','=', item["QUECATEGORY_ID"])])
                    sql_delete_relation = "delete from audit_record_category_relation where id = " + str(org_data.id)
                    print sql_delete_relation
                    http.request.env.cr.execute(sql_delete_relation)
    
    
    
    
    
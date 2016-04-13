# -*- coding: utf-8 -*-

'''
Created on 2016-3-28

@author: WangKui
'''

from openerp import models, fields, http, api
import audit_record_category_relation
import os
import sys

class audit_record(models.Model):
    _name = 'audit.record'
    _description = u'问题记录表'
    
    record_id = fields.Char(u'问题记录编号')
    site_id = fields.Char(u'单位ID')
    site_name = fields.Char(u'单位名称')
    company_id = fields.Char(u'总公司ID')
    company_name = fields.Char(u'总公司名称')
    problem_describtion = fields.Char(u'问题描述', size=300)
    check_way = fields.Char(u'审核方式')
    record_property = fields.Char(u'问题性质')
    user_id = fields.Char(u'用户id')
    plan_id = fields.Char(u'计划id')
    subplan_id = fields.Char(u'任务id')
    period = fields.Char(u'审核期次')
    
    
    #获取当前人员当前审核期次的所有问题记录列表
    #created by wangkui
    def get_Record(self, user_id, period):
        records = self.search([('user_id','=', user_id), ('period','=', period)])
        result = []
        for rec in records:
            obj = {}
            obj['RECORD_ID'] = rec.record_id
            obj['SITE_ID'] = rec.site_id
            obj['SITE_NAME'] = rec.site_name
            obj['COMPANY_ID'] = rec.company_id
            obj['COMPANY_NAME'] = rec.company_name
            obj['PROBLEM_DESC'] = rec.problem_describtion
            obj['CHECK_WAY'] = rec.check_way
            obj['RowActionState'] = '2'
            result.append(obj)
        return result
    
    #获取当前人员当前计划的所有问题记录列表
    #created by wangkui
    def get_Recordlist(self, user_id, plan_id):
        records = self.search([('user_id','=', user_id), ('plan_id','=', plan_id)])
        result = []
        for rec in records:
            result.append(rec.id)
        return result
    
    #新建编辑问题记录
    #created by wangkui
    def set_Record(self, record_base, category_list):
        self.set_RecordBase(record_base, category_list)
        audit_record_category_relation.audit_record_category_relation.set_CategoryList(self.env['audit.record.category.relation'], category_list)
        return "{\"result\" : \"1\"}"
    
    #新建编辑基本问题
    #created by wangkui
    def set_RecordBase(self, record_base, category_list):
        item = record_base.copy()
        if item.has_key("RECORD_ID") \
        and item.has_key("SITE_ID") \
        and item.has_key("SITE_NAME") \
        and item.has_key("PROBLEM_DESC") \
        and item.has_key("CHECK_WAY") \
        and item.has_key("USER_ID") and item["USER_ID"].isdigit() \
        and item.has_key("PLAN_ID") \
        and item.has_key("SUBPLAN_ID")\
        and item.has_key("PERIOD") \
        and item.has_key("RowActionState") and item["RowActionState"].isdigit():
            data  = {}
            data["record_id"] = item["RECORD_ID"]
            data["site_id"] = item["SITE_ID"]
            data["site_name"] = item["SITE_NAME"]
            data["problem_describtion"] = item["PROBLEM_DESC"]
            data["check_way"] = item["CHECK_WAY"]
            data["user_id"] = int(item["USER_ID"])
            if item["PLAN_ID"].isdigit() and item["SUBPLAN_ID"].isdigit():
                data["plan_id"] = int(item["PLAN_ID"])
                data["subplan_id"] = int(item["SUBPLAN_ID"])
            data["period"] = item["PERIOD"]
            if item["RowActionState"] == "2":
                org_data = self.search([('record_id','=',data["record_id"])])
                org_data.write(data)
            elif item["RowActionState"] == "1":
                self.create(data)
    #获取当前问题记录的媒体列表
    #created by wangkui
    def show_media(self, record_id):
        result = []
        records = self.search([('record_id','=', record_id)])
        for rec in records:
            medias = http.request.env['ir.attachment'].search([('res_id', '=', rec.id),('res_model', '=', 'audit.record')])
            for media in medias:
                print media.category
                if media.category == u'音频':
                    obj = {}
                    obj['ID'] = media.media_id
                    if obj['ID'] == False:
                        obj['ID'] = ''
                    obj['RECORD_ID'] = record_id
                    obj['URL'] = media.url
                    if obj['URL'] == False:
                        obj['URL'] = ''
                    obj['NAME'] = media.name
                    if obj['NAME'] == False:
                        obj['NAME'] = ''
                    obj['CATEGORY'] = media.category
                    if obj['CATEGORY'] == False:
                        obj['CATEGORY'] = ''
                    obj['REMARK'] = media.description
                    if obj['REMARK'] == False:
                        obj['REMARK'] = ''
                    obj['LENGTH'] = media.length
                    obj['RowActionState'] = '2'
                    result.append(obj)
                else:
                    obj = {}
                    obj['ID'] = media.media_id
                    if obj['ID'] == False:
                        obj['ID'] = ''
                    obj['RECORD_ID'] = record_id
                    obj['URL'] = media.url
                    if obj['URL'] == False:
                        obj['URL'] = ''
                    obj['NAME'] = media.name
                    if obj['NAME'] == False:
                        obj['NAME'] = ''
                    obj['CATEGORY'] = media.category
                    if obj['CATEGORY'] == False:
                        obj['CATEGORY'] = ''
                    obj['REMARK'] = media.description
                    if obj['REMARK'] == False:
                        obj['REMARK'] = ''
                    obj['LENGTH'] = media.file_size
                    obj['RowActionState'] = '2'
                    result.append(obj)
        return result
    
    @api.model
    def deleteMediaRecord(self, id, store_fname, db):
        remove_filepath = os.path.join(os.path.abspath(os.path.dirname(sys.argv[0])), 'data/filestore/'+db+'/'+store_fname)
        if os.path.exists(remove_filepath):
            os.remove(remove_filepath)
        sql_delete_media = "delete from ir_attachment where id = " + str(id)
        print sql_delete_media
        http.request.env.cr.execute(sql_delete_media)
    #新建编辑媒体列表
    #created by wangkui
#     def set_MediaList(self, record_base, media_list, category_list):
    
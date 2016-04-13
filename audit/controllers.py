# -*- coding: utf-8 -*-
from openerp import http, models,api
from openerp.http import request, serialize_exception
from basic_info import audit_vld_site, audit_standard
from plan_info import audit_plan, audit_score_info
import json
import base64
import functools
import simplejson
import werkzeug.wrappers
from record_info import audit_record, audit_record_category_relation
from datetime import datetime, date
from openerp.http import request, serialize_exception as _serialize_exception

def serialize_exception_(f):
    @functools.wraps(f)
    def wrap(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception, e:
            se = _serialize_exception(e)
            error = {
                'code': 200,
                'message': "Odoo Server Error",
                'data': se
            }
            return werkzeug.exceptions.InternalServerError(simplejson.dumps(error))
    return wrap

#----------------------------------------------------------
# SysAudit Controllers
#----------------------------------------------------------
class SysAudit(http.Controller):
    
    #added by wangkui
    @http.route('/sys_audit/RouterAction', type='http', auth="public")
    def sys_audit(self, redirect=None, **kw):
        
        #added by wangkui
        requestlog = request.httprequest
        values = request.params.copy()
        if values.get('action') == 'login':
            return self.sys_audit_login(request)
        if values.get('action') == 'getsite':
            return self.sys_audit_getallsite(request)
        if values.get('action') == 'getrecord':
            return self.sys_audit_getallrecord(request)
        if values.get('action') == 'getrelation':
            return self.sys_audit_getrecordcategoryrelation(request)
        if values.get('action') == 'setrecord':
            return self.sys_audit_setrecord(request)
        
        #附件上传
        if requestlog.form.get('action') == 'upload':
            return self.sys_audit_upload_media(request)
        #附件显示
        if values.get('action') == 'getMedia':
            return self.sys_audit_show_media(request)
        
        #added by hanlu
        if values.get('action') == 'getTaskStandardLevel1':
            return self.sys_audit_gettaskstandardlevel1(request)
        if values.get('action') == 'getTaskStandardLevel2':
            return self.sys_audit_gettaskstandardlevel2(request)
        if values.get('action') == 'getTaskStandardLevel3':
            return self.sys_audit_gettaskstandardlevel3(request)
        if values.get('action') == 'getTaskStandardLevel4':
            return self.sys_audit_gettaskstandardlevel4(request)
        if values.get('action') == 'getTaskOfExpert':
            return self.sys_audit_gettaskofexpert(request)
        if values.get('action') == 'getAllStandards':
            return self.sys_audit_getallstandards(request)
        if values.get('action') == 'getTaskStandardLevel':
            return self.sys_audit_gettaskstandardlevel(request)
        if values.get('action') == 'insertScoreInfo':
            return self.sys_audit_insertscoreinfo(request)
        if values.get('action') == 'getALLSTD':
            return self.sys_audit_getallstd(request)
     
    #登陆接口        
    #added by wangkui
    @http.route('/sys_audit/login', type='http', auth="public")
    def sys_audit_login(self, httprequest, **kw):

        thisrequest = request.httprequest
        type = request.httprequest.method
        values = request.params.copy()
        if values.get('params'):
            params = values.get('params')
            params_list = json.loads(params)
            if params_list.get('filter').get('db'):
                db = params_list.get('filter').get('db')
                login = params_list.get('filter').get('PER_EMAIL')
                password = params_list.get('filter').get('PER_PASS')
                password = '123456'
#                 db = 'jsi'
#                 login = "wutongxin@cnpc.com.cn"
#                 password = "admin"
                uid = request.session.authenticate(db, login, password)
                if uid is not False:
                    jsonobj = {'session_id':request.session.sid}
                    jsonobj['data'] = self.sys_audit_getdata(login) 
                    jsonstr = "jsonpCallback("+json.dumps(jsonobj)+")"
                    return jsonstr
#             request.uid = old_uid
            values['error'] = "Wrong login/password"
        #disable_footer
        jsonobj = {'session_id':'Wrong login/password'}
        jsonstr = "jsonpCallback("+json.dumps(jsonobj)+")"
        return jsonstr
#         return request.render('web.login', values)

    #获取用户信息
    #added by wangkui
    def sys_audit_getdata(self, login):
        person_base = {}
        plan_base = []
        achievement_list = []
        user = http.request.env['res.users'].search([('login', '=', login)])
        if user is not False:
            
            person_base['PERSON_ID'] = user.id
            person_base['PER_EMAIL'] = user.login
            person_base['PER_PASS'] = user.password
            
            site = user.site_id
            person_base['SITE_ID'] = site.code
            person_base['SITE_NAME'] = site.name
            
            expert = http.request.env['audit.expert.info'].search([('email', '=', login)])
            if expert is not False:
                person_base['BIRTH_DAY'] = expert.birthday
                person_base['PER_TITLE'] = expert.profession_title
                person_base['PER_JOB'] = expert.duty
                person_base['CONSULT_LEVEL'] = expert.level
                person_base['SKILLED_AREA'] = expert.good_business
                person_base['PER_PHONE'] = expert.cell_phone
                
                expert_plans = http.request.env['audit.plan.expert'].search([('audit_expert_id', '=', expert.id)])
                for expert_plan in expert_plans:
                    plan = expert_plan.audit_plan_id
                    plan_start_date = datetime.strptime(plan.start_time, "%Y-%m-%d").date()
                    plan_end_date = datetime.strptime(plan.end_time, "%Y-%m-%d").date()
                    if date.today() > plan_start_date and date.today() < plan_end_date:
                        plan_obj = {}
                        plan_obj['PLAN_ID'] = plan.id
                        plan_obj['ENTERPRISE_ID'] = plan.enterprise_id.name
                        plan_obj['OVAPLAN_ID'] = plan.ovaplan_id.name
                        plan_obj['AUDIT_METHOD'] = plan.audit_method.name
                        plan_obj['PERIOD'] = plan.period
                        plan_base.append(plan_obj)
            achievement = http.request.env['audit.expert.achievement'].search([('email', '=', login)])
            achievement_obj= {}
            achievement_details = achievement.achievement_details_ids
            for achievement_detail in achievement_details:
                achievement_obj['ACHIEVEMENT_ID'] = achievement_detail.id
                achievement_obj['APPLY_CATEGORY'] = achievement_detail.type
                achievement_obj['APPLY_DESC'] = achievement_detail.description
                achievement_obj['PER_FILE'] = achievement_detail.attachment
                achievement_obj['REMARK'] = achievement_detail.remarks
                achievement_list.append(achievement_obj)
        result = {'PERSON_BASE':person_base, 'PLAN_BASE':plan_base, 'ACHIEVEMENT_LIST':achievement_list}
        return result
        #return "Hello World!"
        
    #获取所有单位列表
    #added by wangkui
    @http.route('/sys_audit/get_all_site/', type='http', auth='public')
    def sys_audit_getallsite(self, httprequest, **kw):
        values = request.params.copy()
        if values.get('params'):
            params = values.get('params')
            params_list = json.loads(params)
            if params_list.get('filter').get('USER_ID'):
                user_id = params_list.get('filter').get('USER_ID')
                plan_id = params_list.get('filter').get('PLAN_ID')
                jsonobj = {'rows' : audit_vld_site.audit_vld_site.get_Site(http.request.env['audit.vld.site'])}
                jsonstr = "jsonpCallback("+json.dumps(jsonobj)+")"
                return jsonstr
        jsonobj = {'error':'1'}
        jsonstr = "jsonpCallback("+json.dumps(jsonobj)+")"
        return jsonstr    
    #获取当前审核人员的所有审核记录列表
    #added by wangkui
    @http.route('/sys_audit/get_all_record/', type='http', auth='public')
    def sys_audit_getallrecord(self, httprequest, **kw):
        values = request.params.copy()
        if values.get('params'):
            params = values.get('params')
            params_list = json.loads(params)
            if params_list.get('filter').get('USER_ID'):
                user_id = params_list.get('filter').get('USER_ID')#人员id
                period = params_list.get('filter').get('PERIOD')#审核批次
                jsonobj = {'rows' : audit_record.audit_record.get_Record(http.request.env['audit.record'], user_id, period)}
                jsonstr = "jsonpCallback("+json.dumps(jsonobj)+")"
                return jsonstr
        jsonobj = {'error':'1'}
        jsonstr = "jsonpCallback("+json.dumps(jsonobj)+")"
        return jsonstr   
        
    #获取问题记录与类型关系列表
    #added by wangkui
    @http.route('/sys_audit/get_record_category_relation/', type='http', auth='public')
    def sys_audit_getrecordcategoryrelation(self, httprequest, **kw):
        values = request.params.copy()
        if values.get('params'):
            params = values.get('params')
            params_list = json.loads(params)
            if params_list.get('filter').get('USER_ID'):
                user_id = params_list.get('filter').get('USER_ID')#人员id，计划id
                plan_id = params_list.get('filter').get('PLAN_ID')#人员id，计划id
                jsonobj = {'rows' : audit_record_category_relation.audit_record_category_relation.get_Record_Category_Relation(http.request.env['audit.record.category.relation'], user_id, plan_id)}
                jsonstr = "jsonpCallback("+json.dumps(jsonobj)+")"
                return jsonstr
        jsonobj = {'error':'1'}
        jsonstr = "jsonpCallback("+json.dumps(jsonobj)+")"
        return jsonstr   
    
    #新建编辑问题记录
    #added by wangkui
    @http.route('/sys_audit/set_record/', type='http', auth='public')
    def sys_audit_setrecord(self, httprequest, **kw):
        values = request.params.copy()
        if values.get('params'):
            params = values.get('params')
            params_list = json.loads(params)
            if params_list.get('filter').get('RECORD_BASE'):
                record_base = params_list.get('filter').get('RECORD_BASE')
                category_list = params_list.get('filter').get('CATEGORY_LIST')
                jsonobj = audit_record.audit_record.set_Record(http.request.env['audit.record'], record_base, category_list)
                jsonstr = "jsonpCallback("+json.dumps(jsonobj)+")"
                return jsonstr
        jsonobj = "{\"result\" : \"0\"}"
        jsonstr = "jsonpCallback("+json.dumps(jsonobj)+")"
        return jsonstr
    
    @http.route('/sys_audit/upload', type='http', auth="public")
    @serialize_exception_
    def sys_audit_upload_media(self, httprequest):
        
        thisrequest = httprequest
        form = httprequest.httprequest.form
        files = httprequest.httprequest.files
        f = files['file']

        Model = request.session.model('ir.attachment')
        model = 'audit.record'
        RECORD_ID = form.get('RECORD_ID')
        record_id = http.request.env['audit.record'].search([('record_id', '=', form.get('RECORD_ID'))])
        if form.get('RowActionState') == "2":
            try:
                attachment = http.request.env['ir.attachment'].search([('media_id', '=', form.get('MEDIA_ID'))])
                audit_record.audit_record.deleteMediaRecord(http.request.env['audit.record'], attachment.id, attachment.store_fname, request.session.db)
#                 http.request.env.cr.execute('delete from ir_attachment where media_id = 122')
#                 models.Model.unlink(http.request.env['ir.attachment'], http.request.cr, http.request.uid, attachment.id, request.context)
                attachment_id = Model.create({
                    'name': form.get('NAME'),
                    'datas': base64.encodestring(f.stream.read()),
                    'datas_fname': f.filename,
                    'res_model': model,
                    'res_id': record_id,
                    'media_id': form.get('MEDIA_ID'),
                    'category': form.get('CATEGORY'),
                    'description': form.get('REMARK'),
                    'url': form.get('URL'),
                    'length':form.get('LENGTH')
                }, request.context)
                args = {
                    'filename': f.filename,
                    'id':  attachment_id
                }
            except Exception:
                args = {'id': False,'filename': False } 
                jsonobj = "{\"result\" : \"0\"}"
                jsonstr = "jsonpCallback("+json.dumps(jsonobj)+")"
                return jsonstr
        elif form.get('RowActionState') == "1":
            try:
                attachment_id = Model.create({
                    'name': form.get('NAME'),
                    'datas': base64.encodestring(f.stream.read()),
                    'datas_fname': f.filename,
                    'res_model': model,
                    'res_id': record_id,
                    'media_id': form.get('MEDIA_ID'),
                    'category': form.get('CATEGORY'),
                    'description': form.get('REMARK'),
                    'url': form.get('URL'),
                    'length':form.get('LENGTH')
                }, request.context)
                args = {
                    'filename': f.filename,
                    'id':  attachment_id
                }
            except Exception:
                args = {'id': False,'filename': False } 
                jsonobj = "{\"result\" : \"0\"}"
                jsonstr = "jsonpCallback("+json.dumps(jsonobj)+")"
                return jsonstr
        elif form.get('RowActionState') == "3":
            attachment = http.request.env['ir.attachment'].search([('media_id', '=', form.get('MEDIA_ID'))])
            audit_record.audit_record.deleteMediaRecord(http.request.env['audit.record'], attachment.id, attachment.store_fname, request.session.db)
        jsonobj = "{\"result\" : \"1\"}"
        jsonstr = "jsonpCallback("+json.dumps(jsonobj)+")"
        return jsonstr
    
    
    
    @http.route('/sys_audit/show_media/', type='http', auth='public')
    def sys_audit_show_media(self, httprequest, **kw):
        values = request.params.copy()
        if values.get('params'):
            params = values.get('params')
            params_list = json.loads(params)
            if params_list.get('filter').get('RECORD_ID'):
                record_id = params_list.get('filter').get('RECORD_ID')
                jsonobj = audit_record.audit_record.show_media(http.request.env['audit.record'], record_id)
                jsonstr = "jsonpCallback("+json.dumps(jsonobj)+")"
                return jsonstr
        jsonobj = "{\"result\" : \"0\"}"
        jsonstr = "jsonpCallback("+json.dumps(jsonobj)+")"
        return jsonstr

    #当前任务所属计划的审核主题---审核标准表一级类型
    #added by hanlu
    @http.route('/sys_audit/getTaskStandardLevel1/', type='http', auth='public')
    def sys_audit_gettaskstandardlevel1(self, httprequest, **kw):
        values = request.params.copy()    
        if values.get('params'):
            params = values.get('params')
            params_list = json.loads(params)
            if params_list.get('filter').get('task_id') and params_list.get('filter').get('user_id'):
                task_id = params_list.get('filter').get('task_id')
                user_id = params_list.get('filter').get('user_id')
                if task_id and user_id and task_id.isdigit() and user_id.isdigit():
                    jsonobj = {'rows':audit_plan.audit_plan_subplan.get_task_standard_level_1(http.request.env['audit.plan.subplan'], int(task_id), int(user_id))}
                    jsonstr = "jsonpCallback("+json.dumps(jsonobj)+")"
                    print jsonstr
                    return jsonstr
        jsonobj = {'error':'1'}
        jsonstr = "jsonpCallback("+json.dumps(jsonobj)+")"
        return "error gettaskstandardlevel1"   
    
    #当前任务所属计划的审核项---审核标准二级类型
    #added by hanlu
    @http.route('/sys_audit/getTaskStandardLevel2/', type='http', auth='public')
    def sys_audit_gettaskstandardlevel2(self, httprequest, **kw):
        values = request.params.copy()    
        if values.get('params'):
            params = values.get('params')
            params_list = json.loads(params)
            if params_list.get('filter').get('task_id') and params_list.get('filter').get('user_id'):
                task_id = params_list.get('filter').get('task_id')
                user_id = params_list.get('filter').get('user_id')
                if task_id and user_id and task_id.isdigit() and user_id.isdigit():
                    jsonobj = {'rows':audit_plan.audit_plan_subplan.get_task_standard_level_2(http.request.env['audit.plan.subplan'], int(task_id), int(user_id))}
                    jsonstr = "jsonpCallback("+json.dumps(jsonobj)+")"
                    print jsonstr
                    return jsonstr
        jsonobj = {'error':'1'}
        jsonstr = "jsonpCallback("+json.dumps(jsonobj)+")"
        return "error gettaskstandardlevel2"   

    #当前任务所属计划的审核项---审核标准二级类型
    #added by hanlu
    @http.route('/sys_audit/getTaskStandardLevel3/', type='http', auth='public')
    def sys_audit_gettaskstandardlevel3(self, httprequest, **kw):
        values = request.params.copy()    
        if values.get('params'):
            params = values.get('params')
            params_list = json.loads(params)
            if params_list.get('filter').get('task_id') and params_list.get('filter').get('user_id'):
                task_id = params_list.get('filter').get('task_id')
                user_id = params_list.get('filter').get('user_id')
                if task_id and user_id and task_id.isdigit() and user_id.isdigit():
                    jsonobj = {'rows':audit_plan.audit_plan_subplan.get_task_standard_level_3(http.request.env['audit.plan.subplan'], int(task_id), int(user_id))}
                    jsonstr = "jsonpCallback("+json.dumps(jsonobj)+")"
                    print jsonstr
                    return jsonstr
        jsonobj = {'error':'1'}
        jsonstr = "jsonpCallback("+json.dumps(jsonobj)+")"
        return "error gettaskstandardlevel3"
    
    #当前任务所属计划的审核项---审核标准二级类型
    #added by hanlu
    @http.route('/sys_audit/getTaskStandardLevel4/', type='http', auth='public')
    def sys_audit_gettaskstandardlevel4(self, httprequest, **kw):
        values = request.params.copy()    
        if values.get('params'):
            params = values.get('params')
            params_list = json.loads(params)
            if params_list.get('filter').get('task_id') and params_list.get('filter').get('user_id'):
                task_id = params_list.get('filter').get('task_id')
                user_id = params_list.get('filter').get('user_id')
                if task_id and user_id and task_id.isdigit() and user_id.isdigit():
                    jsonobj = {'rows':audit_plan.audit_plan_subplan.get_task_standard_level_4(http.request.env['audit.plan.subplan'], int(task_id), int(user_id))}
                    jsonstr = "jsonpCallback("+json.dumps(jsonobj)+")"
                    print jsonstr
                    return jsonstr
        jsonobj = {'error':'1'}
        jsonstr = "jsonpCallback("+json.dumps(jsonobj)+")"
        return "Wrong gettaskstandardlevel4"
    
    #当前审核人员的任务列表
    #added by hanlu
    @http.route('/sys_audit/getTaskOfExpert/', type='http', auth='public')
    def sys_audit_gettaskofexpert(self, httprequest, **kw):
        values = request.params.copy()    
        if values.get('params'):
            params = values.get('params')
            params_list = json.loads(params)
            if params_list.get('filter') and params_list.get('filter').get('user_id'):
                print params_list.get('filter')
                user_id = params_list.get('filter').get('user_id')
                if user_id and user_id.isdigit():
                    jsonobj = {'rows':audit_plan.audit_plan_subplan.get_task_of_expert(http.request.env['audit.plan.subplan'], int(user_id))}
                    jsonstr = "jsonpCallback("+json.dumps(jsonobj)+")"
                    print jsonstr
                    return jsonstr
        jsonobj = {'error':'1'}
        jsonstr = "jsonpCallback("+json.dumps(jsonobj)+")"
        return jsonstr
    
    #所有标准-树
    #added by hanlu
    @http.route('/sys_audit/getAllStandards', type='http', auth='public')
    def sys_audit_getallstandards(self, httprequest, **kw):
        values = request.params.copy()    
        if values.get('params'):
            params = values.get('params')
            params_list = json.loads(params)
            if params_list.get('filter').get('type'):
                print params_list.get('filter')
                type = params_list.get('filter').get('type')
                if type and type.isdigit():
                    jsonobj = {'rows' : audit_standard.audit_standard.get_all_standard_to_tree(http.request.env['audit.standard'], int(type))}
                    jsonstr = "jsonpCallback("+json.dumps(jsonobj)+")"
                    print jsonstr
                    return jsonstr
        jsonobj = {'error':'1'}
        jsonstr = "jsonpCallback("+json.dumps(jsonobj)+")"
        return jsonstr
    
    #所有标准-树不分类
    #added by hanlu
    @http.route('/sys_audit/getALLSTD', type='http', auth='public')
    def sys_audit_getallstd(self, httprequest, **kw):
        jsonobj = {'rows' : audit_standard.audit_standard.get_all_std_to_tree(http.request.env['audit.standard'])}
        jsonstr = "jsonpCallback("+json.dumps(jsonobj)+")"
        print jsonstr
        return jsonstr
        jsonobj = {'error':'1'}
        jsonstr = "jsonpCallback("+json.dumps(jsonobj)+")"
        return jsonstr
    
    #当前任务的标准审核树 combine 1,2,3,4
    #added by hanlu
    @http.route('/sys_audit/getTaskStandardLevel/', type='http', auth='public')
    def sys_audit_gettaskstandardlevel(self, httprequest, **kw):
        values = request.params.copy()    
        if values.get('params'):
            params = values.get('params')
            params_list = json.loads(params)
            if params_list.get('filter').get('task_id') and params_list.get('filter').get('user_id'):
                print params_list.get('filter')
                task_id = params_list.get('filter').get('task_id')
                user_id = params_list.get('filter').get('user_id')
                if task_id and user_id and task_id.isdigit() and user_id.isdigit():
                    jsonobj = audit_plan.audit_plan_subplan.get_task_standard_level(http.request.env['audit.plan.subplan'], int(task_id), int(user_id))
                    jsonstr = "jsonpCallback("+json.dumps(jsonobj)+")"
                    print jsonstr
                    return jsonstr
        jsonobj = {'error':'1'}
        jsonstr = "jsonpCallback("+json.dumps(jsonobj)+")"
        return jsonstr
    
    #新建/编辑评分
    #added by hanlu
    @http.route('/sys_audit/insertScoreInfo/', type='http', auth='public')
    def sys_audit_insertscoreinfo(self, httprequest, **kw):
        values = request.params.copy()
        if values.get('params'):
            params = values.get('params')
            params_list = json.loads(params)
            if params_list.get('filter') and params_list.get('filter').get('SCORE_INFO'):
                score_info = params_list.get('filter').get('SCORE_INFO')
                print score_info
                jsonobj = audit_score_info.audit_score_info.insert_score_info(http.request.env['audit.score.info'], score_info)
                jsonstr = "jsonpCallback("+json.dumps(jsonobj)+")"
                print jsonstr
                return jsonstr
        jsonobj = "{\"result\" : \"0\"}"
        jsonstr = "jsonpCallback("+json.dumps(jsonobj)+")"
        return jsonstr


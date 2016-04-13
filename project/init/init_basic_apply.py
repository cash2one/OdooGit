# -*- coding: utf-8 -*-
##############################################################################
#    立项申请
#    Created on 2015年12月22日
#    @author: LY
#    Last edit on 2015年12月18日
#    Last edit by  LY
##############################################################################
import time

from openerp import models, fields, api,exceptions

import init_basic


class pm_init_proj_apply(models.Model):
    """
    立项申请记录表
    """
    
    _name = 'pm.init.proj.apply'
    _description = u'立项申请记录表'
    _inherit = 'pm.init.basic'
    
    proj_apply_source = fields.Selection([('g', u'国家下发'), ('j', u'集团指定'), ('t', u'集团统建'), ('q', u'其它来源')], u'项目来源')
    proj_apply_budget_template = fields.Many2one('sys.constant', u'经费模板', domain=[('type', '=', 'PROJ_BUDGET_TEMPLATE')])
    proj_apply_state = fields.Selection([('draft', u'草稿'), ('submitted', u'已提交'), ('fapproved', u'所（中心）已审批'), ('sapproved', u'科研处已审批'), ('tapproved', u'院主管领导已审批'), ('fhapproved', u'主管院长已审批')], u'状态')
    proj_approve_state= fields.Selection([('draft', u'草稿'), ('submitted', u'已提交'), ('fapproved', u'所（中心）已审批')], string=u'状态',default='draft')
    
    proj_apply_state_end = fields.Boolean(string=u'立项申请审批是否结束',default=False)
    proj_approve_state_end = fields.Boolean(string=u'立项结果是否确认完成',default=False) 
    proj_apply_flow_button = fields.Boolean(compute='_hide_apply_flow_button',string=u'立项申请流程按钮控制',default=False)
    proj_approve_flow_button = fields.Boolean(compute='_hide_approve_flow_button',string=u'立项审批流程按钮控制',default=False)
    
    proj_apply_files = fields.Binary(u'开题报告附件')
    proj_apply_keypoints = fields.Text(u'生产需求和需要解决的关键技术问题')
    proj_apply_research_content = fields.Text(u'研究目标和主要研究内容')
    proj_apply_innovate = fields.Text(u'技术创新点和研究路线')
    proj_apply_accomplishments = fields.Text(u'预期成果和考核指标')
    proj_apply_previous_results = fields.Text(u'前期研究基础情况和支撑条件分析')
    proj_apply_import_technology = fields.Text(u'国内外合作研究及技术引进相结合情况')
    
    proj_apply_purchase = fields.One2many('pm.init.proj.purchase', 'proj_apply_id', u'采购计划')
    proj_apply_team = fields.One2many('pm.init.proj.team', 'proj_apply_id', u'项目（课题）组人员名单')
    proj_apply_schedule = fields.One2many('pm.init.proj.schedule', 'proj_apply_id', u'进度计划')
    
    proj_apply_budget = fields.One2many('pm.init.budget', 'proj_apply_id', u'经费预算')
    
    # 计算字段，用于控制字段显隐、流程分支等
    proj_flow_split_cal = fields.Integer(compute='_get_proj_flow_split', string='计算流程分支')
    proj_reply_info_edit=fields.Boolean(compute='_set_color_tree',string=u'批复信息提示')
    proj_pm_uid=fields.Integer(compute='_get_pm_uid',string=u'项目负责人',store=True)
    proj_user_type=fields.Integer(compute='_get_user_type',string=u'判断用户的类型，1-项目经理或超级管理员，2-所中心领导，3-科研处人员,4-主管院长')
    
    # 院主管领导审批意见
    proj_apply_dm = fields.Many2one('oa.staff.basic', string=u'审批人')
    proj_apply_dm_date = fields.Date(string=u'审批时间')
    proj_apply_dm_results = fields.Text(string=u'审批意见和结论')
    
    #主管院长审批意见
    proj_apply_president = fields.Many2one('oa.staff.basic', string=u'审批人')
    proj_apply_president_date = fields.Date(string=u'审批时间')
    proj_apply_president_results = fields.Text(string=u'审批意见和结论')
    
    #批复信息
    proj_reply_info_id=fields.Many2one('pm.init.reply.infos',u'批复信息关联字段')
    proj_reply_file_number=fields.Char(related='proj_reply_info_id.proj_reply_file_number',string=u'批复文号',size=100)
    proj_reply_files=fields.Binary(related='proj_reply_info_id.proj_reply_files',string=u'批复文件')
    proj_reply_fmis=fields.Char(related='proj_reply_info_id.proj_reply_fmis',string=u'FMIS账号')
    proj_reply_contract=fields.Char(related='proj_reply_info_id.proj_reply_contract',string=u'合同编号',size=100)
    proj_reply_funds=fields.Float(related='proj_reply_info_id.proj_reply_funds',string=u'批复总金额')
    proj_reply_start_date=fields.Date(related='proj_reply_info_id.proj_reply_start_date',string=u'开始时间')
    proj_reply_end_date=fields.Date(related='proj_reply_info_id.proj_reply_end_date',string=u'结束时间')
    
    #proj_reply_leaders=fields.Many2one('oa.staff.basic',u'分管所（中心）领导')
    
    #所中心领导审批时间、意见
    proj_final_approve_person=fields.Many2one('oa.staff.basic', string=u'审批人')
    proj_final_approve_date=fields.Date(u='审批时间')
    proj_final_approve_result=fields.Text(u='审批意见')
    
    @api.model
    @api.returns('self', lambda value:value.id)
    def create(self, vals):
        return models.Model.create(self, vals)
    
    @api.multi
    def write(self, vals):
        
        #如果有批复信息，写入批复信息
        new_vals={}
        if vals.has_key('proj_reply_file_number'):
            new_vals['proj_reply_file_number']=vals['proj_reply_file_number']
        if vals.has_key('proj_reply_files'):
            new_vals['proj_reply_files']=vals['proj_reply_files']
        if vals.has_key('proj_reply_fmis'):
            new_vals['proj_reply_fmis']=vals['proj_reply_fmis']
        if vals.has_key('proj_reply_contract'):
            new_vals['proj_reply_contract']=vals['proj_reply_contract']
        if vals.has_key('proj_reply_funds'):
            new_vals['proj_reply_funds']=vals['proj_reply_funds']
        if vals.has_key('proj_reply_start_date'):
            new_vals['proj_reply_start_date']=vals['proj_reply_start_date']
        if vals.has_key('proj_reply_end_date'):
            new_vals['proj_reply_end_date']=vals['proj_reply_end_date']
        if vals.has_key('proj_num'):
            new_vals['proj_num']=vals['proj_num']
        if len(new_vals)>0:
            if(self.proj_reply_info_id.id):
                self.env['pm.init.reply.infos'].write(new_vals)
            else:
                infos_id=self.env['pm.init.reply.infos'].create(new_vals)
                vals['proj_reply_info_id']=infos_id.id
        
        #如果是技术支持类且有任务书或合同，则标识流程结束并将状态变为实施中。
        proj_type_id = self.env['sys.constant'].search([('name','=',u'技术支持类'),('type','=','PROJ_CATEGORY_BIG')]).id
        if self.proj_apply_is_over == True:
            vals['proj_periods'] = self.env['sys.constant'].search([('name','=',u'实施中'),('type','=','PROJ_PERIODS')]).id
            vals['proj_flow_is_end'] = True
            models.Model.write(self, vals)
            return False
        
        #如果院主管领导审批意见不为空，自动填入审批人和审批时间
        if vals.has_key('proj_apply_president_results') and vals['proj_apply_president_results'].strip() != '':
            vals['proj_apply_president_date'] = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()));
            vals['proj_apply_president'] = self.env['oa.staff.basic'].search([('related_user','=',self.env.uid)]).id;
            
        #如果为立项审批流程，中心领导审批意见不为空，自动填入时间和审批人
        if vals.has_key('proj_final_approve_result') and vals['proj_final_approve_result'].strip() != '':
            vals['proj_final_approve_date'] = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()));
            vals['proj_final_approve_person'] = self.proj_reply_leaders.id;
                     
        res = models.Model.write(self, vals)                       
        if self.proj_periods.id != self.env['sys.constant'].search([('name','=',u'立项中'),('type','=','PROJ_PERIODS')]).id:
            res=False
        
        #流程是否结束，改变项目状态，向实施和经费中写入相应信息
        """if self.proj_approve_state == 'fapproved':
            vals = {'proj_periods':self.env['sys.constant'].search([('name','=',u'实施中'),('type','=','PROJ_PERIODS')]).id}
            res = models.Model.write(self, vals)
            if res:
                pid = self.env['pm.impl.quarter.plan'].create({'project_id':self.id})
                bid = self.env['pm.impl.plan.baseline'].create({'project_id':self.id,'version_number':'1.0','flag':True})
                for r in self.proj_apply_schedule:
                    self.env['pm.impl.plan.baseline.version'].create({'quarter_plan_gz_id':pid.id,'plan_baseline_id':bid.id,'year':r.proj_schedule_year.id,'quarter':r.proj_schedule_quarter.id,'plan_content':r.proj_schedule_quarter_work})
                tid = self.env['pm.impl.staff.baseline'].create({'project_id':self.id,'version_number':'1.0','flag':True})
                for r in self.proj_apply_team:
                    if(r.proj_staff_position.name == u'项目经理'):
                        pid.write({'proj_manager':r.staff_id.id})
                    self.env['pm.impl.staff.baseline.version'].create({'staff_baseline_id':tid.id,'staff':r.staff_id.related_user.id,'role':r.proj_staff_position.id})
                self.writeIntoVersion()
            return res"""
        return res
    
    @api.depends('proj_apply_state')
    def _get_user_type(self):
        if self.user_in_groups('aqy_project.group_proj_manager'):
            self.proj_user_type = 1
            return
        if self.user_in_groups('aqy_project.group_unit_leaders'):
            self.proj_user_type = 2
            return
        if self.user_in_groups('aqy_project.group_init_sapproved'):
            self.proj_user_type = 3
            return
        if self.user_in_groups('aqy_project.group_init_apply_fhapproved'):
            self.proj_user_type = 4
            return
    
    @api.depends('proj_approve_state')
    def _hide_approve_flow_button(self):
        c_uid = self.env.uid
        #超级管理员  
        if c_uid == 1:
            self.proj_approve_flow_button = False
            return
        #所中心人员判断
        if self.user_in_groups('aqy_project.group_unit_leaders') and self.proj_approve_state == 'submitted' and self.proj_reply_leaders.related_user.id == c_uid:
                self.proj_approve_flow_button = False
                return
        self.proj_approve_flow_button = True
            
    @api.depends('proj_apply_state')
    def _hide_apply_flow_button(self):
        c_uid = self.env.uid
        #超级管理员  
        if c_uid == 1:
            self.proj_apply_flow_button = False
            return
        #所中心人员判断
        if self.user_in_groups('aqy_project.group_unit_leaders') and self.proj_apply_state == 'submitted' and self.proj_reply_leaders.related_user.id == c_uid:
            if self.proj_flow_split_cal == 3 or self.proj_flow_split_cal == 5:
                self.proj_apply_flow_button = False
                return
        #科研处人员判断
        if self.user_in_groups('aqy_project.group_init_sapproved'):
            if (self.proj_flow_split_cal == 4 and self.proj_apply_state == 'submitted') or (self.proj_flow_split_cal == 5 and self.proj_apply_state == 'fapproved') :
                self.proj_apply_flow_button = False
                return
        #主管院长判断
        if self.user_in_groups('aqy_project.group_init_apply_fhapproved') and self.proj_apply_state == 'sapproved':
            self.proj_apply_flow_button = False
            return
        self.proj_apply_flow_button = True
        #aqy_project.group_unit_leaders,aqy_project.group_init_sapproved,aqy_project.group_init_apply_fhapproved
        
    
    def wkf_sp_s2f(self):
        """
        立项审批工作流，由“已提交”到“所中心审批”，向实施和经费中写入相应信息
        """
        
        #self.proj_approve_state == 'fapproved';
        vals = {'proj_periods':self.env['sys.constant'].search([('name','=',u'实施中'),('type','=','PROJ_PERIODS')]).id,'proj_approve_state':'fapproved'}
        vals['proj_approve_state_end'] = True
        res = models.Model.write(self, vals)
        if res:
            pid = self.env['pm.impl.quarter.plan'].create({'project_id':self.id})
            bid = self.env['pm.impl.plan.baseline'].create({'project_id':self.id,'version_number':'1.0','flag':True})
            for r in self.proj_apply_schedule:
                self.env['pm.impl.plan.baseline.version'].create({'quarter_plan_gz_id':pid.id,'plan_baseline_id':bid.id,'year':r.proj_schedule_year.id,'quarter':r.proj_schedule_quarter.id,'plan_content':r.proj_schedule_quarter_work})
            tid = self.env['pm.impl.staff.baseline'].create({'project_id':self.id,'version_number':'1.0','flag':True})
            for r in self.proj_apply_team:
                if(r.proj_staff_position.name == u'项目经理'):
                    pid.write({'proj_manager':r.staff_id.related_user.id})
                self.env['pm.impl.staff.baseline.version'].create({'staff_baseline_id':tid.id,'staff':r.staff_id.related_user.id,'role':r.proj_staff_position.id})
            self.writeIntoVersion()
    
    def writeIntoVersion(self):
        vals = {}
        vals['proj_id'] = self.id
        vals['proj_num'] = self.proj_reply_info_id.proj_num
        vals['fmis_num'] = self.proj_reply_fmis
        vals['version'] = 1.0
        vals['use_state'] = self.env['sys.constant'].search([('type','=','USE_STATE'),('name','=','当前有效')]).id
        version_id=models.Model.create(self.env['pm.fund.budget.version'], vals).id
        if version_id:            
            detail_res = self.env['pm.init.budget'].search([('proj_apply_id','=',self.id)])
            for record in detail_res:
                detail_vals = record.read(['sn','subject_id','subject_name','year','value'])
                detail_vals[0]['version_id'] = version_id
                models.Model.create(self.env['pm.fund.budget.version.detail'], detail_vals[0])
    
    @api.depends('proj_category', 'proj_type')
    def _get_proj_flow_split(self):
        category = self.proj_category.name
        mini_type = self.proj_type.name
        if (category == u'技术研究和开发类' and mini_type == u'横向项目') or (category == u'技术支持类') or (category == u'技术服务类'):
            self.proj_flow_split_cal = 3
        elif category == u'技术研究和开发类' and mini_type == u'专项项目':
            self.proj_flow_split_cal = 4
        elif category == u'技术研究和开发类' and mini_type == u'纵向项目':
            self.proj_flow_split_cal = 5
        elif category == u'技术研究和开发类' and mini_type == u'院级项目':
            self.proj_flow_split_cal = 5                            #51
        else:
            self.proj_flow_split_cal = 3
            
    @api.depends('proj_apply_team')
    def _get_pm_uid(self):
        pm_id=self.env['oa.project.role'].search([('name','=',u'项目经理')]).id
        if len(self.proj_apply_team)<=0:
            return
        for r in self.proj_apply_team:
            if r.proj_staff_position.id == pm_id:
                self.proj_pm_uid=r.staff_id.related_user.id;
                break
   
    def _work_flow_split(self, value):
        category = self.proj_category.name
        mini_type = self.proj_type.name
        if value == 1:
            if category == u'技术研究和开发类' and (mini_type == u'纵向项目' or mini_type == u'院级项目'):
                return 1
            elif category == u'技术研究和开发类' and mini_type == u'专项项目':
                return 2
            else:
                return 3
        elif value == 2:
            if category == u'技术研究和开发类' and mini_type == u'专项项目':
                return 1
        elif value == 3:
            if category == u'技术研究和开发类' and mini_type == u'院级项目':
                return 1
            elif category == u'技术研究和开发类' and mini_type == u'纵向项目':
                return 2
        else:
            return 4        
    
    def _set_color_tree(self):
        if(self.proj_total_funds==self.proj_reply_funds and self.proj_reply_start_date==self.proj_start_date and self.proj_reply_end_date==self.proj_end_date):
            return True
        return False
    
        #获取jqGrid数据
    def getJqGridData(self, cr, uid, rec_info, context=None):
        detail_obj = self.pool.get('pm.init.budget')
        detail_ids = detail_obj.search(cr, uid, [('proj_apply_id', '=', rec_info['id'])], context=context)
        data_list=[]
        start_year = int(rec_info['proj_start_date'][:4])
        end_year = int(rec_info['proj_end_date'][:4])    

        subject_obj = self.pool.get('pm.common.subject')
        subject_ids = subject_obj.search(cr, uid, [('is_leaf','=',True)], context=context)
        subject_res = subject_obj.browse(cr, uid, subject_ids, context).sorted(key=lambda x:x['sn'])        
        
        for rec in subject_res:
            data={}
            first = rec.parent_id.parent_id.parent_id
            second = rec.parent_id.parent_id
            third = rec.parent_id
            if first:
                data['first'] = first.name
                data['second'] = second.name
                data['third'] = third.name
            elif second:
                data['first'] = second.name
                data['second'] = third.name
                data['third'] = rec.name
            elif third:
                data['first'] = third.name
                data['second'] = rec.name
                data['third'] = rec.name 
            else:
                data['first'] = rec.name
                data['second'] = rec.name
                data['third'] = rec.name
            data['subject_id'] = rec.id
            data['sn'] = rec.sn
            data['subject_name'] = rec.name
            for y in range(start_year, end_year+1):
                if detail_ids:
                    year_ids = detail_obj.search(cr, uid, [('proj_apply_id', '=', rec_info['id']),('year','=',y),('subject_id','=',rec.id)], context=context)
                    year_res = detail_obj.browse(cr, uid, year_ids, context)
                    data[y] = year_res.value
                else:
                    data[y] = 0
                    
            data_list.append(data)
        return {'start_year':start_year, 'end_year':end_year, 'data':data_list}
    
    
class pm_init_proj_schedule(models.Model):
    """
    进度计划，以季度为单位
    """
    _name = 'pm.init.proj.schedule'
    _description = u'进度计划表'
    
    proj_schedule_year = fields.Many2one('sys.constant',string='年份',domain=[('type','=','year')],required=True)   
    proj_schedule_quarter = fields.Many2one('sys.constant',string='季度',domain=[('type','=','quarter')],required=True)
    proj_schedule_quarter_work = fields.Text(u'研究内容及工作量安排')
    proj_schedule_aims = fields.Text(u'阶段目标')
    proj_schedule_charger = fields.Many2one('oa.staff.basic', u'负责人')
    
    proj_apply_id = fields.Many2one('pm.init.proj.apply', u'立项申请表关联字段')
    _sql_constraints = [
        ('year_quarter_key', 'UNIQUE (proj_apply_id,proj_schedule_year,proj_schedule_quarter)', u'年份或者年内季度重复!')
    ]
    

class pm_init_proj_team(models.Model):
    """
    项目组人员名单
    """
    _name = 'pm.init.proj.team'
    _description = u'项目组人员名单'
    
    staff_id = fields.Many2one('oa.staff.basic', u'名称')
    
    proj_staff_name = fields.Char(related='staff_id.name', size=10, required=True)
    proj_staff_position = fields.Many2one('oa.project.role', string='岗位')
    proj_staff_identify_id = fields.Char(related='staff_id.identify_id', string='身份证号码', size=18, readonly=True)
    proj_staff_vld = fields.Many2one(related='staff_id.vld_site', string='单位/部门', readonly=True)
    proj_staff_title = fields.Char(u'职称', size=50)
    proj_staff_major = fields.Char(u'从事专业', size=50)
    proj_staff_total_time = fields.Integer(u'总投入时间（月）')
    proj_staff_phone = fields.Char(related='staff_id.phone_number', string='联系电话', size=12, store=True, readonly=True)
    proj_staff_email = fields.Char(related='staff_id.email', string='Email地址', size=50, store=True, readonly=True)  
    
    proj_apply_id = fields.Many2one('pm.init.proj.apply', u'立项申请表关联字段')
    
    _sql_constraints = [
        ('id_staff_id_key', 'UNIQUE (proj_apply_id,staff_id)', u'项目组人员重复!')
    ]
    

class pm_init_proj_purchase(models.Model):
    """
    采购计划
    """
    
    _name = 'pm.init.proj.purchase'
    _description = u'采购计划表'
    
    name = fields.Char(u'名称', size=30, requried=True)
    proj_plan_category = fields.Many2one('sys.constant', u'分类', domain=[('type', '=', 'PROJ_GOODS_CATEGORY')])
    proj_plan_specifications = fields.Char(u'规格', size=30)
    proj_plan_prices = fields.Float(u'单价')
    proj_plan_count = fields.Float(u'数量')
    proj_plan_budget = fields.Float(u'预算')
    
    proj_apply_id = fields.Many2one('pm.init.proj.apply', u'立项申请表关联字段')
    
    
class pm_init_reply_infos(models.Model):
    """
    项目批复信息
    """
    
    _name = 'pm.init.reply.infos'
    _description = u'项目批复信息'
    
    proj_reply_file_number=fields.Char(string=u'批复文号',size=100)
    proj_reply_files=fields.Binary(string=u'批复文件')
    proj_reply_fmis=fields.Char(string=u'FMIS账号')
    proj_reply_contract=fields.Char(string=u'合同编号',size=100)
    proj_reply_funds=fields.Float(string=u'批复总金额')
    proj_reply_start_date=fields.Date(string=u'开始时间')
    proj_reply_end_date=fields.Date(string=u'结束时间')
    proj_num=fields.Char(string=u'项目编号',size=100)


class pm_init_budget(models.Model):
    """
    经费预算表
    """
    
    _name = 'pm.init.budget'
    _description = u"经费预算信息"
    
    proj_apply_id = fields.Char(u'项目ID', size=10)
    sn = fields.Integer(u'序号')
    subject_id = fields.Integer(u'科目ID')
    subject_name = fields.Char(u'科目名称', size=50)
    year = fields.Integer(u'年度')
    value = fields.Float(u'预算值')
    
    #从jqGrid中取数进行保存
    @api.model
    def saveJqGrid(self, id, start_year, end_year, data):
        detail_res = self.search([('proj_apply_id', '=', id)])
        if not detail_res:
            for record in data:
                record['proj_apply_id'] = id
                _record = record
                for k in range(start_year, end_year+1):
                    _record['year'] = k
                    _record['value'] =  _record[str(k)]
                    self.create(_record)
        else:
            for record in data:
                _record = record
                for k in range(start_year, end_year+1):
                    d_res = self.search([('proj_apply_id', '=', record['proj_id']),('year','=',k),('subject_id','=',record['subject_id'])])
                    _record['value'] =  _record[str(k)]
                    _record['proj_apply_id'] = id
                    _record['year'] = k
                    if not d_res:
                        self.create(_record)
                    else:
                        d_res.write(record)  
    
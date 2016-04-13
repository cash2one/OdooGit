# -*- coding: utf-8 -*-
##############################################################################
#    项目基础信息
#    Created on 2015年12月18日
#    @author: LY
#    Last edit on 2015年12月18日
#    Last edit by  LY
##############################################################################

from openerp import models, fields, api
from lxml import etree

class pm_init_basic(models.Model):
    """
    存储项目基本信息及评估审批信息
    """
    
    _name = 'pm.init.basic'
    _description=u'项目基本信息'
    
    #项目基本信息字段
    name = fields.Char(u'项目名称',size=100,required=True)
    proj_hierarch = fields.Many2one('sys.constant', u'项目层级',domain=[('type','=','PROJ_HIERARCH')])
    proj_parent_id = fields.Many2one('pm.init.basic', u'上级项目')
    proj_first_party = fields.Char(u'项目来源', size=100)
    proj_vld = fields.Many2one('oa.admin.org',u'承担单位',required=True,domain=[('parent_id','=',False)])
    proj_cooperation_vld = fields.Char(u'合作单位', size=100)
    proj_total_funds = fields.Float(string=u'预算总额',digits=(16,2),required=True)
    proj_important = fields.Many2one('sys.constant',u'项目重要性',domain=[('type','=','PROJ_IMPORTANCE')],required=True)
    proj_category =  fields.Many2one('sys.constant', u'项目类别',domain=[('type','=','PROJ_CATEGORY_BIG')],required=True)
    proj_level =  fields.Many2one('sys.constant', u'项目级别',domain=[('type','=','PROJ_LEVEL')])
    proj_start_date = fields.Date(u'项目开始时间',required=True)
    proj_end_date = fields.Date(u'项目结束时间',required=True)
    proj_num=fields.Char(u'项目编号',size=30)
    fmis_num=fields.Char(u'FMIS编号',size=30)
    proj_type=fields.Many2one('sys.constant', u'项目类型',domain=[('type','=','PROJ_CATEGORY_SMALL')])
    proj_state=fields.Selection([('draft',u'草稿'),('submitted',u'已提交'),('fapproved',u'所（中心）已审批'),('sapproved',u'科研处已审批')],u'状态')
    proj_summary=fields.Text(u'项目概述')
    proj_periods=fields.Many2one('sys.constant',u'项目阶段',domain=[('type','=','PROJ_CATEGORY_SMALL')])
    proj_state_count=fields.Integer(u'当前流程指示',default=2)
    proj_rejected_count=fields.Integer(u'流程退回次数',default=0)
    proj_state_total=fields.Integer(compute='_get_proj_state_total',string=u'流程总节点数')
    proj_flow_is_end=fields.Boolean(string=u'流程是否结束',default=False)
    proj_creater=fields.Integer(u'创建者')
        
    #所中心审批情况
    proj_fapproved_date=fields.Date(u'审批时间')
    proj_fapproved_where=fields.Char(u'审批地点',size=100)
    proj_fapproved_peoples=fields.Char(u'审批人员',size=100)
    proj_fapproved_charger=fields.Char(u'审批组织人',size=100)
    proj_fapproved_results=fields.Text(u'审批意见和结论')
    #科研处审批情况
    proj_sapproved_date=fields.Date(u'审批时间')
    proj_sapproved_where=fields.Char(u'审批地点',size=100)
    proj_sapproved_peoples=fields.Char(u'审批人员',size=100)
    proj_sapproved_charger=fields.Char(u'审批组织人',size=100)
    proj_sapproved_results=fields.Text(u'审批意见和结论')
    
    #委托信息
    proj_delegete_people=fields.Char(string=u'委托人',size=30)
    proj_delegete_forms=fields.Many2one('sys.constant',string=u'委托方式',domain=[('type','=','PROJ_DELEGETE_FORMS')])
    proj_delegete_phone=fields.Char(string=u'联系电话',size=13)
    proj_delegete_when=fields.Date(string=u'委托时间')
    proj_delegete_vld=fields.Char(string=u'单位',size=50)
    proj_delegete_contents=fields.Text(string=u'委托内容')
    proj_delegete_files=fields.Binary(string=u'委托接收记录表')
    proj_delegete_suggestions=fields.Text(string=u'技术支持单位对委托任务的意见')
    proj_delegete_contact=fields.Char(string=u'联系人',size=30)
    
    #计算字段，用于获取对应字段信息，设置工作流状态条或者控制字段显示、隐藏
    proj_important_calc=fields.Char(compute='_get_proj_important', string=u'项目重要性计算字段')
    proj_category_calc=fields.Char(compute='_get_proj_category', string=u'项目类别计算字段')
    proj_type_calc=fields.Char(compute='_get_proj_type', string=u'项目类型计算字段')
    proj_hierarch_calc=fields.Char(compute='_get_proj_hierarch', string=u'项目层级计算字段')  
    proj_delegete_forms_calc=fields.Char(compute='_get_proj_delegete_forms', string=u'委托方式计算字段')    
    
    proj_leaders=fields.Char(compute='_get_leaders_ids', string=u'获取当前用户所属所（中心）领导id')
    proj_reply_leaders=fields.Many2one('oa.staff.basic',u'分管所（中心）领导',required=True) #,domain='[("id","in",proj_leaders)]'
    
    proj_flow_button = fields.Boolean(compute='_hide_flow_button',string=u'流程按钮显示/隐藏控制')
    
    #技术支持类项目可以不通过立项流程直接结束
    proj_apply_is_over=fields.Boolean(u'立项是否结束')
    proj_apply_is_over_files=fields.Binary(u'项目合同或计划任务书附件')
    
    def _get_leaders_ids(self):
        leader_staff_ids = self.env['oa.staff.basic'].search([('administrative_post_id.name','in',(u'书记',u'中心主任',u'中心副主任',u'所长',u'副所长',u'所长助理'))]).ids
        self.proj_leaders = '['+','.join([str(item) for item in leader_staff_ids])+']'
    
    @api.depends('proj_important')
    def _get_proj_important(self):
        self.proj_important_calc=self.proj_important.name
    
    @api.depends('proj_state')
    def _hide_flow_button(self):
        c_uid = self.env.uid
        #超级管理员
        if c_uid == 1:
            self.proj_flow_button = False
            return
        #所中心人员判断
        if self.user_in_groups('aqy_project.group_unit_leaders') and self.proj_state == 'submitted' and self.proj_reply_leaders.related_user.id == c_uid:
            self.proj_flow_button = False
            return
        #科研处人员判断
        if self.user_in_groups('aqy_project.group_init_sapproved') and self.proj_state == 'fapproved':
            self.proj_flow_button = False
            return
        
        self.proj_flow_button = True
        #aqy_project.group_unit_leaders,aqy_project.group_init_sapproved,aqy_project.group_init_apply_fhapproved
        
    def user_in_groups(self,groups):
        assert groups and '.' in groups, u"权限组参数不正确"
        module, ext_id = groups.split('.')
        self.env.cr.execute("""SELECT 1 FROM res_groups_users_rel WHERE uid=%s AND gid IN
                        (SELECT res_id FROM ir_model_data WHERE module=%s AND name=%s)""",
                   (self.env.uid, module, ext_id))
        return bool(self.env.cr.fetchone())
    
    @api.onchange('proj_vld')
    def _set_vld_leaders(self):
        if(self.proj_vld.id):
            staff_ids = self.env['oa.staff.basic'].search(['&',('vld_site','=',self.proj_vld.id),'|',('related_user','=',1),('administrative_post_id.name','in',(u'书记',u'中心主任',u'中心副主任',u'所长',u'副所长',u'所长助理'))]).ids
        else:
            staff_ids = self.env['oa.staff.basic'].search(['|',('related_user','=',1),('administrative_post_id.name','in',(u'书记',u'中心主任',u'中心副主任',u'所长',u'副所长',u'所长助理'))]).ids
        return {'domain':{'proj_reply_leaders':[('id','in',staff_ids)]}}
        #self.proj_reply_leaders.
    
    @api.depends('proj_category')
    def _get_proj_category(self):
        self.proj_category_calc=self.proj_category.name
    
    @api.depends('proj_type')    
    def _get_proj_type(self):
        self.proj_type_calc=self.proj_type.name
    
    @api.depends('proj_hierarch')
    def _get_proj_hierarch(self):
        self.proj_hierarch_calc=self.proj_hierarch.name
    
    @api.depends('proj_delegete_forms')    
    def _get_proj_delegete_forms(self):
        self.proj_delegete_forms_calc=self.proj_delegete_forms.name
    
    @api.depends('proj_important','proj_category')
    def _get_proj_state_total(self):
        proj_important_name=self.proj_important.name
        proj_category_name=self.proj_category.name
        if (proj_important_name and proj_important_name == u'一般项目') or (proj_category_name and proj_category_name == u'技术支持类'):
            self.proj_state_total=3
        else:
            self.proj_state_total=4
    
    @api.multi
    def write(self, vals):
        """
        保存的同时提交上级进行审批
        """
        
        res=models.Model.write(self, vals)
        #判断流程是否结束，如果结束则将该记录插入立项申请表中
        if self.proj_flow_is_end:            
            new_vals=self._clean_data(self.read(['proj_creater','name','proj_hierarch','proj_parent_id','proj_first_party','proj_vld','proj_cooperation_vld','proj_total_funds','proj_important','proj_category','proj_type','proj_start_date','proj_end_date','proj_periods','proj_reply_leaders','proj_level'])[0])
            new_vals['action']='insert'
            models.Model.create(self.env['pm.init.proj.apply'], new_vals)
            #self.env['pm.init.proj.apply'].create(new_vals)
        #判断是否技术支持类项目且是否有立项合同之类的文据
        #proj_type_id = self.env['sys.constant'].search([('name','=',u'技术支持类'),('type','=','PROJ_CATEGORY_BIG')]).id
        #if self.proj_category.id == proj_type_id and proj_apply_is_over:
                          
        return res
    
    @api.model
    @api.returns('self', lambda value:value.id)
    def create(self, vals):
        """
        除技术支持类有任务书或者合同的项目直接创建立项结果外，其余项目
        创建的同时提交上级进行审批
        """
        
        #技术支持类有任务书或合同的直接进入到实施阶段
        proj_type_id = self.env['sys.constant'].search([('name','=',u'技术支持类'),('type','=','PROJ_CATEGORY_BIG')]).id
        if vals.has_key('proj_apply_is_over') and vals['proj_apply_is_over']==True and vals.has_key('proj_category') and vals['proj_category'] == proj_type_id:
            vals['proj_periods']=self.env['sys.constant'].search([('name','=',u'实施中'),('type','=','PROJ_PERIODS')]).id            
            vals['proj_flow_is_end'] = True
            vals['proj_creater'] = self.env.uid
            models.Model.create(self.env['pm.init.proj.apply'], vals)
            return models.Model.create(self, vals)
        #vals['proj_state']='submitted'
        #根据项目重要性和项目类型判断流程分支,设定项目阶段
        state_id=self.env['sys.constant'].search([('name','=',u'立项中'),('type','=','PROJ_PERIODS')]).id
        vals['proj_periods']=state_id
        if not vals.has_key('proj_creater'):
            vals['proj_creater']=self.env.uid        
        return models.Model.create(self, vals)
    
    def _clean_data(self,data):        
        if data.has_key('id'):
            data.pop('id')
        keys=data.keys()
        for key in keys:                
            if type(data[key]) == tuple:
                data[key]=data[key][0]
        return data
    """
    def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
        res = super(pm_init_basic, self).fields_view_get(cr, uid, view_id=view_id, view_type=view_type, context=context, toolbar=toolbar,submenu=False)
        view_content=models.Model.fields_view_get(self, cr, uid, view_id=view_id, view_type=view_type, context=context, toolbar=toolbar, submenu=submenu)
        if view_type == 'form':
            doc=etree.XML(view_content['arch'])
            doc.xpath("//field[@name='proj_state']")[0].attrib['statusbar_visible']='draft,submitted'
            view_content['arch'] = etree.tostring(doc)
        return view_content"""
        
        
class pm_proposal_documents(models.Model):
    """
    开题报告信息
    """
    
    _name = 'pm.proposal.documents'
    _description=u'开题报告'
    
    name = fields.Char('文档名称',required=True)
    project_id = fields.Many2one('pm.init.proj.apply',string='所属项目',required=True,domain=[('proj_periods.name','=','实施中')])
    document_type = fields.Many2one('sys.constant',string='文档类型',domain=[('type','=','impl_document_type')],required=True)
    content_zy = fields.Text('内容摘要',required=True)
    document_version_record_id = fields.One2many('pm.proposal.version.info','proposal_document_id',string='版本信息')


class pm_proposal_version_info(models.Model):
    """
    开题报告版本信息
    """
    
    _name = 'pm.proposal.version.info'
    _description = u'版本信息'
    
    number = fields.Char('版本号',required=True)
    operator = fields.Many2one('res.users',string='修改人',required=True)
    remark = fields.Text('修改说明',required=True)
    attach = fields.Binary('附件',required=True)
    proposal_document_id = fields.Many2one('pm.proposal.documents',string='过程文档')

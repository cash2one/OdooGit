# -*- coding: utf-8 -*-
##############################################################################
#    验收
#    Created on 2016年1月14日
#    @author: LY
#    Last edit on 2016年1月14日
#    Last edit by  LY
##############################################################################

from PIL import Image
import StringIO
import io
import urllib2
import cStringIO
import base64
from openerp import models, fields, api
from openerp.http import request

class pm_acceptance(models.Model):
    """
    项目验收表
    """
    
    _name='pm.acceptance'
    _description=u'项目验收表'
    
    pm_proj_id=fields.Many2one('pm.init.proj.apply',string=u'项目关联字段',required=True)
    
    name = fields.Char(related='pm_proj_id.name',string=u'项目名称',size=100,required=True)
    proj_vld = fields.Many2one(related='pm_proj_id.proj_vld',string=u'承担单位',readonly=True)
    proj_hierarch = fields.Many2one(related='pm_proj_id.proj_hierarch',string=u'项目层级',domain=[('type','=','PROJ_HIERARCH')],readonly=True)
    proj_parent_id = fields.Many2one(related='pm_proj_id.proj_parent_id', string=u'上级项目',readonly=True)
    proj_funds=fields.Float(related='pm_proj_id.proj_total_funds',string=u'项目总金额',readonly=True)
    proj_important = fields.Many2one(related='pm_proj_id.proj_important',string=u'项目重要性',domain=[('type','=','PROJ_IMPORTANCE')],readonly=True)
    proj_category =  fields.Many2one(related='pm_proj_id.proj_category', string=u'项目类别',domain=[('type','=','PROJ_CATEGORY_BIG')],readonly=True)
    proj_type = fields.Many2one(related='pm_proj_id.proj_type', string=u'项目类型',domain=[('type','=','PROJ_CATEGORY_SMALL')],readonly=True)
    proj_level =  fields.Many2one(related='pm_proj_id.proj_level', string=u'项目级别',domain=[('type','=','PROJ_LEVEL')],readonly=True)
    proj_start_date = fields.Date(related='pm_proj_id.proj_start_date',string=u'项目开始时间',readonly=True)
    proj_end_date = fields.Date(related='pm_proj_id.proj_end_date',string=u'项目结束时间',readonly=True)
    proj_pm_uid = fields.Integer(related='pm_proj_id.proj_pm_uid',string=u'项目负责人',readonly=True)
    proj_creater = fields.Integer(related='pm_proj_id.proj_creater',string=u'项目创建人',readonly=True)
    proj_accepance_state = fields.Selection([('draft', u'草稿'), ('submitted', u'已提交'), ('szx_approved', u'所（中心）已验收'), ('kyc_approved', u'科研处已验收'), ('yzg_approved', u'院主管领导已审批'), ('fzs_approved', u'副总师已审批')], u'状态')
    proj_selfacceptance_complete=fields.Boolean(string=u'内部验收是否完成')    
    
    pm_acceptance_attachments_id=fields.One2many('pm.acceptance.attachments','pm_acceptance_id',string='验收材料清单')
    
    #所（中心）验收
    pm_facceptance_date=fields.Date(string=u'时间')
    pm_facceptance_where=fields.Char(string=u'地点',size=50)
    pm_facceptance_who=fields.Char(string=u'专家组成员',size=100)
    pm_facceptance_way=fields.Many2one('sys.constant',string=u'评审方式',domain=[('type','=','ACCEPTANCE_WAY')])
    pm_facceptance_fdocuments=fields.Text(string=u'验收意见')    
    
    #科研处验收
    pm_sacceptance_date=fields.Date(string=u'时间')
    pm_sacceptance_where=fields.Char(string=u'地点',size=50)
    pm_sacceptance_who=fields.Char(string=u'专家组成员',size=100)
    pm_sacceptance_way=fields.Many2one('sys.constant',string=u'评审方式',domain=[('type','=','ACCEPTANCE_WAY')])
    pm_sacceptance_sdocuments=fields.Text(string=u'验收意见')
    
    #项目验收
    pm_final_acceptance_date=fields.Date(string=u'时间')
    pm_final_acceptance_where=fields.Char(string=u'地点',size=50)
    pm_final_acceptance_who=fields.Char(string=u'专家组成员',size=100)
    pm_final_acceptance_way=fields.Many2one('sys.constant',string=u'评审方式',domain=[('type','=','ACCEPTANCE_WAY')])
    pm_final_acceptance_sdocuments=fields.Text(string=u'验收意见')

    #副总师审批意见
    pm_fzs_acceptance_who=fields.Char(string=u'审批人',size=100)
    pm_fzs_acceptance_date=fields.Date(string=u'审批时间')
    pm_fzs_acceptance_result=fields.Text(string=u'审批意见')
    
    #主管院长审批意见
    pm_yzg_acceptance_who=fields.Char(string=u'审批人',size=100)
    pm_yzg_acceptance_date=fields.Date(string=u'审批时间')
    pm_yzg_acceptance_result=fields.Text(string=u'审批意见')
    
    #需要授权人授权
    pm_sacceptance_fauth=fields.Boolean(string=u'需要授权验证')
    pm_sacceptance_fauth_who=fields.Many2one('oa.staff.basic',string=u'授权人')
    pm_sacceptance_fauth_date=fields.Date(string=u'授权时间')
    pm_sacceptance_fauth_file=fields.Binary(string=u'授权文件')
    
    #院长核准
    pm_sacceptance_sauth=fields.Boolean(string=u'需要院长核准')
    pm_sacceptance_sauth_who=fields.Many2one('oa.staff.basic',string=u'核准人')
    pm_sacceptance_sauth_date=fields.Date(string=u'核准时间')
    pm_sacceptance_sauth_file=fields.Binary(string=u'核准文件')
    
    #计算字段
    pm_acceptance_workflow_split=fields.Integer(compute='_get_proj_flow_split', string=u'流程分支计算判断')
    pm_acceptance_category=fields.Integer(compute='_get_proj_flow_split', string=u'项目类型判断')
    pm_acceptance_flow_button=fields.Boolean(compute='_hide_flow_button', string=u'控制流程按钮的显示隐藏')
    pm_acceptance_user_type=fields.Integer(compute='_get_user_type',string=u'判断用户的类型，1-项目经理或超级管理员，2-所中心领导，3-科研处人员')
    pm_is_user_pm=fields.Boolean(compute='_is_user_pm',string=u'判断用户是否项目经理')
    
    pm_flow_reject_count = fields.Integer(string=u'流程退回次数',default=0)
    
    def search_read(self, cr, uid, domain=None, fields=None, offset=0, limit=None, order=None, context=None):        
        return models.Model.search_read(self, cr, uid, domain=domain, fields=fields, offset=offset, limit=limit, order=order, context=context)
    
    def writeRejectCount(self):
        self.pm_flow_reject_count = self.pm_flow_reject_count + 1
    
    @api.depends('pm_proj_id')
    def _is_user_pm(self):
        c_uid = self.env.uid
        if self.user_in_groups('aqy_project.group_proj_manager') and self.pm_proj_id.proj_pm_uid == c_uid or c_uid == 1:
            self.pm_is_user_pm = True
        else:
            self.pm_is_user_pm = False
    
    @api.depends('proj_accepance_state')
    def _get_user_type(self):
        c_uid = self.env.uid
        #项目经理判断
        if self.user_in_groups('aqy_project.group_proj_manager') and self.pm_proj_id.proj_pm_uid == c_uid and self.proj_accepance_state == 'draft' or c_uid == 1:
                self.pm_acceptance_user_type = 1
                return
        #所中心人员判断
        if self.user_in_groups('aqy_project.group_unit_leaders') and self.proj_accepance_state == 'submitted' and self.pm_proj_id.proj_reply_leaders.related_user.id == c_uid:
                self.pm_acceptance_user_type = 2
                return
        #科研处人员判断
        if self.user_in_groups('aqy_project.group_acceptance_sapproved') and self.proj_accepance_state == 'szx_approved':
                self.pm_acceptance_user_type = 3
                return
    
    @api.depends('proj_accepance_state')
    def _hide_flow_button(self):
        c_uid = self.env.uid
        #超级管理员  
        if c_uid == 1:
            self.pm_acceptance_flow_button = False
            return
        #项目经理判断
        if self.user_in_groups('aqy_project.group_proj_manager') and self.pm_proj_id.proj_pm_uid == c_uid and self.proj_accepance_state == 'draft':
                self.pm_acceptance_flow_button = False
                return
        #所中心人员判断
        if self.user_in_groups('aqy_project.group_unit_leaders') and self.proj_accepance_state == 'submitted' and self.pm_proj_id.proj_reply_leaders.related_user.id == c_uid:
                self.pm_acceptance_flow_button = False
                return
        #科研处人员判断
        if self.user_in_groups('aqy_project.group_acceptance_sapproved') and self.proj_accepance_state == 'szx_approved':
                self.pm_acceptance_flow_button = False
                return
        self.pm_acceptance_flow_button = True
    
    def user_in_groups(self,groups):
        assert groups and '.' in groups, "External ID must be fully qualified"
        module, ext_id = groups.split('.')
        self.env.cr.execute("""SELECT 1 FROM res_groups_users_rel WHERE uid=%s AND gid IN
                        (SELECT res_id FROM ir_model_data WHERE module=%s AND name=%s)""",
                   (self.env.uid, module, ext_id))
        return bool(self.env.cr.fetchone())
    
    @api.depends('proj_category', 'proj_type','proj_important')
    def _get_proj_flow_split(self):
        """
        根据项目的类别和类型来判断验收需要走哪些流程
        """
        
        #20160229,经过讨论，所有项目验收流程固定为所中心-科研处
        self.pm_acceptance_workflow_split = 5
        return
        i = self.proj_important.name
        t = self.proj_type.name
        c = self.proj_category.name
        
        if c == u'技术研究和开发类':
            if t in (u'专项项目',u'纵向项目'):
                #专项项目与纵向项目的验收流程：所（中心）验收->科研处验收。
                self.pm_acceptance_workflow_split = 5
            elif t in (u'横向项目',u'院级项目'):
                #横向项目和院级项目只需要自验收即所（中心）验收
                self.pm_acceptance_workflow_split = 2
        elif c == u'技术支持类':
            if i == u'重点项目':
                #重点技术支持项目流程：所（中心）验收->院主管领导审批
                self.pm_acceptance_workflow_split = 1
            else:
                #一般技术支持项目只需要自验收即所（中心）验收
                self.pm_acceptance_workflow_split = 2
        elif c == u'技术服务类':
            self.pm_acceptance_category = 1
            if i == u'重点项目':
                #重点技术服务项目流程：所（中心）验收->科研处验收->院业务分管副总师审定，根据需要确定是院授权人签发和主管院长核准
                self.pm_acceptance_workflow_split = 3
            else:
                #一般技术服务项目只需要自验收即所（中心）验收->院业务分管副总师审定
                self.pm_acceptance_workflow_split = 4
        else:
            self.pm_acceptance_workflow_split = 2
            self.pm_acceptance_category = 0
    
    @api.model
    @api.returns('self', lambda value:value.id)
    def create(self, vals):
        return models.Model.create(self, vals)
    
    @api.multi
    def write(self, vals):
        return models.Model.write(self, vals)
    
    _sql_constraints = [
        ('pm_proj_id_key', 'UNIQUE (pm_proj_id)', u'项目已存在!')
    ]
    
    @api.multi
    def auth_fapproved(self):
        """
        授权签发
        """
        
        #self.env.uid  int(image.size[0]*0.618)
        img_data_e_sign = base64.b64decode(self.env['oa.staff.basic'].search([('related_user','=',16)]).e_signature)
        img_data = base64.b64decode(self.pm_sacceptance_fauth_file)
        image_e_sign = Image.open(cStringIO.StringIO(img_data_e_sign))
        image = Image.open(cStringIO.StringIO(img_data))
        left=int(image.size[0]*0.618)
        upper=int(image.size[1]*0.618)
        paste_box = (left,upper,left+image_e_sign.size[0],upper+image_e_sign.size[1])
        image.paste(image_e_sign,paste_box)
        d = image.tobytes()
        self.pm_sacceptance_fauth_file = d #base64.b64encode(image.tostring())
        #image.save('imgout2.png')
        image_e_sign.close()
        image.close()        
    
    @api.multi
    def auth_sapproved(self):
        """
        院长审定
        """
        return 1
    
    
class pm_acceptance_attachments(models.Model):
    """
    项目验收需要的附件表
    """    
    
    _name='pm.acceptance.attachments'
    _description=u'项目验收附件表'
    
    name=fields.Char(string='名称',size=50)
    filename=fields.Char(string='文件名',size=50)
    file=fields.Binary(string=u'附件')
    type=fields.Selection([('f','所（中心）验收材料'),('s','科研处验收材料')])
    
    pm_acceptance_id=fields.Many2one('pm.acceptance',string=u'验收申请表关联字段')

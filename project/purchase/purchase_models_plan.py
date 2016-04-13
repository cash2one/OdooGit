# -*- coding: utf-8 -*-

from openerp import models, fields, api
from _tkinter import create
from openerp.api import onchange

'''
菜单名：采购计划管理
'''
#采购计划
class pm_purchase_plan(models.Model):
    _name = 'pm.purchase.plan'
    _description = u'采购计划'
    
    @api.onchange('project_id')
    def change_project_id(self):
        for record in self:
            record.goods_record_id = False#删除采购物资
            
    @api.onchange('category')
    def change_category(self):
        purchase_category_fw = self.env['sys.constant'].search([('type','=','PROJ_GOODS_CATEGORY'),('name','=',u'服务')])
        for record in self:
            record.goods_record_id = False#删除采购物资
            record.zb_bd_record_id = False#删除招标标包
            if record.category == purchase_category_fw:#如果是服务类采购
                record.is_category_fw = True
            else:
                record.is_category_fw = False
                record.wx_plan_check_result = False
    
    @api.onchange('wx_plan_check_result')
    def change_wx_plan_check_result(self):
        for record in self:
            if record.is_category_fw:
                record.explanation = record.wx_plan_check_result.proj_background
            else:
                record.explanation = False
    @api.onchange('method')
    def change_method(self):
        for record in self:
            purchase_method_zb =  self.env['sys.constant'].search([('type','=','purchase_method'),('name','=',u'招标采购')])
            purchase_method_tp =  self.env['sys.constant'].search([('type','=','purchase_method'),('name','=',u'竞争性谈判采购')])
            if record.method == purchase_method_zb:#如果是招标采购
                record.negotiate_manufacturer = False
                record.negotiate_manufacturer_reason = False
                record.negotiate_expert = False
                record.is_method_zb = True
                record.is_method_tp = False
            elif record.method == purchase_method_tp:#如果是竞争性谈判采购
                record.zb_category = False
                record.procurement_finish_time = False
                record.choose_method = False
                record.delivery_time = False
                record.zb_method = False
                record.zb_bd_record_id = False
                record.fund_source = False
                record.bidder_qualification = False
                record.tender_organ = False
                record.tender_work_plan = False
                record.is_method_zb = False
                record.is_method_tp = True
            else:
                record.zb_category = False
                record.procurement_finish_time = False
                record.choose_method = False
                record.delivery_time = False
                record.zb_method = False
                record.zb_bd_record_id = False
                record.fund_source = False
                record.bidder_qualification = False
                record.tender_organ = False
                record.tender_work_plan = False
                record.negotiate_manufacturer = False
                record.negotiate_manufacturer_reason = False
                record.negotiate_expert = False
                record.is_method_zb = False
                record.is_method_tp = False
    
    @api.onchange('zb_method')
    def change_zb_method(self):
        purchase_zb_method_agent =  self.env['sys.constant'].search([('type','=','purchase_zb_method'),('name','=',u'委托招标')])
        for record in self:
            if record.zb_method == purchase_zb_method_agent:
                record.is_zb_method_agent = True
            else:
                record.is_zb_method_agent = False
                record.tender_organ = False
                
    @api.onchange('choose_method')
    def change_choose_method(self):
        purchase_choose__method_invite =  self.env['sys.constant'].search([('type','=','purchase_choose_method'),('name','=',u'邀请招标')])
        for record in self:
            if record.choose_method == purchase_choose__method_invite:
                record.is_choose__method_invite = True
            else:
                record.is_choose__method_invite = False
                record.choose_manufacturer = False
                record.choose_manufacturer_reason = False
                
    
    @api.onchange('budget')
    def change_budget(self):
        for record in self:
            if record.budget <= 0 or record.budget > record.project_id.proj_reply_funds:
                record.budget = 0.01
                record.method = False
                record.method_yj = False
            elif record.budget < 3:
                record.method = False
                record.method_yj = False
            elif record.budget >= 100:
                purchase_method_zb =  self.env['sys.constant'].search([('type','=','purchase_method'),('name','=',u'招标采购')])
                record.method = purchase_method_zb
                
    @api.model
    @api.returns('self', lambda value:value.id)
    def create(self, vals):
        if vals.has_key('budget'):
            if vals['budget'] >= 100:
                purchase_method_zb =  self.env['sys.constant'].search([('type','=','purchase_method'),('name','=',u'招标采购')])
                vals['method'] = purchase_method_zb.id
        return models.Model.create(self, vals)
    
    @api.multi
    def write(self, vals):
        if vals.has_key('budget'):
            if vals['budget'] >= 100:
                purchase_method_zb =  self.env['sys.constant'].search([('type','=','purchase_method'),('name','=',u'招标采购')])
                vals['method'] = purchase_method_zb.id
        return models.Model.write(self, vals)

    def get_project_id_domain(self):
        if self.env.uid == 1:
            return "[('proj_periods.name','=',u'实施中'),('proj_apply_purchase','!=',False)]"
        return "[('proj_periods.name','=',u'实施中'),('proj_pm_uid','=',uid),('proj_apply_purchase','!=',False)]"

    project_id = fields.Many2one('pm.init.proj.apply',string=u'所属项目',required=True,domain=get_project_id_domain)
    name = fields.Char(string=u'采购计划名称',required=True)
    organ_id = fields.Many2one('oa.admin.org',u'采购单位',required=True)
    category = fields.Many2one('sys.constant',u'采购类别',domain=[('type', '=', 'PROJ_GOODS_CATEGORY')],required=True)
    budget = fields.Float(u'费用预算(万元)',required=True,default=0.01)
    explanation = fields.Text(u'需求及用途',required=True)
    method = fields.Many2one('sys.constant',u'采购方式',domain=[('type','=','purchase_method')])
    agent_id = fields.Many2one('res.users',string=u'经办人',required=True)
    application_date = fields.Date(u'申请日期',required=True)
    method_yj = fields.Text(u'采购方式的选择依据')
    goods_record_id = fields.One2many('pm.purchase.plan.goods','plan_id',string=u'采购物资')
    
    wx_plan_check_result = fields.Many2one('pm.techservice.plan',string=u'外协计划审批结果',domain="[('parent_proj', '=', project_id),('is_over','=',True)]")
    is_category_fw = fields.Boolean(string=u'是否为服务类采购',default=False)
    is_method_zb = fields.Boolean(string=u'是否为招标采购',default=False)
    is_method_tp = fields.Boolean(string=u'是否为竞争性谈判采购',default=False)
    has_purchase_reuslt = fields.Boolean(string=u'是否存在采购结果',default=False)
    
        
#招标方案开始
    zb_category = fields.Many2one('sys.constant',string=u'招标类别',domain=[('type','=','purchase_zb_category')])
    procurement_finish_time = fields.Date(string=u'预期采购完成时间')
    choose_method = fields.Many2one('sys.constant',string=u'选商方式',domain=[('type','=','purchase_choose_method')])
    choose_manufacturer = fields.Text(u'建议邀请谈判厂商')
    choose_manufacturer_reason = fields.Text(u'建议邀请谈判厂商的理由')
    delivery_time = fields.Date(string=u'设备交付时间')
    zb_method = fields.Many2one('sys.constant',string=u'组织形式',domain=[('type','=','purchase_zb_method')])
    zb_bd_record_id = fields.One2many('pm.purchase.zb.bd','plan_id',string=u'招标标包')
    fund_source = fields.Text(u'经费来源')
    bidder_qualification = fields.Text(u'投标人资格条件')
    tender_organ = fields.Char(u'委托招标单位')
    tender_work_plan = fields.Text(u'招标工作计划安排')
    is_zb_method_agent = fields.Boolean(string=u'是否为委托招标',default=False)
    is_choose__method_invite = fields.Boolean(string=u'是否为邀请招标',default=False)
#招标方案结束

#竞争性谈判方案开始    
    negotiate_manufacturer = fields.Text(u'建议邀请谈判厂商')
    negotiate_manufacturer_reason = fields.Text(u'建议邀请谈判厂商的理由')
    negotiate_expert = fields.Text(u'参加谈判专家')
#竞争性谈判方案结束
#所(中心)审批
    suo_suggest = fields.Text(u'审批意见')
    suo_verifier_id = fields.Many2one('res.users',string=u'审批人')
    suo_time = fields.Date(u'日期')
#科研处审批
    ke_suggest = fields.Text(u'审批意见')
    ke_verifier_id = fields.Many2one('res.users',string=u'审批人')
    ke_time = fields.Date(u'日期')
#财务处审批
    cai_suggest = fields.Text(u'审批意见')
    cai_verifier_id = fields.Many2one('res.users',string=u'审批人')
    cai_time = fields.Date(u'日期')
#院办审批
    yb_suggest = fields.Text(u'审批意见')
    yb_verifier_id = fields.Many2one('res.users',string=u'审批人')
    yb_time = fields.Date(u'日期')
#副总师审批
    fzs_suggest = fields.Text(u'审批意见')
    fzs_verifier_id = fields.Many2one('res.users',string=u'审批人')
    fzs_time = fields.Date(u'日期')
#院长办公会审批
    yzbgh_suggest = fields.Text(u'审批意见')
    yzbgh_verifier_id = fields.Many2one('res.users',string=u'审批人')
    yzbgh_time = fields.Date(u'日期')
#院长审批
    yz_suggest = fields.Text(u'审批意见')
    yz_verifier_id = fields.Many2one('res.users',string=u'审批人')
    yz_time = fields.Date(u'日期')
#主管采购院长审批
    yzzgcg_suggest = fields.Text(u'审批意见')
    yzzgcg_verifier_id = fields.Many2one('res.users',string=u'审批人')
    yzzgcg_time = fields.Date(u'日期')
    
    hz_number = fields.Char(u'回执编号')
    zb_file_number = fields.Char(u'招标/文件编号')
    hz_suggest = fields.Text(u'回执意见')
    hz_time = fields.Date(u'回执日期')
    hz_attach = fields.Integer(u'备案回执文件')
    
    state = fields.Selection([('draft',u'草稿'),('submitted', u'已提交'),('suo_stop_accepted', u'所(中心)已审批'),('suo_accepted', u'所(中心)已审批'),('ke_accepted', u'科研处已审批'),('cai_accepted', u'财务处已审批'),('yb_accepted', u'院办已审批'),('fzs_stop_accepted', u'副总师已审批'),('fzs_accepted', u'副总师已审批'),('yzbgh_stop_accepted', u'院长办公会已审批'),('yzbgh_accepted', u'院长办公会已审批'),('yz_stop_accepted', u'院长已审批'),('yz_accepted', u'院长已审批'),('yzzgcg_stop_accepted', u'主管采购院长已审批'),('yzzgcg_accepted', u'主管采购院长已审批'),('jt_accepted', u'集团回执信息已填写')] ,u'审批状态')
    effective = fields.Boolean(string=u'采购计划是否已生效',default=False)
    
    @api.depends('state')
    def _get_can_approve(self):
        for record in self:
            record.can_manager_submit = False
            record.can_suo_approve = False
            record.can_ke_approve = False
            record.can_cai_approve = False
            record.can_yb_approve = False
            record.can_fzs_approve = False
            record.can_yzzgcg_approve = False
            record.can_yz_approve = False
            record.can_yzbgh_approve = False
            record.can_jt_approve = False
            
        #所中心审批
            record.comp_suo_verifier_id = record.suo_verifier_id.name
            record.comp_suo_time = record.suo_time
        #科研处审批
            record.comp_ke_verifier_id = record.ke_verifier_id.name
            record.comp_ke_time = record.ke_time
        #财务处审批
            record.comp_cai_verifier_id = record.cai_verifier_id.name
            record.comp_cai_time = record.cai_time
        #院办审批
            record.comp_yb_verifier_id = record.yb_verifier_id.name
            record.comp_yb_time = record.yb_time
        #副总师审批
            record.comp_fzs_verifier_id = record.fzs_verifier_id.name
            record.comp_fzs_time = record.fzs_time
        #院长办公会审批
            record.comp_yzbgh_verifier_id = record.yzbgh_verifier_id.name
            record.comp_yzbgh_time = record.yzbgh_time
        #院长审批
            record.comp_yz_verifier_id = record.yz_verifier_id.name
            record.comp_yz_time = record.yz_time
        #主管采购院长审批
            record.comp_yzzgcg_verifier_id = record.yzzgcg_verifier_id.name
            record.comp_yzzgcg_time = record.yzzgcg_time
            
            if record.state == 'draft':
                if self.env.uid == 1 :
                    record.can_manager_submit = True
                    
                if self.is_user_in_group('aqy_project.group_proj_manager') and record.project_id.proj_pm_uid == self.env.uid:
                    record.can_manager_submit = True
            elif record.state == 'submitted':
                if self.env.uid == 1 :
                    record.can_suo_approve = True
                    
                if self.is_user_in_group('aqy_project.group_unit_leaders') and record.project_id.proj_reply_leaders.related_user.id == self.env.uid:
                    record.can_suo_approve = True
                    
                if record.can_suo_approve:
                    record.comp_suo_verifier_id = self.env['res.users'].search([('id','=',self.env.uid)]).partner_id.name
                    record.comp_suo_time = fields.Date.today()
                else:
                    if not record.suo_suggest:
                        record.comp_suo_verifier_id = False
                        record.comp_suo_time = False
                    else:
                        record.comp_suo_verifier_id = record.suo_verifier_id.partner_id.name
                        record.comp_suo_time = record.suo_time
            elif record.state == 'suo_accepted':
                if self.env.uid == 1 :
                    record.can_ke_approve = True
                    
                if self.is_user_in_group('aqy_project.group_purchase_ky_approve'):
                    record.can_ke_approve = True
                    
                if record.can_ke_approve:
                    record.comp_ke_verifier_id = self.env['res.users'].search([('id','=',self.env.uid)]).partner_id.name
                    record.comp_ke_time = fields.Date.today()
                else:
                    if not record.ke_suggest:
                        record.comp_ke_verifier_id = False
                        record.comp_ke_time = False
                    else:
                        record.comp_ke_verifier_id = record.ke_verifier_id.partner_id.name
                        record.comp_ke_time = record.ke_time
            elif record.state == 'ke_accepted':
                if self.env.uid == 1 :
                    record.can_cai_approve = True
                    
                if self.is_user_in_group('aqy_project.group_purchase_cai_approve'):
                    record.can_cai_approve = True
                    
                if record.can_cai_approve:
                    record.comp_cai_verifier_id = self.env['res.users'].search([('id','=',self.env.uid)]).partner_id.name
                    record.comp_cai_time = fields.Date.today()
                else:
                    if not record.cai_suggest:
                        record.comp_cai_verifier_id = False
                        record.comp_cai_time = False
                    else:
                        record.comp_cai_verifier_id = record.cai_verifier_id.partner_id.name
                        record.comp_cai_time = record.cai_time
            elif record.state == 'cai_accepted':
                if self.env.uid == 1 :
                    record.can_yb_approve = True
                    
                if self.is_user_in_group('aqy_project.group_purchase_yb_approve'):
                    record.can_yb_approve = True
                    
                if record.can_yb_approve:
                    record.comp_yb_verifier_id = self.env['res.users'].search([('id','=',self.env.uid)]).partner_id.name
                    record.comp_yb_time = fields.Date.today()
                else:
                    if not record.yb_suggest:
                        record.comp_yb_verifier_id = False
                        record.comp_yb_time = False
                    else:
                        record.comp_yb_verifier_id = record.yb_verifier_id.partner_id.name
                        record.comp_yb_time = record.yb_time
            elif record.state == 'yb_accepted':
                if self.is_user_in_group('aqy_project.group_purchase_fzs_approve') and record.check_workflow_num in (2,3):
                    record.can_fzs_approve = True
                    
                    if record.can_fzs_approve:
                        record.comp_fzs_verifier_id = self.env['res.users'].search([('id','=',self.env.uid)]).partner_id.name
                        record.comp_fzs_time = fields.Date.today()
                    else:
                        if not record.fzs_suggest:
                            record.comp_fzs_verifier_id = False
                            record.comp_fzs_time = False
                        else:
                            record.comp_fzs_verifier_id = record.fzs_verifier_id.partner_id.name
                            record.comp_fzs_time = record.fzs_time
                elif self.is_user_in_group('aqy_project.group_purchase_yzzgcg_approve') and record.check_workflow_num in (6,9):
                    record.can_yzzgcg_approve = True
                    
                    if record.can_yzzgcg_approve:
                        record.comp_yzzgcg_verifier_id = self.env['res.users'].search([('id','=',self.env.uid)]).partner_id.name
                        record.comp_yzzgcg_time = fields.Date.today()
                    else:
                        if not record.yzzgcg_suggest:
                            record.comp_yzzgcg_verifier_id = False
                            record.comp_yzzgcg_time = False
                        else:
                            record.comp_yzzgcg_verifier_id = record.yzzgcg_verifier_id.partner_id.name
                            record.comp_yzzgcg_time = record.yzzgcg_time
                elif self.is_user_in_group('aqy_project.group_purchase_yz_approve') and record.check_workflow_num in (5,8):
                    record.can_yz_approve = True
                    
                    if record.can_yz_approve:
                        record.comp_yz_verifier_id = self.env['res.users'].search([('id','=',self.env.uid)]).partner_id.name
                        record.comp_yz_time = fields.Date.today()
                    else:
                        if not record.yz_suggest:
                            record.comp_yz_verifier_id = False
                            record.comp_yz_time = False
                        else:
                            record.comp_yz_verifier_id = record.yz_verifier_id.partner_id.name
                            record.comp_yz_time = record.yz_time
                elif self.is_user_in_group('aqy_project.group_purchase_yzbgh_approve') and record.check_workflow_num in (4,7):
                    record.can_yzbgh_approve = True
                    
                    if record.can_yzbgh_approve:
                        record.comp_yzbgh_verifier_id = self.env['res.users'].search([('id','=',self.env.uid)]).partner_id.name
                        record.comp_yzbgh_time = fields.Date.today()
                    else:
                        if not record.yzbgh_suggest:
                            record.comp_yzbgh_verifier_id = False
                            record.comp_yzbgh_time = False
                        else:
                            record.comp_yzbgh_verifier_id = record.yzbgh_verifier_id.partner_id.name
                            record.comp_yzbgh_time = record.yzbgh_time
            elif record.state == 'fzs_accepted' or record.state == 'yzzgcg_accepted' or record.state == 'yz_accepted' or record.state == 'yzbgh_accepted':
                if self.env.uid == 1 :
                    record.can_jt_approve = True
                    
                if self.is_user_in_group('aqy_project.group_purchase_jt_approve') and record.project_id.proj_pm_uid == self.env.uid:
                    record.can_jt_approve = True
                
    #判断当前用户是否是指定的权限组内
    def is_user_in_group(self,group_str):
        g_res = self.env.ref(group_str)
        if g_res:
            self.env.cr.execute('select count(1) from res_groups_users_rel where uid={0} and gid={1}'.format(self.env.uid,g_res.id))
            res = self.env.cr.fetchone()
            if res and res[0]>0:
                return True
        return False
    
    can_manager_submit = fields.Boolean(compute='_get_can_approve',string='项目经理可提交')
    can_suo_approve = fields.Boolean(compute='_get_can_approve',string='所(中心)可审批')
    can_ke_approve = fields.Boolean(compute='_get_can_approve',string='科研处可审批')
    can_cai_approve = fields.Boolean(compute='_get_can_approve',string='财务处可审批')
    can_yb_approve = fields.Boolean(compute='_get_can_approve',string='院办可审批')
    can_fzs_approve = fields.Boolean(compute='_get_can_approve',string='副总师可审批')
    can_yzzgcg_approve = fields.Boolean(compute='_get_can_approve',string='主管采购院长可审批')
    can_yz_approve = fields.Boolean(compute='_get_can_approve',string='院长可审批')
    can_yzbgh_approve = fields.Boolean(compute='_get_can_approve',string='院长办公会可审批')
    can_jt_approve = fields.Boolean(compute='_get_can_approve',string='集团回执信息可填写')
    
#所中心审批
    comp_suo_verifier_id = fields.Char(compute='_get_can_approve',string=u'审批人',readonly=True)
    comp_suo_time = fields.Date(compute='_get_can_approve',string=u'日期',readonly=True)
#科研处审批
    comp_ke_verifier_id = fields.Char(compute='_get_can_approve',string=u'审批人',readonly=True)
    comp_ke_time = fields.Date(compute='_get_can_approve',string=u'日期',readonly=True)
#财务处审批
    comp_cai_verifier_id = fields.Char(compute='_get_can_approve',string=u'审批人',readonly=True)
    comp_cai_time = fields.Date(compute='_get_can_approve',string=u'日期',readonly=True)
#院办审批
    comp_yb_verifier_id = fields.Char(compute='_get_can_approve',string=u'审批人',readonly=True)
    comp_yb_time = fields.Date(compute='_get_can_approve',string=u'日期',readonly=True)
#副总师审批
    comp_fzs_verifier_id = fields.Char(compute='_get_can_approve',string=u'审批人',readonly=True)
    comp_fzs_time = fields.Date(compute='_get_can_approve',string=u'日期',readonly=True)
#院长办公会审批
    comp_yzbgh_verifier_id = fields.Char(compute='_get_can_approve',string=u'审批人',readonly=True)
    comp_yzbgh_time = fields.Date(compute='_get_can_approve',string=u'日期',readonly=True)
#院长审批
    comp_yz_verifier_id = fields.Char(compute='_get_can_approve',string=u'审批人',readonly=True)
    comp_yz_time = fields.Date(compute='_get_can_approve',string=u'日期',readonly=True)
#主管采购院长审批
    comp_yzzgcg_verifier_id = fields.Char(compute='_get_can_approve',string=u'审批人',readonly=True)
    comp_yzzgcg_time = fields.Date(compute='_get_can_approve',string=u'日期',readonly=True)
    
    def _get_workflow_num(self):
        '''
        #流程一：draft——submitted——suo_stop_accepted
        #流程二：draft——submitted——suo_accepted——ke_accepted——cai_accepted——yb_accepted——fzs_stop_accepted
        #流程三：draft——submitted——suo_accepted——ke_accepted——cai_accepted——yb_accepted——fzs_accepted——jt_accepted
        #流程四：draft——submitted——suo_accepted——ke_accepted——cai_accepted——yb_accepted——yzbgh_stop_accepted
        #流程五：draft——submitted——suo_accepted——ke_accepted——cai_accepted——yb_accepted——yz_stop_accepted
        #流程六：draft——submitted——suo_accepted——ke_accepted——cai_accepted——yb_accepted——yzzgcg_stop_accepted
        #流程七：draft——submitted——suo_accepted——ke_accepted——cai_accepted——yb_accepted——yzbgh_accepted——jt_accepted
        #流程八：draft——submitted——suo_accepted——ke_accepted——cai_accepted——yb_accepted——yz_accepted——jt_accepted
        #流程九：draft——submitted——suo_accepted——ke_accepted——cai_accepted——yb_accepted——yzzgcg_accepted——jt_accepted
        '''
        purchase_zb_category_three =  self.env['sys.constant'].search([('type','=','purchase_zb_category'),('name','=',u'三类')])
        for record in self:
            if record.budget < 3:
                record.check_workflow_num = 1
            elif record.budget >= 3 and record.budget <50 and (not record.is_method_zb or (record.is_method_zb and record.zb_category == purchase_zb_category_three)):
                record.check_workflow_num = 2
            elif record.budget >= 3 and record.budget <50 and record.is_method_zb and record.zb_category != purchase_zb_category_three:
                record.check_workflow_num = 3
            elif record.budget >= 300 and (not record.is_method_zb or (record.is_method_zb and record.zb_category == purchase_zb_category_three)):
                record.check_workflow_num = 4
            elif record.budget >= 100 and record.budget < 300  and (not record.is_method_zb or (record.is_method_zb and record.zb_category == purchase_zb_category_three)):
                record.check_workflow_num = 5
            elif record.budget >= 50 and record.budget < 100  and (not record.is_method_zb or (record.is_method_zb and record.zb_category == purchase_zb_category_three)):
                record.check_workflow_num = 6
            elif record.budget >= 300 and record.is_method_zb and record.zb_category != purchase_zb_category_three:
                record.check_workflow_num = 7
            elif record.budget >= 100 and record.budget < 300 and record.is_method_zb and record.zb_category != purchase_zb_category_three:
                record.check_workflow_num = 8
            elif record.budget >= 50 and record.budget < 100 and record.is_method_zb and record.zb_category != purchase_zb_category_three:
                record.check_workflow_num = 9
    
    check_workflow_num = fields.Integer(compute='_get_workflow_num',string=u'判断是哪个流程')
    
    def draft(self):
        if self.can_suo_approve:
            self.write({'state':'draft','suo_verifier_id':self.env.uid,'suo_time':fields.Date.today()})
        elif self.can_ke_approve:
            self.write({'state':'draft','ke_verifier_id':self.env.uid,'ke_time':fields.Date.today()})
        elif self.can_cai_approve:
            self.write({'state':'draft','cai_verifier_id':self.env.uid,'cai_time':fields.Date.today()})
        elif self.can_yb_approve:
            self.write({'state':'draft','yb_verifier_id':self.env.uid,'yb_time':fields.Date.today()})
        elif self.can_fzs_approve:
            self.write({'state':'draft','fzs_verifier_id':self.env.uid,'fzs_time':fields.Date.today()})
        elif self.can_yzbgh_approve:
            self.write({'state':'draft','yzbgh_verifier_id':self.env.uid,'yzbgh_time':fields.Date.today()})
        elif self.can_yz_approve:
            self.write({'state':'draft','yz_verifier_id':self.env.uid,'yz_time':fields.Date.today()})
        elif self.can_yzzgcg_approve:
            self.write({'state':'draft','yzzgcg_verifier_id':self.env.uid,'yzzgcg_time':fields.Date.today()})
        else:
            self.write({'state':'draft'})
         
    def submitted(self):
        self.write({'state':'submitted'})
         
    def suo_stop_accepted(self):
        self.write({'state':'suo_stop_accepted','effective':True,'suo_verifier_id':self.env.uid,'suo_time':fields.Date.today()})
         
    def suo_accepted(self):
        self.write({'state':'suo_accepted','suo_verifier_id':self.env.uid,'suo_time':fields.Date.today()})
         
    def ke_accepted(self):
        self.write({'state':'ke_accepted','ke_verifier_id':self.env.uid,'ke_time':fields.Date.today()})
         
    def cai_accepted(self):
        self.write({'state':'cai_accepted','cai_verifier_id':self.env.uid,'cai_time':fields.Date.today()})
         
    def yb_accepted(self):
        self.write({'state':'yb_accepted','yb_verifier_id':self.env.uid,'yb_time':fields.Date.today()})
         
    def fzs_stop_accepted(self):
        self.write({'state':'fzs_stop_accepted','effective':True,'fzs_verifier_id':self.env.uid,'fzs_time':fields.Date.today()})
         
    def fzs_accepted(self):
        self.write({'state':'fzs_accepted','fzs_verifier_id':self.env.uid,'fzs_time':fields.Date.today()})
         
    def yzbgh_stop_accepted(self):
        self.write({'state':'yzbgh_stop_accepted','effective':True,'yzbgh_verifier_id':self.env.uid,'yzbgh_time':fields.Date.today()})
         
    def yzbgh_accepted(self):
        self.write({'state':'yzbgh_accepted','yzbgh_verifier_id':self.env.uid,'yzbgh_time':fields.Date.today()})
         
    def yz_stop_accepted(self):
        self.write({'state':'yz_stop_accepted','effective':True,'yz_verifier_id':self.env.uid,'yz_time':fields.Date.today()})
         
    def yz_accepted(self):
        self.write({'state':'yz_accepted','yz_verifier_id':self.env.uid,'yz_time':fields.Date.today()})
         
    def yzzgcg_stop_accepted(self):
        self.write({'state':'yzzgcg_stop_accepted','effective':True,'yzzgcg_verifier_id':self.env.uid,'yzzgcg_time':fields.Date.today()})
         
    def yzzgcg_accepted(self):
        self.write({'state':'yzzgcg_accepted','yzzgcg_verifier_id':self.env.uid,'yzzgcg_time':fields.Date.today()})
         
    def jt_accepted(self):
        self.write({'state':'jt_accepted','effective':True})

    
#采购物资
class pm_purchase_plan_goods(models.Model):
    _name = 'pm.purchase.plan.goods'
    _description = u'采购物资'
    
    plan_id = fields.Many2one('pm.purchase.plan',string=u'采购计划')
    project_id = fields.Many2one(related='plan_id.project_id',string=u'项目')
    category = fields.Many2one(related='plan_id.category',string=u'采购类别')
    name = fields.Many2one('pm.init.proj.purchase',string=u'物资名称',required=True)
    goods_standard = fields.Char(string=u'规格')
    goods_version = fields.Char(u'型号')
    goods_amount = fields.Integer(u'数量')
    goods_manufacturer = fields.Char(u'生产厂家')
    goods_deliverytime = fields.Date(u'供货时间')
    
    @api.onchange('name')
    def _get_default_goods_standard(self):
        for record in self:
            record.goods_standard = record.name.proj_plan_specifications
#招标标包
class pm_purchase_zb_bd(models.Model):
    _name = 'pm.purchase.zb.bd'
    _description = u'招标标包'
    
    @api.depends('content_fw','zb_bd_detail_record_id')
    def _get_content(self):
        for record in self:
            if record.is_category_fw:
                record.content = record.content_fw
            else:
                content_str = ''
                i = 1
                length = len(record.zb_bd_detail_record_id)
                for zb_bd_detail in record.zb_bd_detail_record_id:
                    content_str = content_str + zb_bd_detail.name.name + u' * ' + str(zb_bd_detail.amount)
                    if i < length:
                        content_str = content_str + u', '
                    i = i + 1
                record.content = content_str
    
    plan_id = fields.Many2one('pm.purchase.plan',string=u'采购计划')
    project_id = fields.Many2one(related='plan_id.project_id',string=u'项目')
    category = fields.Many2one(related='plan_id.category',string=u'采购类别')
    is_category_fw = fields.Boolean(related='plan_id.is_category_fw',string=u'是否为服务类采购')
    name =fields.Char(string=u'标包名称',required=True)
    content_fw = fields.Text(string=u'标包详情')
    content = fields.Text(compute='_get_content',string=u'标包详情')
    zb_bd_detail_record_id = fields.One2many('pm.purchase.zb.bd.detail','zb_bd_id',string=u'标包详情')
    
#招标标包详情
class pm_purchase_zb_bd_detail(models.Model):
    _name = 'pm.purchase.zb.bd.detail'
    _description = u'招标标包详情'
    
    zb_bd_id = fields.Many2one('pm.purchase.zb.bd',string=u'招标标包')
    project_id = fields.Many2one(related='zb_bd_id.project_id',string=u'项目')
    category = fields.Many2one(related='zb_bd_id.category',string=u'采购类别')
    name = fields.Many2one('pm.init.proj.purchase',string=u'采购物资名称',required=True)
    amount = fields.Integer(string=u'数量',required=True)

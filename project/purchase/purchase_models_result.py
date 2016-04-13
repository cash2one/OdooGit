# -*- coding: utf-8 -*-

from openerp import models, fields, api

'''
菜单名：采购结果上报
'''
#采购结果上报信息表
class pm_purchase_result(models.Model):
    _name = 'pm.purchase.result'
    _description = u'采购结果上报'
    _sql_constraints = [
        ('unique_key', 'UNIQUE (plan_id)',  '所选采购计划已存在采购结果，请重新选择!')
    ]
    
    @api.depends('plan_id')
    def _get_result_name(self):
        #采购结果名称,不显示在页面，取值为：采购计划名称+"——采购结果"
        for record in self:
            record.name = record.plan_id.name + u'——采购结果'
        
    @api.onchange('plan_id')
    def change_plan_id(self):
        for record in self:
            record.zb_goods_record_id = False
            if record.plan_id.is_method_zb:
                record.is_method_zb = True
                record.is_method_tp = False
                
                record.tp_time = False
                record.tp_place = False
                record.tp_participants = False
                record.tp_note = False
                record.tp_result_record_id = False
                record.tp_suggest_record_id = False
            elif record.plan_id.is_method_tp:
                record.is_method_tp = True
                record.is_method_zb = False
                
                record.zb_number = False
                record.zb_method = False
                record.cg_category = False
                record.zb_start_time = False
                record.zb_place = False
                record.zb_program_check_number = False
                record.pb_report = False
                record.pb_result = False
                record.sb_result = False
            else:
                record.is_method_zb = False
                record.is_method_tp = False
                
                record.zb_number = False
                record.zb_method = False
                record.cg_category = False
                record.zb_start_time = False
                record.zb_place = False
                record.zb_program_check_number = False
                record.pb_report = False
                record.pb_result = False
                record.sb_result = False
                record.tp_time = False
                record.tp_place = False
                record.tp_participants = False
                record.tp_note = False
                record.tp_result_record_id = False
                record.tp_suggest_record_id = False
                
    @api.onchange('total_price')
    def change_total_price(self):
        for record in self:
            if record.total_price <= 0 or record.total_price > record.budget:
                record.total_price = 0.01
    
    name = fields.Char(compute='_get_result_name',string=u'采购结果名称')
    plan_id = fields.Many2one('pm.purchase.plan',string=u'采购计划',domain=[('effective','=',True),('has_purchase_reuslt','=',False)],required=True)
    project_id = fields.Many2one(related='plan_id.project_id',string=u'所属项目',store=True)
    organ_id = fields.Many2one(related='plan_id.organ_id',string=u'采购单位',store=True,readonly=True)
    agent_id = fields.Many2one(related='plan_id.agent_id',string=u'经办人',store=True,readonly=True)
    provider = fields.Char(u'拟选择供应商',required=True)
    budget = fields.Float(related='plan_id.budget',string=u'预算(万元)',readonly=True)
    total_price = fields.Float(u'拟采购总价(万元)',required=True,default=0.01)
    zb_goods_record_id = fields.One2many('pm.purchase.zb.goods','project_purchase_ht_id',string=u'设备明细')
    
    is_category_fw = fields.Boolean(related='plan_id.is_category_fw',string=u'是否为服务类采购',default=False)
    is_method_zb = fields.Boolean(related='plan_id.is_method_zb',string=u'是否为招标采购',default=False)
    is_method_tp = fields.Boolean(related='plan_id.is_method_tp',string=u'是否为竞争性谈判采购',default=False)
    has_purchase_trace = fields.Boolean(string=u'是否存在采购跟踪',default=False)
    
#招标过程信息开始
    zb_number = fields.Char(string=u'招标编号')
    zb_method = fields.Many2one(related='plan_id.zb_method',string=u'组织形式',readonly=True)
    cg_category = fields.Many2one(related='plan_id.category',string=u'采购类别',readonly=True)
    zb_start_time = fields.Date(string=u'开标时间 ')
    zb_place = fields.Char(string=u'开标地点')
    zb_program_check_number = fields.Char(string=u'招标方案批复/备案文号')
    pb_report = fields.Integer(string=u'评标报告')
    pb_result = fields.One2many('pm.purchase.pb.result','ht_id',string=u'评标结果')
    sb_result = fields.One2many('pm.purchase.sb.result','ht_id',string=u'授标建议')
#招标过程信息结束
    
#竞争性谈判过程信息开始
    tp_time = fields.Date(string=u'谈判时间')
    tp_place = fields.Char(string=u'谈判地点')
    tp_participants = fields.Char(string=u'参与人员')
    tp_note = fields.Integer(string=u'谈判备忘录')
    tp_result_record_id = fields.One2many('pm.purchase.tp.result','ht_id',string=u'评标结果')
    tp_suggest_record_id = fields.One2many('pm.purchase.tp.suggest','ht_id',string=u'授标建议')
#竞争性谈判过程信息结束
    

    
    suo_suggest = fields.Text(u'审批意见')
    suo_verifier_id = fields.Many2one('res.users',string=u'审批人')
    suo_time = fields.Date(u'日期')

    yb_suggest = fields.Text(u'审批意见')
    yb_verifier_id = fields.Many2one('res.users',string=u'审批人')
    yb_time = fields.Date(u'日期')

    yzzgcg_suggest = fields.Text(u'审批意见')
    yzzgcg_verifier_id = fields.Many2one('res.users',string=u'审批人')
    yzzgcg_time = fields.Date(u'日期')
    
    hz_number = fields.Char(u'回执编号')
    zb_file_number = fields.Char(u'招标/文件编号')
    hz_time = fields.Date(u'回执日期')
    hz_attach = fields.Integer(u'备案回执文件')
    
    #流程一：draft——submitted——suo_accepted——yb_accepted——yzzgcg_accepted——jt_accepted
    #流程二：draft——submitted——suo_accepted——yb_accepted——yzzgcg_stop_accepted
    state = fields.Selection([('draft',u'草稿'),('submitted', u'已提交'),('suo_stop_accepted', u'所(中心)已审批'),('suo_accepted', u'所(中心)已审批'),('yb_accepted', u'院办已审批'),('yzzgcg_stop_accepted', u'主管采购院长已审批'),('yzzgcg_accepted', u'主管采购院长已审批'),('jt_accepted', u'集团回执信息已填写')] ,u'审批状态')
    effective = fields.Boolean(string=u'合同计划是否已生效',default=False)
    
    @api.depends('state')
    def _get_can_approve(self):
        for record in self:
            record.can_manager_submit = False
            record.can_suo_approve = False
            record.can_yb_approve = False
            record.can_yzzgcg_approve = False
            record.can_jt_approve = False
            
            record.comp_suo_verifier_id = record.suo_verifier_id.name
            record.comp_suo_time = record.suo_time
            record.comp_yb_verifier_id = record.yb_verifier_id.name
            record.comp_yb_time = record.yb_time
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
                if self.env.uid == 1 :
                    record.can_yzzgcg_approve = True
                    
                if self.is_user_in_group('aqy_project.group_purchase_yzzgcg_approve'):
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
            elif record.state == 'yzzgcg_accepted':
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
    can_yb_approve = fields.Boolean(compute='_get_can_approve',string='院办可审批')
    can_yzzgcg_approve = fields.Boolean(compute='_get_can_approve',string='主管采购院长可审批')
    can_jt_approve = fields.Boolean(compute='_get_can_approve',string='集团回执信息可填写')
    
    comp_suo_verifier_id = fields.Char(compute='_get_can_approve',string=u'审批人',readonly=True)
    comp_suo_time = fields.Date(compute='_get_can_approve',string=u'日期',readonly=True)
    comp_yb_verifier_id = fields.Char(compute='_get_can_approve',string=u'审批人',readonly=True)
    comp_yb_time = fields.Date(compute='_get_can_approve',string=u'日期',readonly=True)
    comp_yzzgcg_verifier_id = fields.Char(compute='_get_can_approve',string=u'审批人',readonly=True)
    comp_yzzgcg_time = fields.Date(compute='_get_can_approve',string=u'日期',readonly=True)
    
    def _get_workflow_num(self):
        for record in self:
            if record.plan_id.check_workflow_num in (3,7,8,9):
                record.check_workflow_num = 1
            elif record.plan_id.check_workflow_num in (1,2,4,5,6):
                record.check_workflow_num = 2
    
    check_workflow_num = fields.Integer(compute='_get_workflow_num',string=u'判断是哪个流程')
    
    def draft(self):
        if self.can_suo_approve:
            self.write({'state':'draft','suo_verifier_id':self.env.uid,'suo_time':fields.Date.today()})
        elif self.can_yb_approve:
            self.write({'state':'draft','yb_verifier_id':self.env.uid,'yb_time':fields.Date.today()})
        elif self.can_yzzgcg_approve:
            self.write({'state':'draft','yzzgcg_verifier_id':self.env.uid,'yzzgcg_time':fields.Date.today()})
        else:
            self.write({'state':'draft'})
    
    def submitted(self):
        self.write({'state':'submitted'})
    
    def suo_accepted(self):
        self.write({'state':'suo_accepted','suo_verifier_id':self.env.uid,'suo_time':fields.Date.today()})
    
    def yb_accepted(self):
        self.write({'state':'yb_accepted','yb_verifier_id':self.env.uid,'yb_time':fields.Date.today()})
    
    def yzzgcg_stop_accepted(self):
        self.write({'state':'yzzgcg_stop_accepted','effective':True,'yzzgcg_verifier_id':self.env.uid,'yzzgcg_time':fields.Date.today()})
    
    def yzzgcg_accepted(self):
        self.write({'state':'yzzgcg_accepted','yzzgcg_verifier_id':self.env.uid,'yzzgcg_time':fields.Date.today()})
    
    def jt_accepted(self):
        self.write({'state':'jt_accepted','effective':True})
        
    @api.model
    @api.returns('self', lambda value:value.id)
    def create(self, vals):
        if vals.has_key('plan_id'):
            self.env['pm.purchase.plan'].search([('id','=',vals['plan_id'])]).write({'has_purchase_reuslt':True})
        return models.Model.create(self, vals)

    def unlink(self, cr, uid, ids, context=None):
        for id in ids:
            ref_plan = self.pool.get('pm.purchase.result').browse(cr,uid,id,context).plan_id
            ref_plan.write({'has_purchase_reuslt':False})
        return models.Model.unlink(self, cr, uid, ids, context=context)
    
#招标设备明细
class pm_purchase_zb_goods(models.Model):
    _name = 'pm.purchase.zb.goods'
    _description = u'招标设备明细'
    
    project_purchase_ht_id = fields.Many2one('pm.purchase.result',string=u'合同')
    plan_id = fields.Many2one(related='project_purchase_ht_id.plan_id',string=u'采购计划')
    name = fields.Many2one('pm.purchase.plan.goods',string=u'设备名称',required=True)
    goods_version = fields.Char(string=u'型号',required=True)
    goods_amount = fields.Integer(string=u'数量',required=True)
    goods_unit_price = fields.Float(string=u'单价(万元)',required=True)
    goods_total_price = fields.Float(string=u'总价(万元)',required=True)
    
#评标结果
class pm_purchase_pb_result(models.Model):
    _name = 'pm.purchase.pb.result'
    _description = u'评标结果'
    
    ht_id = fields.Many2one('pm.purchase.result',string=u'采购结果')
    plan_id = fields.Many2one(related='ht_id.plan_id',string=u'采购计划')
    pb_bd = fields.Many2one('pm.purchase.zb.bd',string=u'标包名称',required=True)
    tender = fields.Char(string=u'投标人',required=True)
    tender_price = fields.Float(string=u'投标报价(万元)',required=True)
    technology = fields.Char(string=u'技术',required=True)
    business = fields.Char(string=u'商务',required=True)
    total_points = fields.Char(string=u'总分',required=True)
    
#授标建议
class pm_purchase_sb_result(models.Model):
    _name = 'pm.purchase.sb.result'
    _description = u'授标建议'
    
    ht_id = fields.Many2one('pm.purchase.result',string=u'采购结果')
    plan_id = fields.Many2one(related='ht_id.plan_id',string=u'采购计划')
    sb_bd = fields.Many2one('pm.purchase.zb.bd',string=u'标包名称',required=True)
    winner = fields.Char(string=u'推荐中标人',required=True)
    zb_amount = fields.Integer(string=u'中标数量',required=True)
    zb_price = fields.Float(string=u'中标金额(万元)',required=True)
    remark = fields.Char(string=u'备注',required=True)

#谈判结果
class pm_purchase_tp_result(models.Model):
    _name = 'pm.purchase.tp.result'
    _description = u'谈判结果'
    
    ht_id = fields.Many2one('pm.purchase.result',string=u'采购结果')
    plan_id = fields.Many2one(related='ht_id.plan_id',string=u'采购计划')
    goods = fields.Many2one('pm.purchase.plan.goods',string=u'设备名称',required=True)
    tp_manufacturer = fields.Char(string=u'厂商',required=True)
    tp_price = fields.Float(string=u'报价(万元)',required=True)
    tp_clause = fields.Char(string=u'关键条款',required=True)

#供应商建议
class pm_purchase_tp_suggest(models.Model):
    _name = 'pm.purchase.tp.suggest'
    _description = u'供应商建议'
    
    ht_id = fields.Many2one('pm.purchase.result',string=u'采购结果')
    plan_id = fields.Many2one(related='ht_id.plan_id',string=u'采购计划')
    goods = fields.Many2one('pm.purchase.plan.goods',string=u'设备名称',required=True)
    tp_winner = fields.Char(string=u'推荐厂商',required=True)
    amount = fields.Integer(string=u'数量',required=True)
    tp_zb_price = fields.Float(string=u'金额(万元)',required=True)
    tp_remark = fields.Char(string=u'备注',required=True)


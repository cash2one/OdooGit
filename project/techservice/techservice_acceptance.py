# -*- coding: utf-8 -*-

from openerp import models, fields, api
from string import join

class pm_techservice_acceptance(models.Model):
    _name = 'pm.techservice.acceptance'
    _description = u"外协验收管理"
    _sql_constraints = [
        ('unique_key', 'UNIQUE (proj_id)',  '外协项目已存在!')
    ]
    
    #判断当前用户是否发起人
    @api.depends()
    def _get_is_create_uid(self):
        if self.create_uid.id == self.env.uid:
            self.is_create_uid = True
        else:
            self.is_create_uid = False
            
    #获取所(中心)审批意见
    @api.depends('unit_accept_result')
    def _get_unit_accept_result(self):
        self.comp_unit_accept_result = self.unit_accept_result.name
    
    #根据状态和当前用户是否在审批组中，判断当前用户是否可以审批
    @api.depends('state')
    def _get_can_apporve(self):
        self.rd_can_approve = False
        if self.state =='unit_approved':
            g_res = self.env.ref('aqy_project.group_techservice_rd_approve')
            if g_res:
                self.env.cr.execute('select count(1) from res_groups_users_rel where uid={0} and gid={1}'.format(self.env.context['uid'],g_res.id))
                res = self.env.cr.fetchone()
                if res and res[0]>0: 
                    self.rd_can_approve = True
    
    @api.depends('proj_id')
    def _get_name(self):
        for record in self:
            record.name = record.proj_id.name.ht_id.plan_id.wx_plan_check_result.name + '-' + u'验收'  
        
    name = fields.Char(compute='_get_name', string='外协任务验收')
    
    proj_id = fields.Many2one('pm.techservice.init', string='外协任务名称', required=True)
    parent_proj = fields.Many2one(related='proj_id.name.ht_id.plan_id.wx_plan_check_result.parent_proj', string='外协任务所属项目', readonly=True, store=True)
    proj_num = fields.Char(related='proj_id.proj_num', string='外协任务编号', readonly=True, store=True)
    client = fields.Many2one(related='proj_id.client', string="委托单位", store=True, readonly=True) 
    bear_vld = fields.Char(related='proj_id.bear_vld', string='承担单位', store=True, readonly=True) 
    start_time = fields.Date(related='proj_id.start_time', string='项目开始时间', store=True, readonly=True)
    end_time = fields.Date(related='proj_id.end_time', string='项目结束时间', store=True, readonly=True)
    contract_account = fields.Float(related='proj_id.contract_account', string='合同总额', store=True, readonly=True)
    unit_accept_time = fields.Date('验收时间', required=True)
    unit_accept_address = fields.Char('验收地点', size=50, required=True)
    unit_accept_specialist = fields.Char('验收专家列表', size=200, required=True)
    unit_accept_suggest = fields.Text('验收意见', required=True)
    unit_accept_result = fields.Many2one('sys.constant', string='验收结论', domain=[('type','=','TECHSERVICE_CHECK_RESULT')], required=True)
    comp_unit_accept_result = fields.Char(compute='_get_unit_accept_result', string='所(中心)验收结论')
    unit_attachment_ids = fields.One2many('pm.techservice.unit.acceptance.attachment', 'acceptance_id', string='所(中心)验收附件')
    rd_accept_time = fields.Date('验收时间')
    rd_accept_address = fields.Char('验收地点', size=50)
    rd_accept_specialist = fields.Char('验收专家列表', size=200)
    rd_accept_suggest = fields.Text('验收意见')
    rd_accept_result = fields.Many2one('sys.constant', string='验收结论', domain=[('type','=','TECHSERVICE_CHECK_RESULT')])
    rd_attachment_ids = fields.One2many('pm.techservice.rd.acceptance.attachment', 'acceptance_id', string='科研处验收附件')
    rd_can_approve = fields.Boolean(compute='_get_can_apporve', string='科研处是否可以审批')
    is_create_uid = fields.Boolean(compute='_get_is_create_uid', string='是否发起人')
    state = fields.Selection([('rd_returned','科研处已退回'),('unit_approved','所(中心)已通过'),('rd_approved','科研处已通过')])
    
    #所(中心)审批事件
    def unit_approve(self):
        if self.contract_account>20 and self.unit_accept_result.name!=u'不通过':
            self.write({'state':'unit_approved'})
        else:
            #只有所(中心)审批，审批完毕向采购跟踪写验收信息
            trace_rec = self.env['pm.purchase.trace'].search([('id','=',self.proj_id.name.id)])
            trace_rec.write({'ht_ys':self.id})
        
    #科研处审批事件
    def rd_approve(self):
        self.write({'state':'rd_approved'})
        #向采购跟踪写验收信息
        trace_rec = self.env['pm.purchase.trace'].search([('id','=',self.proj_id.name.id)])
        trace_rec.write({'ht_ys':self.id})
    
    #科研处退回事件
    def rd_return(self):
        self.write({'state':'rd_returned'})
     
class pm_techservice_unit_acceptance_attachment(models.Model):
    _name = 'pm.techservice.unit.acceptance.attachment'
    _description = u"所(中心)验收附件"
     
    seq = fields.Integer('序号') 
    name = fields.Char(string='附件名称', size=50)
    attachment = fields.Integer('附件', required=True)
    content = fields.Text('文档说明')
    acceptance_id = fields.Many2one('pm.techservice.acceptance', string='外协项目验收')

class pm_techservice_rd_acceptance_attachment(models.Model):
    _name = 'pm.techservice.rd.acceptance.attachment'
    _description = u"科研处验收附件"
    
    seq = fields.Integer('序号')  
    name = fields.Char(string='附件名称', size=50)
    attachment = fields.Integer('附件', required=True)
    content = fields.Text('文档说明')
    acceptance_id = fields.Many2one('pm.techservice.acceptance', string='外协项目验收')
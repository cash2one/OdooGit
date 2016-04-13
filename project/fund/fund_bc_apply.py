# -*- coding: utf-8 -*-

from openerp import models, fields, api
from openerp.osv import osv

class pm_fund_bc_apply(models.Model):
    _name = 'pm.fund.bc.apply'
    _description = u"预算变更申请表"
    
    #根据状态和当前用户是否在审批组中，判断当前用户是否可以审批
    @api.depends('state')
    def _get_can_apporve(self):
        self.comp_unit_sug_person = self.unit_sug_person.partner_id.name
        self.comp_unit_sug_date = self.unit_sug_date
        self.comp_rd_sug_person = self.rd_sug_person.partner_id.name
        self.comp_rd_sug_date = self.rd_sug_date
        self.unit_can_approve = self.rd_can_approve = False
        #获取当前用户是否与项目中分管领导为同一人，如果是，则可以审批，返回true，否则返回false
        if (self.state =='submitted' and self.proj_id.proj_reply_leaders.related_user.id == self.env.context['uid']) or (self.state =='submitted' and self.env.uid==1):
            self.unit_can_approve = True
            #如果审批人存在(已审批过)则显示数据库中审批人，否则显示当前用户,审批时间相同逻辑
            if not self.unit_sug_person:    
                self.comp_unit_sug_person = self.env['res.users'].search([('id','=',self.env.context['uid'])]).partner_id.name
            if not self.unit_sug_date:     
                self.comp_unit_sug_date = fields.Date.today()
        if self.state =='unit_approved':
            g_res = self.env.ref('aqy_project.group_fund_rd_approve')
            if g_res:
                self.env.cr.execute('select count(1) from res_groups_users_rel where uid={0} and gid={1}'.format(self.env.context['uid'],g_res.id))
                res = self.env.cr.fetchone()
                if res and res[0]>0: 
                    self.rd_can_approve = True
                    if not self.rd_sug_person:    
                        self.comp_rd_sug_person = self.env['res.users'].search([('id','=',self.env.context['uid'])]).partner_id.name
                    if not self.rd_sug_date:     
                        self.comp_rd_sug_date = fields.Date.today()
    
    #判断当前用户是否发起人
    @api.depends()
    def _get_is_create_uid(self):
        if self.create_uid.id == self.env.context['uid']:
            self.is_create_uid = True
        else:
            self.is_create_uid = False
    
    def get_project_id_domain(self):
        if self.env.uid == 1:
            return "[('proj_periods.name','=',u'实施中')]"
        return "[('proj_periods.name','=',u'实施中'),('proj_pm_uid','=',uid)]"     
    
    name = fields.Char('名称', size=100)
    proj_id = fields.Many2one('pm.init.proj.apply', string='项目名称', required=True, domain=get_project_id_domain)
    proj_num = fields.Char(related='proj_id.proj_reply_info_id.proj_num', string="项目编号", store=True)
    fmis_num = fields.Char(related='proj_id.proj_reply_info_id.proj_reply_fmis', string="FMIS编号", store=True)
    proj_vld = fields.Many2one('oa.admin.org',related='proj_id.proj_vld', string="项目承担单位", store=True)
    budget_year = fields.Many2one('sys.constant',string='预算年度', required=True, domain=[('type','=','year')])
    content = fields.Text('预算变更内容说明')
    reason = fields.Text('预算变更原因说明')
    apply_person = fields.Char('变更申请人', size=30)
    apply_date = fields.Date('变更申请日期')
    state = fields.Selection([('unit_returned','草稿'),('rd_returned','草稿'),('submitted','已提交'),('unit_approved','所(中心)已审批'),('rd_approved','科研处已审批')], string='审批状态', default='submitted')
    remarks = fields.Text('备注')
    unit_suggest = fields.Text('所(中心)审批意见')
    unit_sug_person = fields.Many2one('res.users', string='审批人')
    unit_sug_date = fields.Date('审批时间')
    comp_unit_sug_person = fields.Char(compute='_get_can_apporve',string='审批人', readonly=True)
    comp_unit_sug_date = fields.Date(compute='_get_can_apporve',string='审批时间', readonly=True)
    rd_suggest = fields.Text('科研处审批意见')
    rd_sug_person =  fields.Many2one('res.users', string='审批人')
    rd_sug_date = fields.Date('审批时间')
    comp_rd_sug_person = fields.Char(compute='_get_can_apporve',string='审批人', readonly=True)
    comp_rd_sug_date = fields.Date(compute='_get_can_apporve',string='审批时间', readonly=True)
    unit_can_approve = fields.Boolean(compute='_get_can_apporve',string='所(中心)领导是否可以审批')
    rd_can_approve = fields.Boolean(compute='_get_can_apporve', string='科研处是否可以审批')
    is_create_uid = fields.Boolean(compute='_get_is_create_uid', string='是否发起人')
    
    #删除时若存在变更基线的引用则提示
    def unlink(self, cr, uid, ids, context=None):
        version_obj = self.pool.get('pm.fund.budget.version')
        version_ids = version_obj.search(cr, uid, [('version_basis', 'in', ids)], context=context)
        if version_ids:
            raise osv.except_osv('提示',"变更基线中存在对该申请的引用，不能删除!")
        else:  
            return models.Model.unlink(self, cr, uid, ids, context=context)
    
    #创建同时提交工作流表单
    @api.model
    @api.returns('self', lambda value:value.id)
    def create(self, vals):
        if self.state:
            vals['state'] = 'submitted'
        return models.Model.create(self, vals)
    
    #提交事件
    def submit(self):
        self.write({'state':'submitted'})
    
    #所(中心)审批事件
    def unit_approve(self):
        self.write({'state':'unit_approved','unit_sug_person':self.env.uid,'unit_sug_date':fields.Date.today()})
    
    #财务处审批事件
    def rd_approve(self):
        self.write({'state':'rd_approved','rd_sug_person':self.env.uid,'rd_sug_date':fields.Date.today()})
    
    #财务处退回事件
    def unit_return(self):
        self.write({'state':'unit_returned','unit_sug_person':self.env.uid,'unit_sug_date':fields.Date.today()})
    
    #财务处退回事件
    def rd_return(self):
        self.write({'state':'rd_returned','rd_sug_person':self.env.uid,'rd_sug_date':fields.Date.today()})

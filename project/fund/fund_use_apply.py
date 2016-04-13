# -*- coding: utf-8 -*-

from openerp import models, fields, api
from openerp.osv import osv

class pm_fund_apply_info(models.Model):
    _name = 'pm.fund.use.apply'
    _description = u"经费使用申请基本信息表"
    
    #获取默认的申请人
    def _get_default_person(self):
        user_name = self.env['res.users'].search([('id','=',self.env.context['uid'])]).partner_id.name
        return user_name
    
    #获取默认的申请日期
    def _get_default_date(self):
        return fields.Date.today()
    
    #获取默认的申请人单位
    def _get_default_site(self):
        site_name = self.env['oa.staff.basic'].search([('related_user','=',self.env.context['uid'])]).vld_site.name
        return site_name
    
    #根据状态和当前用户是否在审批组中，判断当前用户是否可以审批
    @api.depends('state')
    def _get_can_apporve(self):
        self.comp_pm_sug_person = self.pm_sug_person.partner_id.name
        self.comp_pm_sug_date = self.pm_sug_date
        self.comp_unit_sug_person = self.unit_sug_person.partner_id.name
        self.comp_unit_sug_date = self.unit_sug_date
        self.pm_can_approve = self.unit_can_approve = False 
        if self.state =='submitted':
            g_res = self.env.ref('aqy_project.group_proj_manager')
            if g_res:
                self.env.cr.execute('select count(1) from res_groups_users_rel where uid={0} and gid={1}'.format(self.env.context['uid'],g_res.id))
                res = self.env.cr.fetchone()
                if res and res[0]>0: 
                    self.pm_can_approve = True
                    #如果审批人存在(已审批过)则显示数据库中审批人，否则显示当前用户,审批时间相同逻辑
                    if not self.pm_sug_person:    
                        self.comp_pm_sug_person = self.env['res.users'].search([('id','=',self.env.context['uid'])]).partner_id.name
                    if not self.pm_sug_date:     
                        self.comp_pm_sug_date = fields.Date.today()
        #获取当前用户是否与项目中分管领导为同一人，如果是，则可以审批，返回true，否则返回false
        if (self.state =='pm_approved' and self.proj_id.proj_reply_leaders.related_user.id == self.env.context['uid']) or (self.state =='pm_approved' and self.env.uid==1):
            self.unit_can_approve = True
            #如果审批人存在(已审批过)则显示数据库中审批人，否则显示当前用户,审批时间相同逻辑
            if not self.unit_sug_person:    
                self.comp_unit_sug_person = self.env['res.users'].search([('id','=',self.env.context['uid'])]).partner_id.name
            if not self.unit_sug_date:     
                self.comp_unit_sug_date = fields.Date.today()
    
    #判断当前用户是否发起人
    @api.depends()
    def _get_is_create_uid(self):
        if self.create_uid.id == self.env.context['uid']:
            self.is_create_uid = True
        else:
            self.is_create_uid = False
        
    name = fields.Char('名称', size=100, default='经费使用申请')
    proj_id = fields.Many2one('pm.init.proj.apply', string='列支项目', required=True, domain=[('proj_periods.name','=','实施中')])
    subject = fields.Many2one('pm.common.subject', string="申请科目", required=True, domain=[('is_leaf','=',True),('parent_id','!=',False)])
    subject_name = fields.Char(compute='_get_subject_name')
    budget_total = fields.Float(string="申请科目总预算", digits=(16,2), readonly=True)
    budget_left = fields.Float(string="申请科目剩余预算", digits=(16,2), readonly=True)
    apply_person = fields.Char('申请人', size=30, default=_get_default_person)
    apply_date = fields.Date('申请日期', default=_get_default_date)
    apply_site = fields.Char('申请人单位',size=50, default=_get_default_site)
    apply_reason = fields.Text('申请事由', required=True)
    remarks = fields.Text('备注')
    apply_account = fields.Float('申请金额', required=True)
    actual_account = fields.Float('实际使用')
    state = fields.Selection([('pm_returned','草稿'),('unit_returned','草稿'),('submitted','已提交'),('pm_approved','项目经理已审批'),('unit_approved','所(中心)已审批'),('validated','已确认')], string='审批状态', default='submitted')
    pm_suggest = fields.Text('项目经理审批意见')
    pm_sug_person = fields.Many2one('res.users',string='审批人')
    pm_sug_date = fields.Date('审批时间')
    comp_pm_sug_person = fields.Char(compute='_get_can_apporve',string='审批人', readonly=True)
    comp_pm_sug_date = fields.Date(compute='_get_can_apporve',string='审批时间', readonly=True)
    unit_suggest = fields.Text('所(中心)审批意见')
    unit_sug_person = fields.Many2one('res.users',string='审批人')
    unit_sug_date = fields.Date('审批时间')
    comp_unit_sug_person = fields.Char(compute='_get_can_apporve',string='审批人', readonly=True)
    comp_unit_sug_date = fields.Date(compute='_get_can_apporve',string='审批时间', readonly=True)
    aptrip_ids = fields.One2many('pm.fund.aptrip.info', 'apply_id', string="差旅费申请信息")
    goods_ids = fields.One2many('pm.fund.goods.info', 'apply_id', string="物品购置申请信息")
    unit_can_approve = fields.Boolean(compute='_get_can_apporve',string='所(中心)领导是否可以审批')
    pm_can_approve = fields.Boolean(compute='_get_can_apporve',string='项目经理是否可以审批')
    is_create_uid = fields.Boolean(compute='_get_is_create_uid', string='是否发起人')
    
    @api.onchange('proj_id','subject')
    def _onchange_subject(self):
        if self.proj_id:
            #获取当前有效状态的经费预算版本
            c_id = self.env['sys.constant'].search([('type','=','USE_STATE'),('name','=','当前有效')]).id
            version_id = self.env['pm.fund.budget.version'].search([('proj_id','=',self.proj_id.id),('use_state','=',c_id)]).id
            if version_id:
                #获取科目预算合计
                budget_detail_res = self.env['pm.fund.budget.version.detail'].search([('version_id','=',version_id),('subject_id','=',self.subject.id)])
                budget_total = 0
                budget_total = sum(budget_rec.value for budget_rec in budget_detail_res)
                #计算所选项目、确认过的、实际花费和
                used_res = self.search([('proj_id','=',self.proj_id.id),('state','=','validated')])
                budget_cost = 0
                budget_cost = sum(used_rec.actual_account for used_rec in used_res)
                self.budget_total = budget_total
                self.budget_left = (budget_total*10000-budget_cost)/10000

     
    @api.depends('subject')
    def _get_subject_name(self):
        self.subject_name = self.subject.name
    
    #创建同时提交工作流表单
    @api.model
    @api.returns('self', lambda value:value.id)
    def create(self, vals):
        #获取当前有效状态的经费预算版本
        c_id = self.env['sys.constant'].search([('type','=','USE_STATE'),('name','=','当前有效')]).id
        version_id = self.env['pm.fund.budget.version'].search([('proj_id','=',vals['proj_id']),('use_state','=',c_id)]).id
        if version_id:
            #获取科目预算合计
            budget_detail_res = self.env['pm.fund.budget.version.detail'].search([('version_id','=',version_id),('subject_id','=',vals['subject'])])
            budget_total = 0
            budget_total = sum(budget_rec.value for budget_rec in budget_detail_res)
            #计算所选项目、所选科目、申请通过、当年的实际花费和
            used_res = self.search([('proj_id','=',vals['proj_id']),('state','=','validated')])
            budget_cost = 0
            budget_cost = sum(used_rec.actual_account for used_rec in used_res)
            budget_left = budget_total*10000-budget_cost
            if vals['apply_account']>budget_left:
                raise osv.except_osv('警告',"申请金额已超过剩余金额!")
            else:
                vals['budget_total'] = budget_total
                vals['budget_left'] = budget_left/10000   
                return models.Model.create(self, vals)
        else:
            raise osv.except_osv('警告',"申请金额已超过剩余金额!")
    
    @api.multi
    def write(self, vals):
        #获取当前有效状态的经费预算版本
        c_id = self.env['sys.constant'].search([('type','=','USE_STATE'),('name','=','当前有效')]).id
        proj_id = self.proj_id.id
        if vals.has_key('proj_id'):
            proj_id = vals['proj_id']
        version_id = self.env['pm.fund.budget.version'].search([('proj_id','=',proj_id),('use_state','=',c_id)]).id
        if version_id:
            #获取科目预算合计
            subject_id = self.subject.id
            if vals.has_key('subject'):
                subject_id = vals['subject']
            budget_detail_res = self.env['pm.fund.budget.version.detail'].search([('version_id','=',version_id),('subject_id','=',subject_id)])
            budget_total = 0
            budget_total = sum(budget_rec.value for budget_rec in budget_detail_res)
            #计算所选项目、所选科目、申请通过、当年的实际花费和
            used_res = self.search([('proj_id','=',proj_id),('state','=','validated')])
            budget_cost = 0
            budget_cost = sum(used_rec.actual_account for used_rec in used_res)
            budget_left = budget_total*10000-budget_cost
            apply_account = self.apply_account
            if vals.has_key('apply_account'):
                apply_account = vals['apply_account']
            if apply_account>budget_left:
                raise osv.except_osv('警告',"申请金额已超过剩余金额!")
            else:
                vals['budget_total'] = budget_total
                vals['budget_left'] = budget_left
                return models.Model.write(self, vals)
        else:
            raise osv.except_osv('警告',"申请金额已超过剩余金额!")    
        
    #提交事件
    def submit(self):
        self.write({'state':'submitted'})
    
    #财务处审批事件
    def pm_approve(self):
        self.write({'state':'pm_approved','pm_sug_person':self.env.uid,'pm_sug_date':fields.Date.today()})
    
    #所(中心)审批事件
    def unit_approve(self):
        self.write({'state':'unit_approved','unit_sug_person':self.env.uid,'unit_sug_date':fields.Date.today()})
    
    #申请人确认事件
    def validate(self):
        self.write({'state':'validated'})
        
    #财务处退回事件
    def pm_return(self):
        self.write({'state':'pm_returned','pm_sug_person':self.env.uid,'pm_sug_date':fields.Date.today()})
    
    #财务处退回事件
    def unit_return(self):
        self.write({'state':'unit_returned','unit_sug_person':self.env.uid,'unit_sug_date':fields.Date.today()})

class pm_fund_aptrip_info(models.Model):
    _name = 'pm.fund.aptrip.info'
    _description = u"差旅费申请信息表"
    
    name = fields.Char('名称', size=100, default='差旅费申请信息')
    person_name = fields.Many2one('oa.staff.basic', string='出差人', required=True)
    person_site = fields.Many2one(related='person_name.vld_site', string='出差人单位', readonly=True)
    trip_address = fields.Char('出差地点', size=100, required=True)
    trip_stime = fields.Date('出差开始时间', required=True)
    trip_etime = fields.Date('出差结束时间', required=True) 
    apply_id = fields.Many2one('pm.fund.use.apply', string="经费使用申请基本信息")

class pm_fund_goods_info(models.Model):
    _name = 'pm.fund.goods.info'
    _description = u'物品购置费申请信息表'
    
    @api.depends('num','unit_price')
    def _get_total_price(self):
        for record in self:
            if record.num and record.unit_price:
                record.price_total = record.num*record.unit_price
    
    name = fields.Char('物品名称', size=100, required=True)
    num = fields.Integer('物品数量', required=True)
    unit_price = fields.Float('物品单价', digits=(16,2), required=True)
    price_total = fields.Float(compute='_get_total_price', string='小计', digits=(16,2))
    apply_id = fields.Many2one('pm.fund.use.apply', string="经费使用申请基本信息")
    
class pm_fund_aptrain_info(models.Model):
    _description=u'培训费申请信息'
    _inherit='pm.fund.use.apply'
    
    train_org_type = fields.Selection([('inner','集团内部培训'),('outer','集团外部培训')],string='培训类型')
    train_address = fields.Char('培训地点', size=200)
    train_content = fields.Text('培训内容')
    train_stime = fields.Date('培训开始时间')
    train_etime = fields.Date('培训结束时间')

class pm_fund_apconference_info(models.Model):
    _description=u'培训费申请信息'
    _inherit='pm.fund.use.apply'
    
    conf_name = fields.Char('会议名称', size=100)
    conf_type = fields.Selection([('gldbhy','各类代表会议'),('ndgzhy','年度工作会议'),('xxythy','学习研讨会议'),('pshy','评审会议'),('zyhy','专业会议'),('xxywhy','小型业务会议')],string='会议类型')
    conf_address = fields.Char('会议地点', size=200)
    conf_content = fields.Text('会议内容')
    conf_stime = fields.Date('会议开始时间')
    conf_etime = fields.Date('会议结束时间')
    conf_person_num = fields.Integer('会议代表人数')
    conf_person_list = fields.Char('会议人员列表')

class pm_fund_apbusiness_info(models.Model):
    _description=u'业务招待费申请信息'
    _inherit='pm.fund.use.apply'
    
    business_address = fields.Char('业务招待地点')
    business_person_num = fields.Integer('招待人数')
    business_person_list = fields.Char('招待人员列表')
    
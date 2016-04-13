# -*- coding: utf-8 -*-

from openerp import models, fields, api

class pm_fund_proj_monthplan(models.Model):
    _name = 'pm.fund.proj.monthplan'
    _description = u"项目月度计划"
    _sql_constraints = [
        ('unique_key', 'UNIQUE (proj_id,year,month)',  '请勿重复填报 !')
    ]
    
    #获取默认的填报用户
    def _get_default_report_person(self):
        user_name = self.env['res.users'].search([('id','=',self.env.context['uid'])]).partner_id.name
        return user_name
    
    #获取默认的填报日期
    def _get_default_regtime(self):
        return fields.Date.today()
        
    #获取年和月的组合
    @api.depends('year','month')
    def _get_ny(self):
        for record in self:
            if record.year and record.month:
                record.ny = record.year.name + '-' + record.month.name
    
    #获取计划金额
    @api.depends()
    def _get_plan_total(self):
        for record in self:
            detail_obj = self.env['pm.fund.proj.monthplan.detail']
            plan_value = detail_obj.search([('monthplan_id', '=', record.id),('subject_name', '=', '合计')]).plan_value
            record.plan_total = plan_value if plan_value else 0
    
    #获取实用总额
    @api.depends()
    def _get_actual_total(self):
        for record in self:
            detail_obj = self.env['pm.fund.proj.monthplan.detail']
            actual_value = detail_obj.search([('monthplan_id', '=', record.id),('subject_name', '=', '合计')]).actual_value
            record.actual_total = actual_value if actual_value else 0
    
    #根据状态和当前用户是否在审批组中，判断当前用户是否可以审批
    @api.depends('state')
    def _get_can_apporve(self):
        self.comp_unit_sug_person = self.unit_sug_person.partner_id.name
        self.comp_unit_sug_date = self.unit_sug_date
        self.comp_rd_sug_person = self.rd_sug_person.partner_id.name
        self.comp_rd_sug_date = self.rd_sug_date
        self.comp_fd_sug_person = self.fd_sug_person.partner_id.name
        self.comp_fd_sug_date = self.fd_sug_date
        self.unit_can_approve = self.rd_can_approve = self.fd_can_approve = False
        group_obj = self.env['res.groups']
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
        if self.state =='rd_approved':
            g_res = self.env.ref('aqy_project.group_fund_fd_approve')
            if g_res:
                self.env.cr.execute('select count(1) from res_groups_users_rel where uid={0} and gid={1}'.format(self.env.context['uid'],g_res.id))
                res = self.env.cr.fetchone()
                if res and res[0]>0: 
                    self.fd_can_approve = True
                    if not self.fd_sug_person:    
                        self.comp_fd_sug_person = self.env['res.users'].search([('id','=',self.env.context['uid'])]).partner_id.name
                    if not self.fd_sug_date:     
                        self.comp_fd_sug_date = fields.Date.today()
    
    #判断当前用户是否发起人
    @api.depends()
    def _get_is_create_uid(self):
        if self.create_uid.id == self.env.uid or self.env.uid==1:
            self.is_create_uid = True
        else:
            self.is_create_uid = False
    
    def get_project_id_domain(self):
        if self.env.uid == 1:
            return "[('proj_periods.name','=',u'实施中')]"
        return "[('proj_periods.name','=',u'实施中'),('proj_pm_uid','=',uid)]"
       
    name = fields.Char('名称', size=100, default='项目经费月度计划')
    proj_id = fields.Many2one('pm.init.proj.apply', string='项目名称', required=True, domain=get_project_id_domain)
    proj_num = fields.Char(related='proj_id.proj_reply_info_id.proj_num', string="项目编号", store=True)
    fmis_num = fields.Char(related='proj_id.proj_reply_info_id.proj_reply_fmis', string="FMIS编号", store=True)
    budget_total = fields.Float(related='proj_id.proj_total_funds', string="合同总额", store=True)
    proj_vld = fields.Many2one('oa.admin.org',related='proj_id.proj_vld', string="项目承担单位", store=True)
    proj_manager = fields.Char('项目经理')
    proj_pm_uid = fields.Integer(related='proj_id.proj_pm_uid', string='项目经理')
    proj_start_date = fields.Date(related='proj_id.proj_start_date', string="项目开始时间", store=True)
    proj_end_date = fields.Date(related='proj_id.proj_end_date', string="项目结束时间", store=True)
    year = fields.Many2one('sys.constant',string='年度', required=True, domain=[('type','=','year')])
    month = fields.Many2one('sys.constant',string='月度',required=True, domain=[('type','=','month')])
    ny = fields.Char(compute='_get_ny', string='年月', stroe=True)
    report_person = fields.Char('填报人', size=30, default=_get_default_report_person)
    report_date = fields.Date('填报日期', default=_get_default_regtime)
    state = fields.Selection([('unit_returned','草稿'),('rd_returned','草稿'),('fd_returned','草稿'),('submitted','已提交'),('unit_approved','所(中心)已审批'),('rd_approved','科研处已审批'),('fd_approved','财务处已审批')], string='状态')
    remarks = fields.Text('备注')
    plan_total = fields.Float(compute='_get_plan_total', string='月计划总额', digits=(16,2))
    actual_total = fields.Float(compute='_get_actual_total', string='月实用总额', digits=(16,2))
    unit_suggest = fields.Text('所(中心)审批意见')
    unit_sug_person = fields.Many2one('res.users', string='审批人')
    unit_sug_date = fields.Date('审批时间')
    comp_unit_sug_person = fields.Char(compute='_get_can_apporve', string='审批人', readonly=True)
    comp_unit_sug_date = fields.Date(compute='_get_can_apporve', string='审批时间', readonly=True)
    rd_suggest = fields.Text('科研处审批意见')
    rd_sug_person = fields.Many2one('res.users',string='审批人')
    rd_sug_date = fields.Date('审批时间')
    comp_rd_sug_person = fields.Char(compute='_get_can_apporve', string='审批人', readonly=True)
    comp_rd_sug_date = fields.Date(compute='_get_can_apporve', string='审批时间', readonly=True)
    fd_suggest = fields.Text('财务处审批意见')
    fd_sug_person = fields.Many2one('res.users',string='审批人')
    fd_sug_date = fields.Date('审批时间')
    comp_fd_sug_person = fields.Char(compute='_get_can_apporve', string='审批人', readonly=True)
    comp_fd_sug_date = fields.Date(compute='_get_can_apporve', string='审批时间', readonly=True)
    unit_can_approve = fields.Boolean(compute='_get_can_apporve',string='所(中心)领导是否可以审批')
    rd_can_approve = fields.Boolean(compute='_get_can_apporve', string='科研处是否可以审批')
    fd_can_approve = fields.Boolean(compute='_get_can_apporve', string='财务处是否可以审批')
    is_create_uid = fields.Boolean(compute='_get_is_create_uid', string='是否发起人')
    
    #选择项目时，将项目经理带过来
    @api.onchange('proj_id')
    def _onchange_proj(self):
        if self.proj_id:
            manager_res = self.env['pm.init.proj.team'].search([('proj_apply_id.id','=',self.proj_id.id),('proj_staff_position.name','=','项目经理')])
            if manager_res:
                self.proj_manager = manager_res[0].proj_staff_name
    
    #删除时同时删除明细表
    def unlink(self, cr, uid, ids, context=None):
        detail_obj = self.pool.get('pm.fund.proj.monthplan.detail')
        detail_ids = detail_obj.search(cr, uid, [('monthplan_id', 'in', ids)], context=context)
        models.Model.unlink(detail_obj, cr, uid, detail_ids, context=context)
        return models.Model.unlink(self, cr, uid, ids, context=context)
    
    #创建同时提交工作流表单
    @api.model
    @api.returns('self', lambda value:value.id)
    def create(self, vals):
        if not self.state:
            vals['state'] = 'submitted'
        #modify by liuhongtai 2016-03-23 保存项目经理字段
        manager_res = self.env['pm.init.proj.team'].search([('proj_apply_id.id','=',vals['proj_id']),('proj_staff_position.name','=','项目经理')])
        if manager_res:
            vals['proj_manager'] = manager_res[0].proj_staff_name
        return models.Model.create(self, vals)
    
    #提交事件
    def submit(self):
        self.write({'state':'submitted'})
    
    #所(中心)审批事件
    def unit_approve(self):
        self.write({'state':'unit_approved','unit_sug_person':self.env.uid,'unit_sug_date':fields.Date.today()})
        
    #科研处审批事件
    def rd_approve(self):
        self.write({'state':'rd_approved','rd_sug_person':self.env.uid,'rd_sug_date':fields.Date.today()})
    
    #财务处审批事件
    def fd_approve(self):
        self.write({'state':'fd_approved','fd_sug_person':self.env.uid,'fd_sug_date':fields.Date.today()})
    
    #所(中心)退回事件
    def unit_return(self):
        self.write({'state':'unit_returned','unit_sug_person':self.env.uid,'unit_sug_date':fields.Date.today()})
    
    #科研处退回事件
    def rd_return(self):
        self.write({'state':'rd_returned','rd_sug_person':self.env.uid,'rd_sug_date':fields.Date.today()})
    
    #财务处退回事件
    def fd_return(self):
        self.write({'state':'fd_returned','fd_sug_person':self.env.uid,'fd_sug_date':fields.Date.today()})
        
    #获取jqGrid数据
    @api.model
    def getJqGridData(self, monthplan_id):
        detail_obj = self.env['pm.fund.proj.monthplan.detail']
        _res = detail_obj.search([('monthplan_id', '=', monthplan_id)])
        #新建时取默认初始数据 
        data_list=[]
        if monthplan_id=='New' or not _res:
            subject_obj = self.env['pm.common.subject']
            res = subject_obj.search([('is_leaf','=',True)],order='sn')
            #res_ids = subject_obj.browse(cr, uid, ids, context).sorted(key=lambda x:x['sn'])
            for record in res:
                data={}
                data['detail_id'] = 'New'
                data['subject_id'] = record.id
                first = record.parent_id.parent_id.parent_id
                second = record.parent_id.parent_id
                third = record.parent_id
                if first:
                    data['first'] = first.name
                    data['second'] = second.name
                    data['third'] = third.name
                elif second:
                    data['first'] = second.name
                    data['second'] = third.name
                    data['third'] = record.name
                elif third:
                    data['first'] = third.name
                    data['second'] = record.name
                    data['third'] = record.name 
                else:
                    data['first'] = record.name
                    data['second'] = record.name
                    data['third'] = record.name
                data['sn'] = record.sn
#                 if record.show_sn:
#                     data['show_sn'] = record.show_sn
#                 else:
#                     data['show_sn'] = ''
                data['subject_name'] = record.name
                data['plan_value'] = 0
                data['actual_value'] = 0
                data['cost_total'] = 0
                data['left_value'] = 0
                data_list.append(data)
        else:
            #非新建时取pm.fund.proj.monthplan.detail中数据
            res = detail_obj.search([('monthplan_id', '=', monthplan_id)])
            month_res = self.search([('id', '=', monthplan_id)])
            if res:
                #c_id:当前有效id，version_id:有效版本id
                c_id = self.env['sys.constant'].search([('type','=','USE_STATE'),('name','=','当前有效')]).id
                version_id = self.env['pm.fund.budget.version'].search([('proj_id','=',month_res.proj_id.id),('use_state','=',c_id)]).id
                version_detail_obj = self.env['pm.fund.budget.version.detail']
                subject_obj = self.env['pm.common.subject']
                #获取当前年本月之前月份的所有计划明细
                month_before_res = self.search([('proj_id','=',month_res.proj_id.id),('year.name', '=', month_res.year.name),('month.name','<',month_res.month.name),('state','=','fd_approved')])
                for record in res:
                    data={}
                    #根据subject_id查找父节点
                    res_subject = subject_obj.search([('id','=',record.subject_id)])
                    first = res_subject.parent_id.parent_id.parent_id
                    second = res_subject.parent_id.parent_id
                    third = res_subject.parent_id
                    if first:
                        data['first'] = first.name
                        data['second'] = second.name
                        data['third'] = third.name
                    elif second:
                        data['first'] = second.name
                        data['second'] = third.name
                        data['third'] = res_subject.name
                    elif third:
                        data['first'] = third.name
                        data['second'] = res_subject.name
                        data['third'] = res_subject.name 
                    else:
                        data['first'] = res_subject.name
                        data['second'] = res_subject.name
                        data['third'] = res_subject.name
                    data['detail_id'] = record.id
                    data['subject_id'] = record.subject_id
                    data['sn'] = record.sn
#                     if res_subject.show_sn:
#                         data['show_sn'] = res_subject.show_sn
#                     else:
#                         data['show_sn'] = ''
                    data['subject_name'] = record.subject_name
                    data['plan_value'] = record.plan_value
                    data['actual_value'] = record.actual_value
                    data['cost_total'] = record.cost_total
                    data['left_value'] = record.left_value
                    #如果状态为科研处已审批，增加两列：科目总额和已使用总额
                    if month_res.state=='rd_approved':
                        data['curyear_total'] = version_detail_obj.search([('version_id','=',version_id),('year','=',month_res.year.name),('subject_id','=',record.subject_id)]).value
                        curyear_cost = 0
                        for rec_detail in month_before_res:
                            curyear_cost += detail_obj.search([('monthplan_id', '=', rec_detail.id),('subject_id','=',record.subject_id)]).actual_value
                        data['curyear_cost'] = curyear_cost
                    data_list.append(data)
        return {'data':data_list}
    
class pm_fund_proj_monthplan_detail(models.Model):
    _name = 'pm.fund.proj.monthplan.detail' 
    _description = u"项目月度计划科目明细"  
    
    monthplan_id = fields.Char('月度计划表id')
    sn = fields.Integer('序号')
    subject_id = fields.Integer('科目ID')
    subject_name = fields.Char('科目名称', size=50)
    plan_value = fields.Float('计划使用', digits=(16,2))
    actual_value = fields.Float('实际使用', digits=(16,2))
    cost_total = fields.Float('支出合计', digits=(16,2))
    left_value = fields.Float('当前余额', digits=(16,2))
    
    #从jqGrid中取数进行保存
    def saveJqGrid(self, cr, uid, flag, data, context=None):
        if flag=='NewSave':
            for record in data:
                self.create(cr, uid, record, context=context)
        else:
            for record in data:
                if record['detail_id']!='New':
                    ids = []
                    ids.append(int(record['detail_id']))
                    self.write(cr, uid, ids, record, context=context)      
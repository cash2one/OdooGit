# -*- coding: utf-8 -*-

from openerp import models, fields, api
from openerp.osv import osv

class pm_fund_account(models.Model):
    _name = 'pm.fund.account'
    _description = u"经费到账信息"
        
    name = fields.Char('名称', size=100, default='经费到账信息')
    proj_id = fields.Many2one('pm.init.proj.apply', string='项目名称', required=True, domain=[('proj_periods.name','=','实施中')])
    proj_num = fields.Char(related='proj_id.proj_reply_info_id.proj_num', string="项目编号", store=True)
    fmis_num = fields.Char(related='proj_id.proj_reply_info_id.proj_reply_fmis', string="FMIS编号", store=True)
    budget_total = fields.Float(related='proj_id.proj_total_funds', string="合同总额", store=True)
    proj_vld = fields.Many2one('oa.admin.org',related='proj_id.proj_vld', string="项目承担单位", store=True)
    proj_start_date = fields.Date(related='proj_id.proj_start_date', string="项目开始时间", store=True)
    proj_end_date = fields.Date(related='proj_id.proj_end_date', string="项目结束时间", store=True)
    arrival_account = fields.Float(compute='_get_total_arrived', string="已到账总额")
    latest_arrived_account = fields.Float(compute='_get_latest_arrived', string="最近一次到账金额")
    latest_arrived_time = fields.Date(compute='_get_latest_arrived', string="最近一次到账时间")  
    assignplan_ids = fields.One2many('pm.fund.assignplan', 'account_id', string="经费下达计划")
    
    #获取已到账总金额(计算函数)
    @api.depends('assignplan_ids.assign_account')
    def _get_total_arrived(self):
        for record in self:
            record.arrival_account = sum(assignplan.actu_arrived_total for assignplan in record.assignplan_ids)
    
    #循环获取最近一次到账日期和金额(计算函数)
    @api.depends()
    def _get_latest_arrived(self):
        for record in self:
            for assignplan in record.assignplan_ids:
                for arrived in assignplan.arrived_ids:
                    if record.latest_arrived_time<=arrived.arrived_time:
                        record.latest_arrived_time = arrived.arrived_time
                        record.latest_arrived_account = arrived.arrived_account
    
    #选择项目名称时判断是否该项目已经保存过到账记录(默认一个项目只能有一条主记录)
    @api.onchange('proj_id')                    
    def check_change_proj_name(self):
        record=self.search([('proj_id','=',self.proj_id.id)])
        if record.exists():
            raise osv.except_osv('提示',"该项目已存在记录!")
        
    @api.model
    @api.returns('self', lambda value:value.id)
    def create(self, vals):
        if vals['assignplan_ids']:
            #存在assignplan_ids(下达计划)
            assign_total = 0
            assignplan_list = vals['assignplan_ids']
            for ass in assignplan_list:
                arrived_total = 0
                assign_account = ass[2]['assign_account']
                assign_total += assign_account
                arrived_list = ass[2]['arrived_ids']
                if arrived_list:
                    #若存在arrived_ids(实际到账记录)
                    for arr in arrived_list:
                        arrived_total += arr[2]['arrived_account']
                    if arrived_total>assign_account:
                        raise osv.except_osv('警告',"实际到账金额大于下达计划金额，请检查!")
            #查询合同总额
            budget_total = self.env['pm.init.proj.apply'].search([('id','=',vals['proj_id'])]).proj_total_funds
            if assign_total > budget_total:
                raise osv.except_osv('警告',"下达计划金额大于合同总额，请检查!")
        return models.Model.create(self, vals)
    
    @api.multi
    def write(self, vals):
        if vals['assignplan_ids']:
            #存在assignplan_ids的更新(下达计划)
            assign_total = 0
            assignplan_list = vals['assignplan_ids']
            for ass in assignplan_list:
                arrived_total = 0
                if ass[1] and (not ass[2] or not ass[2].has_key('assign_account')):
                    assign_account = self.env['pm.fund.assignplan'].search([('id','=',ass[1])]).assign_account
                else:
                    assign_account = ass[2]['assign_account']
                assign_total += assign_account
                if ass[2]:
                    arrived_list = ass[2]['arrived_ids']
                    if arrived_list:
                        #若存在arrived_ids(实际到账记录)
                        for arr in arrived_list:
                            if arr[1] and (not arr[2] or not arr[2].has_key('arrived_account')):
                                arrived_total += self.env['pm.fund.arrived'].search([('id','=',arr[1])]).arrived_account
                            else:
                                arrived_total += arr[2]['arrived_account']
                        if arrived_total>assign_account:
                            raise osv.except_osv('警告',"实际到账金额大于下达计划金额，请检查!")
            #查询合同总额
            budget_total = self.env['pm.init.proj.apply'].search([('id','=',self.proj_id.id)]).proj_total_funds
            if assign_total > budget_total:
                raise osv.except_osv('警告',"下达计划金额大于合同总额，请检查!")
        return models.Model.write(self, vals)
    
class pm_fund_assignplan(models.Model):
    _name = 'pm.fund.assignplan'    
    _description = u"经费下达计划"
    
    #获取实际到账金额(计算函数)
    @api.depends('arrived_ids.arrived_account')
    def _get_actu_arrived_total(self):
        for record in self:
            record.actu_arrived_total = sum(arrived.arrived_account for arrived in record.arrived_ids)
    
    #获取实际到账次数(计算函数)
    @api.depends('arrived_ids')
    def _get_actu_arrived_times(self):
        for record in self:
            record.actu_arrived_times = len(record.arrived_ids.ids) 
    
    name = fields.Char('名称', size=100, default='经费下达计划')
    assign_account = fields.Float('计划下达金额', digits=(16,2), required=True)
    assign_pnum = fields.Char('批文号', size=30, required=True)
    attachment = fields.Integer('批文附件')
    instruction = fields.Text('说明')
    assign_time = fields.Date('批文日期')
    actu_arrived_times = fields.Integer(compute='_get_actu_arrived_times',string='实际到账次数')
    actu_arrived_total = fields.Float(compute='_get_actu_arrived_total',string='实际到账金额')
    account_id = fields.Many2one('pm.fund.account', string="经费到账信息")
    arrived_ids = fields.One2many('pm.fund.arrived', 'assignplan_id', string="实际到账记录")
    
class pm_fund_arrived(models.Model):
    _name = 'pm.fund.arrived'    
    _description = u"经费到账记录"
    
    name = fields.Char('名称', size=100, default='经费到账记录')
    arrived_account = fields.Float('实际到账金额', digits=(16,2), required=True)
    arrived_time = fields.Date('实际到账日期', required=True)
    assignplan_id = fields.Many2one('pm.fund.assignplan', string="经费下达计划")
    

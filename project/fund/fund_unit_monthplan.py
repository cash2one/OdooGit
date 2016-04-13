# -*- coding: utf-8 -*-

from openerp import models, fields, api
from openerp.osv import osv

class pm_fund_unit_monthplan(models.Model):
    _name = 'pm.fund.unit.monthplan'
    _description = u"单位月度计划"
    _sql_constraints = [
        ('unique_key', 'UNIQUE (report_site,year,month)',  '请勿重复填报 !')
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
            detail_obj = self.env['pm.fund.unit.monthplan.detail']
            plan_value = detail_obj.search([('monthplan_id', '=', record.id),('subject_name', '=', '总计')]).plan_value
            record.plan_total = plan_value if plan_value else 0
    
    #获取实用总额
    @api.depends()
    def _get_actual_total(self):
        for record in self:
            detail_obj = self.env['pm.fund.unit.monthplan.detail']
            actual_value = detail_obj.search([('monthplan_id', '=', record.id),('subject_name', '=', '总计')]).actual_value
            record.actual_value = actual_value if actual_value else 0
    
    name = fields.Char('名称', size=100, default='单位经费月度计划')
    report_site = fields.Many2one('oa.admin.org', string='填报单位', size=100)
    year = fields.Many2one('sys.constant',string='年度', required=True, domain=[('type','=','year')])
    month = fields.Many2one('sys.constant',string='月度',required=True, domain=[('type','=','month')])
    ny = fields.Char(compute='_get_ny', string='年月', stroe=True)
    report_person = fields.Char('填报人', size=30, default=_get_default_report_person)
    report_date = fields.Date('填报日期', default=_get_default_regtime)
    state = fields.Selection([('unit_returned','已退回'),('fd_returned','已退回'),('draft','草稿'),('submitted','已提交'),('unit_approved','所(中心)已审批'),('fd_approved','财务处已审批')], string='状态', default='draft')
    remarks = fields.Text('备注')
    plan_total = fields.Float(compute='_get_plan_total', string='计划总额', digits=(16,2))
    actual_total = fields.Float(compute='_get_actual_total', string='实用总额', digits=(16,2))
    unit_suggest = fields.Text('所(中心)审批意见')
    unit_sug_person = fields.Char('审批人',size=30)
    unit_sug_date = fields.Date('审批时间')
    fd_suggest = fields.Text('财务处审批意见')
    fd_sug_person = fields.Char('审批人',size=30)
    fd_sug_date = fields.Date('审批时间')
    
    #删除时同时删除明细表
    def unlink(self, cr, uid, ids, context=None):
        detail_obj = self.pool.get('pm.fund.unit.monthplan.detail')
        detail_ids = detail_obj.search(cr, uid, [('monthplan_id', 'in', ids)], context=context)
        models.Model.unlink(detail_obj, cr, uid, detail_ids, context=context)
        return models.Model.unlink(self, cr, uid, ids, context=context)
    
    #创建同时提交工作流表单
    @api.model
    @api.returns('self', lambda value:value.id)
    def create(self, vals):
        return models.Model.create(self, vals)
    
    #提交事件
    def submit(self):
        self.write({'state':'submitted'})
    
    #所(中心)审批事件
    def unit_approve(self):
        self.write({'state':'unit_approved'})
    
    #财务处审批事件
    def fd_approve(self):
        self.write({'state':'fd_approved'})
    
    #财务处退回事件
    def unit_return(self):
        self.write({'state':'unit_returned'})
    
    #财务处退回事件
    def fd_return(self):
        self.write({'state':'fd_returned'})
        
    #获取jqGrid数据
    def get_jqGrid_data(self, cr, uid, res_id, context=None):
        data_list=[]
        #非新建时取pm.fund.proj.monthplan.detail中数据
        detail_obj = self.pool.get('pm.fund.unit.monthplan.detail')
        ids = detail_obj.search(cr, uid, [('monthplan_id', '=', res_id)], context=context)
        if ids:
            res_ids = detail_obj.browse(cr, uid, ids, context)
            for record in res_ids:
                data={}
                data['monthplan_id'] = record.monthplan_id
                data['detail_id'] = record.id
                data['sn'] = record.sn
                data['subject_name'] = record.subject_name
                data['plan_value'] = record.plan_value
                data['actual_value'] = record.actual_value
                data['cost_total'] = record.cost_total
                data['left_value'] = record.left_value
                data_list.append(data)
            return {'data':data_list}
        else:
            raise osv.except_osv('Warning!',"还未汇总本月数据或汇总失败，请检查！")
    
class pm_fund_unit_monthplan_detail(models.Model):
    _name = 'pm.fund.unit.monthplan.detail' 
    _description = u"单位月度计划科目明细"  
    
    monthplan_id = fields.Char('月度计划表id')
    sn = fields.Char('序号', size=10)
    subject_name = fields.Char('科目名称', size=50)
    plan_value = fields.Float('计划使用', digits=(16,2))
    actual_value = fields.Float('实际使用', digits=(16,2))
    cost_total = fields.Float('支出合计', digits=(16,2))
    left_value = fields.Float('当前余额', digits=(16,2))
    
    #从jqGrid中取数进行保存
    def save_jqGrid_data(self, cr, uid, res_id, data, context=None):
        if not data['detail_id']:
            self.create(cr, uid, data, context=context)
        else:
            ids = self.search(cr, uid, [('id', '=', data['detail_id'])], context=context)
            self.write(cr, uid, ids, data, context)
            
        
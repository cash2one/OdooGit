# -*- coding: utf-8 -*-

from openerp import models, fields, api

class pm_techservice_init(models.Model):
    _name = 'pm.techservice.init'
    _description = u"外协立项管理"
    _sql_constraints = [
        ('unique_key', 'UNIQUE (name)',  '外协项目已存在!')
    ]
    
    #获取默认的填报人
    def _get_default_registrant(self):
        user_name = self.env['res.users'].search([('id','=',self.env.context['uid'])]).partner_id.name
        return user_name
    
    #获取默认的填报日期
    def _get_default_reg_time(self):
        return fields.Date.today() 
    
    def get_name_domain(self):
        if self.env.uid == 1:
            return "[('is_category_fw','=',True),('ht_id.plan_id.wx_plan_check_result.is_selected_init','=',False)]"
        return "[('is_category_fw','=',True),('ht_id.plan_id.wx_plan_check_result.parent_proj.proj_pm_uid','=',uid),('ht_id.plan_id.wx_plan_check_result.is_selected_init','=',False)]"
        
    name = fields.Many2one('pm.purchase.trace', string='外协任务名称', required=True, domain=get_name_domain)
    proj_num = fields.Char('外协任务编号', size=20, required=True)
    parent_proj = fields.Many2one(related='name.ht_id.plan_id.wx_plan_check_result.parent_proj', string="外协任务所属项目", store=True, readonly=True)
    client = fields.Many2one(related='name.ht_id.plan_id.wx_plan_check_result.client', string="委托单位", store=True, readonly=True)
    bear_vld = fields.Char(related='name.provider', string='承担单位', store=True, readonly=True) 
    contract_account = fields.Float(related='name.ht_total_price', string='合同总额', store=True, readonly=True)
    bear_vld_director = fields.Char(related='name.contacts', string='负责人', store=True, readonly=True)
    bear_vld_phone = fields.Char(related='name.phone', string='负责人电话', store=True, readonly=True)
    start_time = fields.Date(related='name.ht_id.plan_id.wx_plan_check_result.start_time', string='项目开始时间', store=True, readonly=True)
    end_time = fields.Date(related='name.ht_id.plan_id.wx_plan_check_result.end_time', string='项目结束时间', store=True, readonly=True)
    registrant = fields.Char(string='登记人', size=30, default=_get_default_registrant, readonly=True)
    reg_time = fields.Date('登记时间', default=_get_default_reg_time, readonly=True)
    contract_name = fields.Char(related='name.ht_name', string='合同名称', store=True, readonly=True)
    contract_num = fields.Char(related='name.ht_number', string='合同编号', store=True, readonly=True)
    contract_date = fields.Date(related='name.ht_time', string='合同签订日期', store=True, readonly=True)
    contract_attach = fields.Integer(related='name.ht_content', string='合同文本', store=True, readonly=True)
    
    @api.model
    @api.returns('self', lambda value:value.id)
    def create(self, vals):
        new_id = models.Model.create(self, vals)
        if new_id:
            #在外协计划中将is_selected_init字段设为已选
            res_trace = self.env['pm.purchase.trace'].search([('id','=',vals['name'])])
            if res_trace:
                res_plan = self.env['pm.techservice.plan'].search([('id','=',res_trace.ht_id.plan_id.wx_plan_check_result.id)])
                if res_plan:
                    res_plan.write({'is_selected_init':True})
                    return new_id
        
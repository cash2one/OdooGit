# -*- coding: utf-8 -*-

from openerp import models, fields, api

'''
菜单名：采购跟踪管理
'''
#采购跟踪信息表
class pm_purchase_trace(models.Model):
    _name = 'pm.purchase.trace'
    _description = u'采购跟踪信息'
    
    @api.onchange('ht_id')
    def change_ht_id(self):
        for record in self:
            record.goods_arrival_record_id = False
    
    ht_name = fields.Char(string=u'合同名称',required=True)
    ht_id = fields.Many2one('pm.purchase.result',string=u'采购结果',domain=[('effective','=',True)],required=True)
    plan_id = fields.Many2one(related='ht_id.plan_id',string=u'采购计划',store=True,readonly=True)
    project_id = fields.Many2one(related='ht_id.project_id',string=u'项目',store=True,readonly=True)
    manager_id = fields.Integer(related='project_id.proj_pm_uid',string=u'项目经理id',readonly=True)
    name = fields.Many2one(related='plan_id.wx_plan_check_result',string=u'外协任务')
    organ_id = fields.Many2one(related='ht_id.organ_id',string=u'采购单位',store=True,readonly=True)
    ht_number = fields.Char(string=u'合同编号',required=True)
    ht_time = fields.Date(string=u'合同签定日期',required=True)
    agent = fields.Many2one('res.users',string=u'经办人',required=True)
    provider = fields.Char(string=u'供应商',required=True)
    ht_content = fields.Integer(string=u'合同文本',required=True)
    ht_total_price = fields.Float(string=u'合同总额(万元)',required=True)
    contacts = fields.Char(string=u'联系人',required=True)
    phone = fields.Char(string=u'联系方式',required=True)
    goods_arrival_record_id = fields.One2many('pm.purchase.goods.arrival','trace_id',string=u'到货情况')
    
    ht_ys = fields.Many2one('pm.techservice.acceptance',string=u'合同验收')#类型为Many2one,关联外协验收管理
    
    zy_time = fields.Date(string=u'终验日期')
    zy_participants = fields.Many2one('res.users',string=u'终验人员')
    zy_result = fields.Text(string=u'终验结论')
    zy_attach = fields.Integer(string=u'终验附件')
    payment_record_id = fields.One2many('pm.purchase.payment','trace_id',string=u'付款情况')
    is_category_fw = fields.Boolean(related='ht_id.plan_id.is_category_fw',string=u'是否为服务类采购',default=False)
    
    @api.model
    @api.returns('self', lambda value:value.id)
    def create(self, vals):
        if not vals['is_category_fw']:
            #如果不是服务类采购，新增到货信息时，将设备信息保存到"采购设备明细表中"
            if vals['ht_id']:
                current_ht = self.env['pm.purchase.result'].search([('id','=',vals['ht_id'])])#选中的采购结果
                new_last_goods = self.env['pm.purchase.last.goods'].search([('project_id','=',current_ht.plan_id.project_id.id)])
                if not new_last_goods:
                    new_last_goods = self.env['pm.purchase.last.goods'].create({'project_id':current_ht.plan_id.project_id.id,'manager_id':current_ht.plan_id.project_id.proj_pm_uid})
                if vals['goods_arrival_record_id']:
                    for dh in vals['goods_arrival_record_id']:
                        if dh[2]:
                            goods_id = self.env['pm.purchase.zb.goods'].search([('id','=',dh[2]['name'])]).name.name.id
                            for i in range(dh[2]['goods_amount']):
                                self.env['pm.purchase.last.goods.detail'].create({'last_goods_id':new_last_goods.id,'name':goods_id,'provider':vals['provider'],'provide_time':dh[2]['dh_time'],'responsible_person':vals['agent']})
        
        return models.Model.create(self, vals)

#到货情况
class pm_purchase_goods_arrival(models.Model):
    _name = 'pm.purchase.goods.arrival'
    _description = u'到货情况'
    
    trace_id = fields.Many2one('pm.purchase.trace',string=u'采购跟踪信息')
    ht_id = fields.Many2one(related='trace_id.ht_id',string=u'采购结果')
    name = fields.Many2one('pm.purchase.zb.goods',string=u'设备名称',required=True)
    goods_version = fields.Char(string=u'型号',required=True)
    goods_amount = fields.Integer(string=u'数量',required=True)
    dh_place = fields.Char(string=u'到货地点',required=True)
    dh_time = fields.Date(string=u'到货日期',required=True)
    ys_time = fields.Date(string=u'验收日期',required=True)
    ys_participants = fields.Char(string=u'验收人员',required=True)
    ys_result = fields.Char(string=u'验收结果',required=True)

#付款情况
class pm_purchase_payment(models.Model):
    _name = 'pm.purchase.payment'
    _description = u'付款情况'
    
    trace_id = fields.Many2one('pm.purchase.trace',string=u'采购跟踪信息')
    price = fields.Float(string=u'付款额度(万元)')
    fk_time = fields.Date(string=u'付款日期')
    remark = fields.Char(string=u'备注')
# -*- coding: utf-8 -*-

from openerp import models, fields, api

'''
菜单名：采购设备明细
'''
#采购设备明细
class pm_purchase_last_goods(models.Model):
    _name = 'pm.purchase.last.goods'
    _description = u'采购设备明细'
    _sql_constraints = [
        ('unique_key', 'UNIQUE (project_id)',  '所选项目已存在设备明细信息!')
    ]
    
    def _get_amount(self):
        for record in self:
            record.amount = len(record.last_goods_record_id)
            
    @api.onchange('project_id')
    def change_project_id(self):
        for record in self:
            proj_pm_uid = record.project_id.proj_pm_uid
            if proj_pm_uid:
                record.manager_id = self.env['res.users'].search([('id','=',proj_pm_uid)])

    def get_project_id_domain(self):
        if self.env.uid == 1:
            return "[('proj_periods.name','=',u'实施中')]"
        return "[('proj_periods.name','=',u'实施中'),('proj_pm_uid','=',uid)]"
           
    project_id = fields.Many2one('pm.init.proj.apply',string=u'项目',required=True,domain=get_project_id_domain)
    organ_id = fields.Many2one(related='project_id.proj_vld',string=u'承担单位',required=True)
    manager_id = fields.Many2one('res.users',string=u'项目经理',required=True)
    amount =  fields.Integer(compute='_get_amount',string=u'设备数量')
    last_goods_record_id = fields.One2many('pm.purchase.last.goods.detail','last_goods_id',string=u'采购设备明细详情')

#采购设备明细详情
class pm_purchase_last_goods_detail(models.Model):
    _name = 'pm.purchase.last.goods.detail'
    _description = u'采购设备明细详情'
    
    last_goods_id = fields.Many2one('pm.purchase.last.goods',string=u'采购设备明细')
    name = fields.Many2one('pm.init.proj.purchase',string=u'设备名称')
    provider = fields.Char(string=u'供应商')
    provide_time = fields.Date(string=u'供货日期')
    responsible_person = fields.Many2one('res.users',string=u'负责人')
    goods_num = fields.Char(string=u'资产登记号')
    sequence = fields.Char(string=u'序列号')
    place = fields.Char(string=u'部署地点')


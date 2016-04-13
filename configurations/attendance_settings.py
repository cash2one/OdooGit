# -*- coding: utf-8 -*-

from openerp import models, fields, api
from openerp.osv import osv
    
# 假期类型2
class holidays_type(models.Model):
    _name='oa.holiday.type'
    _description=u"假期类型" 
    _order = 'order'
    
    name=fields.Char('假期名称', required=True)
    type=fields.Selection([('holiday','休假'),('trip','差旅')],'类型')
    order = fields.Integer('显示顺序')

# 考勤时钟3
class attendance_clock(models.Model):
    _name='oa.attendance.clock'
    _description=u"考勤时钟设置表" 
    
    attendance_start_time=fields.Char('考勤起时钟',default='00:00:00')
    attendance_end_time=fields.Char('考勤止时钟',default='00:00:00')
    
    @api.model
    @api.returns('self', lambda value:value.id)
    def create(self, vals):
        #确定只有一条记录
        res=self.search([])
        if res:
            raise osv.except_osv('Warning!',"已存在记录，不能添加第二条！")
        else:
            return models.Model.create(self, vals)
    
    @api.multi
    def write(self, vals):
        if 'attendance_start_time' in vals:
            if len(vals['attendance_start_time'])!=8:
                raise osv.except_osv('Warning!',"考勤起时钟格式必须为00:00:00，请检查！")
        if 'attendance_end_time' in vals:
            if len(vals['attendance_end_time'])!=8:
                raise osv.except_osv('Warning!',"考勤止时钟格式必须为00:00:00，请检查！")
        return models.Model.write(self, vals)

class work_calendar(models.Model):
    _name='oa.work.calendar'
    _description=u"工作日历表" 
    
    oa_day=fields.Date('日期', required=True, select=True)
    is_work=fields.Integer('是否工作日', required=True)
    ori_is_work=fields.Integer('原始是否工作日', required=True)
    
# 日历假期记录表
class calendar_holi_records(models.Model):
    _name='oa.calendar.holi.records'
    _description=u"工作日历假期记录" 
    
    @api.model
    @api.returns('self', lambda value:value.id)
    def create(self, vals):
        #判断在日期范围内有记录
        is_ids=self.search([('date_start','<=',vals['date_end']),('date_end','>=',vals['date_start'])])
        if is_ids:
            raise osv.except_osv('Warning!',"已存在区间内记录，不能创建，请检查！")
        else:
            festival_name = {
              'NewYear': lambda : '元旦',
              'Spring': lambda : '春节',
              'Qingming': lambda : '清明节',
              'LaborDay' : lambda : '劳动节',
              'DragonBoat' : lambda : '端午节',
              'MidAutumn' : lambda : '中秋节',
              'NationalDay' : lambda : '国庆节',
              'Other' : lambda : '其他'
            }[vals['name']]()
            
            work_or_rest={
              'Work': lambda : '班',
              'Rest': lambda : '休'          
            }[vals['type']]()
            vals['name_and_type']=''.join([festival_name,'(',work_or_rest,')'])
            new_id=models.Model.create(self, vals)
            if new_id:
                #修改oa_work表中工作日状态
                record_obj = self.env['oa.work.calendar']
                record_res = record_obj.search([('oa_day', '>=', vals['date_start']), ('oa_day', '<=', vals['date_end'])]) 
                for r in record_res:
                    r.write({'ori_is_work':r.is_work})
                if vals['type']=='Work':
                    record_res.write({'is_work':1})
                else:
                    record_res.write({'is_work':0})
            return new_id
        
    @api.multi
    def write(self, vals):
        raise osv.except_osv('Warning!',"由于需要，不能进行二次编辑，请先删除，再新建！")    
        #return models.Model.write(self, vals)
    
    def unlink(self, cr, uid, ids, context=None):
        #恢复原始工作日状态
        rec_obj=self.browse(cr, uid, ids, context)
        record_obj = self.pool.get('oa.work.calendar')
        record_ids = record_obj.search(cr,uid,[('oa_day', '>=', rec_obj.date_start), ('oa_day', '<=', rec_obj.date_end)],context=context)
        record_res = record_obj.browse(cr, uid,record_ids,context)
        for re in record_res:
            re.write({'is_work':re.ori_is_work}) 
            re.write({'ori_is_work':0})
        return models.Model.unlink(self, cr, uid, ids, context=context)    
        
    name=fields.Selection([('NewYear','元旦'),('Spring','春节'),('Qingming','清明节'),('LaborDay','劳动节'),('DragonBoat','端午节'),('MidAutumn','中秋节'),('NationalDay','国庆节'),('Other','其他')],'节假日',required=True)
    type=fields.Selection([('Work','班'),('Rest','休')],'类型',required=True)
    date_start=fields.Date('开始日期', required=True)
    date_end=fields.Date('结束日期', required=True)
    name_and_type=fields.Char('节日及班休')                       
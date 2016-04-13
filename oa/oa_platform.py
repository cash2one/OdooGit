# -*- coding: utf-8 -*-

from openerp import models, fields, api
from openerp.osv.fields import datetime
import openerp

#领导行程
class leader_schedule(models.Model):
    _name="oa.leader.schedule"
    _description=u"领导行程"
    
    name=fields.Char('活动或会议',size=200,required=True)
    start_time=fields.Datetime('开始时间',required=True)
    end_time=fields.Datetime('结束时间',required=True)
    address=fields.Char('地点',size=200,required=True)
    attendance_leaders=fields.Many2many('oa.staff.basic','leader_schedule_staff_rel','leader_schedule_id','staff_id','拟出席领导')
    organization=fields.Char('组织部门',size=200)
    contacts=fields.Char('联系人',size=200)
    remarks=fields.Text('备注')
    
#发送通知
class send_notification(models.Model):
    _name="oa.send.notification"
    #继承mail.thread(消息提醒用)
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description=u"发送通知"
    
    #获取默认的发送人
    def get_default_name(self):
        uid= self.env.context['uid']
        return self.env['res.users'].search([('id','=',uid)]).partner_id.name
      
    @api.model
    @api.returns('self', lambda value:value.id)
    def create(self, vals):
        vals['from_person']=self.env['res.users'].search([('id','=',self.env.context['uid'])]).partner_id.name
        vals['from_time']=datetime.now()
        new_id = models.Model.create(self, vals)
        if new_id:
            #创建成功后发送通知
            #部门内所有员工
            if vals['to_department']:
                org_ids=vals['to_department'][0][2]
                staff_ids=self.env['oa.staff.basic'].search([('vld_site','=',org_ids)]).ids
                user_ids=list(set(u.related_user.id for u in self.env['oa.staff.basic'].browse(staff_ids)))
                d_partner_ids=list(set(v.partner_id.id for v in self.env['res.users'].browse(user_ids)))
            if vals['to_person']:
                _user_ids=list(set(w.related_user.id for w in self.env['oa.staff.basic'].browse(vals['to_person'][0][2])))
                p_partner_ids=list(set(g.partner_id.id for g in self.env['res.users'].browse(_user_ids)))
        partner_ids=d_partner_ids + p_partner_ids
        if partner_ids:
            openerp.noti_message.insert_message(new_id,self,'','',vals['name'],'',partner_ids)
        return new_id    
            
    name=fields.Char('通知标题',size=200,required=True)
    content=fields.Text('通知内容',required=True) 
    to_department=fields.Many2many('oa.admin.org','send_notification_org_rel','send_notification_id','org_id','通知部门')
    to_person=fields.Many2many('oa.staff.basic','send_notification_staff_rel','send_notification_id','staff_id','通知人员')
    from_person=fields.Char('发送人员',default=get_default_name) 
    from_time=fields.Datetime('发送时间',default=datetime.now())     

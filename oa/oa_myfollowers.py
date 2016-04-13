# -*- coding: utf-8 -*-

from openerp import models, fields

#我关注的
class oa_myfollowers(models.Model):
    _name = 'oa.myfollowers'
    _description = u'我的关注'
    _sql_constraints = [
        ('unique_key', 'UNIQUE (staff_id)',  '姓名重复 !')
    ]
    
    staff_id = fields.Many2one('oa.staff.basic', string='姓名')
    followers = fields.Many2many('oa.staff.basic','oa_myfollowers_staff_rel','oa_myfollowers_id','staff_id','关注的人')
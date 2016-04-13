# -*- coding: utf-8 -*-

from openerp import models, fields, api

class audit_management_regulations(models.Model):
    _name = 'audit.management.regulations'
    _description = u"管理规定表"
        
    name = fields.Char(u'标题', size=200, required=True)
    num = fields.Char(u'文号', size=100, required=True)
    public_vld = fields.Char(u'发布单位', size=100)
    public_date = fields.Date('发布日期')
    public_level = fields.Selection([('gj',u'国家'),('jt',u'集团'),('bk',u'板块'),('qy',u'企业')], u'发布级别')
    content = fields.Text(u'正文')
    attachment = fields.Binary(u'附件')
    
class audit_standard_regulations(models.Model):
    _name = 'audit.standard.regulations'
    _description = u"法规标准表"
        
    name = fields.Char(u'标题', size=200, required=True)
    num = fields.Char(u'文号', size=100, required=True)
    public_vld = fields.Char(u'发布单位', size=100)
    public_date = fields.Date(u'发布日期')
    public_level = fields.Selection([('gj',u'国家'),('jt',u'集团'),('bk',u'板块'),('qy',u'企业')], u'发布级别')
    type = fields.Selection([('fg',u'法规'),('bz',u'标准')], u'法规标准')
    content = fields.Text(u'正文')
    attachment = fields.Binary(u'附件')
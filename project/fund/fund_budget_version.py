# -*- coding: utf-8 -*-

from openerp import models, fields, api
from openerp.osv import osv

class pm_fund_budget_version(models.Model):
    _name = 'pm.fund.budget.version'
    _description = u"经费预算变更版本信息"
    _sql_constraints = [
        ('unique_key', 'UNIQUE (proj_id,version)',  '版本重复 !')
    ]
    
    #获取默认的登记人
    def _get_default_registrant(self):
        user_name = self.env['res.users'].search([('id','=',self.env.uid)]).partner_id.name
        return user_name
    
    #获取默认的登记日期
    def _get_default_reg_date(self):
        return fields.Date.today()
    
    #新建时获取默认的状态(当前有效)
    def _get_default_state(self):
        return self.env['sys.constant'].search([('type','=','USE_STATE'),('name','=','当前有效')]).id
    
    def get_project_id_domain(self):
        if self.env.uid == 1:
            return "[('proj_periods.name','=',u'实施中')]"
        return "[('proj_periods.name','=',u'实施中'),('proj_pm_uid','=',uid)]"
    
    name = fields.Char('名称', size=100, default='经费预算版本')
    proj_id = fields.Many2one('pm.init.proj.apply', string='项目名称', required=True, domain=get_project_id_domain)
    proj_num = fields.Char(related='proj_id.proj_num', string="项目编号", store=True)
    fmis_num = fields.Char(related='proj_id.fmis_num', string="FMIS编号", store=True)
    version = fields.Float(string="预算变更版本号", digits=(3,1), required=True)
    use_state = fields.Many2one('sys.constant', string="使用状态", domain=[('type','=','USE_STATE')], required=True, default=_get_default_state)
    version_basis = fields.Many2one('pm.fund.bc.apply', string="变更依据", domain=[('state','=','rd_approved')])
    registrant = fields.Char('登记人', size=30, default=_get_default_registrant)
    reg_date = fields.Date('登记日期', default=_get_default_reg_date)
    
    @api.model
    @api.returns('self', lambda value:value.id)
    def create(self, vals):
        con_obj = self.env['sys.constant']
        c_id = con_obj.search([('type','=','USE_STATE'),('name','=','当前有效')]).id
        h_id = con_obj.search([('type','=','USE_STATE'),('name','=','历史版本')]).id
        res = self.search([('proj_id','=',vals['proj_id']),('use_state','=',c_id)])
        res.write({'use_state':h_id})
        return models.Model.create(self, vals)
    
    #删除时同时删除明细表
    def unlink(self, cr, uid, ids, context=None):
        con_obj = self.pool.get('sys.constant')
        c_ids = con_obj.search(cr, uid, [('type','=','USE_STATE'),('name','=','当前有效')], context=context)
        res = self.browse(cr, uid, ids, context)
        is_exist = False 
        for record in res: 
            if c_ids[0] and record.use_state.id==c_ids[0]:
                is_exist = True
                break
        if is_exist:
            raise osv.except_osv('提示',"当前有效版本不能删除，请检查!")
        else:   
            detail_obj = self.pool.get('pm.fund.budget.version.detail')
            detail_ids = detail_obj.search(cr, uid, [('version_id', 'in', ids)], context=context)
            models.Model.unlink(detail_obj, cr, uid, detail_ids, context=context)
            return models.Model.unlink(self, cr, uid, ids, context=context)
    
    #获取jqGrid数据
    def getJqGridData(self, cr, uid, rec_info, context=None):
        detail_obj = self.pool.get('pm.fund.budget.version.detail')
        detail_ids = detail_obj.search(cr, uid, [('version_id', '=', rec_info['version_id'])], context=context)
        proj_obj = self.pool.get('pm.init.proj.apply')
        proj_ids = proj_obj.search(cr, uid, [('id', '=', rec_info['proj_id'])], context=context)
        proj_res = proj_obj.browse(cr, uid, proj_ids, context)
        data_list=[]
        if proj_res:
            constant_obj = self.pool.get('sys.constant')
            constant_ids = constant_obj.search(cr, uid, [('type','=','USE_STATE'),('name','=','当前有效')], context=context)
            constant_res = constant_obj.browse(cr, uid, constant_ids, context)
            version_obj = self.pool.get('pm.fund.budget.version')
            version_ids = version_obj.search(cr, uid, [('proj_id','=',rec_info['proj_id']),('use_state', '=', constant_res.id)], context=context)
            if version_ids:
                version_res = version_obj.browse(cr, uid, version_ids[0], context)
                v_id = version_res.id
            else:
                v_id = 0
#             if not detail_ids and not v_id:
#                 raise osv.except_osv('提示',"该项目没有可用的预算经费，请检查!")
            start_year = int(proj_res.proj_start_date[:4])
            end_year = int(proj_res.proj_end_date[:4])    
            #新建时取默认初始数据 
            subject_obj = self.pool.get('pm.common.subject')
            subject_ids = subject_obj.search(cr, uid, [('is_leaf','=',True)], context=context)
            subject_res = subject_obj.browse(cr, uid, subject_ids, context).sorted(key=lambda x:x['sn'])        
            
            for rec in subject_res:
                data={}
                first = rec.parent_id.parent_id.parent_id
                second = rec.parent_id.parent_id
                third = rec.parent_id
                if first:
                    data['first'] = first.name
                    data['second'] = second.name
                    data['third'] = third.name
                elif second:
                    data['first'] = second.name
                    data['second'] = third.name
                    data['third'] = rec.name
                elif third:
                    data['first'] = third.name
                    data['second'] = rec.name
                    data['third'] = rec.name 
                else:
                    data['first'] = rec.name
                    data['second'] = rec.name
                    data['third'] = rec.name
                data['subject_id'] = rec.id
                data['sn'] = rec.sn
                data['subject_name'] = rec.name
                for y in range(start_year, end_year+1):
                    if rec_info['version_id']=='New' or not detail_ids:
                        year_ids = detail_obj.search(cr, uid, [('version_id', '=', v_id),('year','=',y),('subject_id','=',rec.id)], context=context)
                    else:
                        year_ids = detail_obj.search(cr, uid, [('version_id', '=', rec_info['version_id']),('year','=',y),('subject_id','=',rec.id)], context=context)
                    if year_ids:
                        year_res = detail_obj.browse(cr, uid, year_ids, context)
                        data[y] = year_res.value
                data_list.append(data)
        else:
            start_year = 0
            end_year = 0
        return {'start_year':start_year, 'end_year':end_year, 'data':data_list}
        
class pm_fund_budget_version_detail(models.Model):
    _name = 'pm.fund.budget.version.detail'
    _description = u"经费预算变更版本科目信息"
    
    version_id = fields.Char('版本ID', size=10)
    sn = fields.Integer('序号')
    subject_id = fields.Integer('科目ID')
    subject_name = fields.Char('科目名称', size=50)
    year = fields.Integer('年度')
    value = fields.Float('预算值')
      
    #从jqGrid中取数进行保存
    def saveJqGrid(self, cr, uid, flag, start_year, end_year, data, context=None):
        if flag=='NewSave':
            for record in data:
                _record = record
                for k in range(start_year, end_year+1):
                    _record['year'] = k
                    _record['value'] =  _record[str(k)]
                    self.create(cr, uid, _record, context=context)
        else:
            detail_obj = self.pool.get('pm.fund.budget.version.detail')
            for record in data:
                _record = record
                for k in range(start_year, end_year+1):
                    detail_ids = detail_obj.search(cr, uid, [('version_id', '=', record['version_id']),('year','=',k),('subject_id','=',record['subject_id'])], context=context)
                    _record['value'] =  _record[str(k)]
                    self.write(cr, uid, detail_ids, record, context=context)  
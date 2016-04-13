# -*- coding: utf-8 -*-

from datetime import date, datetime
from openerp import models, fields, api

class audit_ovaplan_info(models.Model):
    _name = 'audit.ovaplan.info'
    _description = u'总体方案表'
    
    name = fields.Char(u'方案名称', required=True)
    period = fields.Many2one('sys.constant', domain=[('type','=','audit_period')], string=u'审核期次', required=True)
    start_time = fields.Date(u'审核开始日期', required=True)
    end_time = fields.Date(u'审核结束日期', required=True)
    remark = fields.Char(u'备注')
    attachments = fields.Integer(u'培训材料')
    
    audit_plan_ids = fields.One2many('audit.plan.info', 'ovaplan_id', string='审核计划')
    audit_ovaplan_enterprise_ids = fields.One2many('audit.ovaplan.enterprise', 'ovaplan_id', string='受审企业')
    audit_ovaplan_standard_ids = fields.One2many('audit.ovaplan.standard', 'ovaplan_id', u'方案审核标准')
            
class audit_ovaplan_enterprise(models.Model):
    _name = 'audit.ovaplan.enterprise'
    _decription = u'受审企业表'
    
    enterprise_id = fields.Many2one('audit.vld.site', u'受审企业')
    audit_method = fields.Many2one('sys.constant', domain=[('type','=','audit_type')], string=u'审核方式')
    org_to_audit = fields.Many2one('sys.constant', domain=[('type','=','audit_org')], string=u'组织实施')
    start_time = fields.Date(u'审核开始日期')
    end_time = fields.Date(u'审核结束日期')
    
    ovaplan_id = fields.Many2one('audit.ovaplan.info', u'审核方案名称')
            
class audit_ovaplan_standard(models.Model):
    _name = 'audit.ovaplan.standard'
    _description = u'总体方案审核标准表'
    
    ovaplan_id = fields.Many2one('audit.ovaplan.info', u'审核方案名称')
    standard_id = fields.Many2one('audit.standard', u'审核标准')
    
    #获取方案审核标准，按类别分类
    @api.model
    def get_all_and_ova_standard(self, type, ova_id):
        sql_ova_std_by_type = '''
        select std.id, std.name, std.level_name, std.parent_id, std.seq 
        from (select * from audit_standard where type='{0}') std 
        inner join (select standard_id from audit_ovaplan_standard where ovaplan_id = '{1}') ova_std 
        on std.id = ova_std.standard_id
                        '''
        sql_ova_std_by_type = sql_ova_std_by_type.format(type, ova_id)
        self.env.cr.execute(sql_ova_std_by_type)
        ret_ova_std = []
        for row in self.env.cr.fetchall():
            item = {}
            item['id'] = row[0]
            item['text'] = row[1]
            item['levelname'] = row[2]
            item['parentid'] = row[3]
            item['seq'] = row[4]
            item['value'] = 0
            item['showcheck'] = True
            item['complete'] = True
            item['isexpand'] = False
            item['checkstate'] = 1
            item['hasChildren'] = False
            ret_ova_std.append(item)
            
        sql_std_by_type = '''
                            select id, name, level_name, parent_id, seq from audit_standard where type='{0}'
                        '''
        sql_std_by_type = sql_std_by_type.format(type)
        self.env.cr.execute(sql_std_by_type)
        ret_std = []
        for row in self.env.cr.fetchall():
            item = {}
            item['id'] = row[0]
            item['text'] = row[1]
            item['levelname'] = row[2]
            item['parentid'] = row[3]
            item['seq'] = row[4]
            item['value'] = 0
            item['showcheck'] = True
            item['complete'] = True
            item['isexpand'] = False
            item['checkstate'] = 0
            item['hasChildren'] = False
            ret_std.append(item)
            
        
        ret = {}
        ret["r_std"] = ret_ova_std
        ret["l_std"] = ret_std
        return ret 
    
    @api.model
    def updateOvaStd(self, stds, ova_id):
        print '+++++++++++++++++++++++++++++++++++'
        print ova_id
        sql_rev_ova_stds = '''
                    delete from audit_ovaplan_standard where ovaplan_id = '{0}'
                        '''
        sql_rev_ova_stds = sql_rev_ova_stds.format(ova_id)
        self.env.cr.execute(sql_rev_ova_stds)
        
        sql_ins_ova_stds = '''
                        insert into audit_ovaplan_standard ( standard_id, ovaplan_id ) values {0}
                            '''
        values = ''
        for  std_id in stds:
            values = values+'('+str(std_id)+','+str(ova_id)+'),'
            
        values = values[:-1]
        sql_ins_ova_stds = sql_ins_ova_stds.format(values)
        print sql_ins_ova_stds
        self.env.cr.execute(sql_ins_ova_stds)
        
class audit_plan_info(models.Model):
    _name = "audit.plan.info"
    _description = u'审核计划表'
    
    enterprise_id = fields.Many2one('audit.vld.site', u'受审企业')
    audit_method = fields.Many2one('sys.constant', domain=[('type','=','audit_type')], string=u'审核方式')
    org_to_audit = fields.Many2one('sys.constant', domain=[('type','=','audit_org')], string=u'组织实施')
    start_time = fields.Date(u'审核开始日期')
    end_time = fields.Date(u'审核结束日期')
    
    ovaplan_id = fields.Many2one('audit.ovaplan.info', u'审核方案名称')
    audit_plan_standard_ids = fields.One2many('audit.plan.standard', 'audit_plan_id', u'企业审核标准')
    audit_plan_subplan_ids = fields.One2many('audit.plan.subplan', 'audit_plan_id', string=u'现场审核计划安排')
    audit_plan_expert_ids = fields.One2many('audit.plan.expert', 'audit_plan_id', string=u'审核成员')
    period = fields.Char(compute='_get_audit_period', string="审核期次")
    
    #获取审核时间
    @api.onchange('ovaplan_id')
    def _get_plan_start_end_date(self):
        if self.ovaplan_id:
            ovaplan_obj = self.env['audit.ovaplan.info'].search([('id','=',self.ovaplan_id.id)])
            if ovaplan_obj:
                self.start_time = ovaplan_obj.start_time
                self.end_time = ovaplan_obj.end_time
    
    #获取审核期次
    @api.depends('ovaplan_id')
    def _get_audit_period(self):
        if self.ovaplan_id:
            print '**********************************'
            print self.ovaplan_id.id
            audit_period = self.env['audit.ovaplan.info'].search([('id', '=', self.ovaplan_id.id)]).period
            self.period=audit_period.name
    
    #获取审核方式
    @api.onchange('enterprise_id', 'ovaplan_id')
    def _onchange_enterprise_and_ova(self):
        print "on change"
        if(self.enterprise_id and self.ovaplan_id):
            ovaplan_enterprise_obj = self.env['audit.ovaplan.enterprise'].search([('ovaplan_id', '=', self.ovaplan_id.id), ('enterprise_id', '=', self.enterprise_id.id)])
            if ovaplan_enterprise_obj:
                self.audit_method = ovaplan_enterprise_obj.audit_method
                
    @api.onchange('audit_method')
    def _onchange_audit_method(self):
        print "on change audit_method"
            
 
class audit_plan_standard(models.Model):
    _name = 'audit.plan.standard'
    _description = u'审核计划标准表'
    
    audit_plan_id = fields.Many2one('audit.plan.info', u'审核计划')
    standard_id = fields.Many2one('audit.standard', u'审核标准')
    
    #获取企业计划审核标准
    @api.model
    def get_exsit_plan_form_standard_tree(self, plan_id):
        print "*********************"
        print plan_id
        #audit_plan_info
        plan_obj = self.env['audit.plan.info']
        plan_audit_type = plan_obj.search([('id', '=', plan_id)]).audit_method.id
        sql_plan_std_by_type = '''
        select std.id, std.name, std.level_name, std.parent_id, std.seq 
        from (select * from  audit_standard where type='{0}') std 
        inner join (select standard_id from audit_plan_standard where audit_plan_id = '{1}') plan_std 
        on std.id = plan_std.standard_id
                        '''
        sql_plan_std_by_type = sql_plan_std_by_type.format(plan_audit_type, plan_id)
        self.env.cr.execute(sql_plan_std_by_type)
        ret_plan_std = []
        for row in self.env.cr.fetchall():
            item = {}
            item['id'] = row[0]
            item['text'] = row[1]
            item['levelname'] = row[2]
            item['parentid'] = row[3]
            item['seq'] = row[4]
            item['value'] = 0
            item['showcheck'] = True
            item['complete'] = True
            item['isexpand'] = False
            item['checkstate'] = 1
            item['hasChildren'] = False
            ret_plan_std.append(item)
            
        #左边树的审核标准(与右树的选择状态完全一致，并显示所有树节点)
        sql_std_by_type = '''
                            select id, name, level_name, parent_id, seq from audit_standard where type='{0}'
                        '''
        sql_std_by_type = sql_std_by_type.format(plan_audit_type)
        self.env.cr.execute(sql_std_by_type)
        ret_std = []
        for row in self.env.cr.fetchall():
            item = {}
            item['id'] = row[0]
            item['text'] = row[1]
            item['levelname'] = row[2]
            item['parentid'] = row[3]
            item['seq'] = row[4]
            item['value'] = 0
            item['showcheck'] = True
            item['complete'] = True
            item['isexpand'] = False
            item['checkstate'] = 0
            item['hasChildren'] = False
            ret_std.append(item)
            
        
        ret = {}
        ret["r_std"] = ret_plan_std
        ret["l_std"] = ret_std
        return ret 
    
    @api.model
    def get_init_plan_form_standard_tree(self, ovaplan_id, type):
        print '*************************'
        print type
        print ovaplan_id
        
        #用选中的方案与审核方式下的审核元素初始化左右树
        sql_ova_std_by_type = '''
        select std.id, std.name, std.level_name, std.parent_id, std.seq 
        from (select * from audit_standard where type='{0}') std 
        inner join (select standard_id from audit_ovaplan_standard where ovaplan_id = '{1}') ova_std 
        on std.id = ova_std.standard_id
                        '''
        sql_ova_std_by_type = sql_ova_std_by_type.format(type, ovaplan_id)
        self.env.cr.execute(sql_ova_std_by_type)
        ret_ova_std = []
        for row in self.env.cr.fetchall():
            item = {}
            item['id'] = row[0]
            item['text'] = row[1]
            item['levelname'] = row[2]
            item['parentid'] = row[3]
            item['seq'] = row[4]
            item['value'] = 0
            item['showcheck'] = True
            item['complete'] = True
            item['isexpand'] = False
            item['checkstate'] = 1
            item['hasChildren'] = False
            ret_ova_std.append(item)
            
        sql_std_by_type = '''
                            select id, name, level_name, parent_id, seq from audit_standard where type='{0}'
                        '''
        sql_std_by_type = sql_std_by_type.format(type)
        self.env.cr.execute(sql_std_by_type)
        ret_std = []
        for row in self.env.cr.fetchall():
            item = {}
            item['id'] = row[0]
            item['text'] = row[1]
            item['levelname'] = row[2]
            item['parentid'] = row[3]
            item['seq'] = row[4]
            item['value'] = 0
            item['showcheck'] = True
            item['complete'] = True
            item['isexpand'] = False
            item['checkstate'] = 0
            item['hasChildren'] = False
            ret_std.append(item)
        
        ret = {}
        ret["l_std"] = ret_std
        ret["r_std"] = ret_ova_std
        return ret 
    
    @api.model
    def updatePlanStd(self, stds, plan_id):
        print '+++++++++++++++++++++++++++++++++++'
        print plan_id
        sql_rev_plan_stds = '''
                    delete from audit_plan_standard where audit_plan_id = '{0}'
                        '''
        sql_rev_plan_stds = sql_rev_plan_stds.format(plan_id)
        self.env.cr.execute(sql_rev_plan_stds)
        
        sql_ins_plan_stds = '''
                        insert into audit_plan_standard ( standard_id, audit_plan_id ) values {0}
                            '''
        values = ''
        for  std_id in stds:
            values = values+'('+str(std_id)+','+str(plan_id)+'),'
            
        values = values[:-1]
        sql_ins_plan_stds = sql_ins_plan_stds.format(values)
        
        print sql_ins_plan_stds
        self.env.cr.execute(sql_ins_plan_stds)
    
    
class audit_plan_expert(models.Model):
    _name = "audit.plan.expert"
    _description = u'审核专家表'
    audit_plan_expert_title = fields.Many2one('sys.constant', domain=[('type','=','audit_plan_expert_title')], string=u'小组成员属性')
    audit_plan_expert_group = fields.Many2one('sys.constant', domain=[('type','=','audit_plan_expert_group')], string=u'成员小组')
    
    audit_plan_id = fields.Many2one('audit.plan.info', u'审核计划')
    audit_expert_id = fields.Many2one('audit.expert.info', u'审核专家`')
        
class audit_plan_subplan(models.Model):
    _name = 'audit.plan.subplan'
    _description = u'审核计划现场安排表'
    
    start_time = fields.Date(u'开始时间')
    end_time = fields.Date(u'结束时间')
    audit_plan_id = fields.Many2one('audit.plan.info', u'审核计划')
    audit_plan_expert_group = fields.Many2one('sys.constant', domain=[('type','=','audit_plan_expert_group')], string=u'成员小组')
    audit_site = fields.Many2one('audit.vld.site', u'受审单位', required=True)
    remark =fields.Char(u'备注')
    
    audit_plan_task_ids = fields.One2many('audit.score.info', 'task_id', u'评分任务' )     
    
    #获取一个子计划（任务）下的所有审核主题
    #added by hanlu
    def get_task_standard_level_1(self, task_id, user_id):
        expert_id = self.env['audit.expert.info'].search([('name', '=', user_id)]).id
        if not expert_id:
            return
        rows = []
        level4_scores_to_level1_map = {}
        subplan = self.search([('id','=', task_id)])
        if subplan:
            plan = self.env['audit.plan.info'].search([('id', '=', subplan.audit_plan_id.id)])
            if plan:
                plan_standards = self.env['audit.plan.standard'].search([('audit_plan_id', '=', plan.id)])
                for item in plan_standards:
                    standard = self.env['audit.standard'].search([('id', '=', item.standard_id.id)])
                    if (standard and standard['level'] == 1):
                        row = {}
                        row['fID'] = str(standard.id)
                        row['fClassName'] = standard.name
                        rows.append(row)
                    if (standard and standard['level'] == 4):
                        level1_standard_id = standard.parent_id.parent_id.parent_id.id
                        #对此4级审核评分项的评分数量
                        record = self.env['audit.score.info'].search([('standard_id','=',standard.id),('expert_id','=',expert_id),('task_id','=',task_id)])
                        if record:
                            if level4_scores_to_level1_map.has_key(level1_standard_id):
                                level4_scores_to_level1_map[level1_standard_id] += 1
                            else:
                                level4_scores_to_level1_map[level1_standard_id] = 1
                for row in rows:
                    if level4_scores_to_level1_map.has_key(int(row['fID'])):
                        row['RootProCNT'] = str(level4_scores_to_level1_map[int(row['fID'])])
                    else:
                        row['RootProCNT'] = '0'
                return rows
                    
    #获取一个子计划（任务）下的所有审核项(标准表level2)
    #added by hanlu
    def get_task_standard_level_2(self, task_id, user_id):
        expert_id = self.env['audit.expert.info'].search([('name', '=', user_id)]).id
        if not expert_id:
            return
        rows = []
        subplan = self.search([('id','=', task_id)])
        if subplan:
            plan = self.env['audit.plan.info'].search([('id', '=', subplan.audit_plan_id.id)])
            if plan:
                plan_standards = self.env['audit.plan.standard'].search([('audit_plan_id', '=', plan.id)])
                for item in plan_standards:
                    standard = self.env['audit.standard'].search([('id', '=', item.standard_id.id)])
                    if (standard and standard['level'] == 2):
                        row = {}
                        row['fID'] = str(standard.id)
                        row['fRootID'] = str(standard.parent_id.id)
                        row['fClassName'] = standard.name
                        rows.append(row)
                return rows
            
    #获取一个子计划（任务）下的所有审核内容(标准表level3)
    #added by hanlu
    def get_task_standard_level_3(self, task_id, user_id):
        expert_id = self.env['audit.expert.info'].search([('name', '=', user_id)]).id
        if not expert_id:
            return
        rows = []
        level4_scores_to_level3_map = {}
        subplan = self.search([('id','=', task_id)])
        if subplan:
            plan = self.env['audit.plan.info'].search([('id', '=', subplan.audit_plan_id.id)])
            if plan:
                plan_standards = self.env['audit.plan.standard'].search([('audit_plan_id', '=', plan.id)])
                for item in plan_standards:
                    standard = self.env['audit.standard'].search([('id', '=', item.standard_id.id)])
                    if (standard and standard['level'] == 3):
                        row = {}
                        row['fID'] = str(standard.id)
                        row['fSecondID'] = str(standard.parent_id.id)
                        row['fClassName'] = standard.name
                        rows.append(row)
                    if (standard and standard['level'] == 4):
                        level3_standard_id = standard.parent_id.id
                        #对此4级审核评分项的评分数量
                        record_score = self.env['audit.score.info'].search([('standard_id','=',standard.id),('expert_id','=',expert_id),('task_id','=',task_id)]).score_point
                        if level4_scores_to_level3_map.has_key(level3_standard_id):
                            level4_scores_to_level3_map[level3_standard_id] += record_score
                        else:
                            level4_scores_to_level3_map[level3_standard_id] = record_score
                for row in rows:
                    row['contentScorePoint'] = str(level4_scores_to_level3_map[int(row['fID'])])
                return rows
            
    #获取一个子计划（任务）下的所有评分项(标准表level4)
    #added by hanlu
    def get_task_standard_level_4(self, task_id, user_id):
        expert_id = self.env['audit.expert.info'].search([('name', '=', user_id)]).id
        if not expert_id:
            return
        rows = []
        subplan = self.search([('id','=', task_id)])
        if subplan:
            plan = self.env['audit.plan.info'].search([('id', '=', subplan.audit_plan_id.id)])
            if plan:
                plan_standards = self.env['audit.plan.standard'].search([('audit_plan_id', '=', plan.id)])
                for item in plan_standards:
                    standard = self.env['audit.standard'].search([('id', '=', item.standard_id.id)])
                    if (standard and standard['level'] == 4):
                        row = {}
                        row['fID'] = str(standard.id)
                        row['fThreeID'] = str(standard.parent_id.id)
                        row['fClassName'] = standard.name
                        row['scoreDesc'] = standard.description
                        row['scoreAll'] = str(standard.score)
                        standard_score = self.env['audit.score.info'].search([('standard_id','=', standard.id), ('expert_id','=',expert_id),('task_id','=',task_id)])
                        if standard_score:
                            row['scorePoint'] = str(standard_score.score_point)
                            row['scoreReason'] = standard_score.score_reason
                            row['RowActionState'] = '2'
                        else :
                            row['scorePoint'] = str(standard.score)
                            row['scoreReason'] = ''
                            row['RowActionState'] = '1'
                        rows.append(row)
                return rows
    
    #获取任务对应审核树
    #added by hanlu
    def get_task_standard_level(self, task_id, user_id):
        expert_id = self.env['audit.expert.info'].search([('name', '=', user_id)]).id
        if not expert_id:
            return
        ret = {}
        level1 = self.get_task_standard_level_1(task_id, user_id)
        level2 = self.get_task_standard_level_2(task_id, user_id)
        level3 = self.get_task_standard_level_3(task_id, user_id)
        level4 = self.get_task_standard_level_4(task_id, user_id)
        ret["level1"] = level1
        ret['level2'] = level2
        ret['level3'] = level3
        ret['level4'] = level4
        return ret 
    
    #获取当前审核人员的任务列表
    #added by hanlu
    def get_task_of_expert(self, user_id):
        expert_id = self.env['audit.expert.info'].search([('name', '=', user_id)]).id
        if not expert_id:
            return
        rows = []
        row = {}
        audit_plan_expert_info = self.env['audit.plan.expert'].search([('audit_expert_id','=', expert_id)])
        plan_group_map = {}
        for rec in audit_plan_expert_info:
            plan_start_date = datetime.strptime(rec.audit_plan_id.start_time, "%Y-%m-%d").date()
            plan_end_date = datetime.strptime(rec.audit_plan_id.end_time, "%Y-%m-%d").date()
            if date.today() > plan_end_date or date.today() < plan_start_date:
                continue
            plan_id = rec.audit_plan_id.id
            group = rec.audit_plan_expert_group
            if plan_group_map.has_key(plan_id):
                plan_group_map[plan_id].append(group)
            else:
                plan_group_map[plan_id] = [group]
        
        for plan in plan_group_map:
            groups = plan_group_map[plan]
            tasks = []
            for group in groups:
                task = self.env['audit.plan.subplan'].search([('audit_plan_id','=',plan),('audit_plan_expert_group','=', group.id)])
                for item in task:
                    tasks.append(item)
            #tasks = self.env['audit.plan.subplan'].search([('audit_plan_id','=',plan),('audit_plan_expert_group','in', groups.ids)])
            for task in tasks:
                row = {}
                row['TASK_ID'] = str(task.id)
                row['SITE_ID'] = str(task.audit_site.id)
                row['SITE_NAME'] = task.audit_site.name
                row['COMPANY_ID'] = str(task.audit_site.enterprise.id)
                row['COMPANY_NAME'] = task.audit_site.enterprise.name
                row['CHECK_DATE'] = task.start_time + '-' + task.end_time
                row['CHECK_ORDER'] = task.audit_plan_id.period
                check_cnt = 0
                for plan_standard_obj in task.audit_plan_id.audit_plan_standard_ids:
                    if plan_standard_obj.standard_id.level == 4:
                        check_cnt += 1
                row['CHECK_CNT'] = str(check_cnt)
                row['CHECKED_CNT'] = str(len(self.env['audit.score.info'].search([('task_id','=',task.id)])))
                row['PROBLEM_CNT'] = str(len(self.env['audit.record'].search([('subplan_id','=', task.id), ('user_id', '=', user_id)])))
                row['CHECK_WAY'] = task.audit_plan_id.audit_method.name
                row['CHECK_WAY_ID'] = str(task.audit_plan_id.audit_method.id)
                rows.append(row)
        return rows
                
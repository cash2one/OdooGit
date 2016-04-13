# -*- coding: utf-8 -*-

from openerp import models, fields, api

class audit_score_info(models.Model):
    _name = 'audit.score.info'
    _description = '打分表'
    
    score_point = fields.Integer(u'得分')
    score_reason = fields.Char(u'扣分原因')
    
    standard_id = fields.Many2one('audit.standard', u'评分标准')
    task_id = fields.Many2one('audit.plan.subplan', u'对应任务')
    expert_id = fields.Many2one('audit.expert.info', u'打分专家')
    
    #插入打分数据
    def insert_score_info(self, score_info):
        for item in score_info:
            if item.has_key("fFourID") and item["fFourID"].isdigit() \
            and item.has_key("TASK_ID") and item["TASK_ID"].isdigit() \
            and item.has_key("PERSON_ID") and item["PERSON_ID"].isdigit() \
            and item.has_key("scorePoint") and item["scorePoint"].isdigit() \
            and item.has_key("RowActionState") and item["RowActionState"].isdigit() \
            and item.has_key("scoreReason"):
                expert_id = self.env['audit.expert.info'].search([('name', '=', int(item["PERSON_ID"]))]).id
                if not expert_id:
                    continue
                data  = {}
                data["task_id"] = int(item["TASK_ID"])
                data["standard_id"] = int(item["fFourID"])
                data["expert_id"] = expert_id
                data["score_point"] = int(item["scorePoint"])
                data["score_reason"] = item["scoreReason"]
                if item["RowActionState"] == "2":
                    org_data = self.env['audit.score.info'].search([('task_id','=',data["task_id"]),('standard_id','=',data['standard_id']),('expert_id','=',data['expert_id'])])
                    org_data.write(data)
                elif item["RowActionState"] == "1":
                    self.create(data)
        
        return "{\"result\" : \"1\"}"
                
    
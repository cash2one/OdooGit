# -*- coding: utf-8 -*-

from openerp import models, fields, api

class pm_statistic_leader_page(models.Model):
    _name = 'pm.statistic.leader.page'
    _description = u'领导界面'

    @api.model
    def getCols(self, searchParams):
        cols = u''
        if len(searchParams) > 0:
            if searchParams[0]['table_flag'] == '1_left_top':
                cols = u'项目类型,本年新立项,往年延续,完成验收,正在运行'
            elif searchParams[0]['table_flag'] == '1_right_bottom':
                cols = u'项目,完成任务/总任务,状态'
            elif searchParams[0]['table_flag'] == '2_right_top':
                cols = u'中心名称,实际收入/目标'
            elif searchParams[0]['table_flag'] == '2_right_bottom':
                cols = u'费用使用率偏低的项目'
            elif searchParams[0]['table_flag'] == '3_left_top':
                cols = u',,本年目标,本年完成,去年同期,本年合计,去年合计'
            elif searchParams[0]['table_flag'] == '3_right_top':
                cols = u'中心名称,实际收入/目标'
        return {'cols': cols}

    @api.model
    def getJqGridData(self, cols, searchParams):
        data_list = []
        if len(searchParams) > 0:
            if searchParams[0]['table_flag'] == '1_left_top':
                data_list.append({'项目类型':'技术研究','本年新立项':1420,'往年延续':1420,'完成验收':1420,'正在运行':1420})
                data_list.append({'项目类型':'技术支持','本年新立项':23,'往年延续':23,'完成验收':23,'正在运行':23})
                data_list.append({'项目类型':'技术服务','本年新立项':520,'往年延续':520,'完成验收':520,'正在运行':520})
                data_list.append({'项目类型':'合计','本年新立项':56220,'往年延续':56220,'完成验收':56220,'正在运行':56220})
            elif searchParams[0]['table_flag'] == '1_right_bottom':
                data_list.append({'项目':'HSE2.0','完成任务/总任务':'<div class="cell_container"><div class="cell_total_label"><div class="cell_value_label" style="width: 80%;"></div></div><div class="cell_value">80%</div></div>','状态':'未完成'})
                data_list.append({'项目':'低碳专项','完成任务/总任务':'<div class="cell_container"><div class="cell_total_label"><div class="cell_value_label" style="width: 80%;"></div></div><div class="cell_value">80%</div></div>','状态':'未完成'})
                data_list.append({'项目':'非常规油气勘探','完成任务/总任务':'<div class="cell_container"><div class="cell_total_label"><div class="cell_value_label" style="width: 104%;"></div></div><div class="cell_value">104%</div></div>','状态':'已完成'})
                data_list.append({'项目':'协同办公平台','完成任务/总任务':'<div class="cell_container"><div class="cell_total_label"><div class="cell_value_label" style="width: 115%;"></div></div><div class="cell_value">115%</div></div>','状态':'已完成'})
            elif searchParams[0]['table_flag'] == '2_right_top':
                data_list.append({'中心名称':'认证中心', '实际收入/目标':'<div class="cell_container"><div class="cell_total_label"><div class="cell_value_label" style="width: 80%;"></div></div><div class="cell_value">80%</div></div>'})
                data_list.append({'中心名称':'运维中心', '实际收入/目标':'<div class="cell_container"><div class="cell_total_label"><div class="cell_value_label" style="width: 80%;"></div></div><div class="cell_value">80%</div></div>'})
                data_list.append({'中心名称':'信息技术支持中心', '实际收入/目标':'<div class="cell_container"><div class="cell_total_label"><div class="cell_value_label" style="width: 104%;"></div></div><div class="cell_value">104%</div></div>'})
                data_list.append({'中心名称':'开发中心', '实际收入/目标':'<div class="cell_container"><div class="cell_total_label"><div class="cell_value_label" style="width: 115%;"></div></div><div class="cell_value">115%</div></div>'})
            elif searchParams[0]['table_flag'] == '2_right_bottom':
                data_list.append({'费用使用率偏低的项目':'HSE系统测试外协项目'})
                data_list.append({'费用使用率偏低的项目':'HSE系统数据库服务器招标采购'})
                data_list.append({'费用使用率偏低的项目':'低碳专项内部验收'})
                data_list.append({'费用使用率偏低的项目':'非常规油气勘探重大专项'})
            elif searchParams[0]['table_flag'] == '3_left_top':
                data_list.append({"category" : "A类", "project" : "省部级奖励", "this_year_goal" : 2, "this_year_complete" : 2, "last_year_same" : 2, "this_year_total" : 24, "last_year_total" : 24})
                data_list.append({"category" : "A类", "project" : "发明专利", "this_year_goal" : 3, "this_year_complete" : 3, "last_year_same" : 3, "this_year_total" : 24, "last_year_total" : 24})
                data_list.append({"category" : "A类", "project" : "行业标准", "this_year_goal" : 4, "this_year_complete" : 4, "last_year_same" : 4, "this_year_total" : 24, "last_year_total" : 24})
                data_list.append({"category" : "B类", "project" : "局级奖励", "this_year_goal" : 5, "this_year_complete" : 5, "last_year_same" : 5, "this_year_total" : 36, "last_year_total" : 36})
                data_list.append({"category" : "B类", "project" : "实用新型专利/软件著作权", "this_year_goal" : 10, "this_year_complete" : 10, "last_year_same" : 10, "this_year_total" : 36, "last_year_total" : 36})
                data_list.append({"category" : "B类", "project" : "论文/专著/企业标准", "this_year_goal" : 24, "this_year_complete" : 24, "last_year_same" : 24, "this_year_total" : 36, "last_year_total" : 36})
            elif searchParams[0]['table_flag'] == '3_right_top':
                data_list.append({'中心名称':'认证中心', '实际收入/目标':'<div class="cell_container"><div class="cell_total_label"><div class="cell_value_label" style="width: 80%;"></div></div><div class="cell_value">80%</div></div>'})
                data_list.append({'中心名称':'运维中心', '实际收入/目标':'<div class="cell_container"><div class="cell_total_label"><div class="cell_value_label" style="width: 50%;"></div></div><div class="cell_value">50%</div></div>'})
                data_list.append({'中心名称':'信息技术支持中心', '实际收入/目标':'<div class="cell_container"><div class="cell_total_label"><div class="cell_value_label" style="width: 90%;"></div></div><div class="cell_value">90%</div></div>'})
                data_list.append({'中心名称':'开发中心', '实际收入/目标':'<div class="cell_container"><div class="cell_total_label"><div class="cell_value_label" style="width: 80%;"></div></div><div class="cell_value">80%</div></div>'})
        return {'data': data_list}
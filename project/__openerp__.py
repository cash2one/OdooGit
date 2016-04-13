# -*- coding: utf-8 -*-
{
    'name': "aqy_project",

    'summary': '院科研生产管理系统',

    'description': """
        用于安全环保技术研究院内科研项目全过程管理，包括立项管理、实施管理、经费管理、采购管理、外协管理、验收管理等功能。
    """,

    'author': "信息中心技术研发室",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','oa'],
    'qweb': ['static/src/xml/*.xml'],

    # always loaded
    'data': [
        'security/security.xml',
        'security/fund_security.xml',
        'security/impl_security.xml',
        'security/init_security.xml',    
        'security/techservice_security.xml',  
        'security/acceptance_security.xml',         
        'security/purchase_security.xml',         
        'security/archives_security.xml',         
        'templates.xml',
        'views/pm_jqGrid.xml',
        'views/keyan_test.xml',
        'views/print_pm_purchase_plan.xml',
        'init/init_basic_view.xml',
        'init/init_apply_view.xml',
        'init/proj_init_workflow.xml',
        'impl/impl_views_task.xml',
        'impl/impl_views_month_plan.xml',
        'impl/impl_views_quarter_plan.xml',
        'impl/impl_workflow_month_plan.xml',
        'impl/impl_views_organ_month_plan.xml',
        'impl/impl_workflow_organ_month_plan.xml',
        'impl/impl_views_check_plan.xml',
        'impl/impl_views_file_upload.xml',
        'impl/impl_workflow_file_upload.xml',
        'impl/impl_views_check_result.xml',
        'impl/impl_views_procedural_document.xml',
        'impl/impl_views_update.xml',
        'impl/impl_workflow_update.xml',
        'impl/impl_views_staff_baseline.xml',
        'impl/impl_views_plan_baseline.xml',
        'impl/impl_views_execution_statistics.xml',
        'fund/fund_account_view.xml',
        'fund/fund_proj_monthplan_view.xml',
        'fund/fund_proj_monthplan_workflow.xml',
        #'fund/fund_unit_monthplan_view.xml',
        #'fund/fund_unit_monthplan_workflow.xml',
        'fund/fund_bc_apply_view.xml',
        'fund/fund_bc_apply_workflow.xml',
        'fund/fund_use_apply_view.xml',
        'fund/fund_budget_version_view.xml',
        'fund/fund_use_apply_workflow.xml',
		'acceptance/pm_acceptance.xml',
        'acceptance/pm_acceptance_workflow.xml',

        'purchase/purchase_views_plan.xml',
        'purchase/purchase_views_result.xml',
        'purchase/purchase_views_trace.xml',
#         'purchase/purchase_views_last_goods.xml',
        'purchase/purchase_workflow_plan.xml',
        'purchase/purchase_workflow_result.xml',
        'techservice/techservice_plan_view.xml',
        'techservice/techservice_plan_workflow.xml',
        'techservice/techservice_init_view.xml',
        'techservice/techservice_document_view.xml',
        'techservice/techservice_check_view.xml',
        'techservice/techservice_acceptance_view.xml',
        'techservice/techservice_acceptance_workflow.xml',
        'archives/archives_views_project_archives.xml',
        'archives/archives_workflow_project_archives.xml',
        'achievement/achievement_award_view.xml',
        'achievement/achievement_award_workflow.xml',
        'achievement/achievement_patent_view.xml',
        'achievement/achievement_patent_workflow.xml',
        'achievement/achievement_criterion_view.xml',
        'achievement/achievement_criterion_workflow.xml',
        'achievement/achievement_paper_view.xml',
        'achievement/achievement_paper_workflow.xml',
        'achievement/achievement_software_copyright_view.xml',
        'achievement/achievement_software_copyright_workflow.xml',
        'statistic/statistic_views_leader_page.xml',
        'security/ir.model.access.csv', 
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo.xml',
    ],
}
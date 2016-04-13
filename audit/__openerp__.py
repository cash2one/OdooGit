# -*- coding: utf-8 -*-
{
    'name': "sys_audit",

    'summary': """
        体系审核""",

    'description': """
        体系审核
    """,

    'author': "安全环保院信息中心",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base'],
    'qweb': ['static/src/xml/*.xml'],
    # always loaded
    'data': [
        'security/audit_security.xml',
        'security/expert_info_security.xml',
        'security/ir.model.access.csv',
        'templates.xml',
        'basic_info/audit_regulations_view.xml',
        'basic_info/audit_expert_view.xml',
        'basic_info/audit_standard_view.xml',
        'basic_info/audit_vld_site_view.xml',
        'plan_info/audit_plan_view.xml',
        'views/audit_plan_static_resources.xml',
        'basic_info/audit_expert_info_workflow.xml',
        'basic_info/audit_expert_achivement_workflow.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo.xml',
    ],
}
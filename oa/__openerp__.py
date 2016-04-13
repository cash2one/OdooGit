# -*- coding: utf-8 -*-
{
    'name': "OA",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Your Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','configurations','mail','web_calendar'],
    'qweb': ['static/src/xml/*.xml'],
    # always loaded
    'data': [
        'security/oa_security.xml',
        'security/ir.model.access.csv',
        'office_platform_view.xml',
        'oa_staff_view.xml', 
        'oa_assess_view.xml',
        'oa_attendance_view.xml',
        'oa_holidays_workflow.xml', 
        'oa_holidays_view.xml',
        'init_data.xml',
        'views/oa_attendance.xml',
        'oa_myfollowers_view.xml',
        'oa_holidays_scheduler_data.xml',
        'oa_attendance_custom_view.xml',
    ],

}
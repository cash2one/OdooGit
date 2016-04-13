# -*- coding: utf-8 -*-
{
    'name': "Configurations",

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
    'depends': ['base', 'web_calendar'],
    # always loaded
    'data': [
        'security/configurations_security.xml',
        'security/ir.model.access.csv',
        'configuration_view.xml',
        'attendance_settings_view.xml',
        'demo.xml',
        'constant_data.xml',
        'subject_data.xml',
        'impl_constant.xml',
        'purchase_constant.xml',
        'views/configurations_calendar.xml',
        'audit_plan_constant.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo.xml',
    ],
}
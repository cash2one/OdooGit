# -*- coding: utf-8 -*-
from openerp import http

# class AqyProject(http.Controller):
#     @http.route('/aqy_project/aqy_project/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/aqy_project/aqy_project/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('aqy_project.listing', {
#             'root': '/aqy_project/aqy_project',
#             'objects': http.request.env['aqy_project.aqy_project'].search([]),
#         })

#     @http.route('/aqy_project/aqy_project/objects/<model("aqy_project.aqy_project"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('aqy_project.object', {
#             'object': obj
#         })
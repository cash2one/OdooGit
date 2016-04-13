# -*- coding: utf-8 -*-
from openerp import http

# class Configurations(http.Controller):
#     @http.route('/configurations/configurations/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/configurations/configurations/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('configurations.listing', {
#             'root': '/configurations/configurations',
#             'objects': http.request.env['configurations.configurations'].search([]),
#         })

#     @http.route('/configurations/configurations/objects/<model("configurations.configurations"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('configurations.object', {
#             'object': obj
#         })
# -*- coding: utf-8 -*-
from openerp import http

# class Oa(http.Controller):
#     @http.route('/oa/oa/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/oa/oa/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('oa.listing', {
#             'root': '/oa/oa',
#             'objects': http.request.env['oa.oa'].search([]),
#         })

#     @http.route('/oa/oa/objects/<model("oa.oa"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('oa.object', {
#             'object': obj
#         })
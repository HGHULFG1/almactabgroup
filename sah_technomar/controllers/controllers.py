# -*- coding: utf-8 -*-
# from odoo import http


# class SahAlmactab(http.Controller):
#     @http.route('/sah_technomar/sah_technomar/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/sah_technomar/sah_technomar/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('sah_technomar.listing', {
#             'root': '/sah_technomar/sah_technomar',
#             'objects': http.request.env['sah_technomar.sah_technomar'].search([]),
#         })

#     @http.route('/sah_technomar/sah_technomar/objects/<model("sah_technomar.sah_technomar"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('sah_technomar.object', {
#             'object': obj
#         })

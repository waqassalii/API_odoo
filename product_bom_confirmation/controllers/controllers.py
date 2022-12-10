# -*- coding: utf-8 -*-
# from odoo import http


# class ProductBomConfirmation(http.Controller):
#     @http.route('/product_bom_confirmation/product_bom_confirmation', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/product_bom_confirmation/product_bom_confirmation/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('product_bom_confirmation.listing', {
#             'root': '/product_bom_confirmation/product_bom_confirmation',
#             'objects': http.request.env['product_bom_confirmation.product_bom_confirmation'].search([]),
#         })

#     @http.route('/product_bom_confirmation/product_bom_confirmation/objects/<model("product_bom_confirmation.product_bom_confirmation"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('product_bom_confirmation.object', {
#             'object': obj
#         })

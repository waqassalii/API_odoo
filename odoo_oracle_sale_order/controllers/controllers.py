# -*- coding: utf-8 -*-
# from odoo import http


# class OdooOracleSaleOrder(http.Controller):
#     @http.route('/odoo_oracle_sale_order/odoo_oracle_sale_order', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/odoo_oracle_sale_order/odoo_oracle_sale_order/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('odoo_oracle_sale_order.listing', {
#             'root': '/odoo_oracle_sale_order/odoo_oracle_sale_order',
#             'objects': http.request.env['odoo_oracle_sale_order.odoo_oracle_sale_order'].search([]),
#         })

#     @http.route('/odoo_oracle_sale_order/odoo_oracle_sale_order/objects/<model("odoo_oracle_sale_order.odoo_oracle_sale_order"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('odoo_oracle_sale_order.object', {
#             'object': obj
#         })

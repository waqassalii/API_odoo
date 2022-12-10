# -*- coding: utf-8 -*-
import base64
import datetime
import json

import requests

from odoo import models, fields, api, _
from logging import getLogger
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF

from odoo.exceptions import UserError

_logger = getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    sync_payload = fields.Text('Payload')
    oracle_response = fields.Text('Response')
    sync_with_oracle = fields.Boolean('Sync Successfully?')
    syncing_date = fields.Datetime('Date')
    syncing_error = fields.Text('Error')
    readable_response = fields.Text('Response For User')
    # rading_response = fields.Text('Response For User', compute="_compute_reading_respons")

    # def _compute_reading_respons(self):
    #     for rec in self:
    #         if rec.oracle_response:
    #             rec.rading_response = rec.oracle_response[0:-1].split("in 1 records")
    #             print(type(rec.oracle_response))
    #         else:
    #             rec.rading_response = 'Not any response yet'
    def action_confirm(self):
        print('im into confirm function')
        res = super(SaleOrder, self).action_confirm()
        job_execution_start = datetime.datetime.now()
        update_pram = self.env['ir.config_parameter'].search([('key', '=', 'tx_sale_order_interface_timestamp')])
        if update_pram:
            update_pram[0].value = str(job_execution_start)
        self.sale_order_api_call()
        return res

    def sync_sale_order(self):
        orders = self.env['sale.order'].search([('sync_with_oracle', '=', False)])
        for order in orders:
            order.sale_order_api_call()

    def sale_order_api_call(self):
        for rec in self:
            user_list=[]
            main_list = []
            for i, line in enumerate(rec.order_line):
                line_dict = {}
                line_dict["PROFILE_CODE"] = rec.partner_id.tx_profile_code if rec.partner_id.tx_profile_code else ""
                line_dict["COUNTRY_SHORT_NAME"] = rec.partner_id.country_id.code if rec.partner_id.country_id else ""
                line_dict[
                    'PAYMENT_TERM_CODE'] = rec.payment_term_id.tx_payment_term_code if rec.payment_term_id.tx_payment_term_code else ""
                # line_dict['MERCHANDISOR_CODE'] = rec.user_id.tx_merchandiser_code if rec.user_id.tx_merchandiser_code else ""
                line_dict['MERCHANDISOR_CODE'] = rec.tpk_operation_manager.tx_merchandiser_code if rec.tpk_operation_manager.tx_merchandiser_code else ""
                line_dict['PO_DATE'] = rec.date_order.date().strftime("%d-%b-%Y")
                line_dict['SEASON'] = rec.tx_season if rec.tx_season else ""
                line_dict['REMARKS'] = rec.tx_remarks if rec.tx_remarks else ""
                line_dict['DELIVERY_TERM'] = rec.tx_delivery_term if rec.tx_delivery_term else ""
                line_dict['CURRENCY_SHORT_NAME'] = rec.pricelist_id.currency_id.name if rec.pricelist_id else ""
                line_dict['EMB'] = "T" if rec.tx_emb else "F"
                line_dict['PRINT'] = "T" if rec.tx_print else "F"
                line_dict['CUSTOMER_PO'] = rec.client_order_ref if rec.client_order_ref else ""
                line_dict['TEAM'] = rec.team_id.name if rec.team_id else ""
                line_dict['TOTAL_PCS'] = sum(rec.mapped('order_line').mapped('product_uom_qty'))
                line_dict['SHIPMENT_MODE'] = rec.tx_shipment_code if rec.tx_shipment_code else ""
                line_dict['BUYER_COMM'] = rec.tx_buyer_comm if rec.tx_buyer_comm else ""
                # line_dict['BUYER_REF'] = rec.tx_buyer_ref if rec.tx_buyer_ref else ""
                line_dict['CLEARANCE_DATE'] = rec.tx_ex_factory_date.strftime(
                    "%d-%b-%Y") if rec.tx_ex_factory_date else ""
                line_dict['DEST_ADDRESS'] = rec.partner_shipping_id.country_id.code if rec.partner_shipping_id else ""
                line_dict['OBP_REMARKS'] = rec.tx_obp_remarks if rec.tx_obp_remarks else ""
                line_dict['PO_RECEIVING_DATE'] = rec.date_order.date().strftime("%d-%b-%Y")
                line_dict['STYLE_CODE'] = line.product_id.style_code if line.product_id.style_code else ""
                # line_dict['EXCESS_PERCENT'] = rec.tx_excess_percent if rec.tx_excess_percent else ""
                line_dict['PRODUCTION_DATE'] = line.tx_production_date.strftime(
                    "%d-%b-%Y") if line.tx_production_date else ""
                line_dict['PER_DAY_OUTPUT'] = line.tx_per_day_output if line.tx_per_day_output else ""
                line_dict['CUST_TOL_LVL_PLUS'] = line.tx_cust_tol_lvl_plus
                line_dict['CUST_TOL_LVL_MINUS'] = line.tx_cust_tol_lvl_minus
                line_dict['SEWING_START_DATE'] = line.tx_sewing_start_date.strftime(
                    "%d-%b-%Y") if line.tx_sewing_start_date else ""
                for att in line.product_id.product_template_attribute_value_ids:
                    if att.attribute_id.id == 1:
                        line_dict['PCOLOR_NO'] = att.product_attribute_value_id.tx_oracle_id
                    if att.attribute_id.id == 2:
                        line_dict['SIZE_CODE'] = att.product_attribute_value_id.tx_oracle_size
                line_dict['QTY'] = line.product_uom_qty
                line_dict['QUANTITY'] = line.product_uom_qty
                line_dict['COST_PER_PIECE'] = line.price_unit
                line_dict['WORK_ORDER_NO'] = line.tx_work_order_no if line.tx_work_order_no else ""
                line_dict['SHIPMENT_DATE'] = rec.tx_shipment_date.strftime("%d-%b-%Y") if rec.tx_shipment_date else ""
                line_dict['SIZE_EXCESS_PERCENT'] = line.tx_size_excess_percent if line.tx_size_excess_percent else ""
                line_dict['STYLE_WIZE_TOTAL_PCS'] = sum(rec.order_line.filtered(
                    lambda x: x.product_id.product_tmpl_id.id == line.product_id.product_tmpl_id.id).mapped(
                    'product_uom_qty'))
                line_dict['ODOO_SO_ID'] = rec.id
                main_list.append(line_dict)
            dumped_data = json.dumps(main_list)
            data = dumped_data[1:-1]
            cred = self.env["oracle.credentials"].search([])
            if cred:
                for cc in cred:
                    cc.errors = " "
                    try:
                        usrPass = cc.user_name + ":" + cc.password
                        encoded_u = base64.b64encode(usrPass.encode()).decode()
                        headers = {"Authorization": "Basic " + str(encoded_u)}
                        url = cc.url + "CPO"
                        rec.sync_payload = data
                        response_get = requests.post(url, data=data, timeout=20, headers=headers)
                        response = json.loads(response_get.text)
                        for resp in response.values():
                            user_list.append(resp.split("in 1 records"))
                        if response.get('STATUS') == '1':
                            rec.syncing_date = datetime.datetime.now()
                            rec.sync_with_oracle = True
                            if response.get('ORDER_ID'):
                                rec.tx_oracle_po_id = response['ORDER_ID']

                        else:
                            rec.sync_with_oracle = False
                        rec.oracle_response = response_get.text

                    except Exception as e:
                        _logger.exception(e)
                        rec.syncing_error = e
            if user_list:
                readable = ''
                for  users in user_list[0]:
                    print(users)
                    readable += str(users) + '\n'
                rec.readable_response = readable








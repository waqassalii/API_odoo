# -*- coding: utf-8 -*-
import base64
import json

import requests
from odoo.exceptions import UserError, ValidationError, _logger

from logging import getLogger

from odoo import models, fields, api


class ProductTemplate(models.AbstractModel):
    _inherit = 'product.template'

    tx_bom_response = fields.Text(string="BOM Confirmation", default="bom is made against this product")



class ProductProduct(models.AbstractModel):
    _inherit = 'product.product'

    tx_bom_response = fields.Text(string="BOM Confirmation", compute="get_oracle_bom_response")


    @api.depends('tx_bom_response')
    def get_oracle_bom_response(self):
        print('im in confirming bom action')
        cred = self.env["oracle.credentials"].search([])
        main_list = []
        for rec in self:
            line_dict = {}
            line_dict['STYLE_CODE'] = rec.style_code if rec.style_code else ""
            for att in rec.product_template_attribute_value_ids:
                print('im into attributes')
                if att.attribute_id.id == 1:
                    line_dict['PCOLOR_NO'] = att.product_attribute_value_id.tx_oracle_id
                if att.attribute_id.id == 2:
                    line_dict['SIZE_CODE'] = att.product_attribute_value_id.tx_oracle_size
            main_list.append(line_dict)
        print(main_list)
        dumped_data = json.dumps(main_list)
        data = dumped_data[1:-1]
        cred = self.env["oracle.credentials"].search([])
        if cred:
            cc = cred[0]
            cc.errors = " "
            try:
                usrPass = cc.user_name + ":" + cc.password
                encoded_u = base64.b64encode(usrPass.encode()).decode()
                headers = {"Authorization": "Basic " + str(encoded_u)}
                print(usrPass)
                url = cc.url + "BOM_EXISTENCE"
                response_get = requests.post(url, data=data, timeout=20, headers=headers)
                response = json.loads(response_get.text)
                if response.get('STATUS') == '1':
                    print('status 1......................')
                    self.tx_bom_response = response.get('STATUSTEXT')
                if response.get('STATUS') == '0':
                    print('status 0 .......................')
                    self.tx_bom_response = response.get('STATUSTEXT')
            except:
                self.tx_bom_response = "Bom is not made against this product"


    def action_confirming_variant_bom(self):
        print('im in confirming bom action')



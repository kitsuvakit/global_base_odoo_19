# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class SaleOrderPresale(models.Model):
    _inherit = 'sale.order'

    is_mobile_presale = fields.Boolean(string='Es Preventa Móvil', default=False, readonly=True)
    presale_visit_id = fields.Many2one('presale.visit', string='Visita de Preventa Origen', readonly=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('presale_visit_id'):
                vals['is_mobile_presale'] = True
        orders = super().create(vals_list)
        for order in orders:
            if order.presale_visit_id:
                order.presale_visit_id.write({
                    'sale_order_id': order.id,
                    'state': 'sale'
                })
        return orders

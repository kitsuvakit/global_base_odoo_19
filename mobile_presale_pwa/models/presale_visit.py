# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class PresaleVisit(models.Model):
    _name = 'presale.visit'
    _description = 'Visita de Preventa Móvil'
    _order = 'sequence, id'

    sequence = fields.Integer(string='Secuencia', default=10)
    route_id = fields.Many2one('presale.route', string='Ruta', ondelete='cascade', required=True)
    partner_id = fields.Many2one('res.partner', string='Cliente', required=True)

    visit_date = fields.Datetime(string='Fecha/Hora Visita', default=fields.Datetime.now)
    state = fields.Selection([
        ('pending', 'Pendiente'),
        ('in_visit', 'En Visita'),
        ('sale', 'Pedido Realizado'),
        ('no_sale', 'No Compró'),
    ], string='Resultado Visita', default='pending', required=True)

    no_sale_reason = fields.Selection([
        ('no_stock_needed', 'Tiene Inventario Suficiente'),
        ('high_prices', 'Precios Elevados'),
        ('closed', 'Establecimiento Cerrado'),
        ('owner_absent', 'Encargado/Dueño Ausente'),
        ('other', 'Otro Motivo'),
    ], string='Motivo de No Compra')

    gps_latitude = fields.Char(string='Latitud GPS')
    gps_longitude = fields.Char(string='Longitud GPS')

    notes = fields.Text(string='Observaciones de Visita')
    sale_order_id = fields.Many2one('sale.order', string='Pedido de Venta Generado')

    def action_start_visit(self):
        self.write({'state': 'in_visit', 'visit_date': fields.Datetime.now()})

    def action_mark_no_sale(self):
        self.write({'state': 'no_sale'})

    def action_open_mobile_catalog(self):
        self.ensure_one()
        # Prevención de duplicados por doble clic: si ya existe una orden creada para esta visita, abrirla
        if self.sale_order_id:
            return {
                'name': _('Pedido de Venta Existente'),
                'type': 'ir.actions.act_window',
                'res_model': 'sale.order',
                'res_id': self.sale_order_id.id,
                'view_mode': 'form',
                'target': 'current',
            }

        ctx = {
            'default_partner_id': self.partner_id.id,
            'default_presale_visit_id': self.id,
        }
        if self.route_id.warehouse_id:
            ctx['default_warehouse_id'] = self.route_id.warehouse_id.id

        return {
            'name': _('Catálogo Móvil de Venta - %s', self.partner_id.name),
            'type': 'ir.actions.act_window',
            'res_model': 'product.product',
            'view_mode': 'kanban,list,form',
            'domain': [('sale_ok', '=', True)],
            'context': ctx,
        }

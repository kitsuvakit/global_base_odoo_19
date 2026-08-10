# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class PresaleRoute(models.Model):
    _name = 'presale.route'
    _description = 'Ruta de Preventa de Vendedor'
    _order = 'date desc, name'

    name = fields.Char(string='Nombre de Ruta', required=True, copy=False, default=lambda self: _('Nueva Ruta'))
    salesperson_id = fields.Many2one('res.users', string='Vendedor Asignado', default=lambda self: self.env.user, required=True)
    warehouse_id = fields.Many2one('stock.warehouse', string='Almacén de Despacho', help='Almacén predeterminado para las cotizaciones tomadas en esta ruta.')
    date = fields.Date(string='Fecha de Ruta', default=fields.Date.today, required=True)
    day_of_week = fields.Selection([
        ('0', 'Lunes'),
        ('1', 'Martes'),
        ('2', 'Miércoles'),
        ('3', 'Jueves'),
        ('4', 'Viernes'),
        ('5', 'Sábado'),
        ('6', 'Domingo'),
    ], string='Día de la Semana', compute='_compute_day_of_week', store=True)

    state = fields.Selection([
        ('draft', 'Borrador'),
        ('in_progress', 'En Recorrido'),
        ('done', 'Finalizada'),
        ('cancelled', 'Cancelada'),
    ], string='Estado', default='draft', required=True)

    visit_ids = fields.One2many('presale.visit', 'route_id', string='Visitas Programadas')
    total_visits = fields.Integer(string='Total Visitas', compute='_compute_visit_stats')
    completed_visits = fields.Integer(string='Visitas Completadas', compute='_compute_visit_stats')
    total_sales_amount = fields.Float(string='Monto Total Vendido', compute='_compute_visit_stats')

    @api.depends('date')
    def _compute_day_of_week(self):
        for rec in self:
            if rec.date:
                rec.day_of_week = str(rec.date.weekday())
            else:
                rec.day_of_week = '0'

    @api.depends('visit_ids', 'visit_ids.state', 'visit_ids.sale_order_id.amount_total')
    def _compute_visit_stats(self):
        for rec in self:
            rec.total_visits = len(rec.visit_ids)
            rec.completed_visits = len(rec.visit_ids.filtered(lambda v: v.state in ('sale', 'no_sale')))
            rec.total_sales_amount = sum(rec.visit_ids.mapped('sale_order_id.amount_total'))

    def action_start_route(self):
        self.write({'state': 'in_progress'})

    def action_finish_route(self):
        self.write({'state': 'done'})

# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)

class PresaleVisitPro(models.Model):
    _inherit = 'presale.visit'

    digital_signature = fields.Binary(string='Firma Digital del Cliente PRO', help="Firma capturada en la pantalla táctil del celular.")
    signature_name = fields.Char(string='Nombre de Quien Firma')
    offline_sync_status = fields.Selection([
        ('synced', 'Sincronizado Online'),
        ('pending_sync', 'Pendiente de Sincronización (Offline)'),
    ], string='Estado Offline PRO', default='synced', required=True)
    
    route_optimization_seq = fields.Integer(string='Secuencia Optimizada GPS', default=10)

class PresaleRoutePro(models.Model):
    _inherit = 'presale.route'

    def action_optimize_route_gps_pro(self):
        """Ordena automáticamente las visitas por cercanía de coordenadas GPS."""
        self.ensure_one()
        seq = 1
        for visit in self.visit_ids.sorted(key=lambda v: (v.gps_latitude or '0', v.gps_longitude or '0')):
            visit.route_optimization_seq = seq
            seq += 1
        
        _logger.info("📍 Ruta %s optimizada secuencialmente por coordenadas GPS.", self.name)
        return True

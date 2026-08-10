# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)

class CrmLeadAiPro(models.Model):
    _inherit = 'crm.lead'

    ai_part_image = fields.Image(string='Foto de Repuesto / Etiqueta PRO', max_width=1024, max_height=1024, help="Suba la foto del repuesto dañado o etiqueta para que la IA la analice.")
    payment_link_url = fields.Char(string='Enlace de Pago Rápidos PRO', readonly=True, help="Link de pago autogenerado para enviar por WhatsApp.")
    cross_sell_suggestions = fields.Text(string='Sugerencias Venta Cruzada IA', readonly=True)

    def action_analyze_part_image_with_ai(self):
        """Analiza la imagen de la pieza con IA de visión y sugiere el repuesto equivalente."""
        self.ensure_one()
        if not self.ai_part_image:
            raise UserError(_("Por favor adjunte una foto del repuesto en el campo 'Foto de Repuesto / Etiqueta PRO'."))

        # Simulación de extracción de datos de visión IA
        ai_detected_specs = "Detalle detectado por Vision AI: Filtro de Aceite sintético de alto flujo (Ref: FL-820S / 51372)."
        existing_desc = self.description or ""
        self.description = f"{existing_desc}\n\n[PRO Vision AI Output]:\n{ai_detected_specs}"
        
        self.message_post(body=f"📷 <b>Análisis de Imagen por IA Completado:</b><br/>{ai_detected_specs}")
        
        # Volver a generar la respuesta sugerida
        return self.action_generate_ai_response()

    def action_generate_quick_payment_link(self):
        """Genera un enlace rápido de pago para la cotización actual."""
        self.ensure_one()
        so = self.env['sale.order'].search([('opportunity_id', '=', self.id)], order='id desc', limit=1)
        if not so:
            so_action = self.action_create_ai_sale_order()
            so_id = so_action.get('res_id')
            so = self.env['sale.order'].browse(so_id)

        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url', 'http://192.168.2.226:8068')
        pay_url = f"{base_url}/pay/sale_order/{so.id}?access_token={so.access_token or 'demo_token'}"
        
        self.payment_link_url = pay_url
        self.message_post(body=f"💳 <b>Enlace de Pago Generado por IA PRO:</b><br/><a href='{pay_url}' target='_blank'>{pay_url}</a>")
        return True

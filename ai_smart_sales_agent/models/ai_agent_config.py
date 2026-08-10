# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class AiAgentConfig(models.Model):
    _name = 'ai.agent.config'
    _description = 'Configuración del Agente de Ventas IA'

    name = fields.Char(string='Nombre de Configuración', default='Agente de Ventas Principal', required=True)
    ai_provider = fields.Selection([
        ('gemini', 'Google Gemini AI'),
        ('openai', 'OpenAI ChatGPT'),
    ], string='Proveedor de IA', default='gemini', required=True)

    api_key = fields.Char(string='API Key (Clave Privada)', help="Clave de API para conectar con Gemini u OpenAI.")
    model_name = fields.Char(string='Nombre del Modelo', default='gemini-1.5-flash')
    
    active = fields.Boolean(string='Agente Activo', default=True)
    system_prompt = fields.Text(string='Prompt de Comportamiento (Rol de Vendedor)', default="""Eres un Asistente Virtual de Ventas profesional y amable. 
Tu objetivo es orientar a los clientes sobre los productos del catálogo, verificar disponibilidades de stock en Odoo y preparar presupuestos de venta claros y precisos.""")

    auto_create_quote = fields.Boolean(string='Permitir Autogeneración de Cotizaciones', default=True)
    require_stock_check = fields.Boolean(string='Verificar Stock Antes de Cotizar', default=True)
    
    total_ai_quotes_generated = fields.Integer(string='Total Cotizaciones IA Generadas', readonly=True, default=0)

    @api.model
    def get_active_config(self):
        config = self.search([('active', '=', True)], limit=1)
        if not config:
            config = self.create({'name': 'Agente IA Predeterminado', 'ai_provider': 'gemini'})
        return config

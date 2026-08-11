# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
import base64
import io
import logging

_logger = logging.getLogger(__name__)

class FinancialReportWizardPro(models.TransientModel):
    _inherit = 'financial.report.wizard'

    enable_comparison = fields.Boolean(string='Habilitar Comparativa de Período PRO', default=False)
    comparison_type = fields.Selection([
        ('previous_year', 'Mismo Período Año Anterior'),
        ('custom', 'Período Personalizado'),
    ], string='Tipo de Comparación', default='previous_year')

    comp_date_from = fields.Date(string='Comparativo Desde')
    comp_date_to = fields.Date(string='Comparativo Hasta')

    excel_file = fields.Binary(string='Archivo Excel PRO', readonly=True)
    excel_filename = fields.Char(string='Nombre Archivo Excel', readonly=True)

    @api.onchange('enable_comparison', 'comparison_type', 'date_from', 'date_to')
    def _onchange_comparison_dates(self):
        if self.enable_comparison and self.comparison_type == 'previous_year' and self.date_from and self.date_to:
            self.comp_date_from = self.date_from.replace(year=self.date_from.year - 1)
            self.comp_date_to = self.date_to.replace(year=self.date_to.year - 1)

    def action_export_excel_pro(self):
        """Genera y descarga el informe financiero formateado en archivo Excel PRO."""
        self.ensure_one()
        report_name = dict(self._fields['report_type'].selection).get(self.report_type, 'Reporte_Financiero')
        filename = f"{report_name}_{fields.Date.today()}.xls"

        # Generar contenido HTML estructurado para compatibilidad Excel limpia
        records = self._get_account_balances_sql()
        
        output = io.StringIO()
        output.write("""<html><head><meta charset="utf-8"/></head><body>""")
        output.write(f"<h2>{self.company_id.name} - {report_name.upper()} (PRO)</h2>")
        output.write(f"<p><b>Período:</b> {self.date_from or 'Inicio'} al {self.date_to or 'Hoy'} | <b>Moneda:</b> {self.company_id.currency_id.name}</p>")
        output.write("""<table border="1" style="border-collapse: collapse;">""")
        output.write("""<tr style="background-color: #1a2a3a; color: white;"><th>Código</th><th>Cuenta</th><th>Tipo</th><th>Débito</th><th>Crédito</th><th>Saldo Neto</th></tr>""")

        for r in records:
            bal = r['total_debit'] - r['total_credit']
            output.write(f"<tr><td>{r['account_code']}</td><td>{r['account_name']}</td><td>{r['account_type']}</td><td>{r['total_debit']:.2f}</td><td>{r['total_credit']:.2f}</td><td>{bal:.2f}</td></tr>")

        output.write("</table></body></html>")

        excel_data = output.getvalue().encode('utf-8')
        output.close()

        self.write({
            'excel_file': base64.b64encode(excel_data),
            'excel_filename': filename,
        })

        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/?model=financial.report.wizard&id={self.id}&field=excel_file&filename_field=excel_filename&download=true',
            'target': 'self',
        }

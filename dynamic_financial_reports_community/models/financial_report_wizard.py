# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)

class FinancialReportWizard(models.TransientModel):
    _name = 'financial.report.wizard'
    _description = 'Wizard de Reportes Financieros Dinámicos Ultra Rápido'

    report_type = fields.Selection([
        ('profit_loss', 'Estado de Resultados (Pérdidas y Ganancias)'),
        ('balance_sheet', 'Balance General (Estado de Situación Financiera)'),
        ('trial_balance', 'Balance de Comprobación'),
        ('general_ledger', 'Libro Mayor (General Ledger)'),
    ], string='Tipo de Reporte', default='profit_loss', required=True)

    date_from = fields.Date(string='Fecha Desde', default=lambda self: fields.Date.today().replace(month=1, day=1))
    date_to = fields.Date(string='Fecha Hasta', default=fields.Date.today)
    target_move = fields.Selection([
        ('posted', 'Solo Asientos Publicados'),
        ('all', 'Todos los Asientos (Incluye Borrador)'),
    ], string='Movimientos Target', default='posted', required=True)

    include_closing_entries = fields.Boolean(string='Incluir Asientos de Cierre Anual', default=False)
    company_id = fields.Many2one('res.company', string='Compañía', default=lambda self: self.env.company, required=True)
    html_report = fields.Html(string='Vista Reporte Dinámico', readonly=True)

    total_debit = fields.Float(string='Total Débito', readonly=True)
    total_credit = fields.Float(string='Total Crédito', readonly=True)
    net_balance = fields.Float(string='Resultado Neto / Balance', readonly=True)

    def action_generate_html_report(self):
        self.ensure_one()
        if self.report_type == 'profit_loss':
            html_content = self._get_profit_loss_html()
        elif self.report_type == 'balance_sheet':
            html_content = self._get_balance_sheet_html()
        elif self.report_type == 'trial_balance':
            html_content = self._get_trial_balance_html()
        else:
            html_content = self._get_general_ledger_html()

        self.html_report = html_content
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'financial.report.wizard',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def _get_account_balances_sql(self):
        """Consulta SQL optimizada compatible con Odoo 19 (JSONB code_store y name)."""
        where_clauses = ["aml.company_id = %s"]
        params = [self.company_id.id]

        if self.target_move == 'posted':
            where_clauses.append("am.state = 'posted'")
        
        if not self.include_closing_entries:
            where_clauses.append("(aj.type IS NULL OR aj.type != 'situation')")

        if self.date_from:
            where_clauses.append("aml.date >= %s")
            params.append(self.date_from)

        if self.date_to:
            where_clauses.append("aml.date <= %s")
            params.append(self.date_to)

        where_str = " AND ".join(where_clauses)
        company_str_key = str(self.company_id.id)

        query = f"""
            SELECT 
                aa.id AS account_id,
                COALESCE(aa.code_store->>'{company_str_key}', aa.code_store->>'1', '') AS account_code,
                COALESCE(aa.name->>'es_VE', aa.name->>'en_US', '') AS account_name,
                aa.account_type AS account_type,
                COALESCE(SUM(aml.debit), 0.0) AS total_debit,
                COALESCE(SUM(aml.credit), 0.0) AS total_credit,
                COALESCE(SUM(aml.balance), 0.0) AS total_balance
            FROM account_move_line aml
            JOIN account_move am ON aml.move_id = am.id
            LEFT JOIN account_journal aj ON am.journal_id = aj.id
            JOIN account_account aa ON aml.account_id = aa.id
            WHERE {where_str}
            GROUP BY aa.id, aa.code_store, aa.name, aa.account_type
            ORDER BY account_code
        """
        self.env.cr.execute(query, tuple(params))
        return self.env.cr.dictfetchall()

    def _get_profit_loss_html(self):
        records = self._get_account_balances_sql()
        
        income_total = 0.0
        expense_total = 0.0
        account_rows = []
        unclassified_rows = []

        for r in records:
            acct_type = r['account_type'] or ''
            code = r['account_code'] or ''
            
            is_income = acct_type in ('income', 'income_other') or code.startswith(('4', '7'))
            is_expense = acct_type in ('expense', 'expense_depreciation', 'expense_direct_cost') or code.startswith(('5', '6'))

            if is_income:
                bal = r['total_credit'] - r['total_debit']
                income_total += bal
                account_rows.append({
                    'code': code, 'name': r['account_name'],
                    'type_label': 'Ingreso', 'badge': 'bg-success',
                    'balance': bal
                })
            elif is_expense:
                bal = r['total_debit'] - r['total_credit']
                expense_total += bal
                account_rows.append({
                    'code': code, 'name': r['account_name'],
                    'type_label': 'Gasto / Costo', 'badge': 'bg-danger',
                    'balance': bal
                })
            else:
                unclassified_rows.append({
                    'code': code, 'name': r['account_name'],
                    'type_label': 'No Clasificada', 'badge': 'bg-secondary',
                    'balance': r['total_balance']
                })

        net_profit = income_total - expense_total
        self.total_debit = income_total
        self.total_credit = expense_total
        self.net_balance = net_profit

        html = f"""
        <div class="financial-report-container p-3">
            <div class="header text-center mb-4">
                <h2 class="text-primary font-weight-bold">{self.company_id.name}</h2>
                <h4>ESTADO DE RESULTADOS (PÉRDIDAS Y GANANCIAS)</h4>
                <p class="text-muted">Período: {self.date_from or 'Inicio'} al {self.date_to or 'Hoy'} | Asientos: {'Publicados' if self.target_move == 'posted' else 'Todos'} | Moneda: {self.company_id.currency_id.name}</p>
            </div>
            
            <div class="row mb-4">
                <div class="col-md-4">
                    <div class="card bg-success text-white p-3 text-center shadow-sm">
                        <h5 class="mb-1">INGRESOS TOTALES</h5>
                        <h3 class="mb-0">${income_total:,.2f}</h3>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="card bg-danger text-white p-3 text-center shadow-sm">
                        <h5 class="mb-1">COSTOS Y GASTOS</h5>
                        <h3 class="mb-0">${expense_total:,.2f}</h3>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="card {'bg-primary' if net_profit >= 0 else 'bg-warning'} text-white p-3 text-center shadow-sm">
                        <h5 class="mb-1">GANANCIA / PÉRDIDA NETA</h5>
                        <h3 class="mb-0">${net_profit:,.2f}</h3>
                    </div>
                </div>
            </div>

            <table class="table table-striped table-hover table-bordered">
                <thead class="table-dark">
                    <tr>
                        <th width="15%">Código</th>
                        <th width="50%">Nombre de Cuenta</th>
                        <th width="15%">Categoría</th>
                        <th width="20%" class="text-end">Monto Total</th>
                    </tr>
                </thead>
                <tbody>
        """
        for row in sorted(account_rows, key=lambda x: x['code']):
            html += f"""
                    <tr>
                        <td><strong>{row['code']}</strong></td>
                        <td>{row['name']}</td>
                        <td><span class="badge {row['badge']}">{row['type_label']}</span></td>
                        <td class="text-end font-weight-bold">${row['balance']:,.2f}</td>
                    </tr>
            """
        
        if unclassified_rows:
            html += """
                    <tr class="table-warning">
                        <td colspan="4"><strong>⚠️ Cuentas Pendientes de Clasificación Contable:</strong></td>
                    </tr>
            """
            for u in sorted(unclassified_rows, key=lambda x: x['code']):
                html += f"""
                    <tr>
                        <td><strong>{u['code']}</strong></td>
                        <td>{u['name']}</td>
                        <td><span class="badge {u['badge']}">{u['type_label']}</span></td>
                        <td class="text-end text-muted">${u['balance']:,.2f}</td>
                    </tr>
                """

        html += f"""
                </tbody>
                <tfoot class="table-secondary">
                    <tr>
                        <th colspan="3">RESULTADO NETO DEL EJERCICIO</th>
                        <th class="text-end"><h4 class="mb-0">${net_profit:,.2f}</h4></th>
                    </tr>
                </tfoot>
            </table>
        </div>
        """
        return html

    def _get_balance_sheet_html(self):
        records = self._get_account_balances_sql()
        
        asset_total = 0.0
        liability_total = 0.0
        equity_total = 0.0

        for r in records:
            acct_type = r['account_type'] or ''
            code = r['account_code'] or ''

            is_asset = acct_type in ('asset_receivable', 'asset_cash', 'asset_current', 'asset_non_current', 'asset_prepayments', 'asset_fixed') or code.startswith('1')
            is_liability = acct_type in ('liability_payable', 'liability_current', 'liability_non_current') or code.startswith('2')
            is_equity = acct_type in ('equity', 'equity_unaffected') or code.startswith('3')
            is_income = acct_type in ('income', 'income_other') or code.startswith(('4', '7'))
            is_expense = acct_type in ('expense', 'expense_depreciation', 'expense_direct_cost') or code.startswith(('5', '6'))

            if is_asset:
                asset_total += (r['total_debit'] - r['total_credit'])
            elif is_liability:
                liability_total += (r['total_credit'] - r['total_debit'])
            elif is_equity:
                equity_total += (r['total_credit'] - r['total_debit'])
            elif is_income:
                equity_total += (r['total_credit'] - r['total_debit'])
            elif is_expense:
                equity_total -= (r['total_debit'] - r['total_credit'])

        self.total_debit = asset_total
        self.total_credit = liability_total + equity_total
        self.net_balance = asset_total - (liability_total + equity_total)

        html = f"""
        <div class="financial-report-container p-3">
            <div class="header text-center mb-4">
                <h2 class="text-primary font-weight-bold">{self.company_id.name}</h2>
                <h4>BALANCE GENERAL (ESTADO DE SITUACIÓN FINANCIERA)</h4>
                <p class="text-muted">Al: {self.date_to or 'Hoy'} | Moneda: {self.company_id.currency_id.name}</p>
            </div>
            
            <div class="row mb-4">
                <div class="col-md-4">
                    <div class="card bg-info text-white p-3 text-center shadow-sm">
                        <h5 class="mb-1">TOTAL ACTIVOS</h5>
                        <h3 class="mb-0">${asset_total:,.2f}</h3>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="card bg-warning text-dark p-3 text-center shadow-sm">
                        <h5 class="mb-1">TOTAL PASIVOS</h5>
                        <h3 class="mb-0">${liability_total:,.2f}</h3>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="card bg-success text-white p-3 text-center shadow-sm">
                        <h5 class="mb-1">PATRIMONIO NETO</h5>
                        <h3 class="mb-0">${equity_total:,.2f}</h3>
                    </div>
                </div>
            </div>

            <table class="table table-bordered">
                <thead class="table-dark text-center">
                    <tr>
                        <th width="50%">ACTIVOS</th>
                        <th width="50%">PASIVOS + PATRIMONIO</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td class="align-top p-3">
                            <h5 class="text-primary font-weight-bold">ACTIVOS TOTALES</h5>
                            <h3 class="text-end text-success">${asset_total:,.2f}</h3>
                        </td>
                        <td class="align-top p-3">
                            <h5 class="text-warning font-weight-bold">PASIVOS TOTALES</h5>
                            <h4 class="text-end text-danger">${liability_total:,.2f}</h4>
                            <hr/>
                            <h5 class="text-success font-weight-bold">PATRIMONIO Y RESULTADOS</h5>
                            <h4 class="text-end text-info">${equity_total:,.2f}</h4>
                            <hr/>
                            <h5 class="font-weight-bold">TOTAL PASIVO Y PATRIMONIO</h5>
                            <h3 class="text-end text-primary">${(liability_total + equity_total):,.2f}</h3>
                        </td>
                    </tr>
                </tbody>
            </table>
        </div>
        """
        return html

    def _get_trial_balance_html(self):
        records = self._get_account_balances_sql()
        tot_debit = sum(r['total_debit'] for r in records)
        tot_credit = sum(r['total_credit'] for r in records)
        self.total_debit = tot_debit
        self.total_credit = tot_credit

        html = f"""
        <div class="financial-report-container p-3">
            <div class="header text-center mb-4">
                <h2 class="text-primary font-weight-bold">{self.company_id.name}</h2>
                <h4>BALANCE DE COMPROBACIÓN (SUMAS Y SALDOS)</h4>
                <p class="text-muted">Período: {self.date_from or 'Inicio'} al {self.date_to or 'Hoy'}</p>
            </div>
            <table class="table table-striped table-hover table-bordered">
                <thead class="table-dark">
                    <tr>
                        <th>Código</th>
                        <th>Nombre de Cuenta</th>
                        <th class="text-end">Suma Débito</th>
                        <th class="text-end">Suma Crédito</th>
                        <th class="text-end">Saldo Neto</th>
                    </tr>
                </thead>
                <tbody>
        """
        for r in records:
            bal = r['total_debit'] - r['total_credit']
            bal_class = 'text-success' if bal >= 0 else 'text-danger'
            html += f"""
                    <tr>
                        <td><strong>{r['account_code']}</strong></td>
                        <td>{r['account_name']}</td>
                        <td class="text-end">${r['total_debit']:,.2f}</td>
                        <td class="text-end">${r['total_credit']:,.2f}</td>
                        <td class="text-end {bal_class}"><strong>${bal:,.2f}</strong></td>
                    </tr>
            """
        html += f"""
                </tbody>
                <tfoot class="table-dark">
                    <tr>
                        <th colspan="2">TOTALES GENERALES</th>
                        <th class="text-end">${tot_debit:,.2f}</th>
                        <th class="text-end">${tot_credit:,.2f}</th>
                        <th class="text-end">${(tot_debit - tot_credit):,.2f}</th>
                    </tr>
                </tfoot>
            </table>
        </div>
        """
        return html

    def _get_general_ledger_html(self):
        return self._get_trial_balance_html()

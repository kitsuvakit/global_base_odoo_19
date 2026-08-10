# -*- coding: utf-8 -*-
from datetime import date
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class FastDispatchStation(models.Model):
    _name = 'fast.dispatch.station'
    _description = 'Estación de Despacho Rápido'
    _rec_name = 'name'

    name = fields.Char(string='Estación', default='⚡ Estación de Despacho Rápido', readonly=True)

    # --- CONTROL DE MANDO (DASHBOARD KPIs) ---
    today_dispatched_count = fields.Integer(string='Total Despachadas Hoy', compute='_compute_dashboard')
    pending_dispatched_count = fields.Integer(string='Total Pendientes por Despachar', compute='_compute_dashboard')
    paid_pending_count = fields.Integer(string='Cant. Ventas Pagadas', compute='_compute_dashboard')
    unpaid_pending_count = fields.Integer(string='Cant. Ventas Sin Pagar', compute='_compute_dashboard')

    paid_dashboard_line_ids = fields.One2many(
        'fast.dispatch.dashboard.line', 'wizard_id',
        domain=[('tab_type', '=', 'paid')],
        string='Ventas Pagadas por Despachar'
    )
    unpaid_dashboard_line_ids = fields.One2many(
        'fast.dispatch.dashboard.line', 'wizard_id',
        domain=[('tab_type', '=', 'unpaid')],
        string='Ventas Sin Pagar (CxC)'
    )

    # --- CAMPOS DE BÚSQUEDA Y OPERACIÓN ---
    search_query = fields.Char(
        string='Escanear Ticket / Orden / Producto',
        help='Escanee el ticket de venta o código de barras de un producto'
    )
    picking_id = fields.Many2one('stock.picking', string='Orden de Entrega', readonly=True)
    picking_name = fields.Char(related='picking_id.name', string='Número de Entrega', readonly=True)
    origin = fields.Char(related='picking_id.origin', string='Origen (Venta/POS)', readonly=True)
    partner_id = fields.Many2one(related='picking_id.partner_id', string='Cliente', readonly=True)
    company_id = fields.Many2one('res.company', string='Compañía', default=lambda self: self.env.company, readonly=True)
    location_id = fields.Many2one(related='picking_id.location_id', string='Ubicación Origen', readonly=True)
    picking_state = fields.Selection(related='picking_id.state', string='Estado Entrega', readonly=True)

    line_ids = fields.One2many('fast.dispatch.line', 'wizard_id', string='Piezas a Despachar')
    status_message = fields.Char(string='Mensaje', readonly=True, default='Escanee o ingrese el número de ticket u orden para comenzar.')
    status_type = fields.Selection([
        ('info', 'Información'),
        ('success', 'Éxito'),
        ('warning', 'Advertencia'),
        ('danger', 'Error')
    ], string='Tipo de Estado', default='info', readonly=True)

    total_qty_demanded = fields.Float(compute='_compute_totals', string='Total Solicitado')
    total_qty_scanned = fields.Float(compute='_compute_totals', string='Total Escaneado')
    total_qty_missing = fields.Float(compute='_compute_totals', string='Faltante por Escanear')
    is_fully_scanned = fields.Boolean(compute='_compute_totals', string='Totalmente Escaneado')

    @api.depends('line_ids.qty_demanded', 'line_ids.scanned_qty', 'line_ids.qty_to_dispatch')
    def _compute_totals(self):
        for rec in self:
            demanded = sum(rec.line_ids.mapped('qty_demanded'))
            scanned = sum(rec.line_ids.mapped('scanned_qty'))
            rec.total_qty_demanded = demanded
            rec.total_qty_scanned = scanned
            rec.total_qty_missing = max(0.0, demanded - scanned)
            rec.is_fully_scanned = bool(demanded > 0 and scanned >= demanded)

    def _compute_dashboard(self):
        for rec in self:
            company_id = rec.company_id.id or self.env.company.id
            today = date.today()
            domain_base = [('company_id', '=', company_id), ('picking_type_code', '=', 'outgoing')]

            # Total Despachadas Hoy
            rec.today_dispatched_count = self.env['stock.picking'].sudo().search_count(domain_base + [
                ('state', '=', 'done'),
                ('date_done', '>=', today.strftime('%Y-%m-%d 00:00:00'))
            ])

            # Entregas Pendientes
            pending_pickings = self.env['stock.picking'].sudo().search(domain_base + [
                ('state', 'in', ('assigned', 'confirmed', 'waiting'))
            ])

            rec.pending_dispatched_count = len(pending_pickings)

            paid_count = 0
            unpaid_count = 0

            for p in pending_pickings:
                so = p.sale_id
                is_paid = False

                if p.origin and ('POS' in p.origin.upper() or 'PV' in p.origin.upper()):
                    is_paid = True
                elif so:
                    paid_invs = so.invoice_ids.filtered(lambda i: i.state == 'posted' and i.payment_state in ('paid', 'in_payment'))
                    if paid_invs:
                        is_paid = True

                if is_paid:
                    paid_count += 1
                else:
                    unpaid_count += 1

            rec.paid_pending_count = paid_count
            rec.unpaid_pending_count = unpaid_count

    def update_dashboard_lines(self):
        for rec in self:
            company_id = rec.company_id.id or self.env.company.id
            domain_base = [('company_id', '=', company_id), ('picking_type_code', '=', 'outgoing')]

            pending_pickings = self.env['stock.picking'].sudo().search(domain_base + [
                ('state', 'in', ('assigned', 'confirmed', 'waiting'))
            ], order='scheduled_date asc, id desc')

            paid_lines = []
            unpaid_lines = []

            for p in pending_pickings:
                so = p.sale_id
                is_paid = False
                label = "🔴 Sin Pagar (CxC)"

                if p.origin and ('POS' in p.origin.upper() or 'PV' in p.origin.upper()):
                    is_paid = True
                    label = "🟢 Pagado en POS"
                elif so:
                    paid_invs = so.invoice_ids.filtered(lambda i: i.state == 'posted' and i.payment_state in ('paid', 'in_payment'))
                    if paid_invs:
                        is_paid = True
                        label = "🟢 Factura Pagada"
                    elif any(i.payment_state == 'partial' for i in so.invoice_ids):
                        label = "🟡 Pago Parcial"

                qty_sum = sum(p.move_ids.mapped('product_uom_qty'))
                line_data = (0, 0, {
                    'picking_id': p.id,
                    'tab_type': 'paid' if is_paid else 'unpaid',
                    'payment_status_label': label,
                    'total_qty': qty_sum,
                })

                if is_paid:
                    paid_lines.append(line_data)
                else:
                    unpaid_lines.append(line_data)

            rec.paid_dashboard_line_ids = [(5, 0, 0)] + paid_lines
            rec.unpaid_dashboard_line_ids = [(5, 0, 0)] + unpaid_lines

    def action_refresh_dashboard(self):
        self.ensure_one()
        self.update_dashboard_lines()
        self.status_message = "🔄 Control de Mando actualizado con las métricas y entregas del día."
        self.status_type = 'info'
        return True

    def action_load_picking_by_id(self, picking_id_val):
        self.ensure_one()
        picking = self.env['stock.picking'].sudo().browse(picking_id_val)
        if picking and picking.exists():
            return self.action_search_picking(query=picking.name)
        return True

    def process_scan_input(self, query=None):
        query = (query or self.search_query or '').strip()
        self.search_query = False

        if not query:
            return True

        # 1. Si hay orden activa no finalizada, probar si es un producto de esa orden
        if self.picking_id and self.picking_id.state not in ('done', 'cancel'):
            matched_line = False
            for line in self.line_ids:
                p = line.product_id
                if query in (p.barcode, p.default_code, p.name) or (p.barcode and query.lower() == p.barcode.lower()) or (p.default_code and query.lower() == p.default_code.lower()):
                    matched_line = line
                    break

            if matched_line:
                if matched_line.scanned_qty < matched_line.qty_demanded:
                    matched_line.is_missing = False
                    matched_line.scanned_qty += 1.0
                    matched_line.qty_to_dispatch = matched_line.scanned_qty
                    matched_line.is_checked = (matched_line.scanned_qty >= matched_line.qty_demanded)
                    
                    total_scanned = sum(self.line_ids.mapped('scanned_qty'))
                    total_demanded = sum(self.line_ids.mapped('qty_demanded'))
                    
                    if total_scanned >= total_demanded:
                        self.status_message = f"🎉 ¡CONTEO COMPLETO ({int(total_scanned)}/{int(total_demanded)} piezas)! Presione el botón 'VALIDAR Y DESPACHAR' para finalizar la entrega."
                        self.status_type = 'success'
                        return True
                    else:
                        self.status_message = f"🔍 Escaneado (+1): [{matched_line.default_code}] {matched_line.product_id.name} ({int(matched_line.scanned_qty)}/{int(matched_line.qty_demanded)} piezas)."
                        self.status_type = 'info'
                        return True
                else:
                    self.status_message = f"⚠️ ALERTA PIEZAS DE MÁS: Ya se completaron las {int(matched_line.qty_demanded)} piezas solicitadas de [{matched_line.default_code}]. No se permite escanear piezas adicionales."
                    self.status_type = 'danger'
                    return True

        # 2. Si no es un producto o no hay orden cargada, buscar nueva orden por coincidencia exacta
        return self.action_search_picking(query)

    def action_search_picking(self, query=None):
        if not query:
            query = (self.search_query or '').strip()

        self.search_query = False

        if not query:
            return True

        company_id = self.env.company.id
        Picking = self.env['stock.picking'].sudo()

        domain_base = [
            ('company_id', '=', company_id),
            ('picking_type_code', '=', 'outgoing'),
        ]

        # 1. Coincidencia exacta estricta en pendientes (Nombre, Origen o Pedido de Venta)
        picking = Picking.search(domain_base + [
            ('state', 'not in', ('done', 'cancel')),
            '|', '|',
            ('name', '=ilike', query),
            ('origin', '=ilike', query),
            ('sale_id.name', '=ilike', query),
        ], limit=1)

        # 2. Coincidencia por prefijo exacto de ticket (SO15239, SO-15239, POS/15239, %/15239)
        if not picking:
            picking = Picking.search(domain_base + [
                ('state', 'not in', ('done', 'cancel')),
                '|', '|', '|', '|',
                ('origin', '=ilike', f'SO{query}'),
                ('origin', '=ilike', f'SO-{query}'),
                ('origin', '=ilike', f'POS/{query}'),
                ('sale_id.name', '=ilike', f'SO{query}'),
                ('name', '=ilike', f'%/{query}'),
            ], limit=1)

        # 3. Si no se encuentra en pendientes, buscar en entregas YA DESPACHADAS por coincidencia exacta
        if not picking:
            done_picking = Picking.search(domain_base + [
                ('state', '=', 'done'),
                '|', '|',
                ('name', '=ilike', query),
                ('origin', '=ilike', query),
                ('sale_id.name', '=ilike', query),
            ], limit=1)

            if not done_picking:
                done_picking = Picking.search(domain_base + [
                    ('state', '=', 'done'),
                    '|', '|', '|', '|',
                    ('origin', '=ilike', f'SO{query}'),
                    ('origin', '=ilike', f'SO-{query}'),
                    ('origin', '=ilike', f'POS/{query}'),
                    ('sale_id.name', '=ilike', f'SO{query}'),
                    ('name', '=ilike', f'%/{query}'),
                ], limit=1)

            if done_picking:
                self.picking_id = done_picking.id
                self.status_message = f"ℹ️ [ENTREGA YA DESPACHADA] Se cargó la entrega {done_picking.name} (Origen: {done_picking.origin or ''}) despachada previamente para su verificación."
                self.status_type = 'warning'

                lines = []
                for move in done_picking.move_ids.filtered(lambda m: m.state == 'done'):
                    loc_name = move.location_id.display_name or ''
                    qty = move.quantity or move.product_uom_qty
                    lines.append((0, 0, {
                        'move_id': move.id,
                        'product_id': move.product_id.id,
                        'default_code': move.product_id.default_code or '',
                        'barcode': move.product_id.barcode or '',
                        'location_name': loc_name,
                        'qty_demanded': move.product_uom_qty,
                        'scanned_qty': qty,
                        'qty_to_dispatch': qty,
                        'is_checked': True,
                        'is_missing': False,
                    }))
                self.line_ids = [(5, 0, 0)] + lines
                return True

            if self.picking_id and self.picking_id.state not in ('done', 'cancel'):
                self.status_message = f"❌ El código escaneado '{query}' NO pertenece a la orden {self.picking_id.name} ni se encontró otra orden exacta con ese número."
                self.status_type = 'danger'
                return True

            self.picking_id = False
            self.status_message = f"❌ No se encontró ninguna entrega exacta para: '{query}' en la compañía actual."
            self.status_type = 'danger'
            self.line_ids = [(5, 0, 0)]
            return True

        self.picking_id = picking.id
        self.status_message = f"📦 Entrega {picking.name} (Origen: {picking.origin or ''}) cargada. Escanee los productos o presione VALIDAR."
        self.status_type = 'info'

        lines = []
        for move in picking.move_ids.filtered(lambda m: m.state not in ('done', 'cancel')):
            loc_name = move.location_id.display_name or ''
            lines.append((0, 0, {
                'move_id': move.id,
                'product_id': move.product_id.id,
                'default_code': move.product_id.default_code or '',
                'barcode': move.product_id.barcode or '',
                'location_name': loc_name,
                'qty_demanded': move.product_uom_qty,
                'scanned_qty': 0.0,
                'qty_to_dispatch': move.product_uom_qty,
                'is_checked': False,
                'is_missing': False,
            }))
        self.line_ids = [(5, 0, 0)] + lines
        return True

    def action_validate_dispatch(self, auto=False):
        self.ensure_one()
        if not self.picking_id:
            raise UserError(_("No hay ninguna entrega seleccionada para despachar."))

        picking = self.picking_id.sudo()

        if picking.state in ('done', 'cancel'):
            self.status_message = f"ℹ️ La entrega {picking.name} ya se encuentra en estado {picking.state}. No requiere validación adicional."
            self.status_type = 'warning'
            return True

        # 1. Bloqueo por piezas DE MÁS escaneadas o colocadas manualmente
        over_lines = self.line_ids.filtered(lambda l: l.scanned_qty > l.qty_demanded)
        if over_lines:
            line_details = ", ".join([f"[{l.default_code}] (Escaneadas: {int(l.scanned_qty)} / Solicitadas: {int(l.qty_demanded)})" for l in over_lines])
            self.status_message = f"❌ VALIDACIÓN BLOQUEADA: Hay piezas DE MÁS escaneadas para: {line_details}. Corrija la cantidad antes de despachar."
            self.status_type = 'danger'
            return True

        # 2. Bloqueo por pistoleo incompleto / Sin escanear
        incomplete_lines = self.line_ids.filtered(lambda l: l.scanned_qty < l.qty_demanded)
        if incomplete_lines:
            for l in self.line_ids:
                l.is_missing = (l.scanned_qty < l.qty_demanded)

            line_details = ", ".join([f"[{l.default_code}] ({int(l.scanned_qty)}/{int(l.qty_demanded)})" for l in incomplete_lines])
            self.status_message = f"❌ VALIDACIÓN BLOQUEADA: Faltan productos por escanear (marcados en ROJO en la lista): {line_details}. Termine de pistolear o edite la cantidad manualmente."
            self.status_type = 'danger'
            return True

        if picking.state in ('draft', 'confirmed'):
            picking.action_assign()

        for line in self.line_ids:
            if line.move_id and line.move_id.picking_id == picking:
                qty = line.scanned_qty if line.scanned_qty > 0 else line.qty_demanded
                line.move_id.quantity = qty

        res = picking.button_validate()

        if isinstance(res, dict) and res.get('res_model') == 'stock.backorder.confirmation':
            backorder_wizard = self.env['stock.backorder.confirmation'].browse(res.get('res_id'))
            if hasattr(backorder_wizard, 'process_cancel_backorder'):
                backorder_wizard.process_cancel_backorder()

        p_name = picking.name
        p_origin = picking.origin or ''

        self.write({
            'search_query': False,
            'picking_id': False,
            'status_message': f"✅ ¡DESPACHO EXITOSO! La entrega {p_name} (Origen: {p_origin}) fue validada correctamente.",
            'status_type': 'success',
            'line_ids': [(5, 0, 0)],
        })

        self.update_dashboard_lines()
        return True

    def action_clear(self):
        self.ensure_one()
        self.write({
            'search_query': False,
            'picking_id': False,
            'status_message': "Listo para escanear el siguiente ticket o número de orden.",
            'status_type': 'info',
            'line_ids': [(5, 0, 0)],
        })
        self.update_dashboard_lines()
        return True


class FastDispatchDashboardLine(models.Model):
    _name = 'fast.dispatch.dashboard.line'
    _description = 'Línea de Control de Mando de Despacho'
    _order = 'scheduled_date asc, id desc'

    wizard_id = fields.Many2one('fast.dispatch.station', string='Estación', ondelete='cascade')
    picking_id = fields.Many2one('stock.picking', string='Orden de Entrega', required=True)
    picking_name = fields.Char(related='picking_id.name', string='Número Entrega', readonly=True)
    origin = fields.Char(related='picking_id.origin', string='Origen / Cotización', readonly=True)
    partner_id = fields.Many2one(related='picking_id.partner_id', string='Cliente', readonly=True)
    scheduled_date = fields.Datetime(related='picking_id.scheduled_date', string='Fecha Programada', readonly=True)
    tab_type = fields.Selection([('paid', 'Pagada'), ('unpaid', 'Sin Pagar')], string='Tipo Tab')
    payment_status_label = fields.Char(string='Estado de Pago')
    total_qty = fields.Float(string='Total Piezas')

    def action_load_this_picking(self):
        self.ensure_one()
        return self.wizard_id.action_load_picking_by_id(self.picking_id.id)


class FastDispatchLine(models.Model):
    _name = 'fast.dispatch.line'
    _description = 'Línea de Pieza de Despacho Rápido'

    wizard_id = fields.Many2one('fast.dispatch.station', string='Wizard', ondelete='cascade')
    move_id = fields.Many2one('stock.move', string='Movimiento de Stock')
    product_id = fields.Many2one('product.product', string='Producto', readonly=True)
    default_code = fields.Char(string='Ref. Interna / Código', readonly=True)
    barcode = fields.Char(string='Código de Barras', readonly=True)
    location_name = fields.Char(string='Ubicación en Almacén', readonly=True)
    qty_demanded = fields.Float(string='Cant. Solicitada', readonly=True)
    scanned_qty = fields.Float(string='Cant. Escaneada', default=0.0)
    qty_to_dispatch = fields.Float(string='Cant. a Despachar')
    is_checked = fields.Boolean(string='Piezas Verificadas', default=False)
    is_missing = fields.Boolean(string='Falta por Escanear', default=False)

    scan_state = fields.Selection([
        ('pending', '⚪ Sin Escanear'),
        ('partial', '🟡 En Conteo'),
        ('completed', '🟢 Completado'),
        ('missing', '🔴 Incompleto / Falta')
    ], string='Estado Conteo', compute='_compute_scan_state', store=True)

    @api.depends('scanned_qty', 'qty_demanded', 'is_missing')
    def _compute_scan_state(self):
        for line in self:
            if line.scanned_qty >= line.qty_demanded and line.qty_demanded > 0:
                line.scan_state = 'completed'
            elif line.is_missing and line.scanned_qty < line.qty_demanded:
                line.scan_state = 'missing'
            elif line.scanned_qty > 0 and line.scanned_qty < line.qty_demanded:
                line.scan_state = 'partial'
            else:
                line.scan_state = 'pending'

    @api.onchange('scanned_qty')
    def _onchange_scanned_qty(self):
        for line in self:
            line.qty_to_dispatch = line.scanned_qty
            line.is_checked = bool(line.scanned_qty >= line.qty_demanded)
            if line.scanned_qty >= line.qty_demanded:
                line.is_missing = False

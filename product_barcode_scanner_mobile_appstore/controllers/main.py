# -*- coding: utf-8 -*-
from odoo import http, _
from odoo.http import request, content_disposition


class ProductBarcodeScannerController(http.Controller):

    @http.route("/product_scanner", type="http", auth="user", website=True)
    def barcode_scanner_web_page(self, **kw):
        user = request.env.user
        has_scanner_access = user.has_group("product_barcode_scanner_mobile_appstore.group_scanner_user") or user._is_admin()
        has_cycle_count_access = user.has_group("product_barcode_scanner_mobile_appstore.group_scanner_cycle_count") or user._is_admin()

        if not has_scanner_access:
            return request.render("product_barcode_scanner_mobile_appstore.scanner_access_denied", {})

        values = {
            "has_cycle_count_permission": has_cycle_count_access,
            "user_name": user.name,
        }
        return request.render("product_barcode_scanner_mobile_appstore.scanner_standalone_page", values)

    @http.route("/product_scanner/search", type="jsonrpc", auth="user", methods=["POST"], csrf=False)
    def search_product(self, barcode=None, **kw):
        user = request.env.user
        has_access = user.has_group("product_barcode_scanner_mobile_appstore.group_scanner_user") or user._is_admin()
        if not has_access:
            return {"success": False, "message": "No posee permisos para usar el Escáner Móvil"}
        return request.env["product.product"].sudo().search_product_for_scanner(barcode)

    @http.route("/product_scanner/initial_data", type="jsonrpc", auth="user", methods=["POST"], csrf=False)
    def get_initial_data(self, **kw):
        return request.env["product.product"].sudo().get_scanner_initial_data()

    # --- CYCLE COUNT ENDPOINTS ---
    @http.route("/product_scanner/cycle_count/start", type="jsonrpc", auth="user", methods=["POST"], csrf=False)
    def cycle_count_start(self, **kw):
        user = request.env.user
        if not (user.has_group("product_barcode_scanner_mobile_appstore.group_scanner_cycle_count") or user._is_admin()):
            return {"success": False, "message": "No posee permisos para realizar Conteos Cíclicos"}

        count = request.env["scanner.cycle.count"].sudo().create({
            "user_id": user.id,
            "state": "in_progress",
        })
        return {
            "success": True,
            "session": self._format_session_dict(count),
        }

    @http.route("/product_scanner/cycle_count/add_line", type="jsonrpc", auth="user", methods=["POST"], csrf=False)
    def cycle_count_add_line(self, session_id=None, barcode=None, **kw):
        user = request.env.user
        if not (user.has_group("product_barcode_scanner_mobile_appstore.group_scanner_cycle_count") or user._is_admin()):
            return {"success": False, "message": "Sin permisos de conteo cíclico"}

        if not session_id or not barcode:
            return {"success": False, "message": "Parámetros de conteo inválidos"}

        session = request.env["scanner.cycle.count"].sudo().browse(session_id)
        if not session.exists() or session.state == "cancelled":
            return {"success": False, "message": "Sesión de conteo inválida o cancelada"}

        # Search product
        search_res = request.env["product.product"].sudo().search_product_for_scanner(barcode)
        if not search_res.get("success"):
            return search_res

        prod_data = search_res["product"]
        product = request.env["product.product"].sudo().browse(prod_data["id"])

        # Check existing line in session
        existing_line = session.line_ids.filtered(lambda l: l.product_id.id == product.id)
        if existing_line:
            existing_line.counted_qty += 1.0
        else:
            request.env["scanner.cycle.count.line"].sudo().create({
                "cycle_count_id": session.id,
                "product_id": product.id,
                "barcode": prod_data["barcode"],
                "default_code": prod_data["default_code"],
                "product_name": prod_data["name"],
                "location_name": prod_data["location"],
                "system_qty": prod_data["qty_available"],
                "counted_qty": 1.0,
                "unit_price_usd": prod_data["list_price"],
            })

        return {
            "success": True,
            "product": prod_data,
            "session": self._format_session_dict(session),
        }

    @http.route("/product_scanner/cycle_count/update_qty", type="jsonrpc", auth="user", methods=["POST"], csrf=False)
    def cycle_count_update_qty(self, line_id=None, new_qty=0.0, **kw):
        user = request.env.user
        if not (user.has_group("product_barcode_scanner_mobile_appstore.group_scanner_cycle_count") or user._is_admin()):
            return {"success": False, "message": "Sin permisos de conteo cíclico"}

        line = request.env["scanner.cycle.count.line"].sudo().browse(line_id)
        if not line.exists():
            return {"success": False, "message": "Línea de conteo no encontrada"}

        try:
            qty_val = max(0.0, float(new_qty))
        except (ValueError, TypeError):
            qty_val = 0.0

        line.counted_qty = qty_val
        session = line.cycle_count_id

        return {
            "success": True,
            "session": self._format_session_dict(session),
        }

    @http.route("/product_scanner/cycle_count/finish", type="jsonrpc", auth="user", methods=["POST"], csrf=False)
    def cycle_count_finish(self, session_id=None, **kw):
        user = request.env.user
        if not (user.has_group("product_barcode_scanner_mobile_appstore.group_scanner_cycle_count") or user._is_admin()):
            return {"success": False, "message": "Sin permisos de conteo cíclico"}

        session = request.env["scanner.cycle.count"].sudo().browse(session_id)
        if not session.exists():
            return {"success": False, "message": "Sesión no encontrada"}

        session.action_finish()
        return {
            "success": True,
            "session": self._format_session_dict(session),
        }

    @http.route("/product_scanner/cycle_count/export_excel/<int:count_id>", type="http", auth="user")
    def export_cycle_count_excel(self, count_id, **kw):
        user = request.env.user
        if not (user.has_group("product_barcode_scanner_mobile_appstore.group_scanner_cycle_count") or user._is_admin()):
            return request.not_found()

        count = request.env["scanner.cycle.count"].sudo().browse(count_id)
        if not count.exists():
            return request.not_found()

        excel_bytes = count.export_excel_report_bytes()
        filename = f"Conteo_Ciclico_{count.name.replace('/', '_')}.xlsx"
        
        headers = [
            ("Content-Type", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"),
            ("Content-Disposition", content_disposition(filename)),
        ]
        return request.make_response(excel_bytes, headers=headers)

    def _format_session_dict(self, session):
        lines_data = []
        for l in session.line_ids:
            lines_data.append({
                "id": l.id,
                "product_id": l.product_id.id,
                "barcode": l.barcode or "N/A",
                "default_code": l.default_code or "N/A",
                "product_name": l.product_name or "",
                "location_name": l.location_name or "Sin Ubicación",
                "system_qty": l.system_qty,
                "counted_qty": l.counted_qty,
                "difference_qty": l.difference_qty,
                "unit_price_usd": l.unit_price_usd,
                "formatted_unit_price": f"${l.unit_price_usd:,.2f} USD",
                "difference_value_usd": l.difference_value_usd,
                "formatted_diff_usd": f"${l.difference_value_usd:,.2f} USD",
                "image_url": f"/web/image/product.product/{l.product_id.id}/image_512",
            })

        return {
            "id": session.id,
            "name": session.name,
            "state": session.state,
            "operator_name": session.user_id.name,
            "date": session.date.strftime("%d/%m/%Y %H:%M") if session.date else "",
            "date_end": session.date_end.strftime("%d/%m/%Y %H:%M") if session.date_end else "",
            "total_lines": session.total_lines,
            "total_system_qty": session.total_system_qty,
            "total_counted_qty": session.total_counted_qty,
            "total_diff_qty": session.total_diff_qty,
            "total_diff_usd": session.total_diff_usd,
            "formatted_total_diff_usd": f"${session.total_diff_usd:,.2f} USD",
            "excel_url": f"/product_scanner/cycle_count/export_excel/{session.id}",
            "lines": lines_data,
        }

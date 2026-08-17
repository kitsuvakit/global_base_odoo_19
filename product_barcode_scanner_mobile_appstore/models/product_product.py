# -*- coding: utf-8 -*-
from odoo import _, api, fields, models


class ProductProductScanner(models.Model):
    _inherit = "product.product"

    @api.model
    def search_product_for_scanner(self, search_term):
        if not search_term:
            return {"success": False, "message": "Debe ingresar o escanear un código de barras"}

        term = str(search_term).strip()

        # 1. Search exact barcode
        product = self.search([("barcode", "=", term)], limit=1)

        # 2. Search default_code (internal reference)
        if not product:
            product = self.search([("default_code", "=", term)], limit=1)

        if not product:
            product = self.search([("default_code", "=ilike", term)], limit=1)

        # 3. Search barcode partial / ilike
        if not product:
            product = self.search([("barcode", "=ilike", f"%{term}%")], limit=1)

        # 4. Search name ilike
        if not product:
            product = self.search([("name", "=ilike", f"%{term}%")], limit=1)

        if not product:
            return {"success": False, "message": f"No se encontró ningún producto con el código '{term}'"}

        # Extract product brand dynamically (Works with standard or any custom brand module)
        brand_name = "N/A"
        if hasattr(product, "product_brand") and product.product_brand:
            brand_name = str(product.product_brand.name if hasattr(product.product_brand, 'name') else product.product_brand)
        elif hasattr(product, "brand_id") and product.brand_id:
            brand_name = product.brand_id.name
        elif hasattr(product.product_tmpl_id, "product_brand") and product.product_tmpl_id.product_brand:
            brand_name = str(product.product_tmpl_id.product_brand.name if hasattr(product.product_tmpl_id.product_brand, 'name') else product.product_tmpl_id.product_brand)
        elif hasattr(product.product_tmpl_id, "brand_id") and product.product_tmpl_id.brand_id:
            brand_name = product.product_tmpl_id.brand_id.name

        # Extract car brand / vehicle compatibility dynamically
        car_brand_name = "N/A"
        if hasattr(product, "brand_car") and product.brand_car:
            car_brand_name = str(product.brand_car)
        elif hasattr(product, "x_marca_car") and product.x_marca_car:
            car_brand_name = str(product.x_marca_car)
        elif hasattr(product.product_tmpl_id, "brand_car") and product.product_tmpl_id.brand_car:
            car_brand_name = str(product.product_tmpl_id.brand_car)
        elif hasattr(product.product_tmpl_id, "x_marca_car") and product.product_tmpl_id.x_marca_car:
            car_brand_name = str(product.product_tmpl_id.x_marca_car)

        # Extract warehouse location dynamically
        location_str = "Sin Ubicación"
        if hasattr(product, "x_ubicacion") and product.x_ubicacion:
            location_str = str(product.x_ubicacion)
        elif hasattr(product, "ubicaciones") and product.ubicaciones:
            location_str = str(product.ubicaciones)
        elif hasattr(product, "location_id") and product.location_id:
            location_str = str(product.location_id.display_name)
        elif hasattr(product.product_tmpl_id, "x_ubicacion") and product.product_tmpl_id.x_ubicacion:
            location_str = str(product.product_tmpl_id.x_ubicacion)

        # Dynamic Multi-Warehouse Stock Breakdown (Standard Odoo 19 Compatibility)
        qty_total = int(round(product.qty_available or 0))
        warehouses_stock = []
        
        if 'stock.quant' in self.env:
            quants = self.env['stock.quant'].search([
                ('product_id', '=', product.id),
                ('location_id.usage', '=', 'internal')
            ])
            wh_map = {}
            for q in quants:
                wh_name = q.location_id.warehouse_id.name or q.location_id.display_name or _("Almacén Principal")
                wh_map[wh_name] = wh_map.get(wh_name, 0.0) + q.quantity
            
            for wh_name, qty in wh_map.items():
                warehouses_stock.append({
                    "name": wh_name,
                    "qty": int(round(qty))
                })
        
        if not warehouses_stock:
            warehouses_stock.append({
                "name": _("Almacén Principal"),
                "qty": qty_total
            })

        # Multi-currency rate calculation (VES / USD fallback)
        price_usd = product.list_price or 0.0
        ves_currency = self.env['res.currency'].search([('name', '=', 'VES')], limit=1)
        bcv_rate = ves_currency.rate if ves_currency and ves_currency.rate else 0.0
        price_ves = price_usd * bcv_rate if bcv_rate else 0.0

        formatted_price_ves = f"{price_ves:,.2f} Bs." if bcv_rate else ""
        formatted_bcv_rate = f"{bcv_rate:,.2f} Bs./$" if bcv_rate else ""

        # Category
        categ_str = product.categ_id.display_name if product.categ_id else "General"

        # Unit of measure
        uom_str = product.uom_id.name if product.uom_id else "Unidades"

        return {
            "success": True,
            "product": {
                "id": product.id,
                "name": product.name or "",
                "default_code": product.default_code or "N/A",
                "barcode": product.barcode or "N/A",
                "product_brand": brand_name,
                "brand_car": car_brand_name,
                "location": location_str,
                "category": categ_str,
                "uom": uom_str,
                "list_price": price_usd,
                "formatted_price": f"${price_usd:,.2f} USD",
                "bcv_rate": bcv_rate,
                "price_ves": price_ves,
                "formatted_price_ves": formatted_price_ves,
                "formatted_bcv_rate": formatted_bcv_rate,
                "image_url": f"/web/image/product.product/{product.id}/image_512",
                "qty_available": qty_total,
                "warehouses_stock": warehouses_stock,
                "is_in_stock": qty_total > 0,
                "odoo_url": f"/web#id={product.id}&model=product.product&view_type=form",
            },
        }

    @api.model
    def get_scanner_initial_data(self):
        ves_currency = self.env['res.currency'].search([('name', '=', 'VES')], limit=1)
        bcv_rate = ves_currency.rate if ves_currency and ves_currency.rate else 0.0
        return {
            "bcv_rate": bcv_rate,
            "formatted_bcv_rate": f"{bcv_rate:,.2f} Bs./$" if bcv_rate else "N/A",
        }

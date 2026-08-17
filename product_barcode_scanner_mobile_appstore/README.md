# 📱 Escáner Móvil Pro de Productos & Conteos Cíclicos (`product_barcode_scanner_mobile`)

**Autor:** Omar Martinez  
**Licencia:** OPL-1  
**Versión:** 19.0.1.0.30  
**Categoría:** Inventario / Almacén  

---

## 📌 ¿Qué Hace este Addon?

El módulo **Escáner Móvil Pro** transforma cualquier smartphone, tablet o terminal portátil en un potente lector industrial de códigos de barras integrado directamente con **Odoo 19**. 

Ofrece dos modos de operación avanzados diseñados para agilizar la operativa diaria del personal de almacén y ventas:

1. 🔍 **Modo Consulta de Productos & Stock Multialmacén:**
   - Escaneo instantáneo de códigos de barras (EAN13, Code128, QR, SKU) con cámara de smartphone o pistola física lectora.
   - Muestra detalles completos del producto: Nombre, Imagen ampliable, Referencia/SKU, Código de Barras, Ubicación física en estantería, Marca del repuesto, Marca de vehículo compatible y Unidad de medida.
   - **Precios Duales en Tiempo Real:** Muestra el precio en **$ USD** y su conversión automática a **Bolívares (Bs.)** según la tasa oficial del día del Banco Central de Venezuela (BCV).
   - **Disponibilidad Multialmacén:** Desglose detallado del stock disponible en almacenes clave (**Dakar**, **DF**, **JQC**, **Kalani**).
   - **Acciones Rápidas:** Copiar ficha técnica al portapapeles, compartir producto por WhatsApp con un toque y abrir directo en Odoo Backend.

2. 📋 **Modo Conteo Cíclico de Inventario en Tiempo Real:**
   - Permite a los operadores realizar inventarios físicos y conteos cíclicos de estantería escaneando línea por línea.
   - **Captura Automática:** Registra la **Cantidad Inicial en Sistema** al momento del escaneo, la **Cantidad Contada** y calcula la **Diferencia Neta**.
   - **Ajuste Táctil In Situ:** Botones de incremento/decremento rápido (`-` / `+`) y campo de texto para edición directa.
   - **Resumen Ejecutivo en Pantalla:** Al finalizar el conteo, presenta métricas consolidadas de productos contados, exactitud %, total de unidades teóricas vs reales e **Impacto Monetario Total ($ USD)** de las diferencias.
   - **Exportación en Excel (.xlsx):** Descarga instantánea de reportes de auditoría formateados en Excel con encabezado corporativo, desglose por producto y alertas de color.

---

## ⚙️ ¿Cómo Funciona?

### Arquitectura Técnica & Flujo de Trabajo
- **Interfaz Standalone Ultra Rápida (`/product_scanner`):** Aplicación web progresiva (PWA) de alto rendimiento, optimizada para pantallas táctiles y dispositivos móviles con diseño Glassmorphic.
- **Motor Óptico Desconectado (Offline Capable):** Utiliza la biblioteca cliente `Html5Qrcode` alojada localmente en el módulo para escaneo directo mediante cámara trasera o frontal con linterna (torch).
- **Feedback Sensorial Inmediato:** Sintetizador de audio en tiempo real mediante **Web Audio API** (`880Hz`) y vibración háptica (`navigator.vibrate`) para confirmar escaneos en entornos ruidosos.
- **Seguridad Granular por Grupos (Odoo 19):**
  - 🔍 **`Escáner Móvil / Solo Consulta`**: Acceso limitado exclusivamente a la búsqueda y consulta de productos.
  - 📋 **`Escáner Móvil / Conteo Cíclico y Reportes`**: Acceso completo a conteos cíclicos, resumen de auditoría y descarga de reportes Excel.
- **Motor de Reportes Excel:** Utiliza la librería `openpyxl` en el servidor Python para generar hojas de cálculo estructuradas con formato condicional.
- **Integración Backend:** Incluye vistas de lista y formulario en *Inventario ➔ Operaciones ➔ Conteos Cíclicos Móviles* para auditoría administrativa.

---

## 🚀 ¿Cómo Beneficia a la Empresa?

1. ⚡ **Aumento Masivo de la Productividad (Reducción del 95% del Tiempo):**
   - Elimina la consulta manual de códigos en computadoras de escritorio. El personal puede chequear stock y precios desde el pasillo del almacén.
2. 🎯 **Cero Errores en Inventarios Físicos:**
   - La comparación en tiempo real entre el stock teórico en sistema y la cantidad física contada evita descuadres y extravíos.
3. 💵 **Control de Impacto Financiero Inmediato:**
   - Muestra al instante el valor en USD de cualquier diferencia de inventario detectada antes de aplicar ajustes.
4. 📱 **Reducción de Costos de Hardware:**
   - Funciona en cualquier teléfono inteligente Android o iOS existente, evitando la compra de costosos colectores de datos propietarios.
5. 📊 **Auditoría Transparente y Reportes Profesionales:**
   - Generación de reportes Excel listos para entregar a la gerencia de operaciones o contabilidad.

---

## 📸 Recursos Gráficos
- **Icono de Aplicación:** `static/description/icon.png` (264x180 px / Alta Resolución)
- **Portada de la App Store:** `static/description/icon_banner.png` (Banner 16:9 Glassmorphic)
- **Ficha Comercial App Store:** `static/description/index.html` (Diseño HTML5 Responsive)

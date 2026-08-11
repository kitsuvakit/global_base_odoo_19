# 📦 Fast Dispatch Station (Odoo 19)

**Autor:** Omar Martinez  
**Licencia:** LGPL-3  
**Compatibilidad:** Odoo 19.0 Inventario & Ventas  

---

## 📌 Descripción

**Fast Dispatch Station** es un centro de mando y verificación ultra-rápida de despacho de pedidos de venta y salidas de almacén. Permite a los operadores de empaque y logística auditar físicamente mediante lectores de código de barra el contenido de cada paquete antes de despacharlo, garantizando cero errores en envíos.

### ✨ Características Principales:
* **Escaneo Ultra-Rápido por Código de Barras:** Interfaz de alto rendimiento para validación de ítems.
* **Verificación de Cantidades:** Comparación instantánea entre la orden de venta y lo empacado físicamente.
* **Control de Mando Visual:** Pantalla completa táctil/escáner diseñada para estaciones de trabajo en almacén.
* **Validación de Entrega en 1-Clic:** Cambia el estado de despacho y notifica al cliente inmediatamente.

---

## 🛠️ Guía Paso a Paso de Uso

### Paso 1: Acceso a la Estación de Despacho
1. Vaya a **Inventario** > **Operaciones** > **Estación de Despacho Rápido**.
2. Abra la pantalla interactiva de despacho.

### Paso 2: Escaneo y Verificación de Pedidos
1. Escanee el código de barras de la Orden de Venta (`SO-XXXXX`) o albarán de entrega.
2. La pantalla cargará la lista de artículos esperados.
3. Escanee cada artículo físico que introduce en la caja de despacho.
4. El sistema marcará los ítems validados en verde.

### Paso 3: Confirmación de Salida
1. Al completar la verificación del 100% de los artículos, presione el botón **"✅ Despachar Pedido"**.

---

## 🔧 Instalación

1. Copie la carpeta `fast_dispatch_station` en su directorio de addons.
2. Vaya a **Aplicaciones** > **Actualizar lista de aplicaciones**.
3. Busque `Fast Dispatch Station` e instálelo.

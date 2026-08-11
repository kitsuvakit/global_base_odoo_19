# 📱 Mobile Presale PWA & Route Planner (Odoo 19)

**Autor:** Omar Martinez  
**Licencia:** LGPL-3  
**Compatibilidad:** Odoo 19.0 Ventas & Almacén  

---

## 📌 Descripción

**Mobile Presale PWA** permite a la fuerza de ventas en terreno (vendedores de calle) gestionar sus rutas diarias de clientes, registrar visitas georreferenciadas con coordenadas GPS, tomar pedidos desde un catálogo móvil tipo Kanban y registrar motivos de no compra.

### ✨ Características Principales:
* **Planificación de Rutas:** Asignación diaria/semanal de clientes por vendedor.
* **Captura de Coordenadas GPS:** Registro de latitud y longitud al iniciar la visita comercial.
* **Catálogo Móvil Kanban:** Visualización táctil optimizada para teléfonos celulares.
* **Prevención de Pedidos Duplicados:** Bloqueo de duplicaciones por doble clic accidental.
* **Propagación de Almacén:** Vinculación directa con el almacén configurado en la ruta.

---

## 🛠️ Guía Paso a Paso de Uso

### Paso 1: Crear y Asignar una Ruta
1. Vaya al menú **Ventas** > **Preventa Móvil** > **Rutas de Venta**.
2. Presione **Crear**, asigne el vendedor, el almacén de despacho y agregue la lista de clientes a visitar.
3. Presione el botón **"Iniciar Recorrido"**.

### Paso 2: Iniciar Visita y Tomar Pedido Móvil
1. El vendedor abre la visita correspondiente en su teléfono celular.
2. Presione **"Iniciar Visita"** para registrar la hora y las coordenadas GPS.
3. Presione **"Ver Catálogo Móvil"** para seleccionar productos e ingresar las cantidades deseadas.

### Paso 3: Registrar No Venta (Si aplica)
1. Si el cliente no compró, seleccione el **Motivo de No Compra** (*Establecimiento Cerrado*, *Tiene Inventario*, etc.) y presione **"Registrar No Venta"**.

---

## 🔧 Instalación

1. Copie la carpeta `mobile_presale_pwa` en su servidor Odoo.
2. Actualice la lista de aplicaciones e instale **Mobile Presale PWA**.

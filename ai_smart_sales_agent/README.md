# 🤖 AI Smart Sales Agent (Odoo 19)

**Autor:** Omar Martinez  
**Licencia:** LGPL-3  
**Compatibilidad:** Odoo 19.0 CRM & Ventas  

---

## 📌 Descripción

**AI Smart Sales Agent** es un asistente de ventas inteligente integrado en Odoo CRM que analiza las solicitudes de los clientes potenciales, consulta el catálogo de productos disponible y redacta cotizaciones y ofertas comerciales de forma automática utilizando modelos de Inteligencia Artificial (Google Gemini / OpenAI).

### ✨ Características Principales:
* **Sugerencia de Respuestas por IA:** Analiza el texto de la oportunidad CRM y genera un mensaje de venta personalizado.
* **Autogeneración de Presupuestos:** Crea automáticamente un pedido de venta (`sale.order`) relacionando los productos del catálogo.
* **Gestión de Tarifas y Precios:** Respeta la lista de precios del cliente seleccionado.
* **Fallbacks Inteligentes:** Crea o vincula automáticamente el cliente si no está registrado previamente.

---

## 🛠️ Guía Paso a Paso de Uso

### Paso 1: Configurar Credenciales de IA
1. Vaya a **CRM** > **Configuración** > **Agentes de IA**.
2. Seleccione el proveedor (*Google Gemini* u *OpenAI*).
3. Ingrese su API Key privada y guarde los cambios.

### Paso 2: Generar Respuesta Cotizada en Oportunidad CRM
1. Abra una Oportunidad en **CRM**.
2. Presione el botón **"🤖 Sugerir Respuesta IA"**.
3. La IA leerá la descripción del cliente y mostrará la propuesta redactada en la pestaña **Agente de Ventas IA**.

### Paso 3: Crear el Pedido de Venta
1. Presione el botón **"⚡ Autogenerar Cotización IA"**.
2. El sistema creará la orden de venta con las líneas de productos correspondientes.

---

## 🔧 Instalación

1. Copie la carpeta `ai_smart_sales_agent` en el directorio de addons de su servidor Odoo.
2. Vaya a **Aplicaciones** > **Actualizar lista de aplicaciones**.
3. Busque `AI Smart Sales Agent` e instálelo.

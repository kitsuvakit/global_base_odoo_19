# 📊 Dynamic Financial Reports Community (Odoo 19)

**Autor:** Omar Martinez  
**Licencia:** LGPL-3  
**Compatibilidad:** Odoo 19.0 Community & Enterprise  

---

## 📌 Descripción

El módulo **Dynamic Financial Reports Community** permite a las empresas generar y visualizar estados financieros interactivos en tiempo real directamente desde la interfaz web de Odoo, eliminando la necesidad de adquirir licencias Enterprise costosas para el área contable.

### ✨ Características Principales:
* **Estado de Resultados (Pérdidas y Ganancias):** Cálculo automatizado de ingresos, costos, gastos y utilidad/pérdida neta.
* **Balance General (Situación Financiera):** Presentación ejecutiva de Activos vs. Pasivos + Patrimonio.
* **Balance de Comprobación (Sumas y Saldos):** Cuadre contable de débitos, créditos y saldos netos por cuenta.
* **Filtros Flexibles:** Consulta por rango de fechas, compañía y estado de asientos (Publicados o Todos).
* **Filtro de Cierre Anual:** Opción para incluir o excluir los asientos de cierre contable de fin de año.
* **Cuentas no Clasificadas:** Identificación de cuentas pendientes de categorización.

---

## 🛠️ Guía Paso a Paso de Uso

### Paso 1: Acceso al Asistente
1. Vaya al menú **Contabilidad** o **Facturación**.
2. En el menú superior de reportes, seleccione **Reportes Dinámicos** > **Reportes Financieros**.

### Paso 2: Configuración de Parámetros
1. **Tipo de Reporte:** Seleccione *Estado de Resultados*, *Balance General* o *Balance de Comprobación*.
2. **Fecha Desde / Hasta:** Establezca el período contable que desea evaluar.
3. **Movimientos Target:** Elija *Solo Asientos Publicados* o *Todos los Asientos*.
4. **Incluir Asientos de Cierre:** Marque la casilla si desea evaluar el balance cerrado.

### Paso 3: Generación del Reporte
1. Haga clic en el botón **"👁️ Generar Reporte HTML"**.
2. La vista mostrará un cuadro dinámico interactivo con tarjetas de resumen contable (KPIs) y la tabla desglosada por cuenta contable.

---

## 🔧 Instalación

1. Copie la carpeta `dynamic_financial_reports_community` dentro del directorio de addons de su servidor Odoo.
2. Active el Modo Desarrollador en Odoo.
3. Vaya a **Aplicaciones** > **Actualizar lista de aplicaciones**.
4. Busque `Dynamic Financial Reports Community` y haga clic en **Instalar**.

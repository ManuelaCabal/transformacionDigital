# 🚀 CRM TechSolutions - Solución Integral de Digitalización

## 📋 Descripción General

Sistema completo de **CRM (Customer Relationship Management)** diseñado para **TechSolutions S.L.**, empresa del sector comercio online con 8 empleados. Soluciona las principales carencias digitales identificadas en la auditoría:

### ✅ Problemas Resueltos

| Carencia | Solución |
|----------|----------|
| ❌ No tiene CRM | ✅ Sistema CRM profesional y escalable |
| ❌ Web poco optimizada | ✅ Dashboard moderno y responsive |
| ❌ No analiza datos | ✅ Análisis avanzados y reportes en tiempo real |
| ❌ Sin automatización | ✅ Workflows automáticos de marketing |

---

## 🎯 Características Principales

### 1. **Gestión de Clientes (CRM)**
- Registro completo de clientes con seguimiento
- Estados: Activo, Prospect, Inactivo, Cliente Perdido
- Historial de interacciones (llamadas, emails, reuniones)
- Asignación a ejecutivos de ventas
- Customer Lifetime Value (CLV)
- Búsqueda y filtrado avanzado

### 2. **Gestión de Productos**
- Catálogo completo con 5 categorías
- Control de stock en tiempo real
- Precios, costos y márgenes
- 8 productos de muestra incluyendo:
  - Sistema CRM Pro (€4,999.99)
  - Consultoría Digital (€2,999.99)
  - Formación y Capacitación (€699.99)
  - Servicios de Infraestructura (€299.99-€1,299.99)
  - Marketing Digital (€1,999.99-€1,499.99)

### 3. **Gestión de Pedidos**
- Creación y seguimiento de pedidos
- Estados: Pendiente, Confirmado, Enviado, Entregado, Cancelado
- Cálculo automático de descuentos y totales
- Métodos de pago integrados
- Historial completo de pedidos por cliente

### 4. **Marketing y Campañas**
- Creación de campañas por canales:
  - Email Marketing
  - Social Media
  - Publicidad Digital
  - Promociones
- Tracking de resultados (aperturas, clicks, conversiones)
- Cálculo automático de ROI

### 5. **Analytics y Reportes**
- Dashboard con KPIs en tiempo real
- Gráficos interactivos con Chart.js:
  - Ingresos por mes
  - Estado de clientes
  - Productos más vendidos
- Análisis de cohortes
- Pipeline de ventas
- Exportación de reportes

### 6. **Automatización**
- Recordatorios de seguimiento
- Interacciones automáticas
- Reportes diarios
- Notificaciones de eventos

---

## 🗂️ Estructura del Proyecto

```
transformacionDigital/
├── app.py                      # Aplicación principal Flask
├── config.py                   # Configuración de BD
├── database.sql                # Script de base de datos (11 tablas + datos)
├── models.py                   # Modelos de datos (ampliable)
├── routers/
│   ├── users.py               # Autenticación de usuarios
│   ├── clients.py             # Gestión de clientes (CRM)
│   ├── products.py            # Catálogo de productos
│   ├── orders.py              # Gestión de pedidos
│   ├── analytics.py           # Análisis y reportes
│   └── campaigns.py           # Marketing y campañas
├── templates/
│   ├── index_landing.html     # Página de bienvenida
│   ├── dashboard.html         # Dashboard principal
│   ├── login.html             # Formulario de login
│   └── index.html             # Página inicial
├── static/
│   ├── style.css              # Estilos modernos (Tailwind + Custom)
│   └── script.js              # JavaScript (Chart.js, Fetch API)
└── README.md                   # Esta documentación
```

---

## 🏗️ Base de Datos

### Tablas Incluidas (11 tablas)

1. **employees** - 8 empleados de la empresa
2. **users** - 5 usuarios del sistema con roles
3. **clients** - 8 clientes del sector comercio online
4. **products** - 8 productos de diferentes categorías
5. **product_categories** - 5 categorías (Software, Consultoría, Formación, Infraestructura, Marketing)
6. **orders** - 7 pedidos con seguimiento completo
7. **order_items** - Detalles de cada pedido
8. **interactions** - 4 interacciones registradas con clientes
9. **marketing_campaigns** - 4 campañas de marketing
10. **campaign_results** - Resultados de campañas con ROI
11. **sales_analytics** - Métricas de ventas diarias

### Datos de Prueba Incluidos

- **8 Empleados** de diferentes departamentos (Dirección, Ventas, Marketing, Tecnología)
- **8 Clientes** activos del sector comercio online
- **7 Pedidos** con valores desde €699.99 hasta €4,999.99
- **4 Campañas** de marketing con ROI calculado
- **8 Productos** listos para vender
- **Ingresos totales simulados**: €12,999.96

---

## 🚀 Instalación y Configuración

### Requisitos Previos

```
Python 3.8+
MySQL 5.7+
pip (incluido con Python)
```

### Paso 1: Instalar Dependencias

```bash
pip install flask flask-mysqldb pymysql
```

### Paso 2: Crear Base de Datos

```bash
# Conectar a MySQL
mysql -u root -p

# Dentro de MySQL ejecutar:
SOURCE /ruta/a/database.sql;
```

### Paso 3: Configurar Conexión (config.py)

```python
class Config:
    MYSQL_HOST = '127.0.0.1'      # o 'localhost'
    MYSQL_USER = 'root'
    MYSQL_PASSWORD = 'tu_contraseña'
    MYSQL_DB = 'crm_kit'
    MYSQL_PORT = 3306
```

### Paso 4: Ejecutar la Aplicación

```bash
python app.py
```

Acceder en: **http://localhost:5000**

---

## 📡 API REST Endpoints Disponibles

### 👥 Clientes
```
GET    /api/clients/                    # Listar clientes (con búsqueda)
GET    /api/clients/<id>                # Obtener cliente con historial
POST   /api/clients/                    # Crear cliente
PUT    /api/clients/<id>                # Actualizar cliente
PUT    /api/clients/<id>/assign         # Asignar a ejecutivo
POST   /api/clients/<id>/interactions   # Registrar interacción
GET    /api/clients/analytics/summary   # Análisis resumen de clientes
```

### 📦 Productos
```
GET    /api/products/                   # Listar productos
GET    /api/products/<id>               # Obtener producto
POST   /api/products/                   # Crear producto
PUT    /api/products/<id>               # Actualizar producto
GET    /api/products/categories         # Obtener categorías
```

### 🛒 Pedidos
```
GET    /api/orders/                     # Listar pedidos
GET    /api/orders/<id>                 # Obtener pedido con items
POST   /api/orders/                     # Crear pedido
PUT    /api/orders/<id>/status          # Cambiar estado
GET    /api/orders/analytics            # Análisis de pedidos
```

### 📊 Analytics
```
GET    /api/analytics/sales             # Ventas por día
GET    /api/analytics/products          # Productos más vendidos
GET    /api/analytics/customers         # Análisis de clientes
GET    /api/analytics/campaigns         # Performance de campañas
GET    /api/analytics/pipeline          # Pipeline de ventas
GET    /api/analytics/cohort            # Análisis de cohortes
```

### 📢 Campañas
```
GET    /api/campaigns/                  # Listar campañas
GET    /api/campaigns/<id>              # Obtener campaña
POST   /api/campaigns/                  # Crear campaña
PUT    /api/campaigns/<id>              # Actualizar campaña
PUT    /api/campaigns/<id>/results      # Actualizar resultados
```

### 🔐 Dashboard
```
GET    /api/dashboard                   # Datos completos del dashboard
```

---

## 🎨 Interfaz de Usuario

### Dashboard Principal
- **4 KPIs en Tiempo Real**: 
  - Total Clientes: 8
  - Pedidos Totales: 7
  - Ingresos: €12,999.96
  - Entregados: 6

- **Gráficos Interactivos**:
  - Línea: Ingresos por mes (Chart.js)
  - Doughnut: Estado de clientes
  - Tabla: Productos top vendidos
  - Tabla: Pedidos recientes

- **Acciones Rápidas**: Crear cliente, pedido, campaña, reportes

### Diseño Visual
- **Tema**: Dark Mode profesional
- **Colores**: Gradientes azul (#3b82f6) a púrpura (#8b5cf6)
- **Framework CSS**: Tailwind CSS + Custom CSS
- **Responsive**: Mobile, tablet, desktop
- **Animaciones**: Transiciones suaves, hover effects

---

## 💻 Ejemplos de Uso

### Ejemplo 1: Crear Cliente

```javascript
fetch('/api/clients/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    name: 'Nueva Empresa',
    email: 'contacto@empresa.es',
    phone: '666123456',
    company: 'Empresa Test',
    industry: 'Comercio',
    status: 'prospect'
  })
})
```

### Ejemplo 2: Crear Pedido

```javascript
fetch('/api/orders/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    client_id: 1,
    items: [
      { product_id: 1, quantity: 1, unit_price: 4999.99 }
    ],
    discount_percentage: 10
  })
})
```

### Ejemplo 3: Obtener Analytics

```javascript
// Ventas últimos 30 días
fetch('/api/analytics/sales?days=30')

// Productos top 5
fetch('/api/analytics/products?limit=5')

// Análisis de clientes
fetch('/api/analytics/customers')
```

---

## 📈 Métricas y KPIs

### Ventas Actuales
- **Ingresos Totales**: €12,999.96
- **Número de Pedidos**: 7
- **Ticket Promedio**: €1,857.14
- **Pedidos Entregados**: 6 (85.7%)

### Clientes
- **Total de Clientes**: 8
- **Clientes Activos**: 6 (75%)
- **Prospects**: 2 (25%)
- **CLV Promedio**: €1,625

### Productos Top
1. **Sistema CRM Pro** - 1 venta = €4,999.99
2. **Auditoría IT** - 1 venta = €3,999.99
3. **Consultoría Digital** - 1 venta = €2,999.99
4. **Posicionamiento SEO** - 1 venta = €1,999.99

### Marketing
- **Campañas Activas**: 2
- **ROI Promedio**: 18.75%
- **Tasa de Conversión**: 3-6%

---

## 🔐 Seguridad Implementada

✅ Validación de entrada en formularios  
✅ Gestión de roles (Admin, Manager, User)  
✅ Autenticación por usuario/contraseña  
✅ SQL Injection Prevention (Prepared Statements)  
✅ Estructura de carpetas protegida  

### Para Producción Adicional
- [ ] Implementar JWT para APIs
- [ ] Hash de contraseñas (bcrypt)
- [ ] HTTPS/SSL
- [ ] Rate limiting
- [ ] CORS configurado
- [ ] Backups automáticos
- [ ] Logs de auditoría

---

## 📞 Información de Contacto

**TechSolutions S.L.**
- 📧 Email: info@techsolutions.es
- 📱 Teléfono: +34 600 123 456
- 📍 Ubicación: España
- 🌐 Sector: Transformación Digital

---

## 📄 Versión y Estado

**Versión**: 1.0.0  
**Estado**: ✅ Listo para Producción  
**Última actualización**: Mayo 2024  
**Ambiente**: Python Flask + MySQL  

---

## 🎓 Notas Importantes

1. **Base de Datos**: Ejecutar `database.sql` antes de iniciar
2. **Configuración**: Actualizar `config.py` con tus credenciales MySQL
3. **Dependencias**: Instalar con `pip install -r requirements.txt`
4. **Puerto**: Por defecto corre en `http://localhost:5000`
5. **Modo Debug**: Habilitado para desarrollo (cambiar para producción)

---

**Desarrollado por TechSolutions S.L.** ©️ 2024  
Solución de CRM para transformación digital de pequeñas y medianas empresas.

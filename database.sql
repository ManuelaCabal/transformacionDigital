SET FOREIGN_KEY_CHECKS = 0;
CREATE DATABASE IF NOT EXISTS crm_kit;
USE crm_kit;

-- TABLA 1: EMPLEADOS (Se elimina el campo password de aquí)
CREATE TABLE IF NOT EXISTS employees (
    id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,      -- Usado como 'username' para el login
    password VARCHAR(255) NOT NULL,           -- Aquí guardarás el hash, nunca texto plano
    position VARCHAR(50),
    department VARCHAR(50) DEFAULT 'Ventas',
    phone VARCHAR(20),
    hire_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- TABLA 2: CLIENTES
CREATE TABLE IF NOT EXISTS clients (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    phone VARCHAR(20),
    company VARCHAR(100),
    address VARCHAR(255),
    city VARCHAR(50),
    postal_code VARCHAR(10),
    country VARCHAR(50) DEFAULT 'España',
    industry VARCHAR(50),
    status ENUM('activo', 'inactivo', 'prospect', 'cliente_perdido') DEFAULT 'prospect',
    customer_lifetime_value DECIMAL(10, 2) DEFAULT 0,
    acquisition_date DATE,
    last_interaction DATE,
    notes TEXT,
    assigned_to INT,
    created_by INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (assigned_to) REFERENCES employees(id) ON DELETE SET NULL,
    FOREIGN KEY (created_by) REFERENCES employees(id) ON DELETE SET NULL
);

-- TABLA 4: CATEGORÍAS DE PRODUCTOS
CREATE TABLE IF NOT EXISTS product_categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    icon VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- TABLA 5: PRODUCTOS
CREATE TABLE IF NOT EXISTS products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    category_id INT NOT NULL,
    sku VARCHAR(50) UNIQUE,
    price DECIMAL(10, 2) NOT NULL,
    cost DECIMAL(10, 2),
    stock INT DEFAULT 0,
    image_url VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES product_categories(id) ON DELETE RESTRICT
);

-- TABLA 6: PEDIDOS
CREATE TABLE IF NOT EXISTS orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    client_id INT NOT NULL,
    order_number VARCHAR(20) UNIQUE NOT NULL,
    order_date DATE NOT NULL,
    delivery_date DATE,
    status ENUM('pendiente', 'confirmado', 'enviado', 'entregado', 'cancelado') DEFAULT 'pendiente',
    total_amount DECIMAL(10, 2) NOT NULL,
    discount_percentage DECIMAL(5, 2) DEFAULT 0,
    final_amount DECIMAL(10, 2) NOT NULL,
    payment_method ENUM('tarjeta', 'transferencia', 'efectivo', 'otros') DEFAULT 'transferencia',
    payment_status ENUM('pendiente', 'pagado', 'parcial') DEFAULT 'pendiente',
    assigned_to INT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (client_id) REFERENCES clients(id) ON DELETE RESTRICT,
    FOREIGN KEY (assigned_to) REFERENCES employees(id) ON DELETE SET NULL
);

-- TABLA 7: DETALLES DE PEDIDOS
CREATE TABLE IF NOT EXISTS order_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL,
    unit_price DECIMAL(10, 2) NOT NULL,
    line_total DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE RESTRICT
);

-- TABLA 8: INTERACCIONES CON CLIENTES
CREATE TABLE IF NOT EXISTS interactions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    client_id INT NOT NULL,
    type ENUM('llamada', 'email', 'reunion', 'nota', 'visita') NOT NULL,
    subject VARCHAR(255),
    description TEXT,
    duration_minutes INT,
    result ENUM('positivo', 'negativo', 'neutral', 'seguimiento_requerido'),
    next_follow_up DATE,
    created_by INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (client_id) REFERENCES clients(id) ON DELETE CASCADE,
    FOREIGN KEY (created_by) REFERENCES employees(id) ON DELETE CASCADE
);

-- TABLA 9: CAMPAÑAS DE MARKETING
CREATE TABLE IF NOT EXISTS marketing_campaigns (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    campaign_type ENUM('email', 'social_media', 'publicidad', 'promocion', 'otros') NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE,
    budget DECIMAL(10, 2),
    target_audience VARCHAR(255),
    status ENUM('planeada', 'en_curso', 'completada', 'cancelada') DEFAULT 'planeada',
    created_by INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES employees(id) ON DELETE CASCADE
);

-- TABLA 10: RESULTADOS DE CAMPAÑAS
CREATE TABLE IF NOT EXISTS campaign_results (
    id INT AUTO_INCREMENT PRIMARY KEY,
    campaign_id INT NOT NULL,
    total_contacts INT DEFAULT 0,
    total_opens INT DEFAULT 0,
    total_clicks INT DEFAULT 0,
    total_conversions INT DEFAULT 0,
    revenue_generated DECIMAL(10, 2) DEFAULT 0,
    roi DECIMAL(5, 2) DEFAULT 0,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (campaign_id) REFERENCES marketing_campaigns(id) ON DELETE CASCADE
);

-- TABLA 11: ANÁLISIS Y MÉTRICAS
CREATE TABLE IF NOT EXISTS sales_analytics (
    id INT AUTO_INCREMENT PRIMARY KEY,
    date DATE UNIQUE NOT NULL,
    total_orders INT DEFAULT 0,
    total_revenue DECIMAL(10, 2) DEFAULT 0,
    average_order_value DECIMAL(10, 2) DEFAULT 0,
    new_customers INT DEFAULT 0,
    returning_customers INT DEFAULT 0,
    conversion_rate DECIMAL(5, 2) DEFAULT 0,
    top_product_id INT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (top_product_id) REFERENCES products(id) ON DELETE SET NULL
);

-- INSERTAR DATOS DE PRUEBA (Sin contraseñas en employees)
INSERT INTO employees (first_name, last_name, position, department, email, phone, hire_date, password) VALUES
('Manuela', 'Cabal', 'Directora de Digitalización', 'Dirección', 'manuela@techsolutions.es', '600123456', '2020-01-15', '$2b$12$2MNgGsYg5Bd7PpIwcRqLReqqnxyIsvS8lvBkXaFF4uVL06zT9pBne'),
('Juan', 'García', 'Gerente de Ventas', 'Ventas', 'juan@techsolutions.es', '600123457', '2021-03-10', '$2b$12$2MNgGsYg5Bd7PpIwcRqLReqqnxyIsvS8lvBkXaFF4uVL06zT9pBne');

SET FOREIGN_KEY_CHECKS = 1;
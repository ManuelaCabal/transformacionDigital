import os
import pymysql
pymysql.install_as_MySQLdb()

from flask import Flask, render_template, jsonify, request, session, redirect, url_for
from flask_mysqldb import MySQL
from config import Config
import bcrypt
from flask import Flask, request, jsonify, session
from flask_mysqldb import MySQL
import bcrypt
from flask import Flask, jsonify, request
from flask_mysqldb import MySQL
import MySQLdb.cursors

app = Flask(__name__)
app.secret_key = 'tu_llave_secreta_muy_segura' # ¡INDISPENSABLE para sesiones!

# ... resto de tu configuración de MySQL ...

app = Flask(__name__)
app.config.from_object(Config)

# Configurar MySQL
mysql = MySQL(app)

app.secret_key = 'your_secret_key_here'  # Cambiar por una clave segura
# 1. API para la Gráfica de Líneas (Evolución de Ventas)
@app.route('/api/analytics/sales')
def get_sales_analytics():
    # Obtenemos los días desde el parámetro ?days=30 del JS
    days = request.args.get('days', 30)
    
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    # Esta consulta suma el total de pedidos agrupados por día
    query = """
        SELECT DATE(order_date) as date, SUM(final_amount) as revenue 
        FROM orders 
        WHERE order_date >= DATE_SUB(CURDATE(), INTERVAL %s DAY)
        GROUP BY DATE(order_date)
        ORDER BY date DESC
    """
    cursor.execute(query, (int(days),))
    data = cursor.fetchall()
    cursor.close()
    
    # Si no hay datos, enviamos una lista vacía para que Chart.js no falle
    return jsonify(data)

# 2. API para la Gráfica de Barras (Top Clientes)
@app.route('/api/analytics/customers')
def get_customer_analytics():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    # Traemos los clientes y sumamos sus compras para calcular su Valor de Vida (LTV)
    query = """
        SELECT c.name, SUM(o.final_amount) as customer_lifetime_value
        FROM clients c
        JOIN orders o ON c.id = o.client_id
        GROUP BY c.id
        ORDER BY customer_lifetime_value DESC
        LIMIT 5
    """
    cursor.execute(query)
    top_clients = cursor.fetchall()
    cursor.close()
    
    return jsonify({"top_clients": top_clients})

# 3. API para la Tabla de Productos (Rendimiento)
@app.route('/api/products/')
def get_products_performance():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    # Traemos datos básicos de productos para llenar la tabla
    cursor.execute("SELECT name, price, stock FROM products LIMIT 5")
    products = cursor.fetchall()
    cursor.close()
    return jsonify(products)

@app.route('/')
def index():
    return render_template('index_landing.html')

@app.route('/dashboard')
def dashboard_page():
    return render_template('dashboard.html')


# Rutas para páginas CRM (plantillas)
@app.route('/clients')
def clients_page():
    return render_template('clients.html')


@app.route('/products')
def products_page():
    return render_template('products.html')


@app.route('/orders')
def orders_page():
    return render_template('orders.html')


@app.route('/campaigns')
def campaigns_page():
    return render_template('campaigns.html')


@app.route('/reports')
def reports_page():
    return render_template('reports.html')


@app.route('/api/debug/status', methods=['GET'])
def debug_status():
    try:
        import pymysql
        from app import mysql
        cursor = mysql.connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT COUNT(*) as total_clients FROM clients")
        clients_count = cursor.fetchone().get('total_clients', 0)
        cursor.execute("SELECT COUNT(*) as total_products FROM products")
        products_count = cursor.fetchone().get('total_products', 0)
        cursor.close()
        return jsonify({"db": "ok", "clients": clients_count, "products": products_count}), 200
    except Exception as e:
        return jsonify({"db": "error", "error": str(e)}), 500
@app.route('/api/dashboard', methods=['GET'])
def dashboard():
    """Endpoint para obtener datos del dashboard"""
    try:
        from app import mysql
        import pymysql
        cursor = mysql.connection.cursor(pymysql.cursors.DictCursor)
        
        # Estadísticas generales
        cursor.execute("""
            SELECT 
                (SELECT COUNT(*) FROM clients) as total_clients,
                (SELECT COUNT(*) FROM orders) as total_orders,
                (SELECT SUM(final_amount) FROM orders) as total_revenue,
                (SELECT COUNT(*) FROM orders WHERE status='entregado') as delivered_orders
        """)
        stats = cursor.fetchone()
        
        # Top productos
        cursor.execute("""
            SELECT p.name, SUM(oi.quantity) as total_sold, SUM(oi.line_total) as revenue
            FROM order_items oi
            JOIN products p ON oi.product_id = p.id
            GROUP BY oi.product_id
            ORDER BY total_sold DESC LIMIT 5
        """)
        top_products = cursor.fetchall()
        
        # Clientes por estado
        cursor.execute("""
            SELECT status, COUNT(*) as count FROM clients GROUP BY status
        """)
        clients_by_status = cursor.fetchall()
        
        cursor.close()
        return jsonify({
            "stats": stats,
            "top_products": top_products,
            "clients_by_status": clients_by_status
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Registrar blueprints
from routers.users import users_bp
from routers.clients import clients_bp
from routers.products import products_bp
from routers.orders import orders_bp
from routers.analytics import analytics_bp
from routers.campaigns import campaigns_bp
from routers.employees import employees_bp

app.register_blueprint(users_bp, url_prefix='/api/users')
app.register_blueprint(clients_bp, url_prefix='/api/clients')
app.register_blueprint(products_bp, url_prefix='/api/products')
app.register_blueprint(orders_bp, url_prefix='/api/orders')
app.register_blueprint(analytics_bp, url_prefix='/api/analytics')
app.register_blueprint(campaigns_bp, url_prefix='/api/campaigns')
app.register_blueprint(employees_bp, url_prefix='/api/employees')


@app.route('/employees')
def employees_page():
    return render_template('employees.html')

@app.route('/login', methods=['GET'])
def login_page():
    return render_template('login.html')

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    cursor = mysql.connection.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT id, password FROM employees WHERE email = %s", (username,))
    employee = cursor.fetchone()
    cursor.close()

    if employee and bcrypt.checkpw(password.encode('utf-8'), employee['password'].encode('utf-8')):
        session['employee_id'] = employee['id']
        return jsonify({"message": "Login exitoso"}), 200
    else:
        return jsonify({"message": "Credenciales incorrectas"}), 401

@app.before_request
def require_login():
    if request.endpoint in ['dashboard_page', 'clients_page', 'products_page', 'orders_page', 'campaigns_page', 'reports_page', 'employees_page'] and 'employee_id' not in session:
        return redirect(url_for('login_page'))

@app.route('/logout', methods=['GET'])
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False, threaded=True)
from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
import pymysql
from app import mysql

analytics_bp = Blueprint('analytics', __name__)

@analytics_bp.route('/sales', methods=['GET'])
def get_sales_analytics():
    """Obtener análisis de ventas"""
    try:
        cursor = mysql.connection.cursor(pymysql.cursors.DictCursor)
        
        days = request.args.get('days', 30, type=int)
        
        cursor.execute("""
            SELECT 
                DATE(order_date) as date,
                COUNT(*) as orders,
                SUM(final_amount) as revenue,
                AVG(final_amount) as avg_order,
                COUNT(DISTINCT client_id) as unique_clients
            FROM orders
            WHERE order_date >= DATE_SUB(NOW(), INTERVAL %s DAY)
            GROUP BY DATE(order_date)
            ORDER BY date DESC
        """, (days,))
        
        data = cursor.fetchall()
        cursor.close()
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@analytics_bp.route('/products', methods=['GET'])
def get_product_analytics():
    """Obtener análisis de productos más vendidos"""
    try:
        cursor = mysql.connection.cursor(pymysql.cursors.DictCursor)
        
        limit = request.args.get('limit', 10, type=int)
        
        cursor.execute("""
            SELECT 
                p.id,
                p.name,
                p.category_id,
                SUM(oi.quantity) as total_sold,
                SUM(oi.line_total) as total_revenue,
                ROUND(AVG(p.price), 2) as avg_price,
                COUNT(DISTINCT oi.order_id) as orders
            FROM order_items oi
            JOIN products p ON oi.product_id = p.id
            GROUP BY p.id
            ORDER BY total_revenue DESC
            LIMIT %s
        """, (limit,))
        
        data = cursor.fetchall()
        cursor.close()
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@analytics_bp.route('/customers', methods=['GET'])
def get_customer_analytics():
    """Obtener análisis de clientes"""
    try:
        cursor = mysql.connection.cursor(pymysql.cursors.DictCursor)
        
        cursor.execute("""
            SELECT 
                COUNT(*) as total_customers,
                COUNT(CASE WHEN status='activo' THEN 1 END) as active,
                COUNT(CASE WHEN status='prospect' THEN 1 END) as prospects,
                COUNT(CASE WHEN status='inactivo' THEN 1 END) as inactive,
                ROUND(AVG(customer_lifetime_value), 2) as avg_ltv,
                MAX(customer_lifetime_value) as max_ltv,
                SUM(customer_lifetime_value) as total_ltv
            FROM clients
        """)
        
        stats = cursor.fetchone()
        
        # Clientes top por valor
        cursor.execute("""
            SELECT id, name, email, customer_lifetime_value, status
            FROM clients
            ORDER BY customer_lifetime_value DESC
            LIMIT 10
        """)
        
        top_clients = cursor.fetchall()
        cursor.close()
        
        return jsonify({"stats": stats, "top_clients": top_clients}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@analytics_bp.route('/campaigns', methods=['GET'])
def get_campaign_analytics():
    """Obtener análisis de campañas de marketing"""
    try:
        cursor = mysql.connection.cursor(pymysql.cursors.DictCursor)
        
        cursor.execute("""
            SELECT 
                mc.id,
                mc.name,
                mc.campaign_type,
                mc.status,
                mc.budget,
                cr.total_contacts,
                cr.total_opens,
                cr.total_clicks,
                cr.total_conversions,
                cr.revenue_generated,
                cr.roi,
                ROUND((cr.total_opens / cr.total_contacts * 100), 2) as open_rate,
                ROUND((cr.total_clicks / cr.total_contacts * 100), 2) as click_rate,
                ROUND((cr.total_conversions / cr.total_contacts * 100), 2) as conversion_rate
            FROM marketing_campaigns mc
            LEFT JOIN campaign_results cr ON mc.id = cr.campaign_id
            ORDER BY mc.created_at DESC
        """)
        
        data = cursor.fetchall()
        cursor.close()
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@analytics_bp.route('/pipeline', methods=['GET'])
def get_sales_pipeline():
    """Obtener pipeline de ventas por estado"""
    try:
        cursor = mysql.connection.cursor(pymysql.cursors.DictCursor)
        
        cursor.execute("""
            SELECT 
                status,
                COUNT(*) as count,
                SUM(final_amount) as total_value,
                ROUND(AVG(final_amount), 2) as avg_value
            FROM orders
            GROUP BY status
        """)
        
        data = cursor.fetchall()
        cursor.close()
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@analytics_bp.route('/cohort', methods=['GET'])
def get_cohort_analysis():
    """Análisis de cohortes de clientes"""
    try:
        cursor = mysql.connection.cursor()
        
        cursor.execute("""
            SELECT 
                DATE_FORMAT(acquisition_date, '%Y-%m') as cohort,
                COUNT(*) as customers,
                SUM(CASE WHEN status='activo' THEN 1 ELSE 0 END) as retained,
                ROUND(SUM(customer_lifetime_value) / COUNT(*), 2) as avg_ltv
            FROM clients
            WHERE acquisition_date IS NOT NULL
            GROUP BY DATE_FORMAT(acquisition_date, '%Y-%m')
            ORDER BY cohort DESC
        """)
        
        data = cursor.fetchall()
        cursor.close()
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@analytics_bp.route('/export/pdf', methods=['POST'])
def export_report_pdf():
    """Exportar reporte en PDF"""
    try:
        # Esta funcionalidad requeriría librería como ReportLab
        return jsonify({"message": "Funcionalidad disponible próximamente"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@analytics_bp.route('/analytics/sales', methods=['GET'])
def get_sales_data():
    days = request.args.get('days', 30, type=int)
    cursor = mysql.connection.cursor()
    query = """
        SELECT DATE(order_date) as date, SUM(final_amount) as revenue
        FROM orders
        WHERE order_date >= CURDATE() - INTERVAL %s DAY
        GROUP BY DATE(order_date)
        ORDER BY DATE(order_date) ASC
    """
    cursor.execute(query, (days,))
    data = cursor.fetchall()
    cursor.close()
    return jsonify(data)

@analytics_bp.route('/analytics/customers', methods=['GET'])
def get_top_customers():
    cursor = mysql.connection.cursor()
    query = """
        SELECT name, customer_lifetime_value
        FROM clients
        ORDER BY customer_lifetime_value DESC
        LIMIT 5
    """
    cursor.execute(query)
    data = cursor.fetchall()
    cursor.close()
    return jsonify({"top_clients": data})

@analytics_bp.route('/analytics/products', methods=['GET'])
def get_product_performance():
    cursor = mysql.connection.cursor()
    query = """
        SELECT p.name, SUM(oi.quantity) as total_sold, SUM(oi.line_total) as revenue
        FROM order_items oi
        JOIN products p ON oi.product_id = p.id
        GROUP BY oi.product_id
        ORDER BY total_sold DESC
        LIMIT 10
    """
    cursor.execute(query)
    data = cursor.fetchall()
    cursor.close()
    return jsonify(data)

@analytics_bp.route('/analytics/categories', methods=['GET'])
def get_categories():
    cursor = mysql.connection.cursor()
    query = "SELECT id, name FROM product_categories ORDER BY name ASC"
    cursor.execute(query)
    data = cursor.fetchall()
    cursor.close()
    return jsonify(data)

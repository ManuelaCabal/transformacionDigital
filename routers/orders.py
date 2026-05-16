from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
import pymysql

orders_bp = Blueprint('orders', __name__)

@orders_bp.route('/', methods=['GET'])
def get_orders():
    """Obtener todos los pedidos con filtros opcionales"""
    try:
        from app import mysql
        cursor = mysql.connection.cursor(pymysql.cursors.DictCursor)
        
        status = request.args.get('status')
        client_id = request.args.get('client_id')
        
        query = """
            SELECT o.*, c.name as client_name, c.email as client_email 
            FROM orders o 
            JOIN clients c ON o.client_id = c.id 
            WHERE 1=1
        """
        params = []
        
        if status:
            query += " AND o.status = %s"
            params.append(status)
        if client_id:
            query += " AND o.client_id = %s"
            params.append(client_id)
            
        query += " ORDER BY o.order_date DESC LIMIT 100"
        cursor.execute(query, params)
        data = cursor.fetchall()
        cursor.close()
        return jsonify({"orders": data}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@orders_bp.route('/<int:order_id>', methods=['GET'])
def get_order(order_id):
    """Obtener detalles de un pedido"""
    try:
        from app import mysql
        cursor = mysql.connection.cursor(pymysql.cursors.DictCursor)
        
        # Obtener pedido
        cursor.execute("""
            SELECT o.*, c.name as client_name, c.email as client_email 
            FROM orders o 
            JOIN clients c ON o.client_id = c.id 
            WHERE o.id = %s
        """, (order_id,))
        order = cursor.fetchone()
        
        # Obtener items
        cursor.execute("""
            SELECT oi.*, p.name as product_name 
            FROM order_items oi 
            JOIN products p ON oi.product_id = p.id 
            WHERE oi.order_id = %s
        """, (order_id,))
        items = cursor.fetchall()
        cursor.close()
        
        if order:
            return jsonify({"order": order, "items": items}), 200
        return jsonify({"error": "Pedido no encontrado"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@orders_bp.route('/', methods=['POST'])
def create_order():
    """Crear nuevo pedido"""
    try:
        data = request.json
        from app import mysql
        cursor = mysql.connection.cursor(pymysql.cursors.DictCursor)
        
        # Generar número de pedido
        order_number = f"PED-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Crear pedido
        cursor.execute("""
            INSERT INTO orders (client_id, order_number, order_date, status, total_amount, final_amount, payment_method)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            data['client_id'], order_number, datetime.now().date(), 
            data.get('status', 'pendiente'), 0, 0, data.get('payment_method', 'transferencia')
        ))
        mysql.connection.commit()
        order_id = cursor.lastrowid
        
        # Insertar items
        total = 0
        if 'items' in data:
            for item in data['items']:
                line_total = item['quantity'] * item['unit_price']
                cursor.execute("""
                    INSERT INTO order_items (order_id, product_id, quantity, unit_price, line_total)
                    VALUES (%s, %s, %s, %s, %s)
                """, (order_id, item['product_id'], item['quantity'], item['unit_price'], line_total))
                total += line_total
        
        # Actualizar total del pedido
        discount = data.get('discount_percentage', 0)
        final = total * (1 - discount/100)
        cursor.execute("""
            UPDATE orders SET total_amount=%s, discount_percentage=%s, final_amount=%s WHERE id=%s
        """, (total, discount, final, order_id))
        mysql.connection.commit()
        cursor.close()
        
        return jsonify({"id": order_id, "order_number": order_number, "message": "Pedido creado"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@orders_bp.route('/<int:order_id>', methods=['DELETE'])
def delete_order(order_id):
    """Eliminar pedido"""
    try:
        from app import mysql
        cursor = mysql.connection.cursor(pymysql.cursors.DictCursor)
        # eliminar items primero
        cursor.execute("DELETE FROM order_items WHERE order_id = %s", (order_id,))
        cursor.execute("DELETE FROM orders WHERE id = %s", (order_id,))
        mysql.connection.commit()
        cursor.close()
        return jsonify({"message": "Pedido eliminado"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@orders_bp.route('/<int:order_id>/status', methods=['PUT'])
def update_order_status(order_id):
    """Actualizar estado del pedido"""
    try:
        data = request.json
        from app import mysql
        cursor = mysql.connection.cursor()
        cursor.execute("""
            UPDATE orders SET status=%s, updated_at=NOW() WHERE id=%s
        """, (data['status'], order_id))
        mysql.connection.commit()
        cursor.close()
        return jsonify({"message": "Estado actualizado"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@orders_bp.route('/analytics', methods=['GET'])
def get_orders_analytics():
    """Obtener análisis de pedidos"""
    try:
        from app import mysql
        cursor = mysql.connection.cursor()
        
        # Últimos 30 días
        days = request.args.get('days', 30)
        
        cursor.execute("""
            SELECT 
                COUNT(*) as total_orders,
                SUM(final_amount) as total_revenue,
                AVG(final_amount) as avg_order_value,
                COUNT(DISTINCT client_id) as unique_customers
            FROM orders 
            WHERE order_date >= DATE_SUB(NOW(), INTERVAL %s DAY)
        """, (days,))
        
        data = cursor.fetchone()
        cursor.close()
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

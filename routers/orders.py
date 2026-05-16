from flask import Blueprint, request, jsonify
from datetime import datetime
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
    """Crear nuevo pedido con validaciones de claves de producto"""
    try:
        data = request.json or {}
        
        if 'client_id' not in data:
            return jsonify({"error": "Falta el campo obligatorio 'client_id'"}), 400
            
        from app import mysql
        cursor = mysql.connection.cursor(pymysql.cursors.DictCursor)
        
        # Generar número de pedido DecoHOME
        order_number = f"PED-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Crear la cabecera del pedido inicializada en 0
        cursor.execute("""
            INSERT INTO orders (client_id, order_number, order_date, status, total_amount, final_amount, payment_method)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            data['client_id'], order_number, datetime.now().date(), 
            data.get('status', 'pendiente'), 0, 0, data.get('payment_method', 'transferencia')
        ))
        mysql.connection.commit()
        order_id = cursor.lastrowid
        
        total = 0
        items_procesados = 0
        
        # Insertar e iterar de forma segura sobre los productos del carrito
        if 'items' in data and isinstance(data['items'], list):
            for item in data['items']:
                # Validación crítica: Extraer el ID buscando variaciones comunes del frontend
                product_id = item.get('product_id') or item.get('id') or item.get('id_producto')
                quantity = int(item.get('quantity', 0))
                unit_price = float(item.get('unit_price') or item.get('price', 0))
                
                # Si no hay ID de producto válido, saltamos la línea para evitar el error 1048
                if not product_id or quantity <= 0:
                    continue
                    
                line_total = quantity * unit_price
                
                cursor.execute("""
                    INSERT INTO order_items (order_id, product_id, quantity, unit_price, line_total)
                    VALUES (%s, %s, %s, %s, %s)
                """, (order_id, product_id, quantity, unit_price, line_total))
                
                total += line_total
                items_procesados += 1
        
        # Si no se pudo procesar ningún artículo válido, revertimos el pedido vacío
        if items_procesados == 0:
            cursor.execute("DELETE FROM orders WHERE id = %s", (order_id,))
            mysql.connection.commit()
            cursor.close()
            return jsonify({"error": "No se enviaron productos válidos con un 'product_id' definido."}), 400
            
        # Calcular descuentos finales del pedido
        discount = float(data.get('discount_percentage', 0))
        final = total * (1 - discount / 100)
        
        cursor.execute("""
            UPDATE orders SET total_amount=%s, discount_percentage=%s, final_amount=%s WHERE id=%s
        """, (total, discount, final, order_id))
        
        mysql.connection.commit()
        cursor.close()
        
        return jsonify({"id": order_id, "order_number": order_number, "message": "Pedido creado con éxito"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@orders_bp.route('/<int:order_id>', methods=['DELETE'])
def delete_order(order_id):
    """Eliminar pedido"""
    try:
        from app import mysql
        cursor = mysql.connection.cursor(pymysql.cursors.DictCursor)
        # eliminar items primero por restricciones FK
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
    """Obtener análisis de pedidos estructurado en formato clave-valor"""
    try:
        from app import mysql
        cursor = mysql.connection.cursor(pymysql.cursors.DictCursor)
        
        days = request.args.get('days', 30)
        
        cursor.execute("""
            SELECT 
                COUNT(*) as total_orders,
                COALESCE(SUM(final_amount), 0) as total_revenue,
                COALESCE(AVG(final_amount), 0) as avg_order_value,
                COUNT(DISTINCT client_id) as unique_customers
            FROM orders 
            WHERE order_date >= DATE_SUB(NOW(), INTERVAL %s DAY)
        """, (days,))
        
        data = cursor.fetchone()
        cursor.close()
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
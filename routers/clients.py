from flask import Blueprint, request, jsonify
from datetime import datetime
import pymysql

clients_bp = Blueprint('clients', __name__)

@clients_bp.route('/', methods=['GET'])
def get_clients():
    """Obtener todos los clientes con búsqueda y filtros"""
    try:
        from app import mysql
        cursor = mysql.connection.cursor(pymysql.cursors.DictCursor)
        
        # Parámetros de búsqueda y filtrado
        search = request.args.get('search', '')
        status = request.args.get('status', '')
        limit = request.args.get('limit', 50)
        offset = request.args.get('offset', 0)
        
        query = "SELECT * FROM clients WHERE 1=1"
        params = []
        
        if search:
            query += " AND (name LIKE %s OR email LIKE %s OR company LIKE %s)"
            search_term = f"%{search}%"
            params.extend([search_term, search_term, search_term])
        
        if status:
            query += " AND status = %s"
            params.append(status)
        
        query += f" ORDER BY created_at DESC LIMIT {limit} OFFSET {offset}"
        cursor.execute(query, params)
        clients = cursor.fetchall()
        
        # Contar total
        count_query = "SELECT COUNT(*) as total FROM clients WHERE 1=1"
        if search:
            count_query += " AND (name LIKE %s OR email LIKE %s OR company LIKE %s)"
            cursor.execute(count_query, params[:3] if search else [])
        else:
            cursor.execute(count_query)
        
        total = cursor.fetchone()['total']
        cursor.close()
        
        return jsonify({"clients": clients, "total": total, "limit": limit, "offset": offset}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@clients_bp.route('/<int:client_id>', methods=['GET'])
def get_client(client_id):
    """Obtener detalles de un cliente"""
    try:
        from app import mysql
        cursor = mysql.connection.cursor(pymysql.cursors.DictCursor)
        
        cursor.execute("SELECT * FROM clients WHERE id = %s", (client_id,))
        client = cursor.fetchone()
        
        if not client:
            cursor.close()
            return jsonify({"error": "Cliente no encontrado"}), 404
        
        # Obtener pedidos del cliente
        cursor.execute("""
            SELECT id, order_number, order_date, status, final_amount 
            FROM orders WHERE client_id = %s 
            ORDER BY order_date DESC LIMIT 10
        """, (client_id,))
        orders = cursor.fetchall()
        
        # Obtener interacciones
        cursor.execute("""
            SELECT id, type, subject, created_at, result 
            FROM interactions WHERE client_id = %s 
            ORDER BY created_at DESC LIMIT 10
        """, (client_id,))
        interactions = cursor.fetchall()
        
        cursor.close()
        return jsonify({
            "client": client, 
            "recent_orders": orders,
            "recent_interactions": interactions
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@clients_bp.route('/', methods=['POST'])
def add_client():
    """Crear nuevo cliente"""
    try:
        data = request.json
        from app import mysql
        cursor = mysql.connection.cursor(pymysql.cursors.DictCursor)
        
        cursor.execute("""
            INSERT INTO clients (name, email, phone, company, address, city, postal_code, 
                                country, industry, status, acquisition_date, created_by)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            data['name'], data['email'], data.get('phone'), data.get('company'),
            data.get('address'), data.get('city'), data.get('postal_code'),
            data.get('country', 'España'), data.get('industry'),
            data.get('status', 'prospect'), datetime.now().date(), data.get('created_by', 1)
        ))
        mysql.connection.commit()
        client_id = cursor.lastrowid
        cursor.close()
        
        return jsonify({"id": client_id, "message": "Cliente añadido correctamente"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@clients_bp.route('/<int:client_id>', methods=['PUT'])
def update_client(client_id):
    """Actualizar información del cliente"""
    try:
        data = request.json
        from app import mysql
        cursor = mysql.connection.cursor(pymysql.cursors.DictCursor)
        
        cursor.execute("""
            UPDATE clients 
            SET name=%s, email=%s, phone=%s, company=%s, address=%s, 
                city=%s, postal_code=%s, industry=%s, status=%s, updated_at=NOW()
            WHERE id=%s
        """, (
            data.get('name'), data.get('email'), data.get('phone'), data.get('company'),
            data.get('address'), data.get('city'), data.get('postal_code'),
            data.get('industry'), data.get('status'), client_id
        ))
        mysql.connection.commit()
        cursor.close()
        
        return jsonify({"message": "Cliente actualizado"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@clients_bp.route('/<int:client_id>', methods=['DELETE'])
def delete_client(client_id):
    """Eliminar cliente"""
    try:
        from app import mysql
        cursor = mysql.connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute("DELETE FROM clients WHERE id = %s", (client_id,))
        mysql.connection.commit()
        cursor.close()
        return jsonify({"message": "Cliente eliminado"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@clients_bp.route('/<int:client_id>/assign', methods=['PUT'])
def assign_client(client_id):
    """Asignar cliente a un ejecutivo"""
    try:
        data = request.json
        from app import mysql
        cursor = mysql.connection.cursor()
        
        cursor.execute("""
            UPDATE clients SET assigned_to=%s, updated_at=NOW() WHERE id=%s
        """, (data['assigned_to'], client_id))
        mysql.connection.commit()
        cursor.close()
        
        return jsonify({"message": "Cliente asignado"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@clients_bp.route('/<int:client_id>/interactions', methods=['POST'])
def add_interaction(client_id):
    """Registrar interacción con cliente"""
    try:
        data = request.json
        from app import mysql
        cursor = mysql.connection.cursor()
        
        cursor.execute("""
            INSERT INTO interactions (client_id, type, subject, description, result, next_follow_up, created_by)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            client_id, data['type'], data.get('subject'), data.get('description'),
            data.get('result'), data.get('next_follow_up'), data.get('created_by', 1)
        ))
        mysql.connection.commit()
        cursor.close()
        
        return jsonify({"message": "Interacción registrada"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@clients_bp.route('/analytics/summary', methods=['GET'])
def get_clients_analytics():
    """Obtener resumen analítico de clientes"""
    try:
        from app import mysql
        cursor = mysql.connection.cursor()
        
        cursor.execute("""
            SELECT 
                COUNT(*) as total_clients,
                SUM(CASE WHEN status='activo' THEN 1 ELSE 0 END) as active_clients,
                SUM(CASE WHEN status='prospect' THEN 1 ELSE 0 END) as prospects,
                ROUND(AVG(customer_lifetime_value), 2) as avg_ltv,
                SUM(customer_lifetime_value) as total_ltv
            FROM clients
        """)
        data = cursor.fetchone()
        cursor.close()
        
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
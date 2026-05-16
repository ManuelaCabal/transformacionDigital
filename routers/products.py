from flask import Blueprint, request, jsonify
from datetime import datetime

products_bp = Blueprint('products', __name__)

@products_bp.route('/', methods=['GET'])
def get_products():
    """Obtener todos los productos con filtros opcionales"""
    try:
        from app import mysql
        cursor = mysql.connection.cursor()
        
        # Filtros opcionales
        category_id = request.args.get('category_id')
        is_active = request.args.get('is_active', True)
        
        query = "SELECT p.*, c.name as category_name FROM products p JOIN product_categories c ON p.category_id = c.id WHERE p.is_active = %s"
        params = [is_active]
        
        if category_id:
            query += " AND p.category_id = %s"
            params.append(category_id)
            
        query += " ORDER BY p.name ASC"
        cursor.execute(query, params)
        data = cursor.fetchall()
        cursor.close()
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@products_bp.route('/<int:product_id>', methods=['GET'])
def get_product(product_id):
    """Obtener detalles de un producto específico"""
    try:
        from app import mysql
        cursor = mysql.connection.cursor()
        cursor.execute("""
            SELECT p.*, c.name as category_name FROM products p 
            JOIN product_categories c ON p.category_id = c.id 
            WHERE p.id = %s
        """, (product_id,))
        data = cursor.fetchone()
        cursor.close()
        if data:
            return jsonify(data), 200
        return jsonify({"error": "Producto no encontrado"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@products_bp.route('/', methods=['POST'])
def create_product():
    """Crear nuevo producto"""
    try:
        data = request.json
        from app import mysql
        cursor = mysql.connection.cursor()
        cursor.execute("""
            INSERT INTO products (name, description, category_id, sku, price, cost, stock, is_active)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            data['name'], data.get('description'), data['category_id'],
            data['sku'], data['price'], data.get('cost'),
            data.get('stock', 0), data.get('is_active', True)
        ))
        mysql.connection.commit()
        product_id = cursor.lastrowid
        cursor.close()
        return jsonify({"id": product_id, "message": "Producto creado exitosamente"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@products_bp.route('/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    """Actualizar producto"""
    try:
        data = request.json
        from app import mysql
        cursor = mysql.connection.cursor()
        cursor.execute("""
            UPDATE products SET name=%s, description=%s, price=%s, cost=%s, stock=%s, is_active=%s
            WHERE id=%s
        """, (data['name'], data.get('description'), data['price'], data.get('cost'), 
              data.get('stock'), data.get('is_active'), product_id))
        mysql.connection.commit()
        cursor.close()
        return jsonify({"message": "Producto actualizado"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@products_bp.route('/categories', methods=['GET'])
def get_categories():
    """Obtener todas las categorías"""
    try:
        from app import mysql
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM product_categories ORDER BY name ASC")
        data = cursor.fetchall()
        cursor.close()
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
from flask import Blueprint, request, jsonify
from datetime import datetime
import pymysql

employees_bp = Blueprint('employees', __name__)


@employees_bp.route('/', methods=['GET'])
def get_employees():
    try:
        from app import mysql
        cursor = mysql.connection.cursor(pymysql.cursors.DictCursor)

        search = request.args.get('search', '')
        query = "SELECT * FROM employees WHERE 1=1"
        params = []
        if search:
            query += " AND (first_name LIKE %s OR last_name LIKE %s OR email LIKE %s)"
            term = f"%{search}%"
            params.extend([term, term, term])

        query += " ORDER BY created_at DESC LIMIT 500"
        cursor.execute(query, params)
        data = cursor.fetchall()
        cursor.close()
        return jsonify({"employees": data}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@employees_bp.route('/<int:employee_id>', methods=['GET'])
def get_employee(employee_id):
    try:
        from app import mysql
        cursor = mysql.connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT * FROM employees WHERE id = %s", (employee_id,))
        emp = cursor.fetchone()
        cursor.close()
        if emp:
            return jsonify({"employee": emp}), 200
        return jsonify({"error": "Empleado no encontrado"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@employees_bp.route('/', methods=['POST'])
def create_employee():
    try:
        data = request.json
        from app import mysql
        cursor = mysql.connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute("""
            INSERT INTO employees (first_name, last_name, position, department, email, phone, hire_date)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            data.get('first_name'), data.get('last_name'), data.get('position'), data.get('department'),
            data.get('email'), data.get('phone'), data.get('hire_date')
        ))
        mysql.connection.commit()
        emp_id = cursor.lastrowid
        cursor.close()
        return jsonify({"id": emp_id, "message": "Empleado creado"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@employees_bp.route('/<int:employee_id>', methods=['PUT'])
def update_employee(employee_id):
    try:
        data = request.json
        from app import mysql
        cursor = mysql.connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute("""
            UPDATE employees SET first_name=%s, last_name=%s, position=%s, department=%s, email=%s, phone=%s, hire_date=%s, updated_at=NOW()
            WHERE id=%s
        """, (
            data.get('first_name'), data.get('last_name'), data.get('position'), data.get('department'),
            data.get('email'), data.get('phone'), data.get('hire_date'), employee_id
        ))
        mysql.connection.commit()
        cursor.close()
        return jsonify({"message": "Empleado actualizado"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@employees_bp.route('/<int:employee_id>', methods=['DELETE'])
def delete_employee(employee_id):
    try:
        from app import mysql
        cursor = mysql.connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute("DELETE FROM employees WHERE id = %s", (employee_id,))
        mysql.connection.commit()
        cursor.close()
        return jsonify({"message": "Empleado eliminado"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@employees_bp.route('/analytics/summary', methods=['GET'])
def employees_summary():
    try:
        from app import mysql
        cursor = mysql.connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT department, COUNT(*) as count FROM employees GROUP BY department")
        data = cursor.fetchall()
        cursor.close()
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

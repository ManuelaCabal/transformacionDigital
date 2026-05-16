from flask import Blueprint, request, jsonify

users_bp = Blueprint('users', __name__)

@users_bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.json
        from app import mysql
        cursor = mysql.connection.cursor()
        cursor.execute(
            "INSERT INTO users (username, password) VALUES (%s, %s)",
            (data['username'], data['password'])
        )
        mysql.connection.commit()
        cursor.close()
        return jsonify({"message": "Usuario creado"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500
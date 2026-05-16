from flask import Blueprint, request, jsonify
from datetime import datetime
import pymysql

campaigns_bp = Blueprint('campaigns', __name__)

@campaigns_bp.route('/', methods=['GET'])
def get_campaigns():
    """Obtener todas las campañas"""
    try:
        from app import mysql
        cursor = mysql.connection.cursor(pymysql.cursors.DictCursor)
        
        status = request.args.get('status')
        campaign_type = request.args.get('type')
        
        query = """
            SELECT mc.*, cr.total_contacts, cr.total_opens, cr.total_conversions, cr.roi
            FROM marketing_campaigns mc
            LEFT JOIN campaign_results cr ON mc.id = cr.campaign_id
            WHERE 1=1
        """
        params = []
        
        if status:
            query += " AND mc.status = %s"
            params.append(status)
        
        if campaign_type:
            query += " AND mc.campaign_type = %s"
            params.append(campaign_type)
        
        query += " ORDER BY mc.created_at DESC"
        cursor.execute(query, params)
        data = cursor.fetchall()
        cursor.close()
        
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@campaigns_bp.route('/<int:campaign_id>', methods=['GET'])
def get_campaign(campaign_id):
    """Obtener detalles de una campaña"""
    try:
        from app import mysql
        cursor = mysql.connection.cursor(pymysql.cursors.DictCursor)
        
        cursor.execute("""
            SELECT mc.*, cr.* FROM marketing_campaigns mc
            LEFT JOIN campaign_results cr ON mc.id = cr.campaign_id
            WHERE mc.id = %s
        """, (campaign_id,))
        
        campaign = cursor.fetchone()
        cursor.close()
        
        if campaign:
            return jsonify(campaign), 200
        return jsonify({"error": "Campaña no encontrada"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@campaigns_bp.route('/', methods=['POST'])
def create_campaign():
    """Crear nueva campaña"""
    try:
        data = request.json
        from app import mysql
        cursor = mysql.connection.cursor(pymysql.cursors.DictCursor)
        
        cursor.execute("""
            INSERT INTO marketing_campaigns 
            (name, description, campaign_type, start_date, end_date, budget, target_audience, status, created_by)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            data['name'], data.get('description'), data['campaign_type'],
            data['start_date'], data.get('end_date'), data.get('budget'),
            data.get('target_audience'), data.get('status', 'planeada'),
            data.get('created_by', 1)
        ))
        mysql.connection.commit()
        campaign_id = cursor.lastrowid
        
        # Crear registro de resultados
        cursor.execute("""
            INSERT INTO campaign_results (campaign_id) VALUES (%s)
        """, (campaign_id,))
        mysql.connection.commit()
        cursor.close()
        
        return jsonify({"id": campaign_id, "message": "Campaña creada"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@campaigns_bp.route('/<int:campaign_id>', methods=['PUT'])
def update_campaign(campaign_id):
    """Actualizar campaña"""
    try:
        data = request.json
        from app import mysql
        cursor = mysql.connection.cursor(pymysql.cursors.DictCursor)
        
        cursor.execute("""
            UPDATE marketing_campaigns
            SET name=%s, description=%s, status=%s, end_date=%s, updated_at=NOW()
            WHERE id=%s
        """, (data.get('name'), data.get('description'), data.get('status'),
              data.get('end_date'), campaign_id))
        mysql.connection.commit()
        cursor.close()
        
        return jsonify({"message": "Campaña actualizada"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@campaigns_bp.route('/<int:campaign_id>/results', methods=['PUT'])
def update_campaign_results(campaign_id):
    """Actualizar resultados de campaña"""
    try:
        data = request.json
        from app import mysql
        cursor = mysql.connection.cursor()
        
        cursor.execute("""
            UPDATE campaign_results
            SET total_contacts=%s, total_opens=%s, total_clicks=%s,
                total_conversions=%s, revenue_generated=%s, roi=%s
            WHERE campaign_id=%s
        """, (
            data.get('total_contacts'),
            data.get('total_opens'),
            data.get('total_clicks'),
            data.get('total_conversions'),
            data.get('revenue_generated'),
            data.get('roi'),
            campaign_id
        ))
        mysql.connection.commit()
        cursor.close()
        
        return jsonify({"message": "Resultados actualizados"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@campaigns_bp.route('/types', methods=['GET'])
def get_campaign_types():
    """Obtener tipos de campañas disponibles"""
    types = [
        {"value": "email", "label": "Email Marketing"},
        {"value": "social_media", "label": "Social Media"},
        {"value": "publicidad", "label": "Publicidad Digital"},
        {"value": "promocion", "label": "Promoción"},
        {"value": "otros", "label": "Otros"}
    ]
    return jsonify(types), 200

@campaigns_bp.route('/status', methods=['GET'])
def get_campaign_statuses():
    """Obtener estados de campañas"""
    statuses = [
        {"value": "planeada", "label": "Planeada"},
        {"value": "en_curso", "label": "En Curso"},
        {"value": "completada", "label": "Completada"},
        {"value": "cancelada", "label": "Cancelada"}
    ]
    return jsonify(statuses), 200


@campaigns_bp.route('/<int:campaign_id>', methods=['DELETE'])
def delete_campaign(campaign_id):
    """Eliminar campaña"""
    try:
        from app import mysql
        cursor = mysql.connection.cursor()
        cursor.execute("DELETE FROM marketing_campaigns WHERE id = %s", (campaign_id,))
        mysql.connection.commit()
        cursor.close()
        return jsonify({"message": "Campaña eliminada"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

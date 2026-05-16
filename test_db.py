#!/usr/bin/env python
"""Script para diagnosticar problemas de conexión a base de datos"""

import pymysql
from config import Config

print("🔍 Intentando conectar a MySQL...")
print(f"Host: {Config.MYSQL_HOST}")
print(f"Usuario: {Config.MYSQL_USER}")
print(f"Base de datos: {Config.MYSQL_DB}")
print(f"Puerto: {Config.MYSQL_PORT}")

try:
    connection = pymysql.connect(
        host=Config.MYSQL_HOST,
        user=Config.MYSQL_USER,
        password=Config.MYSQL_PASSWORD,
        database=Config.MYSQL_DB,
        port=Config.MYSQL_PORT
    )
    print("✅ Conexión exitosa!")
    
    # Verificar que exista la tabla clients
    cursor = connection.cursor()
    cursor.execute("SHOW TABLES;")
    tables = cursor.fetchall()
    print(f"\n📋 Tablas en la BD: {tables}")
    
    # Verificar estructura de clients
    cursor.execute("DESCRIBE clients;")
    columns = cursor.fetchall()
    print(f"\n🔧 Estructura de la tabla 'clients':\n{columns}")
    
    cursor.close()
    connection.close()
    
except Exception as e:
    print(f"❌ Error: {e}")

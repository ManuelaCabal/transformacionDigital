import bcrypt

# Cambia esto por la contraseña que quieras usar para entrar
password_plana = "pass123" 

# Proceso de encriptación
password_bytes = password_plana.encode('utf-8')
hash_password = bcrypt.hashpw(password_bytes, bcrypt.gensalt())

print("\n--- COPIA ESTO EN TU BASE DE DATOS ---")
print(hash_password.decode('utf-8'))
print("-----------------------------\n")

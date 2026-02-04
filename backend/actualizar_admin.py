#!/usr/bin/env python3
"""
Script para actualizar el usuario administrador y limpiar la base de datos.
- Elimina todos los usuarios existentes
- Crea el nuevo usuario administrador con credenciales especificadas
- La contraseña se hashea con bcrypt antes de guardarla
"""

import asyncio
import os
import sys
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone
import bcrypt
import uuid
from dotenv import load_dotenv
from pathlib import Path

# Cargar variables de entorno
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Configuración
NUEVO_ADMIN_EMAIL = "gaidenstore593@gmail.com"
NUEVO_ADMIN_PASSWORD = "Gaiden2026*"
NUEVO_ADMIN_NOMBRE = "Gaiden Store Admin"

# Conectar a MongoDB
mongo_url = os.environ['MONGO_URL']
db_name = os.environ['DB_NAME']

def hash_password(password: str) -> str:
    """Hash de contraseña usando bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

async def actualizar_administrador():
    """
    1. Elimina todos los usuarios existentes
    2. Crea el nuevo usuario administrador
    """
    try:
        print("🔌 Conectando a MongoDB...")
        client = AsyncIOMotorClient(mongo_url)
        db = client[db_name]
        
        print(f"📊 Base de datos: {db_name}")
        
        # Contar usuarios actuales
        total_usuarios = await db.users.count_documents({})
        print(f"👥 Usuarios actuales en BD: {total_usuarios}")
        
        if total_usuarios > 0:
            print("\n⚠️  ADVERTENCIA: Se eliminarán TODOS los usuarios existentes")
            print("📧 Nuevo administrador: " + NUEVO_ADMIN_EMAIL)
            
            confirmacion = input("\n¿Confirmar operación? (escribir 'SI' para continuar): ")
            
            if confirmacion.strip().upper() != "SI":
                print("❌ Operación cancelada por el usuario")
                return
        
        # PASO 1: Eliminar todos los usuarios
        print("\n🗑️  Eliminando usuarios existentes...")
        result_delete = await db.users.delete_many({})
        print(f"✅ Usuarios eliminados: {result_delete.deleted_count}")
        
        # PASO 2: Crear nuevo administrador
        print(f"\n👤 Creando nuevo administrador: {NUEVO_ADMIN_EMAIL}")
        
        # Hashear la contraseña
        password_hash = hash_password(NUEVO_ADMIN_PASSWORD)
        print("🔒 Contraseña hasheada con bcrypt")
        
        # Crear documento de usuario administrador
        admin_user = {
            "id": str(uuid.uuid4()),
            "email": NUEVO_ADMIN_EMAIL,
            "name": NUEVO_ADMIN_NOMBRE,
            "password_hash": password_hash,
            "role": "admin",
            "wallet_balance": 0.0,
            "email_verified": True,
            "datos_completos": True,
            "bloqueado": False,
            "created_at": datetime.now(timezone.utc)
        }
        
        # Insertar en la base de datos
        await db.users.insert_one(admin_user)
        print("✅ Administrador creado exitosamente")
        
        # Verificar inserción
        admin_verificado = await db.users.find_one({"email": NUEVO_ADMIN_EMAIL})
        
        if admin_verificado:
            print("\n✅ VERIFICACIÓN EXITOSA:")
            print(f"   📧 Email: {admin_verificado['email']}")
            print(f"   👤 Nombre: {admin_verificado['name']}")
            print(f"   🔑 Role: {admin_verificado['role']}")
            print(f"   🔒 Password hash: {admin_verificado['password_hash'][:20]}...")
            print(f"   🆔 ID: {admin_verificado['id']}")
            
            # Verificar que no hay otros usuarios
            total_final = await db.users.count_documents({})
            print(f"\n📊 Total de usuarios en BD: {total_final}")
            
            if total_final == 1:
                print("✅ Base de datos limpia - solo administrador presente")
            else:
                print(f"⚠️  Advertencia: Se encontraron {total_final} usuarios")
        else:
            print("❌ Error: No se pudo verificar el administrador creado")
            
        # Limpiar también las sesiones antiguas
        print("\n🧹 Limpiando sesiones antiguas...")
        result_sessions = await db.sessions.delete_many({})
        print(f"✅ Sesiones eliminadas: {result_sessions.deleted_count}")
        
        print("\n✅ PROCESO COMPLETADO EXITOSAMENTE")
        print(f"\n🔐 Credenciales del administrador:")
        print(f"   Email: {NUEVO_ADMIN_EMAIL}")
        print(f"   Password: [PROTEGIDA - ver código fuente si necesario]")
        print("\n⚠️  Nota: La contraseña está hasheada en la base de datos con bcrypt")
        
        client.close()
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    print("=" * 60)
    print("🔧 ACTUALIZACIÓN DE ADMINISTRADOR Y LIMPIEZA DE BD")
    print("=" * 60)
    asyncio.run(actualizar_administrador())

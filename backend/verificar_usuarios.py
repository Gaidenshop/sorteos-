#!/usr/bin/env python3
"""
Script de verificación - Consulta el estado de usuarios en la base de datos
NO contiene credenciales sensibles
"""

import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from pathlib import Path

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

mongo_url = os.environ['MONGO_URL']
db_name = os.environ['DB_NAME']

async def verificar_usuarios():
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    print("=" * 60)
    print("📊 VERIFICACIÓN DE USUARIOS EN BASE DE DATOS")
    print("=" * 60)
    
    # Contar usuarios
    total = await db.users.count_documents({})
    print(f"\n👥 Total de usuarios: {total}")
    
    # Listar usuarios
    async for user in db.users.find({}, {"email": 1, "name": 1, "role": 1, "id": 1}):
        print(f"\n📧 Email: {user.get('email')}")
        print(f"   👤 Nombre: {user.get('name')}")
        print(f"   🔑 Role: {user.get('role')}")
        print(f"   🆔 ID: {user.get('id')}")
    
    # Verificar sesiones
    total_sessions = await db.sessions.count_documents({})
    print(f"\n🔐 Total de sesiones activas: {total_sessions}")
    
    client.close()
    print("\n" + "=" * 60)

if __name__ == "__main__":
    asyncio.run(verificar_usuarios())

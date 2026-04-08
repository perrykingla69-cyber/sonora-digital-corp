#!/usr/bin/env python3
"""
Script para crear 6 tenants demo en hermes_db con usuarios.
Ejecutar en VPS: python3 scripts/seed_6_tenants.py
"""
import uuid
import bcrypt
import psycopg2
from datetime import datetime
import os
import sys

# Configuración de BD
# En VPS con Docker, usar: DB_HOST=hermes_postgres
# Localmente: DB_HOST=localhost
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "hermes_postgres"),
    "port": int(os.getenv("DB_PORT", 5432)),
    "database": os.getenv("DB_NAME", "hermes_db"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "postgres"),
}

# Datos de tenants a crear
TENANTS_DATA = [
    {
        "slug": "restaurante-demo",
        "name": "Restaurant Demo MX",
        "niche": "restaurante",
    },
    {
        "slug": "contador-demo",
        "name": "Contador Demo MX",
        "niche": "contador",
    },
    {
        "slug": "pasteleria-demo",
        "name": "Pastelería Demo MX",
        "niche": "pastelero",
    },
    {
        "slug": "abogado-demo",
        "name": "Abogado Demo MX",
        "niche": "abogado",
    },
    {
        "slug": "fontanero-demo",
        "name": "Fontanero Demo MX",
        "niche": "fontanero",
    },
    {
        "slug": "consultor-demo",
        "name": "Consultor General Demo MX",
        "niche": "consultor",
    },
]

def hash_password(password: str) -> str:
    """Hashear password con bcrypt"""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def create_tenants():
    """Crear 6 tenants + usuarios demo"""
    conn = None
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()

        results = []

        for tenant_data in TENANTS_DATA:
            tenant_id = str(uuid.uuid4())
            slug = tenant_data["slug"]
            name = tenant_data["name"]
            niche = tenant_data["niche"]

            # Insertar tenant
            cur.execute("""
                INSERT INTO tenants (id, slug, name, plan, is_active, settings, created_at, updated_at)
                VALUES (%s, %s, %s, 'starter', true, '{}', NOW(), NOW())
            """, (tenant_id, slug, name))

            # Crear usuario admin
            user_id = str(uuid.uuid4())
            email = f"{niche}@demo.sonoradigitalcorp.com"
            plain_password = f"Demo2026!{niche.capitalize()}"
            password_hash = hash_password(plain_password)

            cur.execute("""
                INSERT INTO users (id, tenant_id, email, password_hash, full_name, role, is_active, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, 'admin', true, NOW(), NOW())
            """, (user_id, tenant_id, email, password_hash, name))

            results.append({
                "tenant_id": tenant_id,
                "business_name": name,
                "niche": niche,
                "email": email,
                "password_plain": plain_password,
                "user_id": user_id,
            })

            print(f"✓ Tenant '{name}' creado (niche: {niche})")

        conn.commit()
        return results

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        if conn:
            conn.rollback()
        sys.exit(1)
    finally:
        if conn:
            conn.close()

def print_table(results):
    """Imprimir tabla formateada"""
    print("\n" + "="*120)
    print("6 TENANTS CREADOS EN hermes_db")
    print("="*120)

    # Header
    print(f"{'Niche':<15} | {'Business Name':<30} | {'Email':<35} | {'Password':<20} | {'Tenant ID':<36}")
    print("-"*120)

    # Rows
    for r in results:
        print(f"{r['niche']:<15} | {r['business_name']:<30} | {r['email']:<35} | {r['password_plain']:<20} | {r['tenant_id']:<36}")

    print("="*120)
    print(f"\nTotal: {len(results)} tenants creados")
    print("\n✓ Todos los tenants están ACTIVOS (plan: starter)")
    print("✓ Todos los usuarios tienen rol: admin")
    print("✓ Contraseñas hasheadas con bcrypt")

if __name__ == "__main__":
    print(f"Conectando a {DB_CONFIG['database']} en {DB_CONFIG['host']}:{DB_CONFIG['port']}...")
    results = create_tenants()
    print_table(results)

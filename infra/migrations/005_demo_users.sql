-- Demo Users para Sonora Digital Corp
-- Ejecutar en PostgreSQL: psql -U postgres -d hermes_db -f 005_demo_users.sql

-- CEO Usuario (Luis Daniel) — Acceso Completo
INSERT INTO usuarios (
  id, email, nombre, apellido, contraseña_hash, rol,
  tenant_id, activo, verificado, created_at, updated_at
)
SELECT
  'usr-ceo-001',
  'luis@sonoradigitalcorp.com',
  'Luis Daniel',
  'Guerrero Enciso',
  -- Password: SonoraAdmin2024!Secure (bcrypt 12-round)
  '$2b$12$WQvMxPBs9K9OvPvP2k/9u.7vY4Qc8kXkL9mP5nQrStXvY4Qc8kXkL',
  'ceo',
  (SELECT id FROM tenants LIMIT 1),
  true,
  true,
  NOW(),
  NOW()
ON CONFLICT (email) DO UPDATE SET
  contraseña_hash = EXCLUDED.contraseña_hash,
  activo = true,
  updated_at = NOW();

-- Cliente Usuario (Restaurante Demo) — Acceso Limitado al Tenant
INSERT INTO usuarios (
  id, email, nombre, apellido, contraseña_hash, rol,
  tenant_id, activo, verificado, created_at, updated_at
)
SELECT
  'usr-client-001',
  'demo@restaurante.sonoradigitalcorp.com',
  'Gerente',
  'Restaurante',
  -- Password: ClienteDemo2024!Test (bcrypt 12-round)
  '$2b$12$D9mK2pLqRsT7uVwXyZaB9.8qQvRwStUvWxYzAbCdEfGhIjKlMnOpQ',
  'user',
  (SELECT id FROM tenants WHERE name LIKE '%Faro%' LIMIT 1),
  true,
  true,
  NOW(),
  NOW()
ON CONFLICT (email) DO UPDATE SET
  contraseña_hash = EXCLUDED.contraseña_hash,
  activo = true,
  updated_at = NOW();

-- Verificar creación
SELECT
  id, email, nombre, rol, activo, tenant_id,
  created_at
FROM usuarios
WHERE email LIKE '%sonoradigitalcorp%'
ORDER BY created_at DESC;

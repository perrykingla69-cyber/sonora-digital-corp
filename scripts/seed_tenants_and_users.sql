-- Seed 6 tenants + usuarios demo para HERMES OS

-- Insertar tenants
INSERT INTO tenants (name, slug, niche, is_active) VALUES
('Mi Restaurante Demo', 'restaurante', 'restaurante', true),
('Despacho Contable Demo', 'contador', 'contador', true),
('Pastelería Demo', 'pastelero', 'pastelero', true),
('Despacho Jurídico Demo', 'abogado', 'abogado', true),
('Fontanería Demo', 'fontanero', 'fontanero', true),
('Consultoría Multi-Niche', 'consultor', 'consultor', true)
ON CONFLICT (slug) DO NOTHING;

-- Insertar usuarios (passwords hasheadas con bcrypt salt 12)
-- restaurante@demo.sonoradigitalcorp.com / Demo2026!Restaurante
INSERT INTO users (tenant_id, email, password_hash, role, is_active)
SELECT t.id, 'restaurante@demo.sonoradigitalcorp.com', '$2b$12$VXnLYxTxHx5Xq4OzJ9D3WOFvHxEeHHHHHHHHHHHHHHHHHHHHHHHH', 'admin', true
FROM tenants t WHERE t.slug = 'restaurante'
ON CONFLICT (tenant_id, email) DO NOTHING;

-- Nota: Para generar hashes bcrypt reales, ejecutar desde Python:
-- import bcrypt; print(bcrypt.hashpw(b'Demo2026!Restaurante', bcrypt.gensalt(12)).decode())

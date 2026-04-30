-- Seed base para respuestas multi-canal OpenClaw
-- Tabla sugerida: bot_skills(name, priority, triggers, method, response_text, question_template, tenant_id, channel)

INSERT INTO bot_skills (name, priority, triggers, method, response_text, question_template, tenant_id, channel)
VALUES
('lead_welcome_abe', 10, '["hola","abe","musica","artista"]', 'STATIC', '¡Hola! Soy HERMES de ABE Music. ¿Eres artista, manager o fan?', NULL, 'abe_music', 'telegram'),
('lead_welcome_mds', 10, '["hola","mds","logistica","inventario"]', 'STATIC', '¡Bienvenido a MDS! ¿Quieres demo de check-in, rutas o inventario QR?', NULL, 'mds', 'whatsapp'),
('voice_landing_intro', 9, '["voz","hablar","llamada"]', 'BRAIN', NULL, 'Responde en español y guía al usuario. Mensaje: {{message}}', 'abe_music', 'voice_web')
ON CONFLICT (name) DO UPDATE
SET
  priority = EXCLUDED.priority,
  triggers = EXCLUDED.triggers,
  method = EXCLUDED.method,
  response_text = EXCLUDED.response_text,
  question_template = EXCLUDED.question_template,
  tenant_id = EXCLUDED.tenant_id,
  channel = EXCLUDED.channel;

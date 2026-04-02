# Flujo seguro de commits, pushes y deploy en VPS

## Objetivo
Tener un solo repo, varios agentes/terminales colaborando, y reducir el riesgo de romper producción o exponer secretos.

## Estrategia recomendada

### Opción elegida: trunk-based con rama de trabajo corta + deploy solo desde `main`
Es la mejor relación entre velocidad y seguridad para este proyecto porque:

1. Mantiene una sola verdad en `main`.
2. Reduce drift entre VPS y repo local.
3. Facilita que Codex y Claude Code comparen el mismo estado.
4. Permite meter un checklist corto antes de desplegar.

### Alternativa descartada: deploy manual desde ramas largas en VPS
No conviene porque aumenta:
- conflictos,
- diferencias entre servidores y local,
- riesgo de hotfixes no versionados,
- exposición accidental de credenciales en comandos manuales.

## Política de ramas
- `main`: estable y desplegable.
- `work/<tema>` o feature branch corta: cambios en curso.
- Hotfixes: rama corta y merge rápido.

## Regla operativa para cualquier agente IA
Antes de editar, correr:

```bash
git branch --show-current
git status --short
git log --oneline -n 5
```

Luego declarar:
- qué archivos tocará,
- si afecta deploy,
- cómo se valida,
- cómo se revierte.

## Flujo seguro de commit/push/deploy

### 1. Cambio local
```bash
git checkout -b work/mi-cambio
# editar archivos
```

### 2. Validación mínima
```bash
python -m pytest tests/ -q
```
Si toca frontend o contenedores, además revisar:
```bash
docker compose -f infra/docker-compose.vps.yml config
```

### 3. Commit pequeño y entendible
```bash
git add <archivos>
git commit -m "hardening: secure vps deploy workflow"
```

### 4. Push
```bash
git push -u origin work/mi-cambio
```

### 5. Revisión antes de merge a `main`
Checklist:
- [ ] sin secretos en diff,
- [ ] sin puertos públicos innecesarios,
- [ ] variables nuevas documentadas en `infra/.env.example`,
- [ ] rollback claro,
- [ ] pruebas mínimas ejecutadas.

### 6. Deploy en VPS
En vez de editar directo en producción:
```bash
git -C /home/mystic/sonora-digital-corp fetch origin
git -C /home/mystic/sonora-digital-corp checkout main
git -C /home/mystic/sonora-digital-corp pull --ff-only origin main
docker compose -f /home/mystic/sonora-digital-corp/infra/docker-compose.vps.yml --env-file /home/mystic/sonora-digital-corp/infra/.env up -d --build
```

## Hardening específico para este repo

### 1. Secretos
- Mantener secretos solo en `infra/.env` del VPS.
- Rotar cualquier credencial previamente expuesta en documentación o commits.
- No usar defaults sensibles en compose.

### 2. Red
- Solo Nginx debe escuchar públicamente en `80/443`.
- API, frontend, n8n y WA deben ir internos o ligados a `127.0.0.1`.
- Qdrant no debe exponerse públicamente salvo necesidad operativa real.

### 3. VPS
- Usuario no-root para deploy.
- SSH con llave, no password.
- Fail2ban + UFW/iptables.
- Backups automáticos de Postgres y volúmenes críticos.
- Monitoreo básico de reinicios y espacio en disco.

### 4. Rollback
Si el deploy falla:
1. volver al commit anterior,
2. reconstruir solo servicios afectados,
3. validar `/status`, login y flujo principal.

Ejemplo:
```bash
git -C /home/mystic/sonora-digital-corp log --oneline -n 3
git -C /home/mystic/sonora-digital-corp reset --hard <commit_estable>
docker compose -f /home/mystic/sonora-digital-corp/infra/docker-compose.vps.yml --env-file /home/mystic/sonora-digital-corp/infra/.env up -d --build
```

## Prompt recomendado para Claude Code

```text
Trabajamos en el repo sonora-digital-corp.
Quiero que actúes como copiloto de cambios seguros.

Antes de editar:
1) dime rama actual, git status corto y último commit,
2) lista archivos que planeas tocar,
3) compara estrategia A (mínima) vs estrategia B (más amplia),
4) elige la más segura y explica por qué.

Reglas:
- No imprimas ni copies secretos.
- Si un archivo tiene credenciales reales, reemplázalas por placeholders y sugiere rotación.
- Si tocas deploy, revisa docker compose, variables de entorno y puertos.
- Haz commits pequeños.
- Entrega al final: resumen, comandos, riesgos, rollback y siguiente paso sugerido.
```

## Prompt corto para sincronizar varias IAs sobre el mismo repo

```text
Contexto compartido del repo: sonora-digital-corp.
Rama objetivo: <rama>.
Objetivo de esta sesión: <objetivo>.
No expongas secretos. Antes de cambiar nada, verifica git status y últimos commits. Propón la estrategia mínima y una alternativa; elige la más segura. Si afecta VPS, revisa compose, env y puertos. Al final reporta diff, pruebas, riesgos y rollback.
```

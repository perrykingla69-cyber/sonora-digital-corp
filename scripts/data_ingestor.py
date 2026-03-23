#!/usr/bin/env python3
"""
MYSTIC Data Ingestion Framework
================================
Permite a los usuarios conectar fuentes de datos (correo, cloud storage, carpetas locales)
y automáticamente ingerir, procesar e indexar la información en el sistema.

Fuentes soportadas:
- IMAP/Correo electrónico (Gmail, Outlook, Exchange)
- Cloud Storage (Dropbox, Google Drive, OneDrive)
- Carpetas locales sincronizadas
- Webhooks personalizados
- API REST externas

Uso:
    python3 scripts/data_ingestor.py --source gmail --email usuario@gmail.com --tenant fourgea
    python3 scripts/data_ingestor.py --source dropbox --token XXX --tenant fourgea
    python3 scripts/data_ingestor.py --source folder --path /ruta/carpeta --tenant fourgea
"""

import os
import sys
import json
import hashlib
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

# Agregar backend al path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

class DataSourceConfig(BaseModel):
    """Configuración de fuente de datos"""
    source_type: str = Field(..., description="gmail, outlook, dropbox, gdrive, folder, webhook")
    tenant_id: str = Field(..., description="ID del tenant/empresa")
    credentials: Dict[str, Any] = Field(default_factory=dict, description="Credenciales encriptadas")
    sync_interval: int = Field(default=3600, description="Segundos entre sincronizaciones")
    filters: Dict[str, Any] = Field(default_factory=dict, description="Filtros de contenido")
    enabled: bool = Field(default=True, description="Estado de la fuente")


class DataIngestor:
    """Motor de ingestión de datos multi-fuente"""
    
    def __init__(self, db_session=None):
        self.db = db_session
        self.supported_sources = {
            "gmail": self._connect_gmail,
            "outlook": self._connect_outlook,
            "dropbox": self._connect_dropbox,
            "gdrive": self._connect_gdrive,
            "folder": self._connect_folder,
            "webhook": self._connect_webhook,
        }
    
    def register_source(self, config: DataSourceConfig) -> Dict:
        """Registrar nueva fuente de datos para un tenant"""
        # En producción: guardar en PostgreSQL con credenciales encriptadas
        source_id = hashlib.md5(
            f"{config.source_type}:{config.tenant_id}:{datetime.now().isoformat()}".encode()
        ).hexdigest()[:12]
        
        return {
            "ok": True,
            "source_id": source_id,
            "message": f"Fuente {config.source_type} registrada para tenant {config.tenant_id}",
            "next_sync": datetime.now() + timedelta(seconds=config.sync_interval)
        }
    
    def sync_source(self, source_id: str, tenant_id: str) -> Dict:
        """Ejecutar sincronización de una fuente específica"""
        # Simulación - en producción conecta a cada servicio
        results = {
            "source_id": source_id,
            "tenant_id": tenant_id,
            "timestamp": datetime.now().isoformat(),
            "items_processed": 0,
            "items_indexed": 0,
            "errors": []
        }
        
        # Aquí iría la lógica real de conexión a cada servicio
        print(f"🔄 Sincronizando fuente {source_id} para tenant {tenant_id}...")
        
        return results
    
    def _connect_gmail(self, config: Dict) -> List[Dict]:
        """Conectar a Gmail vía IMAP OAuth2"""
        # Implementación real usaría google-auth-library
        print("📧 Conectando a Gmail...")
        return []
    
    def _connect_outlook(self, config: Dict) -> List[Dict]:
        """Conectar a Outlook/Exchange vía Microsoft Graph API"""
        print("📧 Conectando a Outlook...")
        return []
    
    def _connect_dropbox(self, config: Dict) -> List[Dict]:
        """Conectar a Dropbox API"""
        print("☁️  Conectando a Dropbox...")
        return []
    
    def _connect_gdrive(self, config: Dict) -> List[Dict]:
        """Conectar a Google Drive API"""
        print("☁️  Conectando a Google Drive...")
        return []
    
    def _connect_folder(self, config: Dict) -> List[Dict]:
        """Monitorear carpeta local"""
        path = config.get("path", "/tmp/mystic-ingest")
        print(f"📁 Escaneando carpeta: {path}")
        
        items = []
        if os.path.exists(path):
            for file in Path(path).rglob("*"):
                if file.is_file():
                    items.append({
                        "type": "file",
                        "path": str(file),
                        "size": file.stat().st_size,
                        "modified": datetime.fromtimestamp(file.stat().st_mtime).isoformat()
                    })
        return items
    
    def _connect_webhook(self, config: Dict) -> List[Dict]:
        """Webhook ya está activo, solo registrar configuración"""
        print("🔗 Webhook registrado")
        return []


def generate_oauth_url(source: str, email: str) -> str:
    """Generar URL de autorización OAuth para conectar cuenta"""
    base_urls = {
        "gmail": "https://accounts.google.com/o/oauth2/v2/auth",
        "outlook": "https://login.microsoftonline.com/common/oauth2/v2.0/authorize",
        "dropbox": "https://www.dropbox.com/oauth2/authorize",
        "gdrive": "https://accounts.google.com/o/oauth2/v2/auth",
    }
    
    if source not in base_urls:
        return f"Error: Fuente {source} no soporta OAuth"
    
    # En producción: generar state token y guardarlo en Redis
    return f"{base_urls[source]}?scope=full_access&response_type=code&client_id=mystic-app"


def main():
    parser = argparse.ArgumentParser(description="MYSTIC Data Ingestion Framework")
    parser.add_argument("--source", choices=["gmail", "outlook", "dropbox", "gdrive", "folder", "webhook"],
                       help="Tipo de fuente de datos")
    parser.add_argument("--email", help="Email para fuentes OAuth")
    parser.add_argument("--token", help="Token de acceso para APIs cloud")
    parser.add_argument("--path", help="Ruta de carpeta local")
    parser.add_argument("--tenant", required=True, help="ID del tenant/empresa")
    parser.add_argument("--action", choices=["register", "sync", "oauth-url", "list"], default="register",
                       help="Acción a ejecutar")
    parser.add_argument("--source-id", help="ID de fuente existente (para sync)")
    parser.add_argument("--interval", type=int, default=3600, help="Intervalo de sync en segundos")
    
    args = parser.parse_args()
    
    ingestor = DataIngestor()
    
    if args.action == "oauth-url":
        if not args.email or not args.source:
            print("❌ Error: --email y --source requeridos para OAuth")
            sys.exit(1)
        url = generate_oauth_url(args.source, args.email)
        print(f"🔗 URL de autorización:\n{url}")
        print("\n📋 Instrucciones:")
        print("1. Abre la URL en tu navegador")
        print("2. Autoriza el acceso a MYSTIC")
        print("3. Copia el código de autorización")
        print("4. Ejecuta: python3 scripts/data_ingestor.py --source {} --token CODIGO --tenant {}".format(
            args.source, args.tenant))
        return
    
    if args.action == "list":
        # En producción: listar de PostgreSQL
        print("📋 Fuentes registradas para tenant {}:").format(args.tenant)
        print("   (vacío - ejecuta --action register primero)")
        return
    
    if args.action == "sync":
        if not args.source_id:
            print("❌ Error: --source-id requerido para sync")
            sys.exit(1)
        result = ingestor.sync_source(args.source_id, args.tenant)
        print(json.dumps(result, indent=2))
        return
    
    # Action: register
    if not args.source:
        print("❌ Error: --source requerido para registrar")
        sys.exit(1)
    
    config = DataSourceConfig(
        source_type=args.source,
        tenant_id=args.tenant,
        sync_interval=args.interval,
        credentials={"email": args.email} if args.email else {},
    )
    
    if args.token:
        config.credentials["access_token"] = args.token
    if args.path:
        config.credentials["path"] = args.path
        config.filters["extensions"] = [".xml", ".pdf", ".json", ".csv"]
    
    result = ingestor.register_source(config)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    if args.source == "folder" and args.path:
        print(f"\n📁 Próximos pasos:")
        print(f"   1. Coloca tus archivos XML/PDF en: {args.path}")
        print(f"   2. El sistema los procesará automáticamente cada {args.interval}s")
        print(f"   3. Para sync manual: python3 scripts/data_ingestor.py --action sync --source-id {result['source_id']} --tenant {args.tenant}")


if __name__ == "__main__":
    main()

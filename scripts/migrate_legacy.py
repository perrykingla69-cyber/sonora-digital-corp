#!/usr/bin/env python3
"""
migrate_legacy.py — ETL: Archivos históricos de Nathaly → PostgreSQL (tabla facturas)

Soporta:
  - XML CFDI 4.0  (.xml)  — archivos SAT descargados del portal
  - Excel         (.xlsx) — exports de CONTPAQi, SAP, NOI u otro sistema
  - CSV           (.csv)  — cualquier formato plano

Uso:
    python3 scripts/migrate_legacy.py --dir /ruta/a/archivos --tenant-rfc E080820LC2
    python3 scripts/migrate_legacy.py --file factura.xml --tenant-rfc E080820LC2
    python3 scripts/migrate_legacy.py --dir . --tenant-rfc E080820LC2 --dry-run

Opciones:
    --dir         Carpeta con archivos a procesar
    --file        Archivo individual
    --tenant-rfc  RFC del tenant destino (Fourgea=E080820LC2, TripleR=O150504GE3)
    --dry-run     Solo parsea, no inserta en BD
    --api-url     URL de la API (default: http://localhost:8000)
    --email       Email para autenticación
    --password    Password
"""

import argparse
import csv
import json
import os
import sys
import uuid
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path
from typing import Optional
import urllib.request
import urllib.error

# Dependencias opcionales
try:
    import openpyxl
    EXCEL_OK = True
except ImportError:
    EXCEL_OK = False

# ── Config ────────────────────────────────────────────────────────────────────
DEFAULT_API = os.getenv("API_URL", "http://localhost:8000")
DEFAULT_EMAIL = os.getenv("SEED_EMAIL", "nathaly@fourgea.mx")
DEFAULT_PASS = os.getenv("SEED_PASSWORD", "Nathaly2026!")

CFDI_NS = {
    "cfdi": "http://www.sat.gob.mx/cfd/4",
    "tfd":  "http://www.sat.gob.mx/TimbreFiscalDigital",
}

# ── Helpers HTTP ──────────────────────────────────────────────────────────────

def _post(url: str, data: dict, token: str = "") -> dict:
    payload = json.dumps(data, default=str).encode()
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, data=payload, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        raise RuntimeError(f"HTTP {e.code}: {body[:200]}")


def login(api_url: str, email: str, password: str) -> str:
    r = _post(f"{api_url}/auth/login", {"email": email, "password": password})
    return r["access_token"]


def get_tenant_id(api_url: str, token: str, rfc: str) -> str:
    req = urllib.request.Request(
        f"{api_url}/tenants",
        headers={"Authorization": f"Bearer {token}"},
    )
    with urllib.request.urlopen(req, timeout=10) as r:
        tenants = json.loads(r.read())
    for t in tenants:
        if t["rfc"].upper() == rfc.upper():
            return t["id"]
    raise ValueError(f"Tenant con RFC '{rfc}' no encontrado. Tenants disponibles: {[t['rfc'] for t in tenants]}")


# ── Parser XML CFDI 4.0 ───────────────────────────────────────────────────────

def parse_xml(path: Path) -> Optional[dict]:
    """Parsea un CFDI 4.0 y devuelve dict listo para insertar."""
    try:
        tree = ET.parse(path)
        root = tree.getroot()

        # Detectar namespace dinámicamente (algunos CFDIs usan versión 3.3)
        tag = root.tag
        if "cfd/4" in tag:
            ns = CFDI_NS
        elif "cfd/3" in tag:
            ns = {
                "cfdi": "http://www.sat.gob.mx/cfd/3",
                "tfd":  "http://www.sat.gob.mx/TimbreFiscalDigital",
            }
        else:
            ns = CFDI_NS

        attr = root.attrib

        # UUID del timbre fiscal
        tfd = root.find(".//tfd:TimbreFiscalDigital", ns)
        uuid_cfdi = tfd.attrib.get("UUID") if tfd is not None else attr.get("Folio", "")

        # Emisor / Receptor
        emisor = root.find("cfdi:Emisor", ns)
        receptor = root.find("cfdi:Receptor", ns)

        rfc_emisor = emisor.attrib.get("Rfc", "") if emisor is not None else ""
        nombre_emisor = emisor.attrib.get("Nombre", "") if emisor is not None else ""
        rfc_receptor = receptor.attrib.get("Rfc", "") if receptor is not None else ""
        nombre_receptor = receptor.attrib.get("Nombre", "") if receptor is not None else ""

        # Importes
        subtotal = float(attr.get("SubTotal", 0))
        total = float(attr.get("Total", 0))
        moneda = attr.get("Moneda", "MXN")
        tipo_cambio = float(attr.get("TipoCambio", 1.0)) if moneda != "MXN" else 1.0

        # IVA — buscar en impuestos trasladados
        iva = 0.0
        impuestos = root.find("cfdi:Impuestos", ns)
        if impuestos is not None:
            traslados = impuestos.find("cfdi:Traslados", ns)
            if traslados is not None:
                for t in traslados.findall("cfdi:Traslado", ns):
                    if t.attrib.get("Impuesto") == "002":  # 002 = IVA
                        iva += float(t.attrib.get("Importe", 0))

        # Tipo de comprobante
        tipo_comp = attr.get("TipoDeComprobante", "I")
        tipo = "ingreso" if tipo_comp == "I" else "egreso" if tipo_comp == "E" else "ingreso"

        # Fecha
        fecha_str = attr.get("Fecha", "")
        try:
            fecha = datetime.fromisoformat(fecha_str.replace("T", " "))
        except Exception:
            fecha = datetime.utcnow()

        # Concepto principal
        conceptos = root.find("cfdi:Conceptos", ns)
        concepto = ""
        if conceptos is not None:
            primer = conceptos.find("cfdi:Concepto", ns)
            if primer is not None:
                concepto = primer.attrib.get("Descripcion", "")[:500]

        # XML crudo (para archivo)
        xml_raw = path.read_text(encoding="utf-8", errors="replace")[:65000]

        return {
            "tipo": tipo,
            "folio": attr.get("Folio", ""),
            "uuid_cfdi": uuid_cfdi,
            "rfc_emisor": rfc_emisor,
            "rfc_receptor": rfc_receptor,
            "nombre_emisor": nombre_emisor,
            "nombre_receptor": nombre_receptor,
            "subtotal": subtotal,
            "iva": iva,
            "total": total,
            "moneda": moneda,
            "tipo_cambio": tipo_cambio,
            "estado": "pagada",
            "fecha_emision": fecha.isoformat(),
            "concepto": concepto,
            "_xml_raw": xml_raw,
            "_source_file": path.name,
        }
    except Exception as e:
        return {"_error": str(e), "_source_file": path.name}


# ── Parser Excel ──────────────────────────────────────────────────────────────

# Mapeo de nombres de columna comunes → campos del modelo
_EXCEL_COL_MAP = {
    # RFC
    "rfc emisor": "rfc_emisor", "rfc_emisor": "rfc_emisor", "emisor rfc": "rfc_emisor",
    "rfc receptor": "rfc_receptor", "rfc_receptor": "rfc_receptor",
    # Nombres
    "nombre emisor": "nombre_emisor", "proveedor": "nombre_emisor", "razón social emisor": "nombre_emisor",
    "nombre receptor": "nombre_receptor", "cliente": "nombre_receptor",
    # Importes
    "subtotal": "subtotal", "sub total": "subtotal", "importe": "subtotal",
    "iva": "iva", "impuesto": "iva", "i.v.a": "iva",
    "total": "total", "total factura": "total",
    # Fecha
    "fecha": "fecha_emision", "fecha emisión": "fecha_emision", "fecha emision": "fecha_emision",
    "fecha factura": "fecha_emision",
    # Otros
    "folio": "folio", "serie folio": "folio",
    "uuid": "uuid_cfdi", "folio fiscal": "uuid_cfdi",
    "concepto": "concepto", "descripción": "concepto", "descripcion": "concepto",
    "moneda": "moneda",
    "tipo": "tipo", "tipo comprobante": "tipo",
    "tipo de cambio": "tipo_cambio", "tc": "tipo_cambio",
    "estado": "estado",
}


def _normalize_col(name: str) -> str:
    return name.strip().lower().replace("  ", " ")


def parse_excel(path: Path) -> list[dict]:
    if not EXCEL_OK:
        print("  ⚠ openpyxl no instalado. Instala con: pip install openpyxl")
        return []
    try:
        wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
        ws = wb.active
        rows = list(ws.iter_rows(values_only=True))
        if not rows:
            return []

        # Detectar fila de encabezados (primera fila no vacía)
        header_row = None
        for i, row in enumerate(rows):
            if any(c is not None for c in row):
                header_row = i
                break
        if header_row is None:
            return []

        headers = [_normalize_col(str(c)) if c else "" for c in rows[header_row]]
        col_map = {}
        for idx, h in enumerate(headers):
            mapped = _EXCEL_COL_MAP.get(h)
            if mapped and mapped not in col_map:
                col_map[idx] = mapped

        results = []
        for row in rows[header_row + 1:]:
            if not any(c is not None for c in row):
                continue
            record = {}
            for idx, field in col_map.items():
                val = row[idx] if idx < len(row) else None
                if val is not None:
                    record[field] = val

            if not record:
                continue

            # Normalizar tipos
            for field in ("subtotal", "iva", "total", "tipo_cambio"):
                if field in record:
                    try:
                        record[field] = float(str(record[field]).replace(",", "").replace("$", "").strip())
                    except Exception:
                        record[field] = 0.0

            # Normalizar fecha
            if "fecha_emision" in record:
                fe = record["fecha_emision"]
                if isinstance(fe, datetime):
                    record["fecha_emision"] = fe.isoformat()
                elif isinstance(fe, str):
                    for fmt in ("%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y", "%Y/%m/%d"):
                        try:
                            record["fecha_emision"] = datetime.strptime(fe.strip(), fmt).isoformat()
                            break
                        except Exception:
                            pass

            # Normalizar tipo
            if "tipo" in record:
                t = str(record["tipo"]).lower()
                record["tipo"] = "egreso" if any(k in t for k in ("e", "egreso", "gasto", "compra")) else "ingreso"
            else:
                record["tipo"] = "ingreso"

            # Defaults
            record.setdefault("moneda", "MXN")
            record.setdefault("tipo_cambio", 1.0)
            record.setdefault("estado", "pagada")
            record["_source_file"] = path.name

            results.append(record)

        wb.close()
        return results
    except Exception as e:
        return [{"_error": str(e), "_source_file": path.name}]


# ── Parser CSV ────────────────────────────────────────────────────────────────

def parse_csv(path: Path) -> list[dict]:
    results = []
    try:
        with path.open(newline="", encoding="utf-8-sig", errors="replace") as f:
            # Detectar delimitador
            sample = f.read(2048)
            f.seek(0)
            dialect = csv.Sniffer().sniff(sample, delimiters=",;\t|")
            reader = csv.DictReader(f, dialect=dialect)
            for row in reader:
                record = {}
                for col, val in row.items():
                    if col is None:
                        continue
                    mapped = _EXCEL_COL_MAP.get(_normalize_col(col))
                    if mapped:
                        record[mapped] = val.strip() if val else ""

                if not record:
                    continue

                for field in ("subtotal", "iva", "total", "tipo_cambio"):
                    if field in record and record[field]:
                        try:
                            record[field] = float(str(record[field]).replace(",", "").replace("$", "").strip())
                        except Exception:
                            record[field] = 0.0

                if "fecha_emision" in record and record["fecha_emision"]:
                    for fmt in ("%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y", "%Y/%m/%d"):
                        try:
                            record["fecha_emision"] = datetime.strptime(record["fecha_emision"], fmt).isoformat()
                            break
                        except Exception:
                            pass

                record.setdefault("tipo", "ingreso")
                record.setdefault("moneda", "MXN")
                record.setdefault("tipo_cambio", 1.0)
                record.setdefault("estado", "pagada")
                record["_source_file"] = path.name
                results.append(record)
    except Exception as e:
        results.append({"_error": str(e), "_source_file": path.name})
    return results


# ── Inserción en BD vía API ───────────────────────────────────────────────────

def insert_factura(api_url: str, token: str, record: dict) -> dict:
    payload = {k: v for k, v in record.items() if not k.startswith("_")}
    return _post(f"{api_url}/facturas", payload, token)


# ── Main ─────────────────────────────────────────────────────────────────────

def collect_files(args) -> list[Path]:
    files = []
    if args.file:
        files.append(Path(args.file))
    if args.dir:
        d = Path(args.dir)
        for ext in ("*.xml", "*.XML", "*.xlsx", "*.XLSX", "*.csv", "*.CSV"):
            files.extend(d.glob(ext))
    return sorted(set(files))


def main():
    parser = argparse.ArgumentParser(description="Migración legacy → Mystic BD")
    parser.add_argument("--dir", help="Carpeta con archivos")
    parser.add_argument("--file", help="Archivo individual")
    parser.add_argument("--tenant-rfc", required=True, help="RFC del tenant destino")
    parser.add_argument("--dry-run", action="store_true", help="Solo parsea, no inserta")
    parser.add_argument("--api-url", default=DEFAULT_API)
    parser.add_argument("--email", default=DEFAULT_EMAIL)
    parser.add_argument("--password", default=DEFAULT_PASS)
    args = parser.parse_args()

    if not args.dir and not args.file:
        parser.error("Especifica --dir o --file")

    print("=== Migración Legacy → Mystic ===\n")
    print(f"  API:       {args.api_url}")
    print(f"  Tenant:    RFC {args.tenant_rfc}")
    print(f"  Dry run:   {args.dry_run}\n")

    # Auth + tenant
    if not args.dry_run:
        print("[1/4] Autenticando...")
        try:
            token = login(args.api_url, args.email, args.password)
            print("      Token OK")
        except Exception as e:
            print(f"      ERROR: {e}")
            sys.exit(1)

        print("[2/4] Obteniendo tenant...")
        try:
            tenant_id = get_tenant_id(args.api_url, token, args.tenant_rfc)
            print(f"      tenant_id: {tenant_id[:8]}...")
        except Exception as e:
            print(f"      ERROR: {e}")
            sys.exit(1)
    else:
        token = ""
        tenant_id = "dry-run-tenant-id"

    # Recolectar archivos
    print("[3/4] Escaneando archivos...")
    files = collect_files(args)
    if not files:
        print("      No se encontraron archivos .xml / .xlsx / .csv")
        sys.exit(0)
    print(f"      {len(files)} archivos encontrados\n")

    # Procesar
    print("[4/4] Procesando e insertando...\n")
    stats = {"ok": 0, "skip": 0, "error": 0, "parse_error": 0}
    error_log = []

    for path in files:
        ext = path.suffix.lower()
        print(f"  📄 {path.name}", end=" → ")

        # Parsear
        if ext == ".xml":
            records = [parse_xml(path)]
        elif ext == ".xlsx":
            records = parse_excel(path)
        elif ext == ".csv":
            records = parse_csv(path)
        else:
            print("skip (formato no soportado)")
            stats["skip"] += 1
            continue

        parsed_ok = [r for r in records if "_error" not in r]
        parsed_err = [r for r in records if "_error" in r]

        if parsed_err:
            for e in parsed_err:
                print(f"\n    ⚠ Parse error: {e['_error']}")
                stats["parse_error"] += 1
            if not parsed_ok:
                continue

        print(f"{len(parsed_ok)} registro(s)")

        for record in parsed_ok:
            if args.dry_run:
                print(f"    [DRY] {record.get('tipo','?')} | {record.get('rfc_emisor','?')} | "
                      f"{record.get('fecha_emision','?')[:10] if record.get('fecha_emision') else '?'} | "
                      f"Total: {record.get('total', 0):,.2f} {record.get('moneda','MXN')}")
                stats["ok"] += 1
                continue

            # Inyectar tenant_id (la API lo sobreescribe con el del token, pero lo mandamos igual)
            record["tenant_id"] = tenant_id

            try:
                result = insert_factura(args.api_url, token, record)
                stats["ok"] += 1
            except Exception as e:
                err_msg = str(e)
                if "uuid_cfdi" in err_msg.lower() or "unique" in err_msg.lower():
                    print(f"    ⚠ Duplicado (uuid_cfdi ya existe): {record.get('uuid_cfdi','?')[:8]}...")
                    stats["skip"] += 1
                else:
                    print(f"    ✗ Error: {err_msg[:100]}")
                    error_log.append({"file": path.name, "error": err_msg})
                    stats["error"] += 1

    # Resumen
    print(f"\n{'='*50}")
    print(f"  ✅ Insertadas:     {stats['ok']}")
    print(f"  ⚠  Duplicadas:     {stats['skip']}")
    print(f"  ✗  Errores BD:     {stats['error']}")
    print(f"  ✗  Errores parse:  {stats['parse_error']}")
    print(f"{'='*50}")

    if error_log:
        log_path = Path("migration_errors.json")
        log_path.write_text(json.dumps(error_log, indent=2, ensure_ascii=False))
        print(f"\n  Log de errores: {log_path}")

    if stats["ok"] > 0 and not args.dry_run:
        print(f"\n✅ Migración completada — {stats['ok']} facturas en la BD de {args.tenant_rfc}")
    elif args.dry_run:
        print(f"\n  Dry run completo — ejecuta sin --dry-run para insertar")


if __name__ == "__main__":
    main()

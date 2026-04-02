#!/usr/bin/env python3
"""
Audit Rules - Verifica que el proyecto cumpla las reglas establecidas
Uso: python3 scripts/audit_rules.py
"""

import os
import re
import sys
from pathlib import Path
from typing import List


class RuleAuditor:
    def __init__(self, root_path: str = "."):
        self.root = Path(root_path)
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.checked_files = 0

    def audit_all(self) -> None:
        print("Iniciando auditoria de reglas del proyecto...\n")
        self.audit_python_files()
        self.audit_typescript_files()
        self.audit_env_files()
        self.audit_docker_files()
        self.audit_structure()
        self.print_report()

    def audit_python_files(self) -> None:
        for file_path in self.root.rglob("*.py"):
            if any(skip in str(file_path) for skip in ("venv", "__pycache__", ".git", "node_modules")):
                continue
            self.checked_files += 1
            content = file_path.read_text(encoding="utf-8", errors="ignore")

            # No usar print() para debug (permitir prints con formato especial)
            debug_prints = [
                i + 1
                for i, line in enumerate(content.split("\n"))
                if "print(" in line and not line.strip().startswith("#")
            ]
            if debug_prints:
                self.warnings.append(f"{file_path}: print() en líneas {debug_prints[:3]}")

            # No hardcodear URLs externas
            if re.search(r'(http://|https://)(?!localhost|127\\.0\\.0\\.1|0\\.0\\.0\\.0|example\\.com)', content):
                self.warnings.append(f"{file_path}: posible URL hardcodeada")

    def audit_typescript_files(self) -> None:
        patterns = list(self.root.rglob("*.tsx")) + list(self.root.rglob("*.ts"))
        for file_path in patterns:
            if "node_modules" in str(file_path) or ".next" in str(file_path):
                continue
            self.checked_files += 1
            content = file_path.read_text(encoding="utf-8", errors="ignore")

            if ": any" in content or "as any" in content:
                self.warnings.append(f"{file_path}: uso de 'any' detectado")

            if re.search(r"\bvar\s+", content):
                self.errors.append(f"{file_path}: uso de 'var' detectado — usar const/let")

    def audit_env_files(self) -> None:
        for file_path in list(self.root.rglob(".env")) + list(self.root.rglob(".env.vps")):
            if ".env.example" in str(file_path) or ".git" in str(file_path):
                continue
            content = file_path.read_text(encoding="utf-8", errors="ignore")
            for pattern in ("PASSWORD=", "SECRET=", "KEY=", "TOKEN="):
                for line in content.split("\n"):
                    if pattern in line and not any(
                        p in line for p in ("your_", "placeholder", "example", "changeme", "=")
                    ):
                        if len(line.split("=", 1)) > 1 and line.split("=", 1)[1].strip():
                            self.warnings.append(f"{file_path}: valor sensible detectado ({pattern})")
                            break

    def audit_docker_files(self) -> None:
        for file_path in self.root.rglob("docker-compose*.yml"):
            content = file_path.read_text(encoding="utf-8", errors="ignore")
            if ("5432:5432" in content or "6379:6379" in content) and "127.0.0.1" not in content:
                self.errors.append(f"{file_path}: puerto de DB expuesto sin restricción 127.0.0.1")

    def audit_structure(self) -> None:
        for dir_name in ("backend", "frontend", "packages", "infra", "docs"):
            if not (self.root / dir_name).exists():
                self.errors.append(f"Directorio requerido faltante: {dir_name}")

    def print_report(self) -> None:
        print(f"Archivos revisados : {self.checked_files}")
        print(f"Errores criticos   : {len(self.errors)}")
        print(f"Advertencias       : {len(self.warnings)}\n")

        if self.errors:
            print("ERRORES CRITICOS:")
            for e in self.errors[:10]:
                print(f"  [ERR] {e}")
            if len(self.errors) > 10:
                print(f"  ... y {len(self.errors) - 10} mas")
            print()

        if self.warnings:
            print("ADVERTENCIAS:")
            for w in self.warnings[:10]:
                print(f"  [WARN] {w}")
            if len(self.warnings) > 10:
                print(f"  ... y {len(self.warnings) - 10} mas")
            print()

        if not self.errors:
            print("[OK] Sin errores criticos")
            sys.exit(0)
        else:
            print("[FAIL] Errores criticos encontrados. Corregir antes de continuar.")
            sys.exit(1)


if __name__ == "__main__":
    root = sys.argv[1] if len(sys.argv) > 1 else "."
    RuleAuditor(root).audit_all()

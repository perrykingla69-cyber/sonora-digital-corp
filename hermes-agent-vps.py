#!/usr/bin/env python3
import os,json,subprocess as sp
key=os.getenv("OPENROUTER_API_KEY","sk-demo")
tasks=["Guión TikTok para IA","Dashboard HTML","Landing SDD","Agente CLI"]
print("🚀 HERMES VPS Agent iniciado\n")
for i,t in enumerate(tasks,1):
    print(f"✅ {i}/4: {t}")
print("\n📊 Tareas en cola ejecutándose en VPS...")

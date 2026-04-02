"""
MYSTIC_ACADEMY - Sistema de Escuela Gamificada
Parte del ecosistema Mystic Swarm Agent V2
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Callable, Any
from enum import Enum, auto
from datetime import datetime
import json
import random

class RangoAcademico(Enum):
    """Sistema de rangos tipo RPG"""
    NOVATO = ("Novato", 0, 100, "🌱")
    APRENDIZ = ("Aprendiz", 100, 300, "🌿")
    ESTUDIANTE = ("Estudiante", 300, 600, "📚")
    DISCIPULO = ("Discípulo", 600, 1000, "🎯")
    ERUDITO = ("Erudito", 1000, 1500, "🧠")
    MAESTRO = ("Maestro", 1500, 2500, "👑")
    SABIO = ("Sabio", 2500, 4000, "🔮")
    LEGENDARIO = ("Legendario", 4000, float('inf'), "⭐")
    
    def __init__(self, nombre, min_exp, max_exp, emoji):
        self.nombre = nombre
        self.min_exp = min_exp
        self.max_exp = max_exp
        self.emoji = emoji

@dataclass
class Logro:
    """Sistema de logros/badges"""
    id: str
    nombre: str
    descripcion: str
    emoji: str
    xp_reward: int
    condicion: Callable[[Any], bool] = field(default=lambda x: True)
    desbloqueado: bool = False
    fecha_desbloqueo: Optional[datetime] = None
    
    def verificar(self, contexto: Any) -> bool:
        if not self.desbloqueado and self.condicion(contexto):
            self.desbloquear()
            return True
        return False
    
    def desbloquear(self):
        self.desbloqueado = True
        self.fecha_desbloqueo = datetime.now()

@dataclass
class Mision:
    """Misiones diarias/semanales"""
    id: str
    titulo: str
    descripcion: str
    tipo: str  # "diaria", "semanal", "especial"
    xp_reward: int
    progreso: int = 0
    objetivo: int = 1
    completada: bool = False
    fecha_creacion: datetime = field(default_factory=datetime.now)
    
    @property
    def progreso_pct(self) -> float:
        return min(100, (self.progreso / self.objetivo) * 100)
    
    def avanzar(self, cantidad: int = 1):
        self.progreso += cantidad
        if self.progreso >= self.objetivo:
            self.completada = True
            return self.xp_reward
        return 0

class EstudianteAgente:
    """Agente con sistema de progresión gamificado"""
    
    def __init__(self, agente_id: str, nombre: str):
        self.agente_id = agente_id
        self.nombre = nombre
        
        # Stats RPG
        self.nivel = 1
        self.experiencia = 0
        self.rango = RangoAcademico.NOVATO
        
        # Atributos mejorables
        self.stats = {
            "inteligencia": 10,
            "creatividad": 10,
            "colaboracion": 10,
            "resiliencia": 10,
            "velocidad": 10
        }
        
        # Sistemas
        self.logros: Dict[str, Logro] = {}
        self.misiones_activas: List[Mision] = []
        self.historial: List[Dict] = []
        self.streak_dias = 0
        self.ultima_actividad = datetime.now()
        
        self._inicializar_logros()
    
    def _inicializar_logros(self):
        """Crea los logros por defecto"""
        logros_default = [
            Logro("primera_mision", "Primeros Pasos", 
                  "Completa tu primera misión", "🎯", 50),
            Logro("maestro_novato", "Graduación", 
                  "Alcanza el rango de Aprendiz", "🎓", 100),
            Logro("experto_colab", "Trabajo en Equipo", 
                  "Colabora en 10 proyectos", "🤝", 200),
            Logro("velocista", "Velocidad de Luz", 
                  "Completa 5 misiones en un día", "⚡", 150),
            Logro("perseverante", "Sin Rendirse", 
                  "Mantén un streak de 7 días", "🔥", 300),
        ]
        for logro in logros_default:
            self.logros[logro.id] = logro
    
    @property
    def xp_para_siguiente_nivel(self) -> int:
        return int(100 * (1.5 ** (self.nivel - 1)))
    
    def ganar_xp(self, cantidad: int, razon: str = ""):
        """Añade experiencia y verifica subidas de nivel"""
        self.experiencia += cantidad
        self.historial.append({
            "tipo": "xp_ganada",
            "cantidad": cantidad,
            "razon": razon,
            "timestamp": datetime.now().isoformat()
        })
        
        # Verificar subida de nivel
        while self.experiencia >= self.xp_para_siguiente_nivel:
            self._subir_nivel()
        
        # Actualizar rango
        self._actualizar_rango()
        
        return self._generar_resumen()
    
    def _subir_nivel(self):
        """Sube de nivel y mejora stats"""
        self.nivel += 1
        # Mejorar stats aleatoriamente
        stat_mejorado = random.choice(list(self.stats.keys()))
        self.stats[stat_mejorado] += 2
        
        self.historial.append({
            "tipo": "nivel_up",
            "nivel": self.nivel,
            "stat_mejorado": stat_mejorado,
            "timestamp": datetime.now().isoformat()
        })
    
    def _actualizar_rango(self):
        """Actualiza el rango académico según XP total"""
        for rango in RangoAcademico:
            if rango.min_exp <= self.experiencia < rango.max_exp:
                if self.rango != rango:
                    self.rango = rango
                    self.historial.append({
                        "tipo": "rango_up",
                        "rango": rango.nombre,
                        "timestamp": datetime.now().isoformat()
                    })
                break
    
    def asignar_mision(self, mision: Mision):
        """Añade una nueva misión al estudiante"""
        self.misiones_activas.append(mision)
        return f"📋 Misión asignada: {mision.titulo}"
    
    def completar_mision(self, mision_id: str) -> Dict:
        """Marca una misión como completada"""
        for mision in self.misiones_activas:
            if mision.id == mision_id and mision.completada:
                xp = mision.xp_reward
                resumen = self.ganar_xp(xp, f"Misión: {mision.titulo}")
                
                # Verificar logros
                self._verificar_logros()
                
                return {
                    "exito": True,
                    "xp_ganada": xp,
                    "resumen": resumen
                }
        return {"exito": False, "error": "Misión no encontrada o no completada"}
    
    def _verificar_logros(self):
        """Verifica condiciones de logros"""
        contexto = {
            "nivel": self.nivel,
            "misiones_completadas": len([m for m in self.historial 
                                        if m.get("tipo") == "mision_completada"]),
            "streak": self.streak_dias
        }
        
        for logro in self.logros.values():
            if logro.verificar(contexto):
                self.ganar_xp(logro.xp_reward, f"Logro desbloqueado: {logro.nombre}")
    
    def _generar_resumen(self) -> Dict:
        """Genera resumen del estado actual"""
        return {
            "nombre": self.nombre,
            "nivel": self.nivel,
            "rango": f"{self.rango.emoji} {self.rango.nombre}",
            "experiencia": f"{self.experiencia}/{self.xp_para_siguiente_nivel}",
            "progreso_pct": (self.experiencia / self.xp_para_siguiente_nivel) * 100,
            "stats": self.stats,
            "misiones_activas": len([m for m in self.misiones_activas if not m.completada]),
            "logros_desbloqueados": len([l for l in self.logros.values() if l.desbloqueado])
        }
    
    def obtener_perfil(self) -> str:
        """Genera representación visual del perfil"""
        bar_length = 20
        progress = int((self.experiencia / self.xp_para_siguiente_nivel) * bar_length)
        bar = "█" * progress + "░" * (bar_length - progress)
        
        perfil = f"""
╔══════════════════════════════════════╗
║     🎓 MYSTIC ACADEMY - PERFIL      ║
╠══════════════════════════════════════╣
║  {self.rango.emoji} {self.nombre:<28} ║
║  {self.rango.nombre:^34} ║
╠══════════════════════════════════════╣
║  Nivel: {self.nivel:<25} ║
║  [{bar}] {self.experiencia}/{self.xp_para_siguiente_nivel:<5} ║
╠══════════════════════════════════════╣
║  STATS:                              ║
║  🧠 INT: {self.stats['inteligencia']:<3}  🎨 CRE: {self.stats['creatividad']:<3}      ║
║  🤝 COL: {self.stats['colaboracion']:<3}  🛡️  RES: {self.stats['resiliencia']:<3}      ║
║  ⚡ VEL: {self.stats['velocidad']:<3}                        ║
╠══════════════════════════════════════╣
║  🔥 Streak: {self.streak_dias:<3} días                ║
║  🏆 Logros: {sum(1 for l in self.logros.values() if l.desbloqueado)}/{len(self.logros)}                  ║
╚══════════════════════════════════════╝
        """
        return perfil

class MysticAcademy:
    """Gestor central de la academia"""
    
    def __init__(self):
        self.estudiantes: Dict[str, EstudianteAgente] = {}
        self.misiones_disponibles: List[Mision] = []
        self.ranking: List[tuple] = []
        self.eventos_especiales: List[Dict] = []
    
    def registrar_estudiante(self, agente_id: str, nombre: str) -> EstudianteAgente:
        """Registra un nuevo agente en la academia"""
        if agente_id not in self.estudiantes:
            estudiante = EstudianteAgente(agente_id, nombre)
            self.estudiantes[agente_id] = estudiante
            return estudiante
        return self.estudiantes[agente_id]
    
    def crear_mision(self, titulo: str, descripcion: str, 
                    tipo: str, xp: int, objetivo: int = 1) -> Mision:
        """Crea una nueva misión para la academia"""
        mision_id = f"mision_{len(self.misiones_disponibles)}_{int(datetime.now().timestamp())}"
        mision = Mision(
            id=mision_id,
            titulo=titulo,
            descripcion=descripcion,
            tipo=tipo,
            xp_reward=xp,
            objetivo=objetivo
        )
        self.misiones_disponibles.append(mision)
        return mision
    
    def asignar_mision_a_estudiante(self, agente_id: str, mision: Mision):
        """Asigna una misión a un estudiante específico"""
        if agente_id in self.estudiantes:
            return self.estudiantes[agente_id].asignar_mision(mision)
        return "Estudiante no encontrado"
    
    def obtener_leaderboard(self, top: int = 10) -> List[Dict]:
        """Obtiene el ranking de estudiantes"""
        ranking = sorted(
            self.estudiantes.values(),
            key=lambda e: (e.nivel, e.experiencia),
            reverse=True
        )
        return [
            {
                "posicion": i+1,
                "nombre": e.nombre,
                "nivel": e.nivel,
                "rango": e.rango.nombre,
                "emoji": e.rango.emoji,
                "xp": e.experiencia
            }
            for i, e in enumerate(ranking[:top])
        ]
    
    def generar_informe(self, agente_id: str) -> Dict:
        """Genera informe detallado de un estudiante"""
        if agente_id not in self.estudiantes:
            return {"error": "Estudiante no encontrado"}
        
        e = self.estudiantes[agente_id]
        return {
            "perfil": e._generar_resumen(),
            "logros": [
                {"nombre": l.nombre, "desbloqueado": l.desbloqueado, "emoji": l.emoji}
                for l in e.logros.values()
            ],
            "misiones": [
                {"titulo": m.titulo, "completada": m.completada, "progreso": m.progreso_pct}
                for m in e.misiones_activas
            ],
            "historial_reciente": e.historial[-10:]
        }

# Factory function para integración con el swarm
def crear_academy() -> MysticAcademy:
    """Crea una instancia de la academia"""
    return MysticAcademy()

def gamificar_agente(academy: MysticAcademy, agente_id: str, nombre: str) -> EstudianteAgente:
    """Envuelve un agente existente con sistema de gamificación"""
    return academy.registrar_estudiante(agente_id, nombre)

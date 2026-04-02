from typing import Optional
from pydantic import BaseModel


class LeadCreate(BaseModel):
    nombre: str
    empresa: Optional[str] = None
    email: Optional[str] = None
    telefono: Optional[str] = None
    fuente: Optional[str] = None
    estado: Optional[str] = None
    notas: Optional[str] = None


class LeadUpdate(BaseModel):
    nombre: Optional[str] = None
    empresa: Optional[str] = None
    email: Optional[str] = None
    telefono: Optional[str] = None
    fuente: Optional[str] = None
    estado: Optional[str] = None
    notas: Optional[str] = None

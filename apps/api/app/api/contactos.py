from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..core import legacy  # noqa: F401
from ..db.session import get_db
from ..services.contact_service import create_contact, deactivate_contact, get_contact, list_contacts, update_contact
from ..schemas import ContactoCreate, ContactoResponse
from security import get_current_user  # type: ignore

router = APIRouter(tags=["Directorio"])


@router.post("/contactos", response_model=ContactoResponse)
async def crear_contacto(body: ContactoCreate, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    return create_contact(db, current_user.tenant_id, body)


@router.get("/contactos", response_model=List[ContactoResponse])
async def listar_contactos(
    tipo: Optional[str] = None,
    buscar: Optional[str] = None,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return list_contacts(db, current_user.tenant_id, tipo, buscar)


@router.get("/contactos/{contacto_id}", response_model=ContactoResponse)
async def obtener_contacto(contacto_id: str, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    return get_contact(db, current_user.tenant_id, contacto_id)


@router.patch("/contactos/{contacto_id}", response_model=ContactoResponse)
async def actualizar_contacto(contacto_id: str, body: dict, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    return update_contact(db, current_user.tenant_id, contacto_id, body)


@router.delete("/contactos/{contacto_id}")
async def eliminar_contacto(contacto_id: str, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    return deactivate_contact(db, current_user.tenant_id, contacto_id)

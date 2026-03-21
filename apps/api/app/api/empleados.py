from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..core import legacy  # noqa: F401
from ..db.session import get_db
from ..services.employee_service import (
    create_employee,
    deactivate_employee,
    get_employee,
    list_employees,
    payroll_preview,
    update_employee,
)
from ..schemas import EmpleadoCreate, EmpleadoResponse
from security import get_current_user  # type: ignore

router = APIRouter(tags=["Nomina"])


@router.post("/empleados", response_model=EmpleadoResponse)
async def crear_empleado(body: EmpleadoCreate, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    return create_employee(db, current_user.tenant_id, body)


@router.get("/empleados", response_model=List[EmpleadoResponse])
async def listar_empleados(
    incluir_bajas: bool = False,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return list_employees(db, current_user.tenant_id, incluir_bajas)


@router.get("/empleados/{empleado_id}", response_model=EmpleadoResponse)
async def obtener_empleado(empleado_id: str, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    return get_employee(db, current_user.tenant_id, empleado_id)


@router.patch("/empleados/{empleado_id}", response_model=EmpleadoResponse)
async def actualizar_empleado(empleado_id: str, body: dict, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    return update_employee(db, current_user.tenant_id, empleado_id, body)


@router.delete("/empleados/{empleado_id}")
async def dar_baja_empleado(empleado_id: str, current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    return deactivate_employee(db, current_user.tenant_id, empleado_id)


@router.get("/nomina/calculos/{empleado_id}")
async def preview_nomina(
    empleado_id: str,
    dias: int = 30,
    percepciones_extra: float = 0.0,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return payroll_preview(db, current_user.tenant_id, empleado_id, dias, percepciones_extra)

from pydantic import BaseModel


class AlertaConfigUpdate(BaseModel):
    activo: bool | None = None
    hora_manana: str | None = None
    hora_tarde: str | None = None
    chat_id_telegram: str | None = None

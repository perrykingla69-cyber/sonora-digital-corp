import os
import logging
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fiscal_agent import FiscalAgent
from schemas.fiscal_requests import FiscalOperationRequest

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Fiscal Agent", version="1.0.0")
agent = FiscalAgent()


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    health_status = await agent.health()
    return JSONResponse(content=health_status, status_code=200)


@app.post("/operate")
async def operate(req: FiscalOperationRequest):
    """Ejecuta operación fiscal."""
    result = await agent.execute(req.operation, req.inputs, req.tenant_id)

    if not result['success']:
        raise HTTPException(status_code=400, detail=result['error'])

    return result


@app.get("/operations")
async def list_operations():
    """Retorna lista de operaciones disponibles."""
    return {"operations": list(agent.OPERATIONS.keys())}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8001))
    uvicorn.run(app, host="0.0.0.0", port=port)

from __future__ import annotations

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from .services.diagnosis_service import DiagnosisService
import uvicorn
import logging

app = FastAPI(title="CausePilot - Phase1")
service = DiagnosisService()


class DiagnoseRequest(BaseModel):
    # Accept free-form JSON; validation done in service
    data: dict


@app.post("/diagnose")
def diagnose(req: dict):
    try:
        result = service.diagnose(req)
        return result.model_dump()
    except Exception as exc:
        logging.exception("diagnose failed")
        raise HTTPException(status_code=400, detail=str(exc))


if __name__ == "__main__":
    uvicorn.run("causepilot.main:app", host="0.0.0.0", port=8000, reload=False)

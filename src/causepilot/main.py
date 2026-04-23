from __future__ import annotations

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from .services.diagnosis_service import DiagnosisService
import uvicorn
import logging
from .config.settings import settings

app = FastAPI(title="CausePilot")
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


def main() -> None:
    """Console entrypoint for `uv run causepilot`.

    Starts the FastAPI app with uvicorn.
    """
    uvicorn.run(
        "causepilot.main:app",
        host=settings.CAUSEPILOT_BIND_HOST,
        port=settings.CAUSEPILOT_BIND_PORT,
        reload=False,
    )


if __name__ == "__main__":
    main()

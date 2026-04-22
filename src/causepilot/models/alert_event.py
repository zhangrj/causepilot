from __future__ import annotations

from typing import Dict, Optional
from pydantic import BaseModel
from datetime import datetime


class AlertEvent(BaseModel):
    alert_id: Optional[str] = None
    title: str
    severity: str
    service: str
    environment: str
    metric: Optional[str]
    metric: Optional[str] = None
    current_value: Optional[float] = None
    threshold: Optional[float] = None
    window_start: datetime
    window_end: datetime
    labels: Optional[Dict[str, str]] = None
    annotations: Optional[Dict[str, str]] = None

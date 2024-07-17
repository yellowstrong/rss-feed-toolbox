from typing import Optional

from pydantic import BaseModel


class ScheduleInfo(BaseModel):
    id: Optional[str] = None
    name: Optional[str] = None
    status: Optional[str] = None
    next_run: Optional[str] = None

from fastapi import APIRouter, BackgroundTasks

from app.utils.response import HttpResponse, response_success
from scheduler import Scheduler

router = APIRouter(prefix="/scheduler", tags=["Scheduler"])


@router.get("/")
def get_all_schedule() -> HttpResponse:
    data = Scheduler().list()
    return response_success(data)


@router.get('/run')
def run_subscribe(id:str,background_tasks: BackgroundTasks) -> HttpResponse:
    background_tasks.add_task(Scheduler().start, job_id=id)
    return response_success()

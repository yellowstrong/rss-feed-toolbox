from fastapi import APIRouter, Request, BackgroundTasks

from app.utils.response import HttpResponse, response_success
from app.jobs.play import PlayJob

router = APIRouter(prefix="/webhook", tags=["WebHook"])


@router.post('/emby')
async def emby_hook(background_tasks: BackgroundTasks, request: Request) -> HttpResponse:
    json_data = await request.json()
    background_tasks.add_task(PlayJob().play_notify, json_data=json_data)
    return response_success()

from fastapi import APIRouter, Request, BackgroundTasks

from app.utils.response import HttpResponse, response_success
from app.service.webhook_service import WebhookService

router = APIRouter(prefix="/webhook", tags=["WebHook"])


@router.post('/emby')
async def emby_hook(background_tasks: BackgroundTasks, request: Request) -> HttpResponse:
    json_data = await request.json()
    background_tasks.add_task(WebhookService().do_webhook, json_data=json_data)
    return response_success()

from fastapi import APIRouter

from app.service.subscribe_service import SubscribeService
from app.types import apiproto

from app.utils.response import HttpResponse, response_success

router = APIRouter(prefix="/subscribe", tags=["Subscribe"])


@router.post('/all')
def get_subscribes(query: apiproto.SubscribeQuery) -> HttpResponse:
    data = SubscribeService.get_subscribes(query)
    return response_success(data)


@router.get('/')
def get_subscribe_by_id(id: int) -> HttpResponse:
    data = SubscribeService.get_subscribe_by_id(id)
    return response_success(data)


@router.post('/')
def edit_subscribe(subscribe: apiproto.Subscribe) -> HttpResponse:
    if subscribe.id:
        SubscribeService.update_subscribe(subscribe)
    else:
        SubscribeService.add_subscribe(subscribe)
    return response_success()


@router.delete('/')
def delete_subscribe(id: int) -> HttpResponse:
    SubscribeService.delete_subscribe(id)
    return response_success()

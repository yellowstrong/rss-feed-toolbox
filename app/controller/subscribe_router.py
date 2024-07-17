from fastapi import APIRouter, Depends

from app.depends.get_curent_user import get_current_user
from app.service.subscribe_service import SubscribeService
from app.types import apiproto

from app.utils.response import HttpResponse, response_success

router = APIRouter(prefix="/subscribe", tags=["Subscribe"])


@router.post('/add')
def add_subscribe(subscribe: apiproto.Subscribe) -> HttpResponse:
    SubscribeService.add_subscribe(subscribe)
    return response_success()


@router.post('/')
def get_subscribes(query: apiproto.SubscribeQuery) -> HttpResponse:
    data = SubscribeService.get_subscribes(query)
    return response_success(data)


@router.get('/detail')
def get_subscribe_by_id(id: int) -> HttpResponse:
    data = SubscribeService.get_subscribe_by_id(id)
    return response_success(data)


@router.put('/update')
def update_subscribe(subscribe: apiproto.Subscribe) -> HttpResponse:
    SubscribeService.update_subscribe(subscribe)
    return response_success()


@router.delete('/delete')
def delete_subscribe(id: int) -> HttpResponse:
    SubscribeService.delete_subscribe(id)
    return response_success()

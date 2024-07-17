from fastapi import APIRouter, Depends
from app.depends.get_curent_user import get_current_user
from app.service.auth_service import AuthService
from app.utils.response import response_success, HttpResponse
from app.types import apiproto

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post('/register')
def register(user: apiproto.User) -> HttpResponse:
    AuthService.register(user)
    return response_success()


@router.post('/login')
def login(login_param: apiproto.Login) -> HttpResponse:
    data = AuthService.login(login_param)
    return response_success(data)


@router.get('/user')
def get_user_info(user:apiproto.User = Depends(get_current_user)) -> HttpResponse:
    return response_success(user)

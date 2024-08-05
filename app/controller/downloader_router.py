from fastapi import APIRouter, Body

from app.service.downloader_service import DownloaderService
from app.types import apiproto
from app.utils.response import HttpResponse, response_success

router = APIRouter(prefix="/downloader", tags=["Downloader"])


@router.post('/all')
def get_downloaders(query: apiproto.DownloaderQuery) -> HttpResponse:
    data = DownloaderService.get_downloaders(query)
    return response_success(data)


@router.get('/')
def get_downloader_by_id(id: int) -> HttpResponse:
    data = DownloaderService.get_downloader_by_id(id)
    return response_success(data)


@router.post('/')
def edit_downloader(downloader: apiproto.Downloader) -> HttpResponse:
    if downloader.id:
        DownloaderService.update_downloader(downloader)
    else:
        DownloaderService.add_downloader(downloader)
    return response_success()


@router.delete('/')
def delete_downloader(id: int) -> HttpResponse:
    DownloaderService.delete_downloader(id)
    return response_success()


@router.post('/setDefault')
def set_default_downloader(id: int = Body(...,embed=True)) -> HttpResponse:
    DownloaderService.set_default_downloader(id)
    return response_success()

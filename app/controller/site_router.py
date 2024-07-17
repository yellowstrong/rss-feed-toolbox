from fastapi import APIRouter
from app.utils.response import HttpResponse, response_success
from app.service.site_service import SiteService
from app.types import apiproto

router = APIRouter(prefix="/site", tags=["Site"])


@router.post('/')
def get_all_site(query: apiproto.SiteQuery) -> HttpResponse:
    data = SiteService.get_all_site(query)
    return response_success(data)


@router.get('/rss')
def get_all_site_rss() -> HttpResponse:
    data = SiteService.get_all_site_rss()
    return response_success(data)


@router.get('/detail')
def get_site_by_id(id: int) -> HttpResponse:
    data = SiteService.get_site_by_id(id)
    return response_success(data)


@router.post('/add')
def add_site(site: apiproto.Site) -> HttpResponse:
    SiteService.add_site(site)
    return response_success()


@router.put('/update')
def update_site(site: apiproto.Site) -> HttpResponse:
    SiteService.update_site(site)
    return response_success()


@router.delete('/delete')
def delete_site(id: int) -> HttpResponse:
    SiteService.delete_site(id)
    return response_success()

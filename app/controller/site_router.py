from fastapi import APIRouter
from app.utils.response import HttpResponse, response_success
from app.service.site_service import SiteService
from app.types import apiproto

router = APIRouter(prefix="/site", tags=["Site"])


@router.post('/all')
def get_sites(query: apiproto.SiteQuery) -> HttpResponse:
    data = SiteService.get_sites(query)
    return response_success(data)


@router.get('/')
def get_site_by_id(id: int) -> HttpResponse:
    data = SiteService.get_site_by_id(id)
    return response_success(data)


@router.post('/')
def edit_site(site: apiproto.Site) -> HttpResponse:
    if site.id:
        SiteService.update_site(site)
    else:
        SiteService.add_site(site)
    return response_success()


@router.delete('/')
def delete_site(id: int) -> HttpResponse:
    SiteService.delete_site(id)
    return response_success()


@router.get('/rss')
def get_site_rss(site_id: int = None) -> HttpResponse:
    data = SiteService.get_site_rss(site_id)
    return response_success(data)

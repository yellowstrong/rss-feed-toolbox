from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.models import Site, SiteRss
from app.helper.exception_helper import BizError


class SiteDao:

    @staticmethod
    def get_all_site(session: Session, page: int = 1, page_size: int = 10) -> (int, list[Site]):
        query = session.query(Site)
        total = query.count()
        offset = (page - 1) * page_size
        query = query.order_by(desc(Site.id)).offset(offset).limit(page_size)
        result = query.all()
        return total, result

    @staticmethod
    def get_all_site_rss(session: Session) -> list[SiteRss]:
        query = session.query(SiteRss)
        result = query.all()
        return result

    @staticmethod
    def get_site_by_id(session: Session, id: int) -> Site:
        query = session.query(Site).filter_by(id=id)
        result = query.first()
        return result

    @staticmethod
    def add_site(session: Session, site: Site, site_rss: list[SiteRss]):
        session.add(site)
        session.flush()
        for item in site_rss:
            item.site_id = site.id
        session.bulk_save_objects(site_rss)

    @staticmethod
    def update_site(session: Session, site: Site, site_rss: list[SiteRss]):
        session.merge(site)
        target_site_rss = session.query(SiteRss).filter_by(site_id=site.id).all()
        to_add = [item for item in site_rss if item.id is None]
        to_modify = [item for item in site_rss if item.id is not None]
        for target_item in target_site_rss:
            deleted = True
            for item in to_modify:
                if item.id and item.id == target_item.id:
                    target_item.alias = item.alias
                    target_item.url = item.url
                    session.merge(target_item)
                    deleted = False
                    break
            if deleted:
                if len(target_item.subscribe) == 0:
                    session.delete(target_item)
                    session.flush()
                else:
                    raise BizError(f'被删除RSS存在订阅使用，无法删除，请检查后重试')
        session.bulk_save_objects(to_add)

    @staticmethod
    def delete_site(session: Session, site: Site):
        session.delete(site)

    @staticmethod
    def get_site_rss_by_id(session: Session, id: int) -> SiteRss:
        query = session.query(SiteRss).filter_by(id=id)
        result = query.first()
        return result

    @staticmethod
    def update_rss_latest_pub(session: Session, site_rss: SiteRss):
        session.merge(site_rss)

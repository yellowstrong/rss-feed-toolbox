import re
import chardet
import traceback
import xml.dom.minidom
from typing import Union
from app.config.app_config import app_config
from app.helper.logger_helper import logger
from app.helper.request_helper import RequestHelper
from app.utils.str import StringUtil


class RssHelper:

    @staticmethod
    def parse(url, timeout: int = 15) -> list[dict] | None:
        ret_array: list = []
        if not url:
            return []
        try:
            ret = RequestHelper(proxies=app_config.PROXY if app_config.PROXY else None, timeout=timeout).get_res(url)
            if not ret:
                return []
        except Exception as err:
            logger.error(f"获取RSS失败：{str(err)} - {traceback.format_exc()}")
            return []
        if ret:
            ret_xml = ""
            try:
                raw_data = ret.content
                if raw_data:
                    try:
                        result = chardet.detect(raw_data)
                        encoding = result['encoding']
                        ret_xml = raw_data.decode(encoding)
                    except Exception as e:
                        logger.debug(f"chardet解码失败：{str(e)}")
                        match = re.search(r'encoding\s*=\s*["\']([^"\']+)["\']', ret.text)
                        if match:
                            encoding = match.group(1)
                            if encoding:
                                ret_xml = raw_data.decode(encoding)
                        else:
                            ret.encoding = ret.apparent_encoding
                if not ret_xml:
                    ret_xml = ret.text
                dom_tree = xml.dom.minidom.parseString(ret_xml)
                root_node = dom_tree.documentElement
                items = root_node.getElementsByTagName("item")
                for item in items:
                    try:
                        title = RssHelper.tag_value(item, "title", default="")
                        if not title:
                            continue
                        description = RssHelper.tag_value(item, "description", default="")
                        link = RssHelper.tag_value(item, "link", default="")
                        enclosure = RssHelper.tag_value(item, "enclosure", "url", default="")
                        if not enclosure and not link:
                            continue
                        if not enclosure and link:
                            enclosure = link
                        size = RssHelper.tag_value(item, "enclosure", "length", default=0)
                        if size and str(size).isdigit():
                            size = int(size)
                        else:
                            size = 0
                        guid = RssHelper.tag_value(item, "guid", default="")
                        pubdate = RssHelper.tag_value(item, "pubDate", default="")
                        if pubdate:
                            pubdate = StringUtil.get_time(pubdate)
                        tmp_dict = {'title': title,
                                    'enclosure': enclosure,
                                    'size': size,
                                    'description': description,
                                    'link': link,
                                    'guid': guid,
                                    'pubdate': pubdate}
                        ret_array.append(tmp_dict)
                    except Exception as e1:
                        logger.debug(f"解析RSS失败：{str(e1)} - {traceback.format_exc()}")
                        continue
            except Exception as e2:
                logger.error(f"解析RSS失败：{str(e2)} - {traceback.format_exc()}")
                _rss_expired_msg = [
                    "RSS 链接已过期, 您需要获得一个新的!",
                    "RSS Link has expired, You need to get a new one!",
                    "RSS Link has expired, You need to get new!"
                ]
                if ret_xml in _rss_expired_msg:
                    return None
        return ret_array

    @staticmethod
    def tag_value(tag_item, tag_name: str, attname: str = "", default: Union[str, int] = None):
        tag_names = tag_item.getElementsByTagName(tag_name)
        if tag_names:
            if attname:
                att_value = tag_names[0].getAttribute(attname)
                if att_value:
                    return att_value
            else:
                first_child = tag_names[0].firstChild
                if first_child:
                    return first_child.data
        return default

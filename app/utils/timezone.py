import zoneinfo

from datetime import datetime

from app.config.app_config import app_config


class TimeZone:
    def __init__(self, tz: str = app_config.DATETIME_ZONE):
        self.tz_info = zoneinfo.ZoneInfo(tz)

    def now(self) -> datetime:
        """获取时区时间"""
        return datetime.now(self.tz_info)

    def f_datetime(self, dt: datetime) -> datetime:
        """datetime 时间转时区时间 """
        return dt.astimezone(self.tz_info)

    def f_str(self, date_str: str, format_str: str = app_config.DATETIME_FORMAT) -> datetime:
        """时间字符串转时区时间"""
        return datetime.strptime(date_str, format_str).replace(tzinfo=self.tz_info)


timezone = TimeZone()

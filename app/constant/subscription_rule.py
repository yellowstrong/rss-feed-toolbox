import re
from enum import Enum


class SubscriptionRule(Enum):
    RESOLUTION_4K = "4k"
    RESOLUTION_1080P = "1080p"
    RESOLUTION_720P = "720p"
    QUALITY_DV = "DV"
    QUALITY_HDR = "HDR"
    QUALITY_EDR = "EDR"
    HIGH_QUALITY = "HQ"
    FPS_60 = "60fps"

    @staticmethod
    def match_rule(text: str, includes: list, excludes: list) -> bool:
        rules = {
            SubscriptionRule.RESOLUTION_4K: r'4k|2160p|x2160',
            SubscriptionRule.RESOLUTION_1080P: r'1080[pi]|x1080',
            SubscriptionRule.RESOLUTION_720P: r'720[pi]|x720',
            SubscriptionRule.QUALITY_DV: r'Dolby[\s.]+Vision|DOVI|[\s.]+DV[\s.]+|杜比视界',
            SubscriptionRule.QUALITY_HDR: r'[\s.]+HDR[\s.]+|HDR10|HDR10\+',
            SubscriptionRule.QUALITY_EDR: r'[\s.]+EDR[\s.]+',
            SubscriptionRule.HIGH_QUALITY: r'[\s.]+HQ[\s.]+',
            SubscriptionRule.FPS_60: r'[\s.]+60fps[\s.]+',
        }

        def get_enum_member(value: str):
            for member in SubscriptionRule:
                if member.value == value:
                    return member
            return None

        for include in includes:
            rule = get_enum_member(include)
            if not re.search(rules[rule], text, re.I):
                return False

        for exclude in excludes:
            rule = get_enum_member(exclude)
            if re.search(rules[rule], text, re.I):
                return False

        return True

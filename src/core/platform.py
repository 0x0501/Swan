from enum import Enum, unique


@unique
class Platform(Enum):
    DAZHONGDIANPING = 0      # 大众点评
    XIECHENG        = 1       # 美团
    RED             = 2       # 小红书
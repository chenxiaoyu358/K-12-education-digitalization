"""Constants: enums, search keywords, and category definitions."""

import enum


class Category(str, enum.Enum):
    """采购项目分类 — 11 ICT 大类 + 真·非 ICT + 其他"""
    NETWORK_INFRA = "network_infra"                  #  1. 网络基础设施
    COMPUTER_TERMINAL = "computer_terminal"          #  2. 计算机与终端设备
    MULTIMEDIA_DISPLAY = "multimedia_display"        #  3. 多媒体显示设备
    DIGITAL_LAB = "digital_lab"                      #  4. 数字化实验室
    MAKER_STEM = "maker_stem"                        #  5. 创客与STEM装备
    TEACHING_SYSTEM = "teaching_system"              #  6. 教学应用系统
    TRAINING_CONSULTING = "training_consulting"      #  7. 培训与咨询（ICT专项）
    OPS_MAINTENANCE = "ops_maintenance"              #  8. 运维与维护（ICT设备/系统）
    SMART_CAMPUS = "smart_campus"                    #  9. 智慧校园管理
    CAMPUS_ENVIRONMENT = "campus_environment"        # 10. 校园环境与安防
    DIGITAL_RESOURCES = "digital_resources"          # 11. 数字资源（电子数据库/电子期刊/数字图书馆）
    NON_ICT = "non_ict"                              # 真·非教育信息化（食堂/物业/印刷/研学等）
    OTHER = "other"                                  # 其他教育信息化（ICT 相关但类别不明）


class UnitType(str, enum.Enum):
    """采购主体类型 — who is buying"""
    EDUCATION_AUTHORITY = "education_authority"   # 教育管理部门（教育局、教育装备中心、电化教育馆等）
    UNIVERSITY = "university"                     # 高校（大学、学院）
    VOCATIONAL = "vocational"                     # 职校（职业学院/学校、技师学院、技工学校）
    MIDDLE_SCHOOL = "middle_school"               # 中学（初级/高级/完全中学、九年一贯制）
    ELEMENTARY_SCHOOL = "elementary_school"       # 小学（含中心校）
    KINDERGARTEN = "kindergarten"                 # 幼儿园
    OTHER = "other"                               # 其他


class ProcurementStage(str, enum.Enum):
    """采购阶段"""
    ANNOUNCEMENT = "announcement"    # 招标/采购公告
    RESULT = "result"                # 中标/成交公告
    CONTRACT = "contract"            # 合同公告
    CORRECTION = "correction"        # 更正公告


class ProcurementMethod(str, enum.Enum):
    """采购方式"""
    OPEN_BID = "open_bid"                          # 公开招标
    COMPETITIVE_NEGOTIATION = "competitive_negotiation"  # 竞争性谈判
    COMPETITIVE_CONSULTATION = "competitive_consultation"  # 竞争性磋商
    SINGLE_SOURCE = "single_source"                # 单一来源
    INQUIRY = "inquiry"                            # 询价
    OTHER = "other"


class SourceSite(str, enum.Enum):
    """数据来源站点"""
    CCGP = "ccgp"              # 中国政府采购网
    GGZY = "ggzy"              # 全国公共资源交易平台
    CEBPUB = "cebpub"          # 中国招标投标公共服务平台
    CAIGOU = "caigou"          # 中国教育装备采购网
    EDUPROCURE = "eduprocure"  # 中国教育公共资源交易信息网
    PROVINCIAL = "provincial"  # 省级采购网


# 教育采购搜索关键词（用于网站搜索接口）
SEARCH_KEYWORDS = [
    # 网络基础设施
    "校园网络", "网络布线", "无线覆盖",
    # 计算机终端
    "计算机教室", "云桌面", "学生电脑",
    # 多媒体显示
    "教学一体机", "电子白板", "智能黑板", "触控一体机",
    "多媒体教室", "录播系统", "班班通",
    # 数字化实验室
    "数字化实验室", "理化生实验", "数字传感器",
    # 创客STEM
    "创客空间", "3D打印", "机器人教育", "人工智能教育",
    "VR教学", "STEM教育", "编程教育",
    # 教学系统
    "在线教学平台", "教务系统", "考试系统", "阅卷系统",
    "教学资源平台", "教育云平台", "网络教学", "远程教育",
    "语音教室", "听力系统",
    # 智慧校园
    "智慧校园", "数字校园", "智慧教育", "教育信息化",
    "校园一卡通", "校园物联网", "教育大数据",
    # 校园环境安防
    "校园安防", "教室照明", "护眼灯", "校园监控",
    "体质测试", "智慧体育", "心理测评",
    "校园广播",
    # 综合
    "教育装备", "教育数字化",
]

# 采购方式关键词映射
METHOD_KEYWORDS = {
    ProcurementMethod.OPEN_BID: ["公开招标"],
    ProcurementMethod.COMPETITIVE_NEGOTIATION: ["竞争性谈判"],
    ProcurementMethod.COMPETITIVE_CONSULTATION: ["竞争性磋商"],
    ProcurementMethod.SINGLE_SOURCE: ["单一来源"],
    ProcurementMethod.INQUIRY: ["询价"],
}

# 阶段关键词映射
STAGE_KEYWORDS = {
    ProcurementStage.ANNOUNCEMENT: ["招标公告", "采购公告", "采购需求公告", "磋商公告", "谈判公告", "询价公告"],
    ProcurementStage.RESULT: ["中标公告", "成交公告", "中标结果", "成交结果", "结果公告"],
    ProcurementStage.CONTRACT: ["合同公告", "合同公示"],
    ProcurementStage.CORRECTION: ["更正公告", "变更公告", "补充公告"],
}

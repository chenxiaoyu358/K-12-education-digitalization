"""Pattern-based non-ICT detection rules.

Used as a high-specificity pre-filter before the keyword-dictionary scoring in
`classify()`. When a title matches one of these patterns, classification short-
circuits to `Category.NON_ICT` without consulting any keyword dict.

Why patterns instead of more keywords:
- The 720-sample study (2026-04-21) showed 314 A-class records still leaked to
  `other` after Round 1 because the non-ICT signal lives in *combinations*
  (e.g. "竞价采购" + "N件" = small daily-goods purchase) not single tokens
  ("手电筒"/"折纸"/"乌龟垫" are too specific to dictionary-ize).
- Specificity is high enough that even when ICT-looking words appear in the
  title, the project is still non-ICT (e.g. a "改造工程" project that mentions
  "网络" is still construction work).

ICT short-circuit safety: rules are checked AGAINST the title only, and only
fire when the pattern is unambiguous. Edge cases that look like ICT are
deliberately excluded by the regex — see test_non_ict_rules.py reverse cases.
"""

from __future__ import annotations

import re

# 1. 小商品竞价采购：诸暨/浣江/特殊教育系列。
#    标题特征：「关于 ... N件 ... 的竞价采购」，N 通常 1~9999 但小额
#    反例守护：必须有 "件" 量词；如果标的物本身是 ICT 设备词（电脑/平板/一体机/
#    投影/服务器/摄像/监控/路由/交换/网络/系统/软件/平台），仍由 ICT 词典处理。
_RULE_1_BIDDING_SMALL_GOODS = re.compile(
    r"竞价采购"
)
_RULE_1_QUANTIFIER = re.compile(r"\d+\s*件")
_RULE_1_ICT_GUARD = re.compile(
    r"电脑|笔记本|平板|一体机|投影|录播|服务器|摄像|监控|"
    r"路由|交换机|网络|系统|软件|平台|终端|U盘|存储|打印机|"
    r"显示器|交互屏|触控屏|白板"
)

# 2. 物业/后勤框架协议：综合物业、保安、保洁、绿化养护...
_RULE_2_FACILITIES_FRAMEWORK = re.compile(
    r"(物业|保洁|清卫|保安|安保|绿化养护|物业管理)"
    r".*"
    r"框架协议"
)

# 3. 基建/装修/修缮工程：必须含"工程/施工/改造/修缮"等强基建词，且不带 ICT 设备词
_RULE_3_CONSTRUCTION = re.compile(
    r"(装修|装饰|修缮|维护修缮|塑胶面层|改扩建|改造提升|"
    r"勘察设计|安全鉴定|楼顶|钢结构|配电|电力增容|"
    r"小额工程|室内工程|改造工程|新建工程)"
)
_RULE_3_SCHOOL_GUARD = re.compile(r"学校|学院|校区|校园|幼儿园|中学|小学|大学")
_RULE_3_ICT_GUARD = re.compile(
    r"信息化|网络|机房|多媒体|一体机|监控系统|安防|智慧|数字|"
    r"录播|计算机|终端|平台|系统集成|弱电|布线"
)

# 4. 消防/机电/暖通/水电基础设施
_RULE_4_INFRASTRUCTURE = re.compile(
    r"(消防系统|消防设施|消防箱|机电设备成套|"
    r"暖通|新风设备|新风系统|给排水|水电改造|"
    r"变电房|配电房|电力改造)"
)

# 5. 培训/赛事/研学（非 ICT 培训）
_RULE_5_NON_ICT_EDU_SERVICE = re.compile(
    r"(综合性培训场所|专业培训场所|干部培养|干部研修|"
    r"创新创业大赛|教学能力大赛|教学能力提升|"
    r"教师教学研究|教学研究服务|"
    r"研学项目|研学实践|海外研学)"
)

# 6. 食堂/餐饮复合：必须含具体后勤动词
_RULE_6_CANTEEN_OPS = re.compile(
    r"(食堂|餐饮|餐厅|中餐配送|厨房)"
    r".*"
    r"(外包|供应|服务|经营|配送|合作)"
)

# 7. 杂项：日常消耗品 / 福利 / 演出服 / 教辅纸质类 复合标识
#    这些不是规则1的"竞价采购+N件"模式，而是更广泛的小额日常物资
_RULE_7_DAILY_GOODS = re.compile(
    r"(端午节福利|节日福利|学生礼物|学生礼品|"
    r"汉服|表演服|舞台服装|"
    r"讲义|试卷|空白簿册|课业本|教学用本|地方课程教材|纸质教材|教师用书|"
    r"国际邮寄|车辆维修|车辆保险|贴息贷款|商铺招租|房屋租金|"
    r"售货机|咖啡机.*招租|"
    r"舞台设备|报告厅舞台|"
    # NOTE: 体质测试 is in campus_environment.txt (智慧体育/体测一体机), must NOT match here
    r"足球场草坪|公共体育服务|"
    r"图书馆.*搬迁|图书.*档案|"
    r"标识标牌|标识导视|"
    r"校舍安全鉴定|"
    r"校园文化项目|教育中心文化建设|文化建设项目)"
)


def matches_non_ict_pattern(title: str) -> bool:
    """Return True if title matches any high-specificity non-ICT pattern.

    Caller should short-circuit to Category.NON_ICT when this returns True.
    """
    if not title:
        return False

    # Rule 1: 竞价采购 + 数量"X件" 且无 ICT 设备词
    if _RULE_1_BIDDING_SMALL_GOODS.search(title) and _RULE_1_QUANTIFIER.search(title):
        if not _RULE_1_ICT_GUARD.search(title):
            return True

    # Rule 2: 物业/保安等 + 框架协议
    if _RULE_2_FACILITIES_FRAMEWORK.search(title):
        return True

    # Rule 3: 装修/修缮/改造工程 + 学校 (但无 ICT 防护词)
    if _RULE_3_CONSTRUCTION.search(title) and _RULE_3_SCHOOL_GUARD.search(title):
        if not _RULE_3_ICT_GUARD.search(title):
            return True

    # Rule 4: 消防/机电/水电 基建
    if _RULE_4_INFRASTRUCTURE.search(title):
        return True

    # Rule 5: 非 ICT 教育培训/赛事/研学
    if _RULE_5_NON_ICT_EDU_SERVICE.search(title):
        return True

    # Rule 6: 食堂复合操作
    if _RULE_6_CANTEEN_OPS.search(title):
        return True

    # Rule 7: 杂项日常物资
    if _RULE_7_DAILY_GOODS.search(title):
        return True

    return False

"""Tests for pattern-based non-ICT rules (Round 2 of `other` category cleanup).

Each rule is exercised with at least one positive (should match non-ICT) and
one reverse case (ICT-looking title that must NOT be mis-classified).
"""


from ztb.classification.category import classify
from ztb.classification.non_ict_rules import matches_non_ict_pattern
from ztb.constants import Category


class TestRule1BiddingSmallGoods:
    """Rule 1: 竞价采购 + N件 → non_ict (unless ICT device keywords present)."""

    def test_flashlights(self):
        assert matches_non_ict_pattern(
            "诸暨市暨阳街道浣江小学教育集团关于手电筒4件等的竞价采购竞价成交公告"
        )

    def test_diary_books(self):
        assert matches_non_ict_pattern("诸暨市浣江小学关于日记本200件的竞价采购竞价公告")

    def test_origami_paper(self):
        # Real Round 1 sample: small-quantity daily goods
        assert matches_non_ict_pattern(
            "诸暨市暨阳街道浣纱幼儿园关于折纸/手工纸1件等的竞价采购竞价终止公告"
        )

    def test_flashlight_4pc(self):
        # Real Round 1 sample with N件 and no ICT words
        assert matches_non_ict_pattern(
            "诸暨市暨阳街道浣江小学教育集团关于手电筒4件等的竞价采购竞价成交公告"
        )

    def test_reverse_usb_drive_stays_ict(self):
        # "U盘" in computer_terminal.txt — should go to ICT despite "竞价采购"
        # Rule 1 bails out because ICT guard matches.
        assert classify("诸暨市特殊教育学校关于U盘的竞价采购") == Category.COMPUTER_TERMINAL

    def test_reverse_aio_device_stays_ict(self):
        # 一体机 triggers ICT guard, so rule 1 does not fire
        assert classify("某校关于教学一体机10件的竞价采购") == Category.MULTIMEDIA_DISPLAY


class TestRule2FacilitiesFramework:
    """Rule 2: 物业/保洁/保安/绿化养护 + 框架协议 → non_ict."""

    def test_integrated_property(self):
        assert matches_non_ict_pattern("湖州市第五中学教育集团关于综合物业的框架协议采购项目成交公告")

    def test_green_maintenance(self):
        assert matches_non_ict_pattern("缙云县新区实验幼儿园关于绿化养护的框架协议采购项目成交公告")

    def test_cleaning_service(self):
        assert matches_non_ict_pattern("杭州市西湖小学关于清卫保洁的框架协议采购项目成交公告")


class TestRule3ConstructionRenovation:
    """Rule 3: 装修/修缮/改造/扩建 工程 + 学校, 且无 ICT 防护词 → non_ict."""

    def test_kindergarten_decoration(self):
        assert matches_non_ict_pattern(
            "浙江中永工程咨询有限公司关于椒江区未来悦幼儿园装饰及配套工程的中标候选人公示单"
        )

    def test_playground_repair(self):
        assert matches_non_ict_pattern("永嘉县教育局下属13所学校操场塑胶面层破损修缮项目的合同公告")

    def test_roof_repair(self):
        assert matches_non_ict_pattern(
            "温州正风招标代理关于浙江省温州中学行政楼楼顶钢结构安全修缮项目的公开招标公告"
        )

    def test_classroom_renovation(self):
        assert matches_non_ict_pattern(
            "杭州市源清中学教育综合楼室内工程（学科教室提升与改造）项目的公开招标公告"
        )

    def test_reverse_smart_campus_renovation_stays_ict(self):
        # 智慧 / 数字 trigger ICT guard — stays with smart_campus dict scoring
        assert (
            classify("某中学智慧校园改造工程项目").value == Category.SMART_CAMPUS.value
        )


class TestRule4InfrastructureMEP:
    """Rule 4: 消防/机电/暖通/水电 → non_ict."""

    def test_fire_box(self):
        assert matches_non_ict_pattern(
            "诸暨市暨阳街道行知幼儿园教育集团西子幼儿园关于消防箱1件等的竞价采购邀请公告"
        )

    def test_fire_system_booster(self):
        assert matches_non_ict_pattern("龙游县北辰中心幼儿园消防系统增压稳压设备采购结果公告")

    def test_fresh_air_system(self):
        assert matches_non_ict_pattern(
            "浙江博策工程项目管理有限公司关于诸暨市智胜、尚学幼儿园新风设备采购项目的公开招标公告"
        )

    def test_power_renovation(self):
        assert matches_non_ict_pattern(
            "浙江星兴关于湖州市第四中学教育集团（白鱼潭校区）变电房单电源改双电源及电力增容改造项目的竞争性磋商公告"
        )


class TestRule5NonIctEduService:
    """Rule 5: 综合性培训场所/干部培养/教学能力大赛/研学 → non_ict."""

    def test_comprehensive_training_venue(self):
        assert matches_non_ict_pattern(
            "杭州市余杭区教育发展研究学院关于综合性培训场所的框架协议采购项目成交公告"
        )

    def test_cadre_training(self):
        assert matches_non_ict_pattern(
            "浙江省教育技术中心关于浙江省高校中青年干部培养项目中标(成交)结果公告"
        )

    def test_teaching_competition(self):
        assert matches_non_ict_pattern("2025年浙江省教师教学能力大赛综合服务采购项目采购公告")

    def test_overseas_research_trip(self):
        assert matches_non_ict_pattern("浙江传媒学院华策电影学院海外研学项目合同公告")

    def test_entrepreneurship_contest(self):
        assert matches_non_ict_pattern(
            "淳安县人力资源和社会保障局智汇千岛 才创未来 2024首届中国·淳安农创客创新创业大赛成交结果公告"
        )


class TestRule6CanteenOperations:
    """Rule 6: 食堂/餐厅 + 外包/供应/服务/经营 → non_ict."""

    def test_canteen_outsourcing(self):
        assert matches_non_ict_pattern(
            "浙江建友工程咨询有限公司关于江山市廿八都小学食堂劳务外包服务采购项目的其他非政府采购结果公告"
        )

    def test_school_canteen_supply(self):
        assert matches_non_ict_pattern(
            "浙江浙大城市学院教育发展有限公司北秀楼二楼食堂调味品（含干货、酱菜）、面粉供应及服务项目的延期公告"
        )

    def test_campus_meal_delivery(self):
        assert matches_non_ict_pattern("关于鹿城区校园中餐配送定点供应商项目的比选公告")

    def test_restaurant_operation(self):
        assert matches_non_ict_pattern("湖州职院新校园餐厅合作经营服务项目公开招标公告")


class TestRule7DailyGoods:
    """Rule 7: Miscellaneous daily goods / non-ICT signatures."""

    def test_paper_textbook(self):
        assert matches_non_ict_pattern(
            "金华市公共资源交易中心东阳分中心关于东阳市教育局2023-2024中小学讲义与试卷采购项目的更正公告"
        )

    def test_grass_lawn(self):
        assert matches_non_ict_pattern("兴隆县教育和体育局足球场草坪采购项目询价中标公告")

    def test_international_mail(self):
        assert matches_non_ict_pattern(
            "浙江求是招标代理有限公司关于浙江科技学院国际教育学院购国际邮寄服务中标结果公告"
        )

    def test_holiday_welfare(self):
        assert matches_non_ict_pattern(
            "浙江豪圣建设项目管理有限公司关于中国教育工会中国美术学院委员会2024年端午节福利采购项目废标公告"
        )

    def test_school_safety_assessment(self):
        assert matches_non_ict_pattern(
            "浙江西建工程管理有限公司关于拱墅区教育系统2024年学校校舍安全鉴定的中标结果公告"
        )

    def test_signage(self):
        assert matches_non_ict_pattern(
            "浙江华诚工程管理有限公司关于绍兴市职业教育中心标识标牌引导指示项目的中标(成交)结果公告"
        )


class TestReverseICTCases:
    """Guard against over-eager rules blocking legitimate ICT projects."""

    def test_network_infra_project(self):
        # Should still classify as NETWORK_INFRA despite "工程"
        assert classify("某某小学校园网络升级改造工程") == Category.NETWORK_INFRA

    def test_multimedia_in_new_classroom(self):
        # "新型教学空间" is in multimedia_display.txt, not rule 5's pattern
        assert classify("某市中小学新型教学空间一体机采购") == Category.MULTIMEDIA_DISPLAY

    def test_smart_campus_keeps(self):
        # "智慧校园" / "数字化" / "教育信息化" must always win
        assert classify("某区教育信息化建设项目") == Category.SMART_CAMPUS

    def test_empty_title(self):
        # Defensive: empty or whitespace titles should not explode
        assert not matches_non_ict_pattern("")
        assert not matches_non_ict_pattern("   ")

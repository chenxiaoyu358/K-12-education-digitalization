"""Tests for category classifier — 8 categories."""


from ztb.classification.category import classify
from ztb.constants import Category


class TestClassify:
    # --- 1. 网络基础设施 ---
    def test_network_infra(self):
        assert classify("某某小学校园网络升级改造项目") == Category.NETWORK_INFRA

    def test_network_wifi(self):
        assert classify("某某中学无线网络覆盖项目") == Category.NETWORK_INFRA

    def test_network_cabling(self):
        assert classify("某某学校综合布线工程采购") == Category.NETWORK_INFRA

    # --- 2. 计算机与终端设备 ---
    def test_computer_classroom(self):
        assert classify("某某小学计算机教室设备采购") == Category.COMPUTER_TERMINAL

    def test_cloud_desktop(self):
        assert classify("某某中学云桌面建设项目") == Category.COMPUTER_TERMINAL

    def test_student_computer(self):
        assert classify("某某区学生电脑采购项目") == Category.COMPUTER_TERMINAL

    # --- 3. 多媒体显示设备 ---
    def test_aio_device(self):
        assert classify("某某区教育局教学一体机采购项目") == Category.MULTIMEDIA_DISPLAY

    def test_electronic_whiteboard(self):
        assert classify("某某小学电子白板及多媒体教学设备采购") == Category.MULTIMEDIA_DISPLAY

    def test_recording_system(self):
        assert classify("某某中学录播教室建设项目") == Category.MULTIMEDIA_DISPLAY

    def test_projector(self):
        assert classify("某某学校投影仪采购项目") == Category.MULTIMEDIA_DISPLAY

    # --- 4. 数字化实验室 ---
    def test_digital_lab(self):
        assert classify("某某中学数字化实验室建设项目") == Category.DIGITAL_LAB

    def test_science_lab(self):
        assert classify("某某学校理化生数字化探究实验室采购") == Category.DIGITAL_LAB

    def test_sensor_lab(self):
        assert classify("某某中学数字传感器实验设备采购") == Category.DIGITAL_LAB

    # --- 5. 创客与STEM装备 ---
    def test_maker_space(self):
        assert classify("某某小学创客空间建设项目") == Category.MAKER_STEM

    def test_3d_printer(self):
        assert classify("某某中学3D打印设备采购") == Category.MAKER_STEM

    def test_robot_education(self):
        assert classify("某某学校机器人教育装备采购") == Category.MAKER_STEM

    def test_vr_teaching(self):
        assert classify("某某中学VR教室建设项目") == Category.MAKER_STEM

    def test_ai_education(self):
        assert classify("某某学校人工智能教育实验室建设") == Category.MAKER_STEM

    # --- 6. 教学应用系统 ---
    def test_teaching_platform(self):
        assert classify("某某区在线教学平台建设项目") == Category.TEACHING_SYSTEM

    def test_exam_system(self):
        assert classify("某某市教育局网上阅卷系统采购") == Category.TEACHING_SYSTEM

    def test_voice_classroom(self):
        assert classify("某某中学语音教室设备采购") == Category.TEACHING_SYSTEM

    def test_listening_system(self):
        assert classify("某某学校英语听力系统采购") == Category.TEACHING_SYSTEM

    # --- 7. 智慧校园管理 ---
    def test_smart_campus(self):
        assert classify("某某中学智慧校园建设项目") == Category.SMART_CAMPUS

    def test_campus_card(self):
        assert classify("某某学校校园一卡通系统采购") == Category.SMART_CAMPUS

    def test_education_informatization(self):
        assert classify("某某区教育信息化建设项目") == Category.SMART_CAMPUS

    # --- 8. 校园环境与安防 ---
    def test_campus_security(self):
        assert classify("某某小学校园安防监控系统采购") == Category.CAMPUS_ENVIRONMENT

    def test_classroom_lighting(self):
        assert classify("某某学校教室照明改造项目") == Category.CAMPUS_ENVIRONMENT

    def test_eye_protection(self):
        assert classify("某某区中小学护眼灯采购") == Category.CAMPUS_ENVIRONMENT

    def test_fitness_test(self):
        assert classify("某某学校体质测试设备采购") == Category.CAMPUS_ENVIRONMENT

    def test_smart_sports(self):
        assert classify("某某中学智慧操场建设项目") == Category.CAMPUS_ENVIRONMENT

    def test_mental_health(self):
        assert classify("某某学校心理测评系统采购") == Category.CAMPUS_ENVIRONMENT

    # --- NON_ICT fallback (previously went to OTHER) ---
    # After 720-sample study (2026-04-21): 82% of OTHER was truly non-ICT noise.
    # Classifier now routes to NON_ICT when non_ict.txt matches and no ICT dict does.
    def test_non_ict_canteen(self):
        assert classify("某某学校食堂装修改造工程") == Category.NON_ICT

    def test_non_ict_security_service(self):
        assert classify("安吉县教育局校园保安服务政府采购项目公告") == Category.NON_ICT

    def test_non_ict_vehicle_rental(self):
        assert classify("杭州市钱塘区教师教育学院关于车辆租赁的框架协议采购项目成交公告") == Category.NON_ICT

    def test_non_ict_printing(self):
        assert classify("绍兴市上虞区崧华学校关于其他印刷品的框架协议采购项目成交公告") == Category.NON_ICT

    def test_non_ict_research_trip(self):
        assert classify("萧山区北干小学2024年组织学生开展研学实践教育项目") == Category.NON_ICT

    # --- OTHER: no ICT keywords AND no non_ict keywords ---
    def test_other_fallback_truly_unknown(self):
        # Short, generic title with nothing the dicts recognize
        assert classify("某某学校日常采购项目") == Category.OTHER

    # --- ICT priority: ICT dict hits win over non_ict hits ---
    # Even though "食堂" is in non_ict.txt, "一体机"/"电子白板" in multimedia_display.txt
    # should win because ICT is checked first.
    def test_ict_wins_over_non_ict(self):
        assert classify("某某学校食堂一体机及电子白板采购") == Category.MULTIMEDIA_DISPLAY

    # B-class (漏网) regression: merged from keyword_patches_2026-04-21.md
    # on Round 2 (2026-04-21 same-day). Locks in that U盘/交互式多媒体classify correctly.
    def test_bclass_interactive_multimedia(self):
        assert classify("平阳县2023年交互式多媒体的公开招标公告") == Category.MULTIMEDIA_DISPLAY

    def test_bclass_usb_drive(self):
        assert classify("诸暨市特殊教育学校关于U盘的竞价采购") == Category.COMPUTER_TERMINAL

    # --- Content-based ---
    def test_content_helps_classify(self):
        # Title alone carries no ICT keyword and classifies as OTHER; the content
        # (教学一体机/电子白板) tips it into MULTIMEDIA_DISPLAY. (Avoids a generic title
        # term like 信息化, which the current lexicon routes to smart_campus.)
        assert classify("某某学校设备采购") == Category.OTHER
        result = classify(
            "某某学校设备采购",
            content="本项目采购内容包括教学一体机50台、电子白板配件等"
        )
        assert result == Category.MULTIMEDIA_DISPLAY

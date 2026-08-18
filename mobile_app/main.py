#!/usr/bin/env python3
"""and-hub Mobile App (Kivy Android Touch GUI).

안드로이드 스마트폰 화면에서 터치로 중복 파일을 스캔하고
확인 후 삭제(휴지통 이동) 및 원위치 복구를 수행하는 Kivy 모바일 앱입니다.
"""

import os
import sys

# 상위 폴더의 중복 정리 엔진 모듈 임포트
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import dedup_downloads as dedup

try:
    from kivy.app import App
    from kivy.clock import Clock
    from kivy.core.window import Window
    from kivy.uix.boxlayout import BoxLayout
    from kivy.uix.button import Button
    from kivy.uix.label import Label
    from kivy.uix.progressbar import ProgressBar
    from kivy.uix.scrollview import ScrollView
    from kivy.uix.textinput import TextInput
except ImportError:
    # PC 테스트 환경 등에서 Kivy가 없을 때의 가이드 안내
    pass


class DedupMobileWidget(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", padding=15, spacing=10, **kwargs)

        # 1. 헤더 타이틀
        self.add_widget(Label(
            text="[b]and-hub 중복 파일 정리기[/b]",
            markup=True,
            font_size="22sp",
            size_hint_y=None,
            height=50,
            color=(0.2, 0.6, 1.0, 1)
        ))

        # 2. 검사 대상 폴더 입력란
        path_box = BoxLayout(orientation="horizontal", size_hint_y=None, height=45, spacing=5)
        path_box.add_widget(Label(text="대상 폴더:", size_hint_x=0.3, font_size="14sp"))
        self.path_input = TextInput(
            text="/storage/emulated/0/Download",
            multiline=False,
            size_hint_x=0.7,
            font_size="13sp"
        )
        path_box.add_widget(self.path_input)
        self.add_widget(path_box)

        # 3. 결과 로그 스크롤 뷰
        self.log_label = Label(
            text="[안내] 아래 버튼을 눌러 스마트폰 중복 정리를 시작하세요.\n- 스캔: 무엇이 중복인지 검사\n- 확인 후 정리: 대화형 안전 이동\n- 원위치 복구: 실수로 정리한 파일 롤백",
            font_size="13sp",
            halign="left",
            valign="top",
            size_hint_y=None,
            color=(0.9, 0.9, 0.9, 1)
        )
        self.log_label.bind(texture_size=self.log_label.setter('size'))
        scroll = ScrollView(size_hint=(1, 1))
        scroll.add_widget(self.log_label)
        self.add_widget(scroll)

        # 4. 버튼 액션 바
        btn_box1 = BoxLayout(orientation="horizontal", size_hint_y=None, height=50, spacing=8)
        self.btn_scan = Button(text="1. 중복 스캔 (미리보기)", background_color=(0.1, 0.5, 0.8, 1))
        self.btn_scan.bind(on_press=self.run_scan)
        self.btn_clean = Button(text="2. 안전 정리 (_trash 이동)", background_color=(0.1, 0.7, 0.3, 1))
        self.btn_clean.bind(on_press=self.run_clean)
        btn_box1.add_widget(self.btn_scan)
        btn_box1.add_widget(self.btn_clean)
        self.add_widget(btn_box1)

        btn_box2 = BoxLayout(orientation="horizontal", size_hint_y=None, height=45, spacing=8)
        self.btn_restore = Button(text="3. 원위치 복구 (Restore)", background_color=(0.8, 0.5, 0.1, 1))
        self.btn_restore.bind(on_press=self.run_restore)
        self.btn_empty = Button(text="4. 휴지통 비우기", background_color=(0.8, 0.2, 0.2, 1))
        self.btn_empty.bind(on_press=self.run_empty_trash)
        btn_box2.add_widget(self.btn_restore)
        btn_box2.add_widget(self.btn_empty)
        self.add_widget(btn_box2)

    def log(self, msg):
        self.log_label.text += f"\n{msg}"

    def run_scan(self, instance):
        target = self.path_input.text.strip()
        self.log_label.text = f"==> [스캔 시작] 대상: {target}\n"
        if not os.path.exists(target):
            self.log(f"[오류] 폴더를 찾을 수 없습니다: {target}")
            return
        
        args = type("Args", (), {
            "directory": target,
            "recursive": True,
            "delete": False,
            "trash": False,
            "interactive": False,
            "workers": 4
        })()
        
        # 파일 중복 스캔 실행
        try:
            dedup.dedup_files(target, args)
            self.log("[완료] 스캔이 끝났습니다. 정리를 원하시면 2번 버튼을 누르세요.")
        except Exception as e:
            self.log(f"[오류 발생] {e}")

    def run_clean(self, instance):
        target = self.path_input.text.strip()
        self.log_label.text = f"==> [안전 정리 시작] 대상: {target}\n"
        if not os.path.exists(target):
            self.log(f"[오류] 폴더를 찾을 수 없습니다: {target}")
            return

        args = type("Args", (), {
            "directory": target,
            "recursive": True,
            "delete": True,
            "trash": True,
            "interactive": False,
            "workers": 4
        })()

        try:
            dedup.dedup_files(target, args)
            dedup.dedup_by_name(target, args)
            self.log("[완료] 중복 파일들이 _duplicates_trash 폴더로 안전 보관되었습니다.")
        except Exception as e:
            self.log(f"[오류 발생] {e}")

    def run_restore(self, instance):
        target = self.path_input.text.strip()
        self.log_label.text = f"==> [원위치 복구 시작] 대상: {target}\n"
        try:
            dedup.restore_from_trash(target)
            self.log("[완료] 파일들이 원래 자리로 복원되었습니다.")
        except Exception as e:
            self.log(f"[오류 발생] {e}")

    def run_empty_trash(self, instance):
        target = self.path_input.text.strip()
        trash_dir = os.path.join(target, dedup.TRASH_NAME)
        if os.path.exists(trash_dir):
            import shutil
            shutil.rmtree(trash_dir)
            self.log_label.text = f"==> [휴지통 비우기 완료] {trash_dir} 삭제됨."
        else:
            self.log_label.text = f"==> 비울 휴지통이 없습니다: {trash_dir}"


class DedupApp(App):
    def build(self):
        self.title = "and-hub 중복 파일 정리기"
        return DedupMobileWidget()


if __name__ == "__main__":
    DedupApp().run()

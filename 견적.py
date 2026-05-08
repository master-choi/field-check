import flet as ft

def main(page: ft.Page):
    page.title = "현장 견적 마스터"
    page.scroll = "auto"
    page.theme_mode = "light"

    # --- [단가 설정부: 나중에 이 숫자만 바꾸면 됩니다] ---
    prices = {
        "insulation": 100000,    # 단열 1m2당
        "wallpaper": 30000,      # 도배 1m2당
        "window_base": 408163,   # 창문 1m2당 (80만원/1.96m2 기준)
        "boiler": 800000,        # 보일러 기본
        "oil_tank": 200000,      # 기름통 추가
        "home_door": 500000,     # 홈도어 기본
    }

    # --- [입력 필드 설정] ---
    height_input = ft.TextField(label="천장 높이(mm)", keyboard_type="number", value="2200")
    width_input = ft.TextField(label="방 가로(mm)", keyboard_type="number")
    length_input = ft.TextField(label="방 세로(mm)", keyboard_type="number")
    
    # 면적 선택 체크박스
    wall_checks = [ft.Checkbox(label=f"벽체 {i+1}면") for i in range(4)]
    ceiling_check = ft.Checkbox(label="천장")
    
    # 추가 품목
    window_w = ft.TextField(label="창문 가로(mm)", value="1400", width=150)
    window_h = ft.TextField(label="창문 세로(mm)", value="1400", width=150)
    
    door_type = ft.Dropdown(
        label="문 종류",
        options=[
            ft.dropdown.Option("홈도어(110)"),
            ft.dropdown.Option("홈도어(120)"),
            ft.dropdown.Option("출입문(여닫이)"),
            ft.dropdown.Option("출입문(미닫이)"),
        ]
    )

    boiler_check = ft.Checkbox(label="보일러 설치")
    tank_check = ft.Checkbox(label="기름통 포함")

    result_text = ft.Text(size=20, weight="bold", color="blue")

    def calculate(e):
        try:
            h = float(height_input.value) / 1000
            w = float(width_input.value) / 1000
            l = float(length_input.value) / 1000
            
            total_price = 0
            ins_area = 0
            
            # 1, 3번 벽 (가로 기준) / 2, 4번 벽 (세로 기준)
            areas = [w * h, l * h, w * h, l * h]
            for i, check in enumerate(wall_checks):
                if check.value:
                    ins_area += areas[i]
            
            if ceiling_check.value:
                ins_area += (w * l)
                
            # 단열 및 도배 계산
            total_price += ins_area * prices["insulation"]
            total_price += ins_area * prices["wallpaper"] # 선택 면적만큼 도배

            # 창문 계산
            win_area = (float(window_w.value) * float(window_h.value)) / 1000000
            total_price += win_area * prices["window_base"]

            # 보일러 및 기타
            if boiler_check.value: total_price += prices["boiler"]
            if tank_check.value: total_price += prices["oil_tank"]

            result_text.value = f"총 견적 금액: {total_price:,.0f} 원"
            page.update()
        except:
            result_text.value = "숫자를 정확히 입력해주세요."
            page.update()

    # 화면 배치
    page.add(
        ft.Text("📏 현장 치수 입력", size=25, weight="bold"),
        height_input, width_input, length_input,
        ft.Divider(),
        ft.Text("🏠 단열/도배 면적 선택"),
        ft.Row(wall_checks[:2]), ft.Row(wall_checks[2:]), ceiling_check,
        ft.Divider(),
        ft.Text("🚪 창호 및 보일러"),
        ft.Row([window_w, window_h]),
        door_type,
        ft.Row([boiler_check, tank_check]),
        ft.ElevatedButton("견적 계산하기", on_click=calculate, height=50),
        result_text
    )

ft.app(target=main)
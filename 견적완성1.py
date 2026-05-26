import streamlit as st
import json

# ==================== 1. 단가 데이터 (자재, 노무, 경비 분리) ====================
# 실제 견적서 기반 단가 (단위: 원)
UNIT_PRICES = {
    # 단열 (㎡당)
    'insulationWall': {'material': 9394, 'labor': 32965, 'expense': 192},
    'insulationCeiling': {'material': 9394, 'labor': 41518, 'expense': 227},
    # 도배 (㎡당)
    'wallpaperWall': {'material': 3378, 'labor': 6662, 'expense': 0},
    'wallpaperCeiling': {'material': 3443, 'labor': 8662, 'expense': 0},
    # 걸레받이 (m당)
    'baseboard': {'material': 1240, 'labor': 3060, 'expense': 183},
    # 창호 (1개당, 크기별 매핑은 별도 테이블, 여기선 기본값)
    'window_base': {'material': 350000, 'labor': 70000, 'expense': 1400},  # 예시
    # 창호 부대공정 (m당)
    'urethane_fill': {'material': 1650, 'labor': 2602, 'expense': 0},
    'sealing_fill': {'material': 576, 'labor': 5015, 'expense': 0},
    'finish_interior': {'material': 1048, 'labor': 8234, 'expense': 340},
    'finish_exterior': {'material': 1048, 'labor': 8234, 'expense': 340},
    'window_removal': {'material': 0, 'labor': 3377, 'expense': 0},  # 개당
    # 공통경비
    'transport_per_m2': {'material': 0, 'labor': 4036, 'expense': 0},
    'waste_per_m2': {'material': 0, 'labor': 3229, 'expense': 0},
    'furniture_move': {'material': 0, 'labor': 0, 'expense': 31309},
    'estimate_expense': {'material': 0, 'labor': 0, 'expense': 34433},
    'survey_expense': {'material': 0, 'labor': 0, 'expense': 22955},
    'consulting_expense': {'material': 0, 'labor': 0, 'expense': 57388},
    'diagnosis_fee': {'material': 0, 'labor': 0, 'expense': 114776},
    # 보일러 등
    'boiler': {'material': 1100000, 'labor': 0, 'expense': 0},
    'oilTank': {'material': 200000, 'labor': 0, 'expense': 0},
    'ac_reattach': {'material': 0, 'labor': 10000, 'expense': 0},
}

# 창호 크기별 단가 테이블 (예시, 실제 데이터로 확장 가능)
WINDOW_PRICES = {
    (1150, 1000): {'material': 390521, 'labor': 70420, 'expense': 1408},
    (1220, 1000): {'material': 390227, 'labor': 70420, 'expense': 1408},
    (1090, 890): {'material': 355840, 'labor': 56932, 'expense': 1138},
    (1080, 880): {'material': 355924, 'labor': 56932, 'expense': 1138},
    (1530, 400): {'material': 314068, 'labor': 56932, 'expense': 1138},
    (1660, 1360): {'material': 594991, 'labor': 70420, 'expense': 1408},
}

ADMIN_PASSWORD = '0131'
PRICE_FILE = "unit_prices.json"

def load_prices():
    try:
        with open(PRICE_FILE, 'r') as f:
            loaded = json.load(f)
            # 기본값과 병합
            for k, v in UNIT_PRICES.items():
                if k not in loaded:
                    loaded[k] = v
            return loaded
    except:
        return UNIT_PRICES.copy()

def save_prices(prices):
    with open(PRICE_FILE, 'w') as f:
        json.dump(prices, f, indent=2)

if 'prices' not in st.session_state:
    st.session_state.prices = load_prices()
p = st.session_state.prices

st.set_page_config(page_title="온성 견적 마스터 (정밀형)", page_icon="🏗️", layout="centered")
st.markdown("<h1 style='text-align: center;'>🏗️ 온성 견적 산출기 (실제 단가 기반)</h1>", unsafe_allow_html=True)

# ==================== 2. 관리자 패널 ====================
with st.expander("🔒 단가 설정 (관리자)"):
    pw = st.text_input("관리자 비밀번호", type="password")
    if pw == ADMIN_PASSWORD:
        st.success("관리자 모드 활성화")
        # 간단히 주요 항목만 노출 (필요시 전체 확장 가능)
        with st.form("price_form"):
            st.subheader("단열/도배 (㎡)")
            col1, col2 = st.columns(2)
            with col1:
                p['insulationWall']['material'] = st.number_input("벽체 단열 자재", value=p['insulationWall']['material'])
                p['insulationWall']['labor'] = st.number_input("벽체 단열 노무", value=p['insulationWall']['labor'])
                p['insulationWall']['expense'] = st.number_input("벽체 단열 경비", value=p['insulationWall']['expense'])
            with col2:
                p['wallpaperWall']['material'] = st.number_input("도배(벽) 자재", value=p['wallpaperWall']['material'])
                p['wallpaperWall']['labor'] = st.number_input("도배(벽) 노무", value=p['wallpaperWall']['labor'])
            # ... 다른 항목들도 유사하게 추가 가능
            if st.form_submit_button("💾 저장"):
                save_prices(p)
                st.success("저장 완료")
    else:
        st.info("비밀번호를 입력하세요")

st.divider()

# ==================== 3. 메인 입력 UI ====================
col_opt1, col_opt2 = st.columns(2)
with col_opt1:
    is_island = st.checkbox("🏝️ 섬 지역 현장 (노무비 50% 할증 적용)", value=False)
with col_opt2:
    limit = st.number_input("💰 공사 한도 금액 (원)", value=3000000, step=100000)

st.subheader("📐 방 치수 입력 (mm)")
col_w, col_l, col_h = st.columns(3)
with col_w: room_w = st.number_input("가로 길이", value=2900, step=100)
with col_l: room_l = st.number_input("세로 길이", value=2500, step=100)
with col_h: room_h = st.number_input("천장 높이", value=2400, step=100)

# 단위 변환
w_m = room_w / 1000
l_m = room_l / 1000
h_m = room_h / 1000
floor_area = w_m * l_m
wall_east_west = w_m * h_m   # 동/서벽 각각 면적
wall_south_north = l_m * h_m  # 남/북벽 각각
ceiling_area = floor_area

st.subheader("🏗️ 단열 시공면 선택 (도배는 단열하는 부위에만 자동 적용)")
col1, col2, col3, col4, col5 = st.columns(5)
with col1: wall_east = st.checkbox("동쪽 벽")
with col2: wall_west = st.checkbox("서쪽 벽")
with col3: wall_south = st.checkbox("남쪽 벽")
with col4: wall_north = st.checkbox("북쪽 벽")
with col5: do_ceiling = st.checkbox("천장 단열")

# 도배 방식: 단순화 - 단열하는 면만 도배 (사용자 요구)
wallpaper_mode = st.radio("도배 방식", ["단열하는 면만 도배", "도배 안함"], horizontal=True)

st.subheader("🪟 걸레받이")
do_baseboard = st.checkbox("걸레받이 설치 (방 둘레 길이 적용)")

st.subheader("🪟 창문 추가")
win_count = st.number_input("창문 개수", min_value=0, max_value=5, step=1)
windows = []
for i in range(win_count):
    st.write(f"**창문 {i+1}**")
    wc1, wc2 = st.columns(2)
    with wc1: win_w = st.number_input(f"가로 (mm)", value=1150, step=10, key=f"ww{i}")
    with wc2: win_h = st.number_input(f"세로 (mm)", value=1000, step=10, key=f"wh{i}")
    windows.append((win_w, win_h))

st.subheader("🚪 추가 옵션")
opt1, opt2 = st.columns(2)
with opt1:
    boiler = st.checkbox("보일러 설치")
    oil_tank = st.checkbox("기름통 추가", disabled=not boiler)
    furniture_move = st.checkbox("가구운반 (장롱)")
with opt2:
    ac_reattach = st.checkbox("에어컨 간이 탈부착 (+10,000원)", disabled=not is_island)
    # 고정 경비는 항상 포함 (견적서 기준)
    include_fixed_expenses = st.checkbox("견적/조사/컨설팅/진단비 포함", value=True)

st.divider()

# ==================== 4. 계산 엔진 ====================
# 단열할 벽면 목록
ins_walls = []
if wall_east: ins_walls.append(('east', wall_east_west))
if wall_west: ins_walls.append(('west', wall_east_west))
if wall_south: ins_walls.append(('south', wall_south_north))
if wall_north: ins_walls.append(('north', wall_south_north))

# 면적 및 길이 변수 초기화
total_material = 0
total_labor = 0
total_expense = 0
details = []

# 1. 단열 및 도배 (단열하는 면에만 도배)
ins_wall_area = sum(area for _, area in ins_walls)
ins_ceil_area = do_ceiling * ceiling_area

# 단열 비용
if ins_wall_area > 0:
    mat = p['insulationWall']['material'] * ins_wall_area
    lab = p['insulationWall']['labor'] * ins_wall_area
    exp = p['insulationWall']['expense'] * ins_wall_area
    total_material += mat
    total_labor += lab
    total_expense += exp
    details.append(f"벽체 단열: {ins_wall_area:.2f}m² → 자재 {mat:,.0f} + 노무 {lab:,.0f} + 경비 {exp:,.0f}")

if ins_ceil_area > 0:
    mat = p['insulationCeiling']['material'] * ins_ceil_area
    lab = p['insulationCeiling']['labor'] * ins_ceil_area
    exp = p['insulationCeiling']['expense'] * ins_ceil_area
    total_material += mat
    total_labor += lab
    total_expense += exp
    details.append(f"천장 단열: {ins_ceil_area:.2f}m² → 자재 {mat:,.0f} + 노무 {lab:,.0f} + 경비 {exp:,.0f}")

# 도배 (단열하는 면만)
if wallpaper_mode == "단열하는 면만 도배":
    # 벽 도배
    if ins_wall_area > 0:
        mat = p['wallpaperWall']['material'] * ins_wall_area
        lab = p['wallpaperWall']['labor'] * ins_wall_area
        total_material += mat
        total_labor += lab
        details.append(f"벽 도배: {ins_wall_area:.2f}m² → 자재 {mat:,.0f} + 노무 {lab:,.0f}")
    # 천장 도배 (단열한 경우만)
    if ins_ceil_area > 0:
        mat = p['wallpaperCeiling']['material'] * ins_ceil_area
        lab = p['wallpaperCeiling']['labor'] * ins_ceil_area
        total_material += mat
        total_labor += lab
        details.append(f"천장 도배: {ins_ceil_area:.2f}m² → 자재 {mat:,.0f} + 노무 {lab:,.0f}")

# 2. 걸레받이
if do_baseboard:
    perimeter = (w_m + l_m) * 2
    mat = p['baseboard']['material'] * perimeter
    lab = p['baseboard']['labor'] * perimeter
    exp = p['baseboard']['expense'] * perimeter
    total_material += mat
    total_labor += lab
    total_expense += exp
    details.append(f"걸레받이: {perimeter:.2f}m → 자재 {mat:,.0f} + 노무 {lab:,.0f} + 경비 {exp:,.0f}")

# 3. 창호
for i, (win_w, win_h) in enumerate(windows):
    # 크기별 단가 매칭 (없으면 기본값)
    key = (win_w, win_h)
    if key in WINDOW_PRICES:
        w_price = WINDOW_PRICES[key]
    else:
        # 근사: 가장 가까운 크기 찾기 (간단히 기본값)
        w_price = p['window_base']
    mat_win = w_price['material']
    lab_win = w_price['labor']
    exp_win = w_price['expense']
    total_material += mat_win
    total_labor += lab_win
    total_expense += exp_win
    details.append(f"창문 {i+1} ({win_w}x{win_h}mm) 설치: 자재 {mat_win:,.0f} + 노무 {lab_win:,.0f} + 경비 {exp_win:,.0f}")

    # 부대공정 (창틀 둘레)
    perimeter_win = (win_w + win_h) * 2 / 1000  # m 단위
    # 발포우레탄
    mat = p['urethane_fill']['material'] * perimeter_win
    lab = p['urethane_fill']['labor'] * perimeter_win
    total_material += mat
    total_labor += lab
    details.append(f"  - 발포우레탄: {perimeter_win:.2f}m → 자재 {mat:,.0f} + 노무 {lab:,.0f}")
    # 씰링
    mat = p['sealing_fill']['material'] * perimeter_win
    lab = p['sealing_fill']['labor'] * perimeter_win
    total_material += mat
    total_labor += lab
    details.append(f"  - 씰링재: {perimeter_win:.2f}m → 자재 {mat:,.0f} + 노무 {lab:,.0f}")
    # 내부 마감
    mat = p['finish_interior']['material'] * perimeter_win
    lab = p['finish_interior']['labor'] * perimeter_win
    exp = p['finish_interior']['expense'] * perimeter_win
    total_material += mat
    total_labor += lab
    total_expense += exp
    details.append(f"  - 내부마감: {perimeter_win:.2f}m → 자재 {mat:,.0f} + 노무 {lab:,.0f} + 경비 {exp:,.0f}")
    # 외부 마감
    mat = p['finish_exterior']['material'] * perimeter_win
    lab = p['finish_exterior']['labor'] * perimeter_win
    exp = p['finish_exterior']['expense'] * perimeter_win
    total_material += mat
    total_labor += lab
    total_expense += exp
    details.append(f"  - 외부마감: {perimeter_win:.2f}m → 자재 {mat:,.0f} + 노무 {lab:,.0f} + 경비 {exp:,.0f}")
    # 창짝 철거 (4개 가정)
    lab_removal = p['window_removal']['labor'] * 4
    total_labor += lab_removal
    details.append(f"  - 창짝 철거(4개): 노무 {lab_removal:,.0f}")

# 4. 추가 옵션
if boiler:
    total_material += p['boiler']['material']
    details.append(f"보일러 설치: 자재 {p['boiler']['material']:,.0f}")
if oil_tank and boiler:
    total_material += p['oilTank']['material']
    details.append(f"기름통: 자재 {p['oilTank']['material']:,.0f}")
if is_island and ac_reattach:
    total_labor += p['ac_reattach']['labor']
    details.append(f"에어컨 탈부착: 노무 {p['ac_reattach']['labor']:,.0f}")
if furniture_move:
    total_expense += p['furniture_move']['expense']
    details.append(f"가구운반: 경비 {p['furniture_move']['expense']:,.0f}")

# 5. 공통 경비 (소운반, 폐자재는 섬 지역만 / 고정 경비는 내륙도 포함)
if is_island:
    # 소운반, 폐자재 (바닥면적 기준)
    trans = p['transport_per_m2']['labor'] * floor_area
    waste = p['waste_per_m2']['labor'] * floor_area
    total_labor += trans + waste
    details.append(f"소운반: {floor_area:.2f}㎡ × {p['transport_per_m2']['labor']:,.0f} = {trans:,.0f}원 (노무)")
    details.append(f"폐자재반출: {floor_area:.2f}㎡ × {p['waste_per_m2']['labor']:,.0f} = {waste:,.0f}원 (노무)")

if include_fixed_expenses:
    # 견적 경비, 조사 경비, 에너지컨설팅 경비, 진단비 (내륙도 에너지컨설팅 포함)
    total_expense += p['estimate_expense']['expense']
    total_expense += p['survey_expense']['expense']
    total_expense += p['consulting_expense']['expense']
    total_expense += p['diagnosis_fee']['expense']
    details.append(f"견적경비 + 조사경비 + 에너지컨설팅 + 진단비 = {p['estimate_expense']['expense']+p['survey_expense']['expense']+p['consulting_expense']['expense']+p['diagnosis_fee']['expense']:,.0f}원")

# ==================== 5. 섬 지역 노무비 할증 및 간접비 ====================
labor_before_surcharge = total_labor
if is_island:
    labor_surcharge = total_labor * 0.5
    total_labor_after = total_labor + labor_surcharge
    details.append(f"🏝️ 섬 노무비 할증 50%: +{labor_surcharge:,.0f}원")
else:
    total_labor_after = total_labor

# 간접비 (산재, 일반관리비, 이윤) : 할증 전 노무비 기준 28.95%
indirect_rate = 0.2895
indirect_cost = labor_before_surcharge * indirect_rate
details.append(f"간접비(산재+일반관리비+이윤): {indirect_rate*100:.1f}% × {labor_before_surcharge:,.0f} = {indirect_cost:,.0f}원")

# 총 합계 (부가세 전)
subtotal = total_material + total_labor_after + total_expense + indirect_cost
vat = subtotal * 0.1
grand_total = subtotal + vat

# ==================== 6. 결과 출력 ====================
st.header("📊 최종 견적 산출 결과")

if grand_total == 0:
    st.info("옵션을 선택해 주세요.")
else:
    remainder = limit - grand_total
    if remainder < 0:
        st.error(f"⚠️ 예산 초과! (초과 금액: {abs(int(remainder)):,}원)")
    else:
        st.success(f"✅ 예산 내 적정 (남은 잔액: {int(remainder):,}원)")

    st.markdown(f"<h2 style='text-align:center; color:#2563eb;'>총 견적 금액: {int(grand_total):,} 원 (부가세 포함)</h2>", unsafe_allow_html=True)

    with st.expander("🔍 세부 산출 내역 보기"):
        for line in details:
            st.write(f"- {line}")
        st.write(f"**자재비 합계**: {total_material:,.0f} 원")
        st.write(f"**노무비 (할증 전)**: {labor_before_surcharge:,.0f} 원")
        if is_island:
            st.write(f"**노무비 할증 50%**: +{labor_surcharge:,.0f} 원 → 할증 후 {total_labor_after:,.0f} 원")
        st.write(f"**경비 합계**: {total_expense:,.0f} 원")
        st.write(f"**간접비**: {indirect_cost:,.0f} 원")
        st.write(f"**소계 (부가세 전)**: {subtotal:,.0f} 원")
        st.write(f"**부가세 10%**: {vat:,.0f} 원")
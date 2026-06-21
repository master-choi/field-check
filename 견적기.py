import streamlit as st
import json

# ==================== 1. 단가 데이터 (자재, 노무, 경비 분리) ====================
UNIT_PRICES = {
    # 단열 (㎡당)
    'insulationWall': {'material': 9394, 'labor': 32965, 'expense': 192},
    'insulationCeiling': {'material': 9394, 'labor': 41518, 'expense': 227},
    # 도배 (㎡당)
    'wallpaperWall': {'material': 3378, 'labor': 6662, 'expense': 0},
    'wallpaperCeiling': {'material': 3443, 'labor': 8662, 'expense': 0},
    # 걸레받이 (m당)
    'baseboard': {'material': 1240, 'labor': 3060, 'expense': 183},
    # 창호 부대공정 (m당) - 본체 단가는 함수에서 별도 처리
    'urethane_fill': {'material': 1650, 'labor': 2602, 'expense': 0},
    'sealing_fill': {'material': 576, 'labor': 5015, 'expense': 0},
    'finish_interior': {'material': 1048, 'labor': 8234, 'expense': 340},
    'finish_exterior': {'material': 1048, 'labor': 8234, 'expense': 340},
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

ADMIN_PASSWORD = '0131'
PRICE_FILE = "unit_prices.json"

def load_prices():
    try:
        with open(PRICE_FILE, 'r') as f:
            loaded = json.load(f)
            for k, v in UNIT_PRICES.items():
                if k not in loaded:
                    loaded[k] = v
            return loaded
    except:
        return UNIT_PRICES.copy()

def save_prices(prices):
    with open(PRICE_FILE, 'w') as f:
        json.dump(prices, f, indent=2)

# ==================== 창호 본체 단가 계산 함수 (실제 견적 기반) ====================
def get_window_cost(window_type, width_mm, height_mm, pane_count):
    """
    window_type: "단창" 또는 "이중창"
    width_mm, height_mm: 창문 크기 (mm)
    pane_count: 창짝 개수 (철거비용에 사용)
    반환: material, labor, expense, removal_labor
    """
    area = (width_mm * height_mm) / 1_000_000  # ㎡

    # ----- 1. 자재비 (면적 × 종류별 기본단가, 체감 반영) -----
    if window_type == "단창":
        if area < 1.0:
            material = int(280000 * area)          # 0.5㎡ → 140,000 (실제 140,861)
        elif area <= 3.0:
            material = int(205000 * area)          # 1.71㎡ → 350,550 (실제 353,663)
        else:
            material = int(175000 * area)          # 3.06㎡ → 535,500 (실제 538,169)
    else:  # 이중창
        if area < 1.0:
            material = int(400000 * area)          # 0.95㎡ → 380,000 (실제 355,924)
        elif area <= 2.0:
            material = int(270000 * area)          # 1.96㎡ → 529,200 (실제 531,535)
        else:
            material = int(340000 * area)          # 3.16㎡ → 1,074,400 (실제 1,088,706)

    # ----- 2. 노무비 (면적 구간별 정액제) -----
    if window_type == "단창":
        if area <= 1.0:
            labor = 48077
        elif area <= 3.0:
            labor = 59745
        else:
            labor = 94913
    else:  # 이중창
        if area <= 1.0:
            labor = 56932
        elif area <= 2.0:
            labor = 70420
        else:
            labor = 108650

    # ----- 3. 경비 (노무비의 2%) -----
    expense = int(round(labor * 0.02))

    # ----- 4. 창짝 철거비 (EA당 3,377원) -----
    removal_labor = pane_count * 3377

    return {
        'material': material,
        'labor': labor,
        'expense': expense,
        'removal_labor': removal_labor
    }

# ==================== Streamlit UI 시작 ====================
if 'prices' not in st.session_state:
    st.session_state.prices = load_prices()
p = st.session_state.prices

st.set_page_config(page_title="온성 견적 마스터 (정밀형)", page_icon="🏗️", layout="centered")
st.markdown("<h1 style='text-align: center;'>🏗️ 온성 견적 산출기 (실제 단가 기반)</h1>", unsafe_allow_html=True)

# ==================== 2. 관리자 패널 (기존 그대로 유지) ====================
with st.expander("🔒 단가 설정 (관리자)"):
    pw = st.text_input("관리자 비밀번호", type="password")
    if pw == ADMIN_PASSWORD:
        st.success("관리자 모드 활성화")
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
            st.subheader("기타 항목 (필요시 확장)")
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
with col_w:
    length_ns = st.number_input("가로 (남/북벽 길이)", value=2900, step=100)
with col_l:
    width_ew = st.number_input("세로 (동/서벽 길이)", value=2500, step=100)
with col_h:
    height = st.number_input("천장 높이", value=2400, step=100)

len_ns_m = length_ns / 1000
wid_ew_m = width_ew / 1000
h_m = height / 1000
floor_area = len_ns_m * wid_ew_m
wall_ns_area = len_ns_m * h_m
wall_ew_area = wid_ew_m * h_m
ceiling_area = floor_area

st.subheader("🏗️ 단열 시공면 선택")
col1, col2, col3, col4, col5 = st.columns(5)
with col1: ins_north = st.checkbox("북쪽 벽")
with col2: ins_south = st.checkbox("남쪽 벽")
with col3: ins_east = st.checkbox("동쪽 벽")
with col4: ins_west = st.checkbox("서쪽 벽")
with col5: ins_ceiling = st.checkbox("천장 단열")

wallpaper_mode = st.radio(
    "도배 방식",
    ["전체 도배 (방 전체 5면 모두)", "단열한 부위만 도배", "도배 안함"],
    horizontal=True
)

st.subheader("🪟 걸레받이")
do_baseboard = st.checkbox("걸레받이 설치 (방 둘레 길이 적용)")

# ==================== 창문 입력 (종류/창짝 수 추가됨) ====================
st.subheader("🪟 창문 추가")
win_count = st.number_input("창문 개수", min_value=0, max_value=5, step=1)
windows = []
for i in range(win_count):
    st.write(f"**창문 {i+1}**")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        win_w = st.number_input(f"가로 (mm)", value=1150, step=10, key=f"ww{i}")
    with col2:
        win_h = st.number_input(f"세로 (mm)", value=1000, step=10, key=f"wh{i}")
    with col3:
        win_type = st.selectbox(f"종류", ["단창", "이중창"], key=f"wt{i}")
    with col4:
        # 기본 창짝 수 추천 (단창=2, 이중창=4)
        default_panes = 2 if win_type == "단창" else 4
        win_panes = st.number_input(f"창짝 수", min_value=1, value=default_panes, step=1, key=f"wp{i}")
    windows.append((win_w, win_h, win_type, win_panes))

st.subheader("🚪 추가 옵션")
opt1, opt2 = st.columns(2)
with opt1:
    boiler = st.checkbox("보일러 설치")
    oil_tank = st.checkbox("기름통 추가", disabled=not boiler)
    furniture_move = st.checkbox("가구운반 (장롱)")
with opt2:
    ac_reattach = st.checkbox("에어컨 간이 탈부착 (+10,000원)", disabled=not is_island)
    include_fixed_expenses = st.checkbox("견적/조사/컨설팅/진단비 포함", value=True)

st.divider()

# ==================== 4. 계산 엔진 ====================
total_material = 0
total_labor = 0
total_expense = 0
details = []

# 단열 면적 계산
ins_wall_area = 0.0
if ins_north: ins_wall_area += wall_ns_area
if ins_south: ins_wall_area += wall_ns_area
if ins_east: ins_wall_area += wall_ew_area
if ins_west: ins_wall_area += wall_ew_area
ins_ceil_area = ins_ceiling * ceiling_area

# 1. 단열 비용
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

# 2. 도배 비용
if wallpaper_mode == "전체 도배 (방 전체 5면 모두)":
    total_wall_area = 2*wall_ns_area + 2*wall_ew_area
    mat_wall = p['wallpaperWall']['material'] * total_wall_area
    lab_wall = p['wallpaperWall']['labor'] * total_wall_area
    total_material += mat_wall
    total_labor += lab_wall
    details.append(f"전체 벽 도배: {total_wall_area:.2f}m² → 자재 {mat_wall:,.0f} + 노무 {lab_wall:,.0f}")
    mat_ceil = p['wallpaperCeiling']['material'] * ceiling_area
    lab_ceil = p['wallpaperCeiling']['labor'] * ceiling_area
    total_material += mat_ceil
    total_labor += lab_ceil
    details.append(f"천장 도배: {ceiling_area:.2f}m² → 자재 {mat_ceil:,.0f} + 노무 {lab_ceil:,.0f}")

elif wallpaper_mode == "단열한 부위만 도배":
    if ins_wall_area > 0:
        mat = p['wallpaperWall']['material'] * ins_wall_area
        lab = p['wallpaperWall']['labor'] * ins_wall_area
        total_material += mat
        total_labor += lab
        details.append(f"단열된 벽 도배: {ins_wall_area:.2f}m² → 자재 {mat:,.0f} + 노무 {lab:,.0f}")
    if ins_ceil_area > 0:
        mat = p['wallpaperCeiling']['material'] * ins_ceil_area
        lab = p['wallpaperCeiling']['labor'] * ins_ceil_area
        total_material += mat
        total_labor += lab
        details.append(f"단열된 천장 도배: {ins_ceil_area:.2f}m² → 자재 {mat:,.0f} + 노무 {lab:,.0f}")

# 3. 걸레받이
if do_baseboard:
    perimeter = (len_ns_m + wid_ew_m) * 2
    mat = p['baseboard']['material'] * perimeter
    lab = p['baseboard']['labor'] * perimeter
    exp = p['baseboard']['expense'] * perimeter
    total_material += mat
    total_labor += lab
    total_expense += exp
    details.append(f"걸레받이: {perimeter:.2f}m → 자재 {mat:,.0f} + 노무 {lab:,.0f} + 경비 {exp:,.0f}")

# ==================== 4-1. 창호 및 부대공정 (수정된 부분) ====================
for i, (win_w, win_h, win_type, win_panes) in enumerate(windows):
    # 새 함수로 본체 비용 계산
    win_cost = get_window_cost(win_type, win_w, win_h, win_panes)
    
    # 본체 설치비
    total_material += win_cost['material']
    total_labor += win_cost['labor']
    total_expense += win_cost['expense']
    details.append(f"창문 {i+1} ({win_type}, {win_w}x{win_h}mm) 설치: 자재 {win_cost['material']:,.0f} + 노무 {win_cost['labor']:,.0f} + 경비 {win_cost['expense']:,.0f}")
    
    # 창짝 철거비 (EA당)
    total_labor += win_cost['removal_labor']
    details.append(f"  - 창짝 철거({win_panes}EA): 노무 {win_cost['removal_labor']:,.0f}")

    # 부대공정 (둘레 기준) - 기존 코드와 동일
    perimeter_win = (win_w + win_h) * 2 / 1000  # m

    # 발포
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
    # 내부마감
    mat = p['finish_interior']['material'] * perimeter_win
    lab = p['finish_interior']['labor'] * perimeter_win
    exp = p['finish_interior']['expense'] * perimeter_win
    total_material += mat
    total_labor += lab
    total_expense += exp
    details.append(f"  - 내부마감: {perimeter_win:.2f}m → 자재 {mat:,.0f} + 노무 {lab:,.0f} + 경비 {exp:,.0f}")
    # 외부마감
    mat = p['finish_exterior']['material'] * perimeter_win
    lab = p['finish_exterior']['labor'] * perimeter_win
    exp = p['finish_exterior']['expense'] * perimeter_win
    total_material += mat
    total_labor += lab
    total_expense += exp
    details.append(f"  - 외부마감: {perimeter_win:.2f}m → 자재 {mat:,.0f} + 노무 {lab:,.0f} + 경비 {exp:,.0f}")

# 5. 추가 옵션
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

# 6. 공통 경비
if is_island:
    trans = p['transport_per_m2']['labor'] * floor_area
    waste = p['waste_per_m2']['labor'] * floor_area
    total_labor += trans + waste
    details.append(f"소운반: {floor_area:.2f}㎡ × {p['transport_per_m2']['labor']:,.0f} = {trans:,.0f}원 (노무)")
    details.append(f"폐자재반출: {floor_area:.2f}㎡ × {p['waste_per_m2']['labor']:,.0f} = {waste:,.0f}원 (노무)")

if include_fixed_expenses:
    total_expense += p['estimate_expense']['expense']
    total_expense += p['survey_expense']['expense']
    total_expense += p['consulting_expense']['expense']
    total_expense += p['diagnosis_fee']['expense']
    details.append(f"견적경비+조사경비+에너지컨설팅+진단비 = {p['estimate_expense']['expense']+p['survey_expense']['expense']+p['consulting_expense']['expense']+p['diagnosis_fee']['expense']:,.0f}원")

# 7. 섬 지역 노무비 할증 및 간접비 (기존 로직 유지)
labor_before = total_labor
if is_island:
    labor_surcharge = total_labor * 0.5
    total_labor = total_labor + labor_surcharge
    details.append(f"🏝️ 섬 노무비 할증 50%: +{labor_surcharge:,.0f}원")
else:
    labor_surcharge = 0

indirect_rate = 0.2895
indirect_cost = labor_before * indirect_rate
details.append(f"간접비(산재+일반관리비+이윤): {indirect_rate*100:.1f}% × {labor_before:,.0f} = {indirect_cost:,.0f}원")

subtotal = total_material + total_labor + total_expense + indirect_cost
vat = subtotal * 0.1
grand_total = subtotal + vat

# ==================== 5. 결과 출력 ====================
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
        st.write(f"**노무비 (할증 전)**: {labor_before:,.0f} 원")
        if is_island:
            st.write(f"**노무비 할증 50%**: +{labor_surcharge:,.0f} 원 → 할증 후 {total_labor:,.0f} 원")
        st.write(f"**경비 합계**: {total_expense:,.0f} 원")
        st.write(f"**간접비**: {indirect_cost:,.0f} 원")
        st.write(f"**소계 (부가세 전)**: {subtotal:,.0f} 원")
        st.write(f"**부가세 10%**: {vat:,.0f} 원")
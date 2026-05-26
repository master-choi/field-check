import streamlit as st
import json
import math

# ==================== 1. 기본 단가 & 파일 경로 (내륙/섬 통합 표준화) ====================
DEFAULT_PRICES = {
    'insulationWall': 42551,      # 벽체 단열 (1m²당)
    'insulationCeiling': 51140,   # 천장 단열 (1m²당)
    'wallpaperWall': 11908,       # 벽체 도배 (1m²당)
    'wallpaperCeiling': 12105,    # 천장 도배 (1m²당)
    
    'window_per_m2': 531125,      # 창문 (1m²당)
    'homeDoor_110': 300000,
    'homeDoor_120': 350000,
    'homeDoor_130': 400000,
    'homeDoor_150': 480000,
    'entrance_hinge': 700000,
    'entrance_hinge_fix': 900000,
    'entrance_sliding': 800000,
    'boiler': 1100000,
    'oilTank': 200000,
    
    # 섬지역 전용 항목들
    'island_ac_reattach': 10000,           # 에어컨 간이 탈부착
    'island_transport_per_m2': 1681.6,     # 소운반비 (m²당)
    'island_waste_per_m2': 1345.4,         # 폐자재반출 (m²당)
    'island_expense_fixed': 34433,         # 고정 경비
    'island_total_amount_rate': 1.1848944, # 순수공사비 -> 총금액 변환 요율
    'island_surcharge_rate': 0.408371,     # 섬 할증률
    'island_indirect_rate': 0.1087947,     # 간접비율
}
ADMIN_PASSWORD = '0131'
PRICE_FILE = "prices_unified.json"

def load_prices():
    try:
        with open(PRICE_FILE, 'r') as f:
            loaded = json.load(f)
            for k, v in DEFAULT_PRICES.items():
                if k not in loaded: loaded[k] = v
            return loaded
    except:
        return DEFAULT_PRICES.copy()

def save_prices(prices):
    with open(PRICE_FILE, 'w') as f:
        json.dump(prices, f, indent=2)

if 'prices' not in st.session_state:
    st.session_state.prices = load_prices()

p = st.session_state.prices

st.set_page_config(page_title="온성 견적 마스터 (통합형)", page_icon="🏗️", layout="centered")
st.markdown("<h1 style='text-align: center;'>🏗️ 온성 견적 산출기</h1>", unsafe_allow_html=True)

# ==================== 2. 관리자 패널 (기존 기능 100% 유지) ====================
with st.expander("🔒 단가 설정 (관리자)"):
    pw = st.text_input("관리자 비밀번호", type="password")
    if pw == ADMIN_PASSWORD:
        st.success("관리자 모드 활성화")
        col1, col2 = st.columns(2)
        with col1:
            p['insulationWall'] = st.number_input("벽체 단열 (1m²당)", value=p['insulationWall'], step=1000)
            p['insulationCeiling'] = st.number_input("천장 단열 (1m²당)", value=p['insulationCeiling'], step=1000)
            p['wallpaperWall'] = st.number_input("벽체 도배 (1m²당)", value=p['wallpaperWall'], step=1000)
            p['wallpaperCeiling'] = st.number_input("천장 도배 (1m²당)", value=p['wallpaperCeiling'], step=1000)
            p['window_per_m2'] = st.number_input("창문 (1m²당)", value=p['window_per_m2'], step=1000)
            p['boiler'] = st.number_input("보일러 설치", value=p['boiler'], step=1000)
            p['oilTank'] = st.number_input("기름통 추가", value=p['oilTank'], step=1000)
        with col2:
            p['homeDoor_110'] = st.number_input("홈도어 110mm", value=p['homeDoor_110'], step=1000)
            p['homeDoor_120'] = st.number_input("홈도어 120mm", value=p['homeDoor_120'], step=1000)
            p['homeDoor_130'] = st.number_input("홈도어 130mm", value=p['homeDoor_130'], step=1000)
            p['homeDoor_150'] = p_val = st.number_input("홈도어 150mm", value=p['homeDoor_150'], step=1000)
            p['entrance_hinge'] = st.number_input("출입문 여닫이", value=p['entrance_hinge'], step=1000)
            p['entrance_hinge_fix'] = st.number_input("출입문 여닫이+픽스창", value=p['entrance_hinge_fix'], step=1000)
            p['entrance_sliding'] = st.number_input("출입문 미닫이", value=p['entrance_sliding'], step=1000)
        
        if st.button("💾 설정 저장", use_container_width=True):
            save_prices(p)
            st.success("설정이 저장되었습니다.")

st.divider()

# ==================== 3. 메인 입력 UI (원래대로 직관적인 한 화면 통합) ====================
col_opt1, col_opt2 = st.columns(2)
with col_opt1:
    is_island = st.checkbox("🏝️ 섬 지역 현장 (체크 시 섬할증 공식 적용)", value=False)
with col_opt2:
    limit = st.number_input("💰 공사 한도 금액 (원)", value=3000000, step=100000)

st.subheader("📐 방 치수 입력 (mm)")
col_w, col_l, col_h = st.columns(3)
with col_w: room_w = st.number_input("동/서벽 가로 길이", value=3300, step=100)
with col_l: room_l = st.number_input("남/북벽 가로 길이", value=2500, step=100)
with col_h: room_h = st.number_input("천장 높이", value=2400, step=100)

# M 단위 변환 및 면적 계산
w_m, l_m, h_m = room_w / 1000, room_l / 1000, room_h / 1000
area_east_west = w_m * h_m
area_south_north = l_m * h_m
area_ceiling = w_m * l_m

st.subheader("🏗️ 단열 시공면 선택")
c_s1, c_s2, c_s3, c_s4, c_s5 = st.columns(5)
with c_s1: wallEast = st.checkbox("동쪽 단열")
with c_s2: wallWest = st.checkbox("서쪽 단열")
with c_s3: wallSouth = st.checkbox("남쪽 단열")
with c_s4: wallNorth = st.checkbox("북쪽 단열")
with c_s5: ceiling = st.checkbox("천장 단열")

st.subheader("🎨 도배 방식 선택")
wallpaper_mode = st.radio(
    "도배 방식",
    ["전체 도배 (방 전체 5면 모두)", "부분 도배 (단열하는 부위만 똑같이)", "도배 안함"],
    horizontal=True
)

st.subheader("🪟 창문 추가")
winCount = st.selectbox("창문 개수", [0, 1, 2, 3])
windows = []
for i in range(winCount):
    st.write(f"**창문 {i+1}**")
    wc1, wc2 = st.columns(2)
    with wc1: winW = st.number_input(f"가로 (mm)", value=1400, step=100, key=f"winW_{i}")
    with wc2: winH = st.number_input(f"세로 (mm)", value=1400, step=100, key=f"winH_{i}")
    windows.append((winW, winH))

st.subheader("🚪 문 및 보일러 옵션")
col_d1, col_d2 = st.columns(2)
with col_d1:
    homeDoorCount = st.selectbox("홈도어(방문) 개수", [0, 1, 2])
    homeDoors = [st.selectbox(f"홈도어 {i+1} 두께", ["110", "120", "130", "150"], index=1, key=f"hd_{i}") for i in range(homeDoorCount)]
    
    entranceDoorCount = st.selectbox("출입문(현관문) 개수", [0, 1, 2])
    entrance_options = {"여닫이 (기본)": "hinge", "여닫이 + 픽스창": "hinge_fix", "미닫이": "sliding"}
    entranceDoors = [st.selectbox(f"출입문 {i+1} 종류", list(entrance_options.keys()), key=f"ed_{i}") for i in range(entranceDoorCount)]
with col_d2:
    st.markdown("<br>", unsafe_allow_html=True)
    boiler = st.checkbox("🔥 보일러 교체 설치")
    oilTank = st.checkbox("🛢️ 보일러 기름통 추가", disabled=not boiler)
    ac_add = st.checkbox("🪛 에어컨 간이 탈부착 추가 (+10,000원)", disabled=not is_island, help="섬지역 선택 시에만 활성화됩니다.")

st.divider()

# ==================== 4. 통합 계산 정밀 로직 ====================
total_base = 0.0
details = []

# --- 면적 계산 및 자동 매칭 연산 ---
ins_wall_area = 0.0
ins_ceil_area = 0.0
if wallEast: ins_wall_area += area_east_west
if wallWest: ins_wall_area += area_east_west
if wallSouth: ins_wall_area += area_south_north
if wallNorth: ins_wall_area += area_south_north
if ceiling: ins_ceil_area += area_ceiling

wp_wall_area = 0.0
wp_ceil_area = 0.0

if wallpaper_mode == "전체 도배 (방 전체 5면 모두)":
    wp_wall_area = (area_east_west * 2) + (area_south_north * 2)
    wp_ceil_area = area_ceiling
elif wallpaper_mode == "부분 도배 (단열하는 부위만 똑같이)":
    wp_wall_area = ins_wall_area
    wp_ceil_area = ins_ceil_area

# 1. 단열 비용 누적
if ins_wall_area > 0:
    cost = ins_wall_area * p['insulationWall']
    total_base += cost
    details.append(f"단열(벽체): {ins_wall_area:.2f}m² × {p['insulationWall']:,}원 = {int(cost):,}원")
if ins_ceil_area > 0:
    cost = ins_ceil_area * p['insulationCeiling']
    total_base += cost
    details.append(f"단열(천장): {ins_ceil_area:.2f}m² × {p['insulationCeiling']:,}원 = {int(cost):,}원")

# 2. 도배 비용 누적
if wp_wall_area > 0:
    cost = wp_wall_area * p['wallpaperWall']
    total_base += cost
    details.append(f"도배(벽체): {wp_wall_area:.2f}m² × {p['wallpaperWall']:,}원 = {int(cost):,}원")
if wp_ceil_area > 0:
    cost = wp_ceil_area * p['wallpaperCeiling']
    total_base += cost
    details.append(f"도배(천장): {wp_ceil_area:.2f}m² × {p['wallpaperCeiling']:,}원 = {int(cost):,}원")

# 3. 창문 비용 누적
for i, (w, h) in enumerate(windows):
    win_area = (w * h) / 1000000
    cost = win_area * p['window_per_m2']
    total_base += cost
    details.append(f"창문 {i+1} ({w}×{h}mm): {win_area:.2f}m² × {p['window_per_m2']:,}원 = {int(cost):,}원")

# 4. 문 및 보일러 비용 누적
for i, thick in enumerate(homeDoors):
    price = p.get(f'homeDoor_{thick}', 350000)
    total_base += price
    details.append(f"홈도어 {i+1} ({thick}mm): {price:,}원")
for i, etype in enumerate(entranceDoors):
    price = p.get(f'entrance_{entrance_options[etype]}', 700000)
    total_base += price
    details.append(f"출입문 {i+1} ({etype}): {price:,}원")
if boiler:
    total_base += p['boiler']
    details.append(f"보일러 설치: {p['boiler']:,}원")
if oilTank:
    total_base += p['oilTank']
    details.append(f"보일러 기름통: {p['oilTank']:,}원")
if is_island and ac_add:
    total_base += p['island_ac_reattach']
    details.append(f"에어컨 간이 탈부착: {p['island_ac_reattach']:,}원")

# 5. 섬지역 전용 공통경비 계산 분기
if is_island and total_base > 0:
    # 일한 면적(시공 활성화된 총 면적) 계산
    active_east = area_east_west if (wallEast or wallpaper_mode == "전체 도배 (방 전체 5면 모두)") else 0
    active_west = area_east_west if (wallWest or wallpaper_mode == "전체 도배 (방 전체 5면 모두)") else 0
    active_south = area_south_north if (wallSouth or wallpaper_mode == "전체 도배 (방 전체 5면 모두)") else 0
    active_north = area_south_north if (wallNorth or wallpaper_mode == "전체 도배 (방 전체 5면 모두)") else 0
    active_ceil = area_ceiling if (ceiling or wallpaper_mode == "전체 도배 (방 전체 5면 모두)") else 0
    total_active_area = active_east + active_west + active_south + active_north + active_ceil
    
    transport_cost = int(total_active_area * p['island_transport_per_m2'] + 0.5)
    waste_cost = int(total_active_area * p['island_waste_per_m2'] + 0.5)
    fixed_exp = int(p['island_expense_fixed'])
    
    common_total = transport_cost + waste_cost + fixed_exp
    total_base += common_total
    details.append(f"⚙️ 섬 공통내역: {common_total:,}원 (소운반 {transport_cost:,} + 폐자재 {waste_cost:,} + 경비 {fixed_exp:,})")

# ==================== 5. 최종 결과 표출 분기 ====================
st.header("📊 최종 견적 산출 결과")

if total_base == 0:
    st.info("👆 시공할 방의 치수와 단열/도배 옵션을 선택해 주세요.")
else:
    if is_island:
        # 🟧 섬 지역 독립정산 공식 적용
        total_base_int = int(total_base)
        total_amount = int(total_base_int * p.get('island_total_amount_rate', 1.1848944))
        island_surcharge = int(total_amount * p.get('island_surcharge_rate', 0.408371))
        indirect_cost = int(total_amount * p.get('island_indirect_rate', 0.1087947))
        grand_total = total_amount + island_surcharge + indirect_cost
        
        remainder = limit - grand_total
        if remainder < 0:
            st.error(f"⚠️ 예산 초과! (초과 금액: {abs(int(remainder)):,}원)")
        else:
            st.success(f"✅ 예산 내 적정 (남은 잔액: {int(remainder):,}원)")
            
        st.markdown(f"<h2 style='text-align:center; color:#e11d48;'>섬지역 총 금액: {grand_total:,} 원</h2>", unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        col1.metric("총금액(요율반영)", f"{total_amount:,}원")
        col2.metric(f"도서 할증({p.get('island_surcharge_rate', 0.408371)*100:.1f}%)", f"{island_surcharge:,}원")
        col3.metric(f"간접비({p.get('island_indirect_rate', 0.1087947)*100:.1f}%)", f"{indirect_cost:,}원")
    else:
        # 🟦 일반 내륙 방식 정산
        grand_total = int(total_base)
        remainder = limit - grand_total
        if remainder < 0:
            st.error(f"⚠️ 예산 초과! (초과 금액: {abs(int(remainder)):,}원)")
        else:
            st.success(f"✅ 예산 내 적정 (남은 잔액: {int(remainder):,}원)")
            
        st.markdown(f"<h2 style='text-align:center; color:#2563eb;'>내륙 총 견적: {grand_total:,} 원</h2>", unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown("**🔍 세부 산출 내역**")
        for line in details:
            st.markdown(f"- {line}")
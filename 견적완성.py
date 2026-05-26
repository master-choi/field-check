import streamlit as st
import json

# ==================== 관공서 기준 자재비/노무비/간접비 단가 ====================
DEFAULT_PRICES = {
    # 단열 벽체 (합계: 42,551)
    'insulationWall_mat': 24351,
    'insulationWall_lab': 18200,
    
    # 단열 천장 (합계: 51,140)
    'insulationCeiling_mat': 29140,
    'insulationCeiling_lab': 22000,
    
    # 도배 (합계: 12,175)
    'wallpaper_mat': 5175,
    'wallpaper_lab': 7000,
    
    # 창문 (1m²당 합계: 531,125)
    'window_mat': 411125,
    'window_lab': 120000,
    
    # 걸레받이 (1m당 합계: 5,000)
    'skirting_mat': 2000,
    'skirting_lab': 3000,
    
    # 문 및 보일러류 (일체형 관리)
    'homeDoor_110': 300000,
    'homeDoor_120': 350000,
    'homeDoor_130': 400000,
    'homeDoor_150': 480000,
    'entrance_hinge': 700000,
    'entrance_hinge_fix': 900000,
    'entrance_sliding': 800000,
    'boiler': 1100000,
    'oilTank': 200000,
    
    # 할증률 및 간접비 세팅
    'island_labor_surcharge_pct': 50.0,  # 섬지역 노무비 할증률 (%)
    'indirect_cost_pct': 10.8            # 일반관리비/이윤 등 간접비 요율 (%)
}

ADMIN_PASSWORD = '0131'
PRICE_FILE = "prices_pro.json"

def load_prices():
    try:
        with open(PRICE_FILE, 'r') as f:
            loaded = json.load(f)
            for k, v in DEFAULT_PRICES.items():
                if k not in loaded:
                    loaded[k] = v
            return loaded
    except:
        return DEFAULT_PRICES.copy()

def save_prices(prices):
    with open(PRICE_FILE, 'w') as f:
        json.dump(prices, f, indent=2)

if 'prices' not in st.session_state:
    st.session_state.prices = load_prices()

st.set_page_config(page_title="온성 견적 마스터 PRO", page_icon="🏗️", layout="centered")
st.markdown("<h1 style='text-align: center;'>🏗️ 온성 견적 산출기 (정밀 정산형)</h1>", unsafe_allow_html=True)

# ==================== 관리자 패널 ====================
with st.expander("🔒 단가 / 할증 / 간접비 설정 (관리자)"):
    pw = st.text_input("관리자 비밀번호", type="password")
    if pw == ADMIN_PASSWORD:
        st.success("관리자 정밀 모드 활성화")
        
        st.markdown("### 🔹 공종별 자재비 / 노무비 분리 입력")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**[자재비 단가]**")
            st.session_state.prices['insulationWall_mat'] = st.number_input("단열 벽 자재비", value=st.session_state.prices['insulationWall_mat'], step=500)
            st.session_state.prices['insulationCeiling_mat'] = st.number_input("단열 천장 자재비", value=st.session_state.prices['insulationCeiling_mat'], step=500)
            st.session_state.prices['wallpaper_mat'] = st.number_input("도배 자재비", value=st.session_state.prices['wallpaper_mat'], step=500)
            st.session_state.prices['window_mat'] = st.number_input("창문 자재비 (1m²당)", value=st.session_state.prices['window_mat'], step=1000)
            st.session_state.prices['skirting_mat'] = st.number_input("걸레받이 자재비 (1m당)", value=st.session_state.prices['skirting_mat'], step=100)
        with col2:
            st.markdown("**[노무비 인건비 단가]**")
            st.session_state.prices['insulationWall_lab'] = st.number_input("단열 벽 노무비", value=st.session_state.prices['insulationWall_lab'], step=500)
            st.session_state.prices['insulationCeiling_lab'] = st.number_input("단열 천장 노무비", value=st.session_state.prices['insulationCeiling_lab'], step=500)
            st.session_state.prices['wallpaper_lab'] = st.number_input("도배 노무비", value=st.session_state.prices['wallpaper_lab'], step=500)
            st.session_state.prices['window_lab'] = st.number_input("창문 노무비 (1m²당)", value=st.session_state.prices['window_lab'], step=1000)
            st.session_state.prices['skirting_lab'] = st.number_input("걸레받이 노무비 (1m당)", value=st.session_state.prices['skirting_lab'], step=100)
            
        st.divider()
        st.markdown("### 🔹 문 및 장비 단가")
        col3, col4 = st.columns(2)
        with col3:
            st.session_state.prices['homeDoor_110'] = st.number_input("홈도어 110mm", value=st.session_state.prices['homeDoor_110'], step=1000)
            st.session_state.prices['homeDoor_120'] = st.number_input("홈도어 120mm", value=st.session_state.prices['homeDoor_120'], step=1000)
            st.session_state.prices['homeDoor_130'] = st.number_input("홈도어 130mm", value=st.session_state.prices['homeDoor_130'], step=1000)
            st.session_state.prices['homeDoor_150'] = st.number_input("홈도어 150mm", value=st.session_state.prices['homeDoor_150'], step=1000)
        with col4:
            st.session_state.prices['entrance_hinge'] = st.number_input("출입문 여닫이", value=st.session_state.prices['entrance_hinge'], step=1000)
            st.session_state.prices['entrance_hinge_fix'] = st.number_input("출입문 여닫이+픽스창", value=st.session_state.prices['entrance_hinge_fix'], step=1000)
            st.session_state.prices['entrance_sliding'] = st.number_input("출입문 미닫이", value=st.session_state.prices['entrance_sliding'], step=1000)
            st.session_state.prices['boiler'] = st.number_input("보일러 설치", value=st.session_state.prices['boiler'], step=1000)
            st.session_state.prices['oilTank'] = st.number_input("기름통 추가", value=st.session_state.prices['oilTank'], step=1000)

        st.divider()
        st.markdown("### 🔹 요율 설정 (할증 및 간접비)")
        col_rate1, col_rate2 = st.columns(2)
        with col_rate1:
            st.session_state.prices['island_labor_surcharge_pct'] = st.number_input("🏝️ 섬지역 노무비 할증률 (%)", value=float(st.session_state.prices.get('island_labor_surcharge_pct', 50.0)), step=0.1, format="%.1f")
        with col_rate2:
            st.session_state.prices['indirect_cost_pct'] = st.number_input("📊 일반관리비 등 간접비율 (%)", value=float(st.session_state.prices.get('indirect_cost_pct', 10.8)), step=0.1, format="%.1f", help="재단 서류상의 기타 대행비, 간접비 총비율입니다.")

        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("💾 정밀 설정 저장", use_container_width=True):
                save_prices(st.session_state.prices)
                st.success("설정 데이터가 안전하게 저장되었습니다.")
        with col_btn2:
            if st.button("🔄 초기화", use_container_width=True):
                st.session_state.prices = DEFAULT_PRICES.copy()
                st.rerun()
    elif pw:
        st.error("비밀번호가 일치하지 않습니다.")

st.divider()

# ==================== 메인 입력 섹션 ====================
col_limit, col_island = st.columns([2, 1])
with col_limit:
    limit = st.number_input("💰 공사 한도 금액 (원)", value=3000000, step=100000)
with col_island:
    st.write("")
    st.write("")
    is_island = st.checkbox("🏝️ 섬 지역 현장 (도서할증)", help="체크 시 순수 노무비 항목에 50% 할증이 적용됩니다.")

st.subheader("📏 방 치수 (mm)")
col_h, col_w, col_l = st.columns(3)
with col_h: height = st.number_input("천장 높이", value=2200, step=100)
with col_w: width = st.number_input("가로", value=0, step=100)
with col_l: length = st.number_input("세로", value=0, step=100)

st.subheader("🏠 단열할 면 선택")
col_s, col_n, col_e, col_w_wall, col_c = st.columns(5)
with col_s: wallSouth = st.checkbox("남벽 (가로)")
with col_n: wallNorth = st.checkbox("북벽 (가로)")
with col_e: wallEast = st.checkbox("동벽 (세로)")
with col_w_wall: wallWest = st.checkbox("서벽 (세로)")
with col_c: ceiling = st.checkbox("천장")

h_m, w_m, l_m = height / 1000, width / 1000, length / 1000
southArea = w_m * h_m
northArea = w_m * h_m
eastArea = l_m * h_m
westArea = l_m * h_m
ceilingArea = w_m * l_m

st.subheader("🪟 창문 치수")
winCount = st.selectbox("창문 개수", [0, 1, 2, 3])
windows = []
for i in range(winCount):
    st.write(f"**창문 {i+1}**")
    wc1, wc2 = st.columns(2)
    with wc1: winW = st.number_input(f"가로 (mm)", value=1400, step=100, key=f"winW_{i}")
    with wc2: winH = st.number_input(f"세로 (mm)", value=1400, step=100, key=f"winH_{i}")
    windows.append((winW, winH))

st.subheader("🚪 홈도어 / 출입문")
hdc, edc = st.columns(2)
with hdc:
    homeDoorCount = st.selectbox("방문(홈도어) 개수", [0, 1, 2])
    homeDoors = []
    for i in range(homeDoorCount):
        thick = st.selectbox(f"방문 {i+1} 바 두께", ["110", "120", "130", "150"], index=1, key=f"hd_{i}")
        homeDoors.append(thick)
with edc:
    entranceDoorCount = st.selectbox("현관문(출입문) 개수", [0, 1, 2])
    entranceDoors = []
    entrance_options = {"여닫이 (기본)": "hinge", "여닫이 + 픽스창": "hinge_fix", "미닫이": "sliding"}
    for i in range(entranceDoorCount):
        etype = st.selectbox(f"현관문 {i+1} 종류", list(entrance_options.keys()), key=f"ed_{i}")
        entranceDoors.append(entrance_options[etype])

st.subheader("🔥 보일러")
bc1, bc2 = st.columns(2)
with bc1: boiler = st.checkbox("보일러 설치")
with bc2: oilTank = st.checkbox("기름통 추가", disabled=not boiler)

st.divider()

# ==================== 면적 및 개구부 공제 연산 ====================
total_window_area = sum([(w * h) / 1000000 for w, h in windows])
total_door_area = (homeDoorCount * 1.89) + (entranceDoorCount * 2.1)
total_opening_area = total_window_area + total_door_area

insWallArea = 0
insCeilingArea = 0
if wallSouth: insWallArea += southArea
if wallNorth: insWallArea += northArea
if wallEast: insWallArea += eastArea
if wallWest: insWallArea += westArea
if ceiling: insCeilingArea += ceilingArea

if insWallArea > 0:
    insWallArea = max(0.0, insWallArea - total_opening_area)

# 도배 및 걸레받이 자동 계산 규칙
insulated_surfaces = [wallSouth, wallNorth, wallEast, wallWest, ceiling]
ins_count = sum(insulated_surfaces)
skirtingLength = 0

if ins_count >= 2:
    total_wall_area = southArea + northArea + eastArea + westArea
    wallpaperArea = max(0.0, total_wall_area - total_opening_area) + ceilingArea
    skirtingLength = (w_m + l_m) * 2
elif ins_count == 1:
    if wallSouth: wallpaperArea = max(0.0, southArea - total_opening_area); skirtingLength = w_m
    elif wallNorth: wallpaperArea = max(0.0, northArea - total_opening_area); skirtingLength = w_m
    elif wallEast: wallpaperArea = max(0.0, eastArea - total_opening_area); skirtingLength = l_m
    elif wallWest: wallpaperArea = max(0.0, westArea - total_opening_area); skirtingLength = l_m
    else: wallpaperArea = ceilingArea; skirtingLength = 0
else:
    wallpaperArea = 0

# ==================== 자재비 / 노무비 분리 계산 ====================
total_mat = 0
total_lab = 0
details = []
p = st.session_state.prices

# 1. 단열 벽체
if insWallArea > 0:
    m_cost = insWallArea * p['insulationWall_mat']
    l_cost = insWallArea * p['insulationWall_lab']
    total_mat += m_cost
    total_lab += l_cost
    details.append(f"단열(벽체) {insWallArea:.2f}m²: 자재 {int(m_cost):,}원 / 노무 {int(l_cost):,}원")

# 2. 단열 천장
if insCeilingArea > 0:
    m_cost = insCeilingArea * p['insulationCeiling_mat']
    l_cost = insCeilingArea * p['insulationCeiling_lab']
    total_mat += m_cost
    total_lab += l_cost
    details.append(f"단열(천장) {insCeilingArea:.2f}m²: 자재 {int(m_cost):,}원 / 노무 {int(l_cost):,}원")

# 3. 도배
if wallpaperArea > 0:
    m_cost = wallpaperArea * p['wallpaper_mat']
    l_cost = wallpaperArea * p['wallpaper_lab']
    total_mat += m_cost
    total_lab += l_cost
    details.append(f"도배 공정 {wallpaperArea:.2f}m²: 자재 {int(m_cost):,}원 / 노무 {int(l_cost):,}원")

# 4. 걸레받이
if skirtingLength > 0:
    m_cost = skirtingLength * p['skirting_mat']
    l_cost = skirtingLength * p['skirting_lab']
    total_mat += m_cost
    total_lab += l_cost
    details.append(f"걸레받이 {skirtingLength:.2f}m: 자재 {int(m_cost):,}원 / 노무 {int(l_cost):,}원")

# 5. 창문
for i, (w, h) in enumerate(windows):
    area = (w * h) / 1000000
    m_cost = area * p['window_mat']
    l_cost = area * p['window_lab']
    total_mat += m_cost
    total_lab += l_cost
    details.append(f"창문 {i+1} ({area:.2f}m²): 자재 {int(m_cost):,}원 / 노무 {int(l_cost):,}원")

# 6. 문, 보일러류 (자재비 70% / 노무비 30% 기본 분할 적용)
for i, thick in enumerate(homeDoors):
    price = p.get(f'homeDoor_{thick}', 350000)
    total_mat += price * 0.7
    total_lab += price * 0.3
    details.append(f"방문 {i+1} ({thick}mm): {price:,}원")

for i, etype in enumerate(entranceDoors):
    price = p.get(f'entrance_{etype}', 700000)
    total_mat += price * 0.7
    total_lab += price * 0.3
    details.append(f"현관문 {i+1}: {price:,}원")

if boiler:
    total_mat += p['boiler'] * 0.7
    total_lab += p['boiler'] * 0.3
    details.append(f"보일러 설치: {p['boiler']:,}원")
if oilTank:
    total_mat += p['oilTank'] * 0.8
    total_lab += p['oilTank'] * 0.2
    details.append(f"기름통 추가: {p['oilTank']:,}원")

# ==================== 관공서식 연산 (할증 및 간접비) ====================
labor_surcharge = 0
if is_island:
    surcharge_pct = p.get('island_labor_surcharge_pct', 50.0)
    # 1. 순수 노무비에 대해서만 50% 도서 할증 계산
    labor_surcharge = total_lab * (surcharge_pct / 100)

# 2. 직접공사비 합계 = 순수 자재비 + 순수 노무비 + 도서할증료
direct_construction_cost = total_mat + total_lab + labor_surcharge

# 3. 간접비 계산 = 직접공사비 × 간접비 요율
indirect_cost_rate = p.get('indirect_cost_pct', 10.8) / 100
indirect_cost = direct_construction_cost * indirect_cost_rate

# 4. 최종 견적 총액 = 직접공사비 + 간접비
final_total = direct_construction_cost + indirect_cost

# ==================== 화면 결과 표출 ====================
st.header("📊 관공서 기준 견적 결과")

if final_total == 0:
    st.info("👆 계산할 면적이나 공종 항목을 선택해 주세요.")
else:
    remainder = limit - final_total
    if remainder < 0:
        st.error(f"⚠️ 예산 초과 상태 (초과액: {abs(int(remainder)):,}원)")
    else:
        st.success(f"✅ 예산 범위 내 적정 (잔여 금액: {int(remainder):,}원)")

    st.markdown(f"<h2 style='text-align:center; color:#1e40af;'>최종 지원 금액 총액: {int(final_total):,} 원</h2>", unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown("**📋 관공서 제출용 정산 내역**")
        st.write(f"- 기본 순수 자재비 합계: {int(total_mat):,} 원")
        st.write(f"- 기본 순수 노무비 합계: {int(total_lab):,} 원")
        
        if is_island:
            st.markdown(f"- <span style='color:#c2410c;'>🏝️ 도서지역 노무비 할증 ({p.get('island_labor_surcharge_pct', 50.0):.1f}%): {int(labor_surcharge):,} 원</span>", unsafe_allow_html=True)
        
        st.write(f"- **직접 공사비 소계**: {int(direct_construction_cost):,} 원")
        st.markdown(f"- **제간접비 및 대행비 ({p.get('indirect_cost_pct', 10.8):.1f}%)**: {int(indirect_cost):,} 원")
        
        st.divider()
        st.caption("🔍 공종별 상세 산출 근거 (참고용)")
        for line in details:
            st.caption(line)
import streamlit as st
import json

# ==================== 기본 단가 & 파일 경로 ====================
DEFAULT_PRICES = {
    'insulationWall': 42551,
    'insulationCeiling': 51140,
    'wallpaper': 12175,
    'window_per_m2': 531125,
    'homeDoor_110': 300000,
    'homeDoor_120': 350000,
    'homeDoor_130': 400000,
    'homeDoor_150': 480000,
    'entrance_hinge': 700000,
    'entrance_hinge_fix': 900000,
    'entrance_sliding': 800000,
    'boiler': 1100000,
    'oilTank': 200000,
    'skirting_per_m': 5000,       # 걸레받이 기본 단가 (1m당)
    'island_surcharge_pct': 40.8  # 섬지역 할증률 기본값 (%)
}
ADMIN_PASSWORD = '0131'
PRICE_FILE = "prices.json"

# ==================== 단가 불러오기/저장 함수 ====================
def load_prices():
    try:
        with open(PRICE_FILE, 'r') as f:
            loaded = json.load(f)
            # 새로운 단가 항목이 기존 파일에 없을 경우를 대비해 병합
            for k, v in DEFAULT_PRICES.items():
                if k not in loaded:
                    loaded[k] = v
            return loaded
    except:
        return DEFAULT_PRICES.copy()

def save_prices(prices):
    with open(PRICE_FILE, 'w') as f:
        json.dump(prices, f, indent=2)

# 세션 상태 초기화
if 'prices' not in st.session_state:
    st.session_state.prices = load_prices()

st.set_page_config(page_title="온성 견적 마스터", page_icon="🏗️", layout="centered")

st.markdown("<h1 style='text-align: center;'>🏗️ 온성 견적 산출기</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: gray;'>치수를 입력하면 자동으로 총액이 계산됩니다</p>", unsafe_allow_html=True)

# ==================== 관리자 패널 ====================
with st.expander("🔒 단가 및 할증 설정 (관리자)"):
    pw = st.text_input("관리자 비밀번호", type="password")
    if pw == ADMIN_PASSWORD:
        st.success("관리자 모드 활성화")
        st.caption("※ 수정 후 반드시 [설정 저장]을 눌러주세요.")

        col1, col2 = st.columns(2)
        with col1:
            st.session_state.prices['insulationWall'] = st.number_input("단열 벽 (1m²당)", value=st.session_state.prices['insulationWall'], step=1000)
            st.session_state.prices['insulationCeiling'] = st.number_input("단열 천장 (1m²당)", value=st.session_state.prices['insulationCeiling'], step=1000)
            st.session_state.prices['wallpaper'] = st.number_input("도배 (1m²당)", value=st.session_state.prices['wallpaper'], step=1000)
            st.session_state.prices['window_per_m2'] = st.number_input("창문 (1m²당)", value=st.session_state.prices['window_per_m2'], step=1000)
            st.session_state.prices['boiler'] = st.number_input("보일러 설치", value=st.session_state.prices['boiler'], step=1000)
            st.session_state.prices['oilTank'] = st.number_input("기름통 추가", value=st.session_state.prices['oilTank'], step=1000)
        with col2:
            st.session_state.prices['homeDoor_110'] = st.number_input("홈도어 110mm", value=st.session_state.prices['homeDoor_110'], step=1000)
            st.session_state.prices['homeDoor_120'] = st.number_input("홈도어 120mm", value=st.session_state.prices['homeDoor_120'], step=1000)
            st.session_state.prices['homeDoor_130'] = st.number_input("홈도어 130mm", value=st.session_state.prices['homeDoor_130'], step=1000)
            st.session_state.prices['homeDoor_150'] = st.number_input("홈도어 150mm", value=st.session_state.prices['homeDoor_150'], step=1000)
            st.session_state.prices['entrance_hinge'] = st.number_input("출입문 여닫이", value=st.session_state.prices['entrance_hinge'], step=1000)
            st.session_state.prices['entrance_hinge_fix'] = st.number_input("출입문 여닫이+픽스창", value=st.session_state.prices['entrance_hinge_fix'], step=1000)
            st.session_state.prices['entrance_sliding'] = st.number_input("출입문 미닫이", value=st.session_state.prices['entrance_sliding'], step=1000)
        
        st.divider()
        st.markdown("**🔧 추가 항목 및 할증률 설정**")
        col3, col4 = st.columns(2)
        with col3:
            st.session_state.prices['skirting_per_m'] = st.number_input("걸레받이 단가 (1m당)", value=st.session_state.prices.get('skirting_per_m', 5000), step=500)
        with col4:
            st.session_state.prices['island_surcharge_pct'] = st.number_input("섬지역 할증률 (%)", value=float(st.session_state.prices.get('island_surcharge_pct', 40.8)), step=0.1, format="%.1f", help="40.8% 또는 50% 등으로 자유롭게 변경 가능합니다.")

        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("💾 설정 저장", use_container_width=True):
                save_prices(st.session_state.prices)
                st.success("설정이 저장되었습니다. (앱을 다시 실행해도 유지됩니다)")
        with col_btn2:
            if st.button("🔄 기본 단가로 초기화", use_container_width=True):
                st.session_state.prices = DEFAULT_PRICES.copy()
                st.success("기본 단가로 초기화되었습니다. 저장하려면 [설정 저장]을 눌러주세요.")
                st.rerun()
    elif pw:
        st.error("비밀번호가 틀렸습니다.")

st.divider()

# ==================== 입력 섹션 ====================
col_limit, col_island = st.columns([2, 1])
with col_limit:
    limit = st.number_input("💰 공사 한도 금액 (원)", value=3000000, step=100000)
with col_island:
    st.write("") # 간격 맞추기용
    st.write("") 
    is_island = st.checkbox("🏝️ 섬 지역 현장", help="체크 시 설정된 비율만큼 도서 할증이 자동 계산됩니다.")

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

st.subheader("🪟 창문")
winCount = st.selectbox("창문 개수", [0, 1, 2, 3])
windows = []
for i in range(winCount):
    st.write(f"**창문 {i+1}**")
    wc1, wc2 = st.columns(2)
    with wc1: winW = st.number_input(f"가로 (mm)", value=1400, step=100, key=f"winW_{i}")
    with wc2: winH = st.number_input(f"세로 (mm)", value=1400, step=100, key=f"winH_{i}")
    windows.append((winW, winH))

st.subheader("🚪 홈도어 (방문)")
homeDoorCount = st.selectbox("홈도어 개수", [0, 1, 2])
homeDoors = []
for i in range(homeDoorCount):
    thick = st.selectbox(f"홈도어 {i+1} 바 두께", ["110", "120", "130", "150"], index=1, key=f"hd_{i}")
    homeDoors.append(thick)

st.subheader("🚪 출입문 (현관문)")
entranceDoorCount = st.selectbox("출입문 개수", [0, 1, 2])
entranceDoors = []
entrance_options = {"여닫이 (기본)": "hinge", "여닫이 + 픽스창": "hinge_fix", "미닫이": "sliding"}
for i in range(entranceDoorCount):
    etype = st.selectbox(f"출입문 {i+1} 종류", list(entrance_options.keys()), key=f"ed_{i}")
    entranceDoors.append(entrance_options[etype])

st.subheader("🔥 보일러 / 기름통")
bc1, bc2 = st.columns(2)
with bc1: boiler = st.checkbox("보일러 설치")
with bc2: oilTank = st.checkbox("기름통 추가", disabled=not boiler)

st.divider()

# ==================== 자동 개구부 면적 계산 ====================
total_window_area = sum([(w * h) / 1000000 for w, h in windows])
# 일반적인 방문 규격(0.9m x 2.1m ≒ 1.89m²), 현관문 규격(1.0m x 2.1m ≒ 2.1m²) 적용
total_door_area = (homeDoorCount * 1.89) + (entranceDoorCount * 2.1)
total_opening_area = total_window_area + total_door_area

# ==================== 면적 및 걸레받이 계산 로직 ====================
insWallArea = 0
insCeilingArea = 0
if wallSouth: insWallArea += southArea
if wallNorth: insWallArea += northArea
if wallEast: insWallArea += eastArea
if wallWest: insWallArea += westArea
if ceiling: insCeilingArea += ceilingArea

# 벽체 단열 면적에서 개구부 차감 (음수 방지)
if insWallArea > 0:
    insWallArea = max(0.0, insWallArea - total_opening_area)

# --- 자동 도배 범위 및 걸레받이 길이(m) 계산 ---
insulated_surfaces = [wallSouth, wallNorth, wallEast, wallWest, ceiling]
ins_count = sum(insulated_surfaces)

skirtingLength = 0  # 걸레받이 길이 (미터)

if ins_count >= 2:
    # 전체 도배 (벽 전체 면적에서 개구부를 빼고 천장을 더함)
    total_wall_area = southArea + northArea + eastArea + westArea
    deducted_wall_area = max(0.0, total_wall_area - total_opening_area)
    wallpaperArea = deducted_wall_area + ceilingArea
    wallpaper_msg = "🎨 전체 도배 (벽+천장) [개구부 자동 차감 반영]"
    # 벽 도배가 들어가므로 방 전체 둘레 걸레받이 추가
    skirtingLength = (w_m + l_m) * 2
elif ins_count == 1:
    if wallSouth:
        wallpaperArea = max(0.0, southArea - total_opening_area)
        msg = "남벽"
        skirtingLength = w_m
    elif wallNorth:
        wallpaperArea = max(0.0, northArea - total_opening_area)
        msg = "북벽"
        skirtingLength = w_m
    elif wallEast:
        wallpaperArea = max(0.0, eastArea - total_opening_area)
        msg = "동벽"
        skirtingLength = l_m
    elif wallWest:
        wallpaperArea = max(0.0, westArea - total_opening_area)
        msg = "서벽"
        skirtingLength = l_m
    else:  # ceiling (천장만 도배)
        wallpaperArea = ceilingArea
        msg = "천장"
        skirtingLength = 0  # 천장 도배만 진행 시 걸레받이 제외
    
    if skirtingLength > 0:
        wallpaper_msg = f"🎨 부분 도배 ({msg}만) [개구부 자동 차감 반영]"
    else:
        wallpaper_msg = f"🎨 부분 도배 ({msg}만)"
else:
    wallpaperArea = 0
    wallpaper_msg = "🎨 도배 안함"
    skirtingLength = 0

st.info(wallpaper_msg)

# ==================== 금액 집계 및 상세 내역 작성 ====================
base_total = 0
details = []
p = st.session_state.prices

# 단열
if insWallArea > 0:
    cost = insWallArea * p['insulationWall']
    base_total += cost
    details.append(f"단열(벽체): {insWallArea:.2f}m² × {p['insulationWall']:,}원 = {int(cost):,}원 (개구부 차감 완료)")

if insCeilingArea > 0:
    cost = insCeilingArea * p['insulationCeiling']
    base_total += cost
    details.append(f"단열(천장): {insCeilingArea:.2f}m² × {p['insulationCeiling']:,}원 = {int(cost):,}원")

# 도배
if wallpaperArea > 0:
    cost = wallpaperArea * p['wallpaper']
    base_total += cost
    modeText = "전체" if ins_count >= 2 else "부분"
    details.append(f"도배 ({modeText}): {wallpaperArea:.2f}m² × {p['wallpaper']:,}원 = {int(cost):,}원")

# 걸레받이 (벽체 도배 시 무조건 자동 추가)
if skirtingLength > 0:
    skirting_cost = skirtingLength * p.get('skirting_per_m', 5000)
    base_total += skirting_cost
    details.append(f"걸레받이: {skirtingLength:.2f}m × {p.get('skirting_per_m', 5000):,}원 = {int(skirting_cost):,}원")

# 창문
for i, (w, h) in enumerate(windows):
    area = (w * h) / 1000000
    cost = area * p['window_per_m2']
    base_total += cost
    details.append(f"창문 {i+1}: {w}×{h}mm ({area:.2f}m²) = {int(cost):,}원")

# 홈도어
for i, thick in enumerate(homeDoors):
    price = p.get(f'homeDoor_{thick}', 350000)
    base_total += price
    details.append(f"홈도어 {i+1} ({thick}mm): {price:,}원")

# 출입문
for i, etype in enumerate(entranceDoors):
    price = p.get(f'entrance_{etype}', 700000)
    label = [k for k, v in entrance_options.items() if v == etype][0]
    base_total += price
    details.append(f"출입문 {i+1} ({label}): {price:,}원")

# 보일러/기름통
if boiler:
    base_total += p['boiler']
    details.append(f"보일러 설치: {p['boiler']:,}원")
if oilTank:
    base_total += p['oilTank']
    details.append(f"기름통 추가: {p['oilTank']:,}원")

# --- 섬지역 할증 연산 ---
final_total = base_total
surcharge_cost = 0
if is_island and base_total > 0:
    surcharge_pct = p.get('island_surcharge_pct', 40.8)
    surcharge_cost = base_total * (surcharge_pct / 100)
    final_total = base_total + surcharge_cost

# ==================== 결과 표시 ====================
st.header("📊 견적 결과")

if final_total == 0:
    st.info("👆 위 항목들을 입력해주세요")
else:
    remainder = limit - final_total

    if remainder < 0:
        st.error(f"⚠️ 예산 초과! (초과 금액: {abs(int(remainder)):,}원)")
    else:
        st.success(f"✅ 예산 내 적정 (남은 잔액: {int(remainder):,}원)")

    st.markdown(f"<h2 style='text-align:center; color:#2563eb;'>총 견적: {int(final_total):,} 원</h2>", unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown("**세부 산출 내역**")
        if total_opening_area > 0:
            st.caption(f"💡 시스템 안내: 창문/문 포함 총 {total_opening_area:.2f}m²의 개구부 면적이 벽체 면적에서 자동 차감되었습니다.")
        
        # 기본 공사 항목 출력
        for line in details:
            st.markdown(f"- {line}")
            
        # 섬지역일 경우 할증 항목 하단에 추가 표시
        if is_island:
            st.markdown(f"<span style='color:#ea580c;'>- **섬지역 도서 할증 ({p.get('island_surcharge_pct', 40.8):.1f}%)**: {int(surcharge_cost):,}원</span>", unsafe_allow_html=True)
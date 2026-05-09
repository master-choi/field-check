import streamlit as st

# ==================== 기본 단가 설정 ====================
DEFAULT_PRICES = {
    'insulationWall': 100000,
    'insulationCeiling': 100000,
    'wallpaper': 30000,
    'window_per_m2': 408163,
    'homeDoor_110': 300000,
    'homeDoor_120': 350000,
    'homeDoor_130': 400000,
    'homeDoor_150': 480000,
    'entrance_hinge': 700000,
    'entrance_hinge_fix': 900000,
    'entrance_sliding': 800000,
    'boiler': 800000,
    'oilTank': 200000
}
ADMIN_PASSWORD = '1234'

# 세션 상태에 단가 초기화
if 'prices' not in st.session_state:
    st.session_state.prices = DEFAULT_PRICES.copy()

st.set_page_config(page_title="현장 견적 마스터", page_icon="🏗️", layout="centered")

st.markdown("<h1 style='text-align: center;'>🏗️ 현장 견적 산출기</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: gray;'>치수를 입력하면 자동으로 총액이 계산됩니다</p>", unsafe_allow_html=True)

# ==================== 관리자 패널 ====================
with st.expander("🔒 단가 설정 (관리자)"):
    pw = st.text_input("관리자 비밀번호", type="password")
    if pw == ADMIN_PASSWORD:
        st.success("관리자 모드 활성화")
        st.caption("※ 수정하면 즉시 적용됩니다.")
        
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
            
        if st.button("🔄 기본 단가로 초기화"):
            st.session_state.prices = DEFAULT_PRICES.copy()
            st.rerun()
    elif pw:
        st.error("비밀번호가 틀렸습니다.")

st.divider()

# ==================== 입력 섹션 ====================
limit = st.number_input("💰 공사 한도 금액 (원)", value=10000000, step=100000)

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

st.subheader("🎨 도배 범위")
wallpaperMode = st.radio("도배 선택", ["전체 도배", "부분 도배 (단열면만)", "도배 안함"], horizontal=True)

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

# ==================== 계산 로직 ====================
h_m, w_m, l_m = height / 1000, width / 1000, length / 1000

southArea = w_m * h_m
northArea = w_m * h_m
eastArea = l_m * h_m
westArea = l_m * h_m
ceilingArea = w_m * l_m

insWallArea = 0
insCeilingArea = 0
if wallSouth: insWallArea += southArea
if wallNorth: insWallArea += northArea
if wallEast: insWallArea += eastArea
if wallWest: insWallArea += westArea
if ceiling: insCeilingArea += ceilingArea

totalWallArea = southArea + northArea + eastArea + westArea + ceilingArea
totalInsArea = insWallArea + insCeilingArea

wallpaperArea = 0
if wallpaperMode == "전체 도배": wallpaperArea = totalWallArea
elif wallpaperMode == "부분 도배 (단열면만)": wallpaperArea = totalInsArea

total = 0
details = []
p = st.session_state.prices

# 단열 계산
if insWallArea > 0:
    cost = insWallArea * p['insulationWall']
    total += cost
    details.append(f"단열(벽): {insWallArea:.2f}m² × {p['insulationWall']:,}원 = {int(cost):,}원")

if insCeilingArea > 0:
    cost = insCeilingArea * p['insulationCeiling']
    total += cost
    details.append(f"단열(천장): {insCeilingArea:.2f}m² × {p['insulationCeiling']:,}원 = {int(cost):,}원")

# 도배 계산
if wallpaperArea > 0:
    cost = wallpaperArea * p['wallpaper']
    total += cost
    modeText = "전체" if wallpaperMode == "전체 도배" else "부분"
    details.append(f"도배 ({modeText}): {wallpaperArea:.2f}m² × {p['wallpaper']:,}원 = {int(cost):,}원")

# 창문 계산
for i, (w, h) in enumerate(windows):
    area = (w * h) / 1000000
    cost = area * p['window_per_m2']
    total += cost
    details.append(f"창문 {i+1}: {w}×{h}mm ({area:.2f}m²) = {int(cost):,}원")

# 홈도어 계산
for i, thick in enumerate(homeDoors):
    price = p.get(f'homeDoor_{thick}', 350000)
    total += price
    details.append(f"홈도어 {i+1} ({thick}mm): {price:,}원")

# 출입문 계산
for i, etype in enumerate(entranceDoors):
    price = p.get(f'entrance_{etype}', 700000)
    label = [k for k, v in entrance_options.items() if v == etype][0]
    total += price
    details.append(f"출입문 {i+1} ({label}): {price:,}원")

# 보일러/기름통 계산
if boiler:
    total += p['boiler']
    details.append(f"보일러 설치: {p['boiler']:,}원")
if oilTank:
    total += p['oilTank']
    details.append(f"기름통 추가: {p['oilTank']:,}원")

# ==================== 결과 표시 ====================
st.header("📊 견적 결과")

if total == 0:
    st.info("👆 위 항목들을 입력해주세요")
else:
    remainder = limit - total
    
    # 상태 알림
    if remainder < 0:
        st.error(f"⚠️ 예산 초과! (초과 금액: {abs(int(remainder)):,}원)")
    else:
        st.success(f"✅ 예산 내 적정 (남은 잔액: {int(remainder):,}원)")
    
    # 총액 큰 글씨로 표시
    st.markdown(f"<h2 style='text-align:center; color:#2563eb;'>총 견적: {int(total):,} 원</h2>", unsafe_allow_html=True)
    
    # 세부 내역
    with st.container(border=True):
        st.markdown("**세부 산출 내역**")
        for line in details:
            st.markdown(f"- {line}")
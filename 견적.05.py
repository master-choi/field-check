import streamlit as st
import json

# ==================== 1. 기본 단가 & 파일 경로 (내륙/섬 통합) ====================
DEFAULT_PRICES = {
    # --- 내륙(기존) 단가 ---
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
    
    # --- 섬지역(신규) 단가 ---
    'island_insulationWall': 45842,      
    'island_insulationCeiling': 51139,   
    'island_wallpaperCeiling': 12105,    
    'island_wallpaperWall': 12138,       
    'island_ac_reattach': 10000,         
    'island_expense_fixed': 34433,       
}
ADMIN_PASSWORD = '0131'
PRICE_FILE = "prices.json"

# 현장에서 터치로 쉽게 뺄 수 있는 제외 면적(창문/문) 표준 규격 (단위: m²)
EXCLUSION_PRESETS = {
    "방문 (900×2100)": 1.89,
    "화장실문 (700×2000)": 1.40,
    "작은 창문 (1200×1200)": 1.44,
    "중간 창문 (1500×1500)": 2.25,
    "큰 거실창 (2000×2000)": 4.00,
    "사용자 직접 입력": 0.00
}

# ==================== 2. 단가 불러오기/저장 함수 ====================
def load_prices():
    try:
        with open(PRICE_FILE, 'r') as f:
            loaded = json.load(f)
            # 기존 json에 없는 신규 단가(섬지역 등)가 생기면 자동으로 병합하여 에러 방지
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

# ==================== 3. 관리자 패널 ====================
with st.expander("🔒 단가 설정 (관리자)"):
    pw = st.text_input("관리자 비밀번호", type="password")
    if pw == ADMIN_PASSWORD:
        st.success("관리자 모드 활성화 (섬지역 단가는 현재 코드 내부 기본값을 따르며, 추후 패널에 추가 가능합니다)")
        st.caption("※ 수정 후 반드시 [설정 저장]을 눌러주세요.")

        col1, col2 = st.columns(2)
        with col1:
            st.session_state.prices['insulationWall'] = st.number_input("내륙 단열 벽 (1m²당)", value=st.session_state.prices['insulationWall'], step=1000)
            st.session_state.prices['insulationCeiling'] = st.number_input("내륙 단열 천장 (1m²당)", value=st.session_state.prices['insulationCeiling'], step=1000)
            st.session_state.prices['wallpaper'] = st.number_input("내륙 도배 (1m²당)", value=st.session_state.prices['wallpaper'], step=1000)
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

        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("💾 설정 저장", use_container_width=True):
                save_prices(st.session_state.prices)
                st.success("설정이 저장되었습니다. (앱을 다시 실행해도 유지됩니다)")
        with col_btn2:
            if st.button("🔄 기본 단가로 초기화", use_container_width=True):
                st.session_state.prices = DEFAULT_PRICES.copy()
                save_prices(st.session_state.prices)
                st.success("기본 단가로 초기화되었습니다.")
                st.rerun()
    elif pw:
        st.error("비밀번호가 틀렸습니다.")

st.divider()

# ==================== 4. 시공 지역 선택 (핵심 분기점) ====================
st.subheader("📍 시공 지역 선택")
region_mode = st.radio(
    "현장 지역", 
    ["일반 내륙 (기존 방식)", "섬 지역 (상세/할증 방식)"], 
    horizontal=True, 
    label_visibility="collapsed"
)
st.divider()


if region_mode == "일반 내륙 (기존 방식)":
    # 🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦
    #                여기서부터 내륙 지역(기존) 코드 시작
    # 🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦
    limit = st.number_input("💰 공사 한도 금액 (원)", value=3000000, step=100000)

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

    # --- 자동 도배 범위 계산 ---
    h_m, w_m, l_m = height / 1000, width / 1000, length / 1000
    southArea = w_m * h_m
    northArea = w_m * h_m
    eastArea = l_m * h_m
    westArea = l_m * h_m
    ceilingArea = w_m * l_m

    insulated_surfaces = [wallSouth, wallNorth, wallEast, wallWest, ceiling]
    ins_count = sum(insulated_surfaces)

    if ins_count >= 2:
        wallpaperArea = southArea + northArea + eastArea + westArea + ceilingArea
        wallpaper_msg = "🎨 전체 도배 (벽+천장)"
    elif ins_count == 1:
        if wallSouth:
            wallpaperArea = southArea
            msg = "남벽"
        elif wallNorth:
            wallpaperArea = northArea
            msg = "북벽"
        elif wallEast:
            wallpaperArea = eastArea
            msg = "동벽"
        elif wallWest:
            wallpaperArea = westArea
            msg = "서벽"
        else:  # ceiling
            wallpaperArea = ceilingArea
            msg = "천장"
        wallpaper_msg = f"🎨 부분 도배 ({msg}만)"
    else:
        wallpaperArea = 0
        wallpaper_msg = "🎨 도배 안함"

    st.info(wallpaper_msg)

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

    # --- 내륙 지역 계산 로직 ---
    insWallArea = 0
    insCeilingArea = 0
    if wallSouth: insWallArea += southArea
    if wallNorth: insWallArea += northArea
    if wallEast: insWallArea += eastArea
    if wallWest: insWallArea += westArea
    if ceiling: insCeilingArea += ceilingArea

    total = 0
    details = []
    p = st.session_state.prices

    if insWallArea > 0:
        cost = insWallArea * p['insulationWall']
        total += cost
        details.append(f"단열(벽): {insWallArea:.2f}m² × {p['insulationWall']:,}원 = {int(cost):,}원")

    if insCeilingArea > 0:
        cost = insCeilingArea * p['insulationCeiling']
        total += cost
        details.append(f"단열(천장): {insCeilingArea:.2f}m² × {p['insulationCeiling']:,}원 = {int(cost):,}원")

    if wallpaperArea > 0:
        cost = wallpaperArea * p['wallpaper']
        total += cost
        modeText = "전체" if ins_count >= 2 else "부분"
        details.append(f"도배 ({modeText}): {wallpaperArea:.2f}m² × {p['wallpaper']:,}원 = {int(cost):,}원")

    for i, (w, h) in enumerate(windows):
        area = (w * h) / 1000000
        cost = area * p['window_per_m2']
        total += cost
        details.append(f"창문 {i+1}: {w}×{h}mm ({area:.2f}m²) = {int(cost):,}원")

    for i, thick in enumerate(homeDoors):
        price = p.get(f'homeDoor_{thick}', 350000)
        total += price
        details.append(f"홈도어 {i+1} ({thick}mm): {price:,}원")

    for i, etype in enumerate(entranceDoors):
        price = p.get(f'entrance_{etype}', 700000)
        label = [k for k, v in entrance_options.items() if v == etype][0]
        total += price
        details.append(f"출입문 {i+1} ({label}): {price:,}원")

    if boiler:
        total += p['boiler']
        details.append(f"보일러 설치: {p['boiler']:,}원")
    if oilTank:
        total += p['oilTank']
        details.append(f"기름통 추가: {p['oilTank']:,}원")

    # --- 내륙 지역 결과 표시 ---
    st.header("📊 내륙 견적 결과")
    if total == 0:
        st.info("👆 위 항목들을 입력해주세요")
    else:
        remainder = limit - total
        if remainder < 0:
            st.error(f"⚠️ 예산 초과! (초과 금액: {abs(int(remainder)):,}원)")
        else:
            st.success(f"✅ 예산 내 적정 (남은 잔액: {int(remainder):,}원)")
        st.markdown(f"<h2 style='text-align:center; color:#2563eb;'>총 견적: {int(total):,} 원</h2>", unsafe_allow_html=True)
        with st.container(border=True):
            st.markdown("**세부 산출 내역**")
            for line in details:
                st.markdown(f"- {line}")


else:
    # 🟧🟧🟧🟧🟧🟧🟧🟧🟧🟧🟧🟧🟧🟧🟧🟧🟧🟧🟧🟧🟧🟧🟧🟧🟧🟧🟧
    #                여기서부터 섬 지역(신규) 코드 시작
    # 🟧🟧🟧🟧🟧🟧🟧🟧🟧🟧🟧🟧🟧🟧🟧🟧🟧🟧🟧🟧🟧🟧🟧🟧🟧🟧🟧
    st.subheader("📏 방 기본 치수 (mm)")
    col_w, col_l, col_h = st.columns(3)
    with col_w: room_w = st.number_input("동/서벽 가로", value=3300, step=100, key="is_w")
    with col_l: room_l = st.number_input("남/북벽 가로", value=2500, step=100, key="is_l")
    with col_h: room_h = st.number_input("천장 높이", value=2400, step=100, key="is_h")

    # --- 도배 시공 방식 전역 세팅 ---
    st.subheader("🎨 도배 시공 방식 선택")
    island_wallpaper_mode = st.radio(
        "도배 방식을 먼저 선택해주세요",
        ["도배 안함", "전체도배 (방 전체 5면)", "부분도배 (벽면/천장 개별 선택)"],
        horizontal=True,
        key="is_wp_mode"
    )

    st.subheader("🛠️ 단열/도배 및 제외면적(창호) 선택")
    st.info("시공할 면을 켜고, 해당 벽면에 있는 문/창문을 선택하세요. 제외면적이 단열과 도배에 자동으로 함께 적용됩니다.")

    walls = {
        "동벽체": {"w": room_w, "h": room_h},
        "서벽체": {"w": room_w, "h": room_h},
        "남벽체": {"w": room_l, "h": room_h},
        "북벽체": {"w": room_l, "h": room_h}
    }
    wall_results = {}

    for wall_name, dims in walls.items():
        with st.expander(f"▶ {wall_name} 시공 설정"):
            col1, col2 = st.columns(2)
            with col1:
                do_insul = st.checkbox(f"{wall_name} 단열", key=f"is_insul_{wall_name}")
            with col2:
                # 전체 도배일 때는 강제로 고정, 부분 도배일때는 체크박스 활성화
                if island_wallpaper_mode == "전체도배 (방 전체 5면)":
                    do_wallp = st.checkbox(f"{wall_name} 도배 (전체도배 적용됨)", value=True, disabled=True, key=f"is_wallp_fix_{wall_name}")
                elif island_wallpaper_mode == "부분도배 (벽면/천장 개별 선택)":
                    do_wallp = st.checkbox(f"{wall_name} 도배 선택", key=f"is_wallp_{wall_name}")
                else:
                    do_wallp = False
            
            # 단열이나 도배 중 하나라도 진행하면 제외면적 입력창 활성화
            if do_insul or do_wallp:
                st.write("**제외할 창문/문 선택 (최대 2개)**")
                exc_col1, exc_col2 = st.columns(2)
                with exc_col1:
                    exc1 = st.selectbox("항목 1", list(EXCLUSION_PRESETS.keys()), index=5, key=f"is_exc1_{wall_name}")
                    exc1_val = EXCLUSION_PRESETS[exc1]
                    if exc1 == "사용자 직접 입력":
                        exc1_val = st.number_input("직접입력 (m²)", min_value=0.0, step=0.1, key=f"is_cus1_{wall_name}")
                with exc_col2:
                    exc2 = st.selectbox("항목 2", list(EXCLUSION_PRESETS.keys()), index=5, key=f"is_exc2_{wall_name}")
                    exc2_val = EXCLUSION_PRESETS[exc2]
                    if exc2 == "사용자 직접 입력":
                        exc2_val = st.number_input("직접입력 (m²)", min_value=0.0, step=0.1, key=f"is_cus2_{wall_name}")
                
                base_area = (dims["w"] / 1000) * (dims["h"] / 1000)
                final_area = max(0.0, base_area - exc1_val - exc2_val)
                st.caption(f"✓ {wall_name} 실제 시공 면적: **{final_area:.2f} m²** (기본 {base_area:.2f} - 제외 {exc1_val+exc2_val:.2f})")
                
                wall_results[wall_name] = {
                    "insul": final_area if do_insul else 0,
                    "wallp": final_area if do_wallp else 0
                }
            else:
                wall_results[wall_name] = {"insul": 0, "wallp": 0}

    # --- 천장 설정 ---
    with st.expander("▶ 천장 시공 설정"):
        col1, col2 = st.columns(2)
        with col1: 
            ceiling_insul = st.checkbox("천장 단열", key="is_ceil_ins")
        with col2:
            if island_wallpaper_mode == "전체도배 (방 전체 5면)":
                ceiling_wallp = st.checkbox("천장 도배 (전체도배 적용됨)", value=True, disabled=True, key="is_ceil_wal_fix")
            elif island_wallpaper_mode == "부분도배 (벽면/천장 개별 선택)":
                ceiling_wallp = st.checkbox("천장 도배 선택", key="is_ceil_wal")
            else:
                ceiling_wallp = False
                
        ceiling_area = (room_w / 1000) * (room_l / 1000)
        if ceiling_insul or ceiling_wallp:
            st.caption(f"✓ 천장 면적: **{ceiling_area:.2f} m²**")

    # ==========================================================
    # TODO: 차후 이곳에 섬지역 전용 창문, 방문, 출입문, 보일러 입력 칸을 추가하세요
    # ==========================================================
    st.divider()
    
    # 부가 항목
    ac_add = st.checkbox("에어컨 간이 탈부착 추가 (+10,000원)", key="is_ac")

    st.divider()

    # --- 섬 지역 계산 로직 ---
    p = st.session_state.prices
    total_base = 0
    details = []

    total_wall_insul_area = sum(w["insul"] for w in wall_results.values())
    total_wall_wallp_area = sum(w["wallp"] for w in wall_results.values())

    # 1. 벽체 단열 금액 합산
    if total_wall_insul_area > 0:
        cost = total_wall_insul_area * p.get('island_insulationWall', 45842)
        total_base += cost
        details.append(f"단열(벽체 합산): {total_wall_insul_area:.2f}m² × {p.get('island_insulationWall', 45842):,}원 = {int(cost):,}원")

    # 2. 벽체 도배 금액 합산 (단열 제외면적이 연동된 순수 면적으로 계산됨)
    if total_wall_wallp_area > 0:
        cost = total_wall_wallp_area * p.get('island_wallpaperWall', 12138)
        total_base += cost
        details.append(f"도배(벽체 합산): {total_wall_wallp_area:.2f}m² × {p.get('island_wallpaperWall', 12138):,}원 = {int(cost):,}원")

    # 3. 천장 단열 금액 합산
    if ceiling_insul:
        cost = ceiling_area * p.get('island_insulationCeiling', 51139)
        total_base += cost
        details.append(f"단열(천장): {ceiling_area:.2f}m² × {p.get('island_insulationCeiling', 51139):,}원 = {int(cost):,}원")

    # 4. 천장 도배 금액 합산
    if ceiling_wallp:
        cost = ceiling_area * p.get('island_wallpaperCeiling', 12105)
        total_base += cost
        details.append(f"도배(천장): {ceiling_area:.2f}m² × {p.get('island_wallpaperCeiling', 12105):,}원 = {int(cost):,}원")

    # 5. 에어컨 비용
    if ac_add:
        total_base += p.get('island_ac_reattach', 10000)
        details.append(f"에어컨 간이 탈부착: {p.get('island_ac_reattach', 10000):,}원")

    # ==========================================================
    # TODO: 차후 이곳에 섬지역 전용 창문, 방문, 보일러 금액 합산 로직을 추가하세요
    # ==========================================================

    # 공통 내역 (면적 비례 근사치 + 고정 경비)
    total_area = total_wall_insul_area + (ceiling_area if ceiling_insul else 0)
    if total_base > 0:
        transport = total_area * 1888
        waste = total_area * 1510
        common_total = transport + waste + p.get('island_expense_fixed', 34433)
        total_base += common_total
        details.append(f"공통내역(소운반+폐자재+경비): {int(common_total):,}원")

    # --- 섬 지역 결과 표시 ---
    st.header("📊 섬지역 견적 결과")
    if total_base == 0:
        st.info("👆 시공할 벽면과 항목을 선택해주세요.")
    else:
        # 역산 데이터 기준: 섬할증 38.3%, 간접비 11.8%
        island_surcharge = total_base * 0.383
        indirect_cost = (total_base + island_surcharge) * 0.118
        grand_total = total_base + island_surcharge + indirect_cost
        
        st.markdown(f"<h2 style='text-align:center; color:#e11d48;'>섬지역 총 지원금액: {int(grand_total):,} 원</h2>", unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        col1.metric("순수 공사합계", f"{int(total_base):,}원")
        col2.metric("도서 할증", f"{int(island_surcharge):,}원")
        col3.metric("간접비", f"{int(indirect_cost):,}원")

        with st.container(border=True):
            st.markdown(f"**세부 산출 내역 ({island_wallpaper_mode})**")
            for line in details:
                st.markdown(f"- {line}")
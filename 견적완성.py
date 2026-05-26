import streamlit as st
import json
import math

# ==================== 관공서 실제 서류 및 표준 단가 세팅 ====================
DEFAULT_PRICES = {
    # 1. 단열 및 도배
    'insulation_mat': 9394, 'insulation_lab': 32965, 'insulation_exp': 192,
    'wallpaper_mat': 3378, 'wallpaper_lab': 6662, 'wallpaper_exp': 0,
    'skirting_mat': 1240, 'skirting_lab': 3060, 'skirting_exp': 183,
    
    # 2. 창호 (서류상 규격별 단가)
    'win1_mat': 390521, 'win1_lab': 70420, 'win1_exp': 1408, # 1150*1000
    'win2_mat': 390227, 'win2_lab': 70420, 'win2_exp': 1408, # 1220*1000
    'win3_mat': 355840, 'win3_lab': 56932, 'win3_exp': 1138, # 1090*890
    
    # 창호 부자재 (내외면 양면 시공 반영)
    'urethane_mat': 1650, 'urethane_lab': 2602,
    'sealing_mat': 576 * 2, 'sealing_lab': 5015 * 2,
    'molding_mat': 1048 * 2, 'molding_lab': 8234 * 2, 'molding_exp': 340 * 2,
    'demolish_lab': 13508, # 창짝 철거 (4개 기준)
    
    # 3. 공통 경비 (바닥면적 기준)
    'transport_exp': 4036, 'cleaning_exp': 3229,
    'furniture_exp': 31309, # 가구 운반비
    
    # 4. 문 및 보일러
    'homeDoor_110': 300000, 'homeDoor_120': 350000, 'homeDoor_130': 400000, 'homeDoor_150': 480000,
    'entrance_hinge': 700000, 'entrance_hinge_fix': 900000, 'entrance_sliding': 800000,
    'boiler': 1000000, 'oilTank': 200000,
    
    # 5. 관공서 고정 경비 및 진단비
    'exp_견적': 34433, 'exp_조사': 22955, 'exp_컨설팅': 57388,
    'diagnostic_fee': 114776,
    
    # 6. 고정 간접비 요율 매칭용 기본값
    'gov_sanjae': 24775, 'gov_gwanli': 34376, 'gov_iyun': 58211           
}

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

if 'prices' not in st.session_state:
    st.session_state.prices = load_prices()

p = st.session_state.prices

st.set_page_config(page_title="온성 견적 마스터 (통합형)", page_icon="🏗️", layout="centered")
st.markdown("<h1 style='text-align: center;'>🏗️ 온성 견적 산출기 (통합 원스톱)</h1>", unsafe_allow_html=True)
st.caption("※ 단열, 창호, 보일러 등 모든 공종을 한 화면에서 입력하여 자재비 포함 최종 총액을 산출합니다.")

# ==================== 메인 입력 섹션 ====================
is_island = st.checkbox("🏝️ 섬지역 현장 적용 (노무비 50% 할증)", value=True)

st.divider()

st.subheader("📏 1. 단열 및 기본 공사")
c1, c2, c3 = st.columns(3)
with c1: ins_area = st.number_input("단열 면적 (㎡)", value=6.96, step=0.01)
with c2: wp_area = st.number_input("도배 면적 (㎡)", value=6.96, step=0.01)
with c3: sk_len = st.number_input("걸레받이 길이 (m)", value=2.90, step=0.01)
base_floor_area = st.number_input("기본 바닥 면적 (㎡) (소운반/청소용)", value=2.90, step=0.01)

st.subheader("🪟 2. 창호(창문) 교체")
win_count = st.selectbox("시공할 창문 개수", [0, 1, 2, 3, 4, 5])
windows = []
for i in range(win_count):
    with st.container(border=True):
        st.markdown(f"**창문 {i+1}**")
        wc1, wc2, wc3 = st.columns(3)
        with wc1:
            w_type = st.selectbox(f"규격", ["1150 x 1000", "1220 x 1000", "1090 x 890"], key=f"wt_{i}")
        with wc2:
            w_len = st.number_input(f"창틀 연장 길이 (m)", value=4.30, step=0.01, key=f"wl_{i}")
        with wc3:
            w_floor = st.number_input(f"해당 방 바닥 면적 (㎡)", value=4.03, step=0.01, key=f"wf_{i}")
        w_furn = st.checkbox(f"장롱 가구 운반비 추가", key=f"wu_{i}")
        windows.append({"type": w_type, "len": w_len, "floor": w_floor, "furn": w_furn})

st.subheader("🚪 3. 문 및 보일러")
bc1, bc2 = st.columns(2)
with bc1:
    homeDoorCount = st.selectbox("방문(홈도어) 개수", [0, 1, 2])
    hd_list = [st.selectbox(f"방문 {i+1} 두께", ["110", "120", "130", "150"], index=1, key=f"hd_{i}") for i in range(homeDoorCount)]
    
    entranceDoorCount = st.selectbox("현관문(출입문) 개수", [0, 1, 2])
    ent_options = {"여닫이 (기본)": "hinge", "여닫이 + 픽스창": "hinge_fix", "미닫이": "sliding"}
    ed_list = [st.selectbox(f"현관문 {i+1} 종류", list(ent_options.keys()), key=f"ed_{i}") for i in range(entranceDoorCount)]

with bc2:
    st.markdown("<br>", unsafe_allow_html=True)
    boiler = st.checkbox("🔥 보일러 교체 설치")
    oilTank = st.checkbox("🛢️ 보일러 기름통 추가", disabled=not boiler)

st.divider()

# ==================== 정밀 연산 로직 ====================
total_mat, total_lab, total_exp = 0, 0, 0

# 1. 단열 공사 누적
total_mat += math.floor(ins_area * p['insulation_mat']) + math.floor(wp_area * p['wallpaper_mat']) + math.floor(sk_len * p['skirting_mat'])
total_lab += math.floor(ins_area * p['insulation_lab']) + math.floor(wp_area * p['wallpaper_lab']) + math.floor(sk_len * p['skirting_lab'])
total_exp += math.floor(ins_area * p['insulation_exp']) + math.floor(wp_area * p['wallpaper_exp']) + math.floor(sk_len * p['skirting_exp'])
total_exp += math.floor(base_floor_area * p['transport_exp']) + math.floor(base_floor_area * p['cleaning_exp'])

# 2. 창호 공사 누적
for w in windows:
    if "1150" in w['type']: prefix = 'win1'
    elif "1220" in w['type']: prefix = 'win2'
    else: prefix = 'win3'
    
    # 창문 본체
    total_mat += p[f'{prefix}_mat']
    total_lab += p[f'{prefix}_lab']
    total_exp += p[f'{prefix}_exp']
    
    # 부자재 (폼, 씰링, 몰딩)
    total_mat += math.floor(w['len'] * p['urethane_mat']) + math.floor(w['len'] * p['sealing_mat']) + math.floor(w['len'] * p['molding_mat'])
    total_lab += math.floor(w['len'] * p['urethane_lab']) + math.floor(w['len'] * p['sealing_lab']) + math.floor(w['len'] * p['molding_lab'])
    total_exp += math.floor(w['len'] * p['molding_exp'])
    
    # 철거 및 경비
    total_lab += p['demolish_lab']
    total_exp += math.floor(w['floor'] * p['transport_exp']) + math.floor(w['floor'] * p['cleaning_exp'])
    if w['furn']: total_exp += p['furniture_exp']

# 3. 문 공사 누적 (자재 7 : 노무 3 비율 유추 적용)
for thick in hd_list:
    door_price = p.get(f'homeDoor_{thick}', 350000)
    total_mat += math.floor(door_price * 0.7)
    total_lab += math.floor(door_price * 0.3)
for etype in ed_list:
    ent_price = p.get(f'entrance_{ent_options[etype]}', 700000)
    total_mat += math.floor(ent_price * 0.7)
    total_lab += math.floor(ent_price * 0.3)

# 4. 보일러 누적
if boiler:
    total_mat += math.floor(p['boiler'] * 0.7)
    total_lab += math.floor(p['boiler'] * 0.3)
if oilTank:
    total_mat += math.floor(p['oilTank'] * 0.8)
    total_lab += math.floor(p['oilTank'] * 0.2)

# ==================== 할증 및 간접비 연산 ====================
direct_total = total_mat + total_lab + total_exp
fixed_expenses = p['exp_견적'] + p['exp_조사'] + p['exp_컨설팅']

# 섬지역 할증 (총 노무비 + 고정경비의 50%)
base_labor_for_island = total_lab + fixed_expenses
island_surcharge = math.floor(base_labor_for_island * 0.5) if is_island else 0

# 제간접비 (서류 요율 기반 비례 산출)
# 기준점: 총 직접비+고정경비가 커질수록 비례해서 증가하도록 설정
sanjae = math.floor(total_lab * 0.0305) # 관공서 노무비 대비 대략 3.05%
gwanli = math.floor((direct_total + fixed_expenses + island_surcharge) * 0.055) # 대략 5.5%
iyun = math.floor((direct_total + fixed_expenses + island_surcharge) * 0.085) # 대략 8.5%
indirect_sum = sanjae + gwanli + iyun

# 최종 총계
grand_total = direct_total + fixed_expenses + island_surcharge + indirect_sum + p['diagnostic_fee']

# ==================== 결과 출력 ====================
st.header("📊 통합 총 공사 금액 (자재비 포함)")

st.markdown(f"<h2 style='text-align:center; color:#2563eb; font-size: 2.5rem;'>최종 총계: {grand_total:,} 원</h2>", unsafe_allow_html=True)
st.caption("<div style='text-align:center;'>※ 재단 공급자재, 시공업체 계약금 구분 없이 전체 자재비와 시공비가 모두 합산된 금액입니다.</div>", unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    with st.container(border=True):
        st.markdown("### 🧱 직접 공사비")
        st.write(f"- 총 자재비: **{total_mat:,} 원**")
        st.write(f"- 총 노무비: **{total_lab:,} 원**")
        st.write(f"- 총 경비: **{total_exp:,} 원**")
        st.divider()
        st.write(f"**직접비 소계: {direct_total:,} 원**")

with col2:
    with st.container(border=True):
        st.markdown("### 🔒 공통/할증 및 간접비")
        st.write(f"- 공통 고정경비(3종): **{fixed_expenses:,} 원**")
        st.write(f"- 🏝️ 도서 노무할증(50%): **{island_surcharge:,} 원**")
        st.write(f"- 📊 제간접비 합계: **{indirect_sum:,} 원**")
        st.caption(f" (산재 {sanjae:,} / 관리 {gwanli:,} / 이윤 {iyun:,})")
        st.write(f"- 📋 재단 진단비: **{p['diagnostic_fee']:,} 원**")
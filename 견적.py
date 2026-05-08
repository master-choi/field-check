import streamlit as st

# 페이지 설정 (스마트폰에서 크게 보이도록)
st.set_page_config(page_title="현장 견적 마스터", layout="centered")

# --- [단가 설정: 사장님이 여기서 직접 수정하세요] ---
prices = {
    "단열": 100000,    # 1m2당
    "도배": 30000,     # 1m2당
    "창문": 408163,    # 1m2당 (1400x1400 기준 80만원)
    "보일러": 800000,  # 기본 설치비
    "기름통": 200000   # 추가 비용
}

st.title("🏗️ 현장 견적 산출기")
st.write("치수를 입력하면 자동으로 총액이 계산됩니다.")

# 1. 예산 한도 설정
limit = st.number_input("💰 공사 한도 금액 (원)", value=10000000, step=100000)

st.divider()

# 2. 기본 치수 입력
st.subheader("📏 기본 치수 (mm)")
col1, col2, col3 = st.columns(3)
with col1:
    h = st.number_input("천장높이", value=2200)
with col2:
    w = st.number_input("방 가로", value=0)
with col3:
    l = st.number_input("방 세로", value=0)

# 3. 단열 면 선택
st.subheader("🏠 단열/도배 면 선택")
cols = st.columns(3)
w1 = cols[0].checkbox("벽체 1면")
w2 = cols[1].checkbox("벽체 2면")
w3 = cols[2].checkbox("벽체 3면")
w4 = cols[0].checkbox("벽체 4면")
ceil = cols[1].checkbox("천장")

# 4. 추가 품목
st.subheader("🚪 창호 및 보일러")
cw, ch = st.columns(2)
win_w = cw.number_input("창문 가로(mm)", value=1400)
win_h = ch.number_input("창문 세로(mm)", value=1400)

boiler = st.checkbox("보일러 설치")
oil_tank = st.checkbox("보일러 기름통 추가")

# --- 계산 로직 ---
total_price = 0
ins_area = 0

# 선택된 면적 합산 (mm -> m 변환)
h_m, w_m, l_m = h/1000, w/1000, l/1000
areas = [w_m * h_m, l_m * h_m, w_m * h_m, l_m * h_m]
checks = [w1, w2, w3, w4]

for i, checked in enumerate(checks):
    if checked:
        ins_area += areas[i]
if ceil:
    ins_area += (w_m * l_m)

# 금액 합산
total_price += ins_area * (prices["단열"] + prices["도배"])
total_price += (win_w * win_h / 1000000) * prices["창문"]
if boiler: total_price += prices["boiler"]
if oil_tank: total_price += prices["oil_tank"]

# --- 결과 표시 ---
st.divider()
remainder = limit - total_price

if remainder < 0:
    st.error(f"⚠️ 예산 초과! (초과금액: {abs(remainder):,.0f}원)")
else:
    st.success(f"✅ 예산 내 적정 (남은잔액: {remainder:,.0f}원)")

st.metric(label="총 합계 금액", value=f"{total_price:,.0f} 원")
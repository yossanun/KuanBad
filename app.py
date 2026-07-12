import streamlit as st
import random

# 1. ตั้งค่าหน้าเว็บ
st.set_page_config(page_title="Badminton Queue Matcher", layout="wide")
st.title("🏸 Badminton Queue Matcher")

# 2. เตรียมระบบจำข้อมูลชั่วคราว (Session State)
if "players" not in st.session_state:
    st.session_state.players = []  # รายชื่อสมาชิกทั้งหมด
if "courts" not in st.session_state:
    st.session_state.courts = {}   # สถานะของแต่ละสนาม เช่น {1: ["A", "B", "C", "D"]}
if "num_courts" not in st.session_state:
    st.session_state.num_courts = 1

# 3. ส่วนควบคุมด้านซ้าย (Sidebar) - จัดการสมาชิกและสนาม
with st.sidebar:
    st.header("⚙️ ตั้งค่าก๊วน")
    
    # เพิ่มจำนวนคอร์ท
    num_courts = st.number_input("จำนวนสนามที่มี:", min_value=1, max_value=15, value=st.session_state.num_courts)
    if num_courts != st.session_state.num_courts:
        st.session_state.num_courts = num_courts
        # อัปเดตจำนวนสนามในระบบ
        for i in range(1, num_courts + 1):
            if i not in st.session_state.courts:
                st.session_state.courts[i] = []
    
    st.write("---")
    
    # เพิ่มชื่อสมาชิก
    new_player = st.text_input("ใส่ชื่อสมาชิก:", key="player_input")
    if st.button("➕ เพิ่มคน") and new_player:
        if new_player not in st.session_state.players:
            st.session_state.players.append(new_player)
            st.rerun()

    # แสดงรายชื่อคนทั้งหมดในก๊วน และเพิ่มปุ่มลบชื่อคนออกจากก๊วนได้ด้วย
    st.write("📋 **รายชื่อคนในก๊วนทั้งหมด:**")
    for idx, p in enumerate(st.session_state.players):
        col_p, col_del = st.columns([4, 1])
        with col_p:
            st.write(f"- {p}")
        with col_del:
            if st.button("❌", key=f"del_p_{idx}"):
                st.session_state.players.remove(p)
                # ถ้าคนนี้อยู่บนสนามให้เอาออกด้วย
                for c_id in st.session_state.courts:
                    if p in st.session_state.courts[c_id]:
                        st.session_state.courts[c_id].remove(p)
                st.rerun()

# 4. ส่วนแสดงผลหลัก (Main Content)
# คำนวณหาคนที่กำลัง "รออยู่ (Waiting)"
players_on_courts = []
for p_list in st.session_state.courts.values():
    players_on_courts.extend(p_list)

waiting_list = [p for p in st.session_state.players if p not in players_on_courts]

# ปุ่มสุ่มคนลงสนาม
st.subheader("🎲 ระบบจัดคนลงสนาม")
if st.button("🚀 สุ่มคนลงสนามที่ว่าง", type="primary"):
    for c_id in range(1, st.session_state.num_courts + 1):
        current_players = st.session_state.courts.get(c_id, [])
        spots_needed = 4 - len(current_players)
        
        if spots_needed > 0 and len(waiting_list) >= spots_needed:
            chosen_players = random.sample(waiting_list, spots_needed)
            st.session_state.courts[c_id] = current_players + chosen_players
            for p in chosen_players:
                waiting_list.remove(p)
                
    st.rerun()

# แสดงผลรายชื่อคนที่กำลังรอ (Waiting List)
st.write(f"⏳ **คนที่กำลังรอลงสนาม ({len(waiting_list)} คน):**")
if waiting_list:
    st.info(", ".join(waiting_list))
else:
    st.write("ไม่มีคนรอ ทุกคนกำลังเล่นอยู่ หรือยังไม่ได้เพิ่มชื่อ")

st.write("---")

# 5. แสดงผลหน้าจอของแต่ละสนาม (เพิ่มระบบแก้ไขคนในสนาม)
st.subheader("🏟️ สถานะสนาม")
cols = st.columns(st.session_state.num_courts)

for idx, c_id in enumerate(range(1, st.session_state.num_courts + 1)):
    with cols[idx]:
        st.markdown(f"### 🏸 สนามที่ {c_id}")
        court_players = st.session_state.courts.get(c_id, [])
        
        # ค้นหาว่าใครบ้างที่มีสิทธิ์ลงสนามนี้ได้ = คนที่อยู่บนสนามนี้อยู่แล้ว + คนที่ยังว่างอยู่ (Waiting)
        # วิธีนี้จะทำให้เราไม่สามารถเลือกคนที่กำลังเล่นอยู่นามอื่นมาซ้ำได้
        available_choices = court_players + waiting_list
        
        # ใช้ multiselect เพื่อให้แก้ไขรายชื่อบนสนามได้แบบ Real-time
        updated_court_players = st.multiselect(
            "คนบนสนาม (สูงสุด 4 คน):",
            options=available_choices,
            default=court_players,
            key=f"court_select_{c_id}",
            max_selections=4
        )
        
        # ถ้ามีการเปลี่ยนแปลงรายชื่อในสลอต ให้กดเซฟอัปเดตสถานะ
        if updated_court_players != court_players:
            st.session_state.courts[c_id] = updated_court_players
            st.rerun()
            
        # แสดงสถานะสีเพื่อให้ดูง่าย
        if len(updated_court_players) == 4:
            st.warning("⚠️ สนามเต็ม (กำลังแข่ง)")
        elif len(updated_court_players) > 0:
            st.info(f"⏳ ขาดอีก {4 - len(updated_court_players)} คน")
        else:
            st.success("🟢 สนามว่าง")
            
        # ปุ่มเมื่อเล่นเสร็จ (เคลียร์สนาม)
        if st.button(f"🏁 เล่นเสร็จแล้ว (สนาม {c_id})", key=f"clear_{c_id}", use_container_width=True):
            st.session_state.courts[c_id] = []
            st.rerun()
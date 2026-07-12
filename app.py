import streamlit as st
import random

# 1. ตั้งค่าหน้าเว็บ
st.set_page_config(page_title="Badminton Queue Matcher", layout="wide")
st.title("🏸 Badminton Queue Matcher")

# 🛠️ เทคนิคพิเศษ: ใส่ CSS เพื่อแปลงกล่องข้อความธรรมดาให้กลืนไปกับตัวหนังสือหัวข้อสนาม
st.markdown("""
    <style>
    div[data-testid="stTextInput"] div[data-custom-style="court-title"] input {
        font-size: 24px !important;
        font-weight: bold !important;
        background-color: transparent !important;
        border: none !important;
        border-bottom: 2px dashed #ccc !important; /* ทำเส้นปรุบางๆ ด้านล่างเพื่อให้รู้ว่าคลิกแก้ได้ */
        padding: 0px !important;
        color: inherit !important;
    }
    div[data-testid="stTextInput"] div[data-custom-style="court-title"] input:focus {
        border-bottom: 2px solid #ff4b4b !important; /* เวลาคลิกพิมพ์ ให้เส้นเปลี่ยนเป็นสีเด่น */
        box-shadow: none !important;
    }
    </style>
""", unsafe_allow_html=True)

# 2. เตรียมระบบจำข้อมูลชั่วคราว (Session State)
if "players" not in st.session_state:
    st.session_state.players = []  # รายชื่อสมาชิกทั้งหมด
if "courts" not in st.session_state:
    st.session_state.courts = {}   # สถานะของแต่ละสนาม เช่น {1: ["A", "B", "C", "D"]}
if "num_courts" not in st.session_state:
    st.session_state.num_courts = 1
# 💡 เตรียมที่เก็บชื่อสนามในระบบ (Default เป็น สนามที่ 1, สนามที่ 2, ...)
if "court_names" not in st.session_state:
    st.session_state.court_names = {i: f"สนามที่ {i}" for i in range(1, 16)}

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
    st.caption("💡 สามารถแก้ไขชื่อผู้เล่นได้จากกล่องข้อความด้านล่าง")

    for idx, p in enumerate(st.session_state.players):
        col_idx, col_p, col_del = st.columns([1, 4, 1.5])
        with col_idx:
            st.write(f"{idx + 1}.")
        with col_p:
            edited_name = st.text_input(f"Edit player {idx}", value=p, key=f"edit_player_input_{idx}", label_visibility="collapsed")
            if edited_name != p and edited_name.strip() != "":
                st.session_state.players[idx] = edited_name
                for c_id in st.session_state.courts:
                    if p in st.session_state.courts[c_id]:
                        c_idx = st.session_state.courts[c_id].index(p)
                        st.session_state.courts[c_id][c_idx] = edited_name
                st.rerun()
        with col_del:
            if st.button("❌", key=f"del_p_{idx}"):
                st.session_state.players.remove(p)
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

# 5. แสดงผลหน้าจอของแต่ละสนาม (เวอร์ชัน Inline แก้ไขที่หัวข้อสนามได้โดยตรง)
st.subheader("🏟️ สถานะสนาม")
cols = st.columns(st.session_state.num_courts)

for idx, c_id in enumerate(range(1, st.session_state.num_courts + 1)):
    with cols[idx]:
        # ดึงชื่อสนามปัจจุบันออกมา ถ้ายังไม่มีข้อความ 🏸 นำหน้า ให้ใส่เข้าไปเพื่อให้ UI สวยงาม
        current_court_name = st.session_state.court_names.get(c_id, f"สนามที่ {c_id}")
        if not current_court_name.startswith("🏸"):
            current_court_name = f"🏸 {current_court_name}"

        # 💡 ยุบรวมช่องกรอกให้กลายเป็นหัวข้อในตัวเดียวผ่าน Container และ CSS
        with st.container():
            edited_court_name = st.text_input(
                f"Edit court {c_id}",
                value=current_court_name,
                key=f"edit_court_input_{c_id}",
                label_visibility="collapsed"  # ซ่อน Label เพื่อความสะอาดตา
            )
            # ฉีดระบุตัวตนพิเศษ เพื่อให้ CSS ด้านบนเข้ามาลบกรอบสีขาวออก
            st.markdown(f'<div data-custom-style="court-title"></div>', unsafe_allow_html=True)
        
        # ถ้ายูสเซอร์คลิกพิมพ์เปลี่ยนชื่อสนามตรงหัวข้อแล้วกด Enter
        if edited_court_name != current_court_name and edited_court_name.strip() != "":
            st.session_state.court_names[c_id] = edited_court_name
            st.rerun()
            
        st.write("") # เติมเว้นวรรคช่องไฟเล็กน้อยแทน
        
        if c_id not in st.session_state.courts:
            st.session_state.courts[c_id] = []

        court_players = st.session_state.courts.get(c_id, [])
        
        # ค้นหาว่าใครบ้างที่มีสิทธิ์ลงสนามนี้ได้ = คนที่อยู่บนสนามนี้อยู่แล้ว + คนที่ยังว่างอยู่ (Waiting)
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

        # ชื่อบนปุ่ม "เล่นเสร็จแล้ว" จะอัปเดตเปลี่ยนตามชื่อสนามที่เราตั้งแบบเรียลไทม์
        if st.button(f"🏁 เล่นเสร็จแล้ว ({st.session_state.court_names[c_id]})", key=f"clear_{c_id}", use_container_width=True):
            st.session_state.courts[c_id] = []
            st.rerun()
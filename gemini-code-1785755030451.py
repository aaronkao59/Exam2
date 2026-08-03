import streamlit as st
import random
import json
import os

APP_VERSION = "v3.1.2 (Warm UI Edition)"

# 💻 10-3.介面視覺架構 (UIUX-CRF v9.0): 定義暖色系色彩變數
# 琥珀色 Amber 600: #D97706 (主色調)
# 琥珀色 Amber 50:  #FFFBEB (淺背景色)
# 橘色 Orange 100:  #FFEDD5 (卡片背景)
# 棕色 Stone 700:   #44403C (文字色)

st.set_page_config(
    page_title="中高級認證 - 阿美語學習認證", 
    page_icon="🎓", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

# 注入 CSS 以完全覆蓋 Streamlit 預設風格為暖色調
st.markdown("""
    <style>
    /* 全域背景與文字顏色調整 */
    .stApp {
        background-color: #FFFBEB; /* Amber 50 - 極淺琥珀色背景 */
        color: #44403C; /* Stone 700 - 深棕色文字，較柔和 */
    }

    /* 💡 [10-3: 第一支柱] 測驗卡片視覺優化 */
    .quiz-card {
        background-color: #FFEDD5; /* Orange 100 - 淺橘色卡片背景 */
        padding: 28px; border-radius: 20px;
        border: 2px solid #FDBA74; /* Orange 300 - 卡片邊框 */
        box-shadow: 0 6px 16px rgba(194, 65, 12, 0.1); /* 帶有橘色的柔和陰影 */
        margin-top: 20px; margin-bottom: 30px;
    }

    /* 標題顏色調整 (h1, h2, h3) - 統一使用琥珀色 Amber 700 */
    h1, h2, h3 { 
        color: #B45309 !important; /* Amber 700 */
    }
    h1 { font-weight: 800 !important; }

    /* 深色模式適配 (暖色系 dark mode) */
    @media (prefers-color-scheme: dark) {
        .stApp { background-color: #1C1917; color: #E7E5E4; } /* Stone 背景與文字 */
        .quiz-card {
            background-color: #292524; /*深Stone */
            border: 2px solid #854D0E; /* Amber 800 */
            box-shadow: 0 6px 16px rgba(0, 0, 0, 0.3);
        }
        h1, h2, h3 { color: #FBBF24 !important; } /* Amber 400 */
    }

    /* Streamlit 原生元件客製化 */
    
    /* 1. 警告框 (stAlert/stSuccess/stError) */
    .stAlert { border-radius: 14px !important; border: none !important; }
    div[data-testid="stAlert"] { background-color: #FEF3C7 !important; color: #92400E !important; border: 1px solid #FCD34D !important; } /* Success 統一用暖黃 */

    /* 2. 分段控制 (stSegmentedControl) */
    div[data-testid="stSegmentedControl"] button {
        border-color: #F59E0B !important; /* Amber 500 */
        color: #B45309 !important; /* Amber 700 */
    }
    div[data-testid="stSegmentedControl"] button[aria-selected="true"] {
        background-color: #F59E0B !important; /* Amber 500 */
        color: white !important;
    }

    /* 3. 按鈕 (stButton) - 預設按鈕 */
    .stButton>button {
        border-radius: 12px !important;
        background-color: white;
        border: 2px solid #F59E0B !important; /* Amber 500 */
        color: #B45309 !important; /* Amber 700 */
        font-weight: 600;
        transition: all 0.2s;
    }
    .stButton>button:hover {
        background-color: #FFFBEB; /* Amber 50 */
        border-color: #D97706 !important; /* Amber 600 */
        box-shadow: 0 2px 5px rgba(217, 119, 6, 0.2);
    }
    
    /* 表單提交按鈕 (特別強調) */
    div[data-testid="stFormSubmitButton"] button {
        background-color: #F59E0B !important; /* Amber 500 */
        color: white !important;
        border: none !important;
    }
    div[data-testid="stFormSubmitButton"] button:hover {
        background-color: #D97706 !important; /* Amber 600 */
    }

    /* 4. 單選框/複選框 (stRadio/stCheckbox) */
    div[data-testid="stRadio"] label, div[data-testid="stCheckbox"] label { color: #44403C !important; }
    div[data-testid="stRadio"] label[data-baseweb="radio"] div:first-child { border-color: #F59E0B !important; } /* 未選中邊框 */
    div[data-testid="stRadio"] label[data-baseweb="radio"] div[aria-checked="true"] { background-color: #F59E0B !important; } /* 選中填充 */

    /* 5. 滑塊 (stSlider) */
    div[data-testid="stSlider"] div[data-baseweb="slider"] div { background-color: #FBBF24 !important; } /* 滑軌 */
    div[data-testid="stSlider"] div[data-baseweb="slider"] div[role="slider"] { background-color: #D97706 !important; border: 2px solid white !important; } /* 滑塊 */

    /* 6. 折疊面板 (stExpander) */
    .stExpander { border-radius: 14px !important; border: 1px solid #FDBA74 !important; background-color: white !important; }

    /* 修復 HorizontalBlock */
    div[data-testid="stHorizontalBlock"] { background: transparent !important; border: none !important; box-shadow: none !important; }
    </style>
""", unsafe_allow_html=True)

# --- 核心邏輯 (保持不變) ---

@st.cache_data(show_spinner=False)
def load_json_data(file_path):
    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []

# 預載入全域題庫防腐層
DB_DIALOGUE = load_json_data("data/listening_dialogue.json")
DB_SPEAKING_READ = load_json_data("data/speaking_quiz.json")
DB_SPEAKING_QA = load_json_data("data/speaking_situations.json")
DB_SPEAKING_IMG = load_json_data("data/speaking_images.json")
DB_READING = load_json_data("data/reading_quiz.json")
DB_WRITING = load_json_data("data/writing_quiz.json")

# 聽音選詞固定的題庫 (範例)
QUIZ_DATA_WORDS = [
    {"id": 1, "audio_path": "assets/audio/01_listening/listening_words/tengil-a1-01.mp3", "question_text": "聆聽音檔，選出關聯的詞彙：", "options": ["riyar", "'alo", "fanaw", "sa'owac"], "correct_text": "riyar"},
    {"id": 2, "audio_path": "assets/audio/01_listening/listening_words/tengil-a1-02.mp3", "question_text": "聆聽音檔，選出關聯的詞彙：", "options": ["korkor", "rohayan", "romakat", "rotarot"], "correct_text": "romakat"},
    {"id": 3, "audio_path": "assets/audio/01_listening/listening_words/tengil-a1-03.mp3", "question_text": "聆聽音檔，選出關聯的詞彙：", "options": ["hadhad", "hakhak", "hawan", "hafay"], "correct_text": "hafay"},
    {"id": 4, "audio_path": "assets/audio/01_listening/listening_words/tengil-a1-04.mp3", "question_text": "聆聽音檔，選出關聯的詞彙：", "options": ["tefo'", "'okoy", "tafokod", "tafolod"], "correct_text": "tafokod"},
    {"id": 5, "audio_path": "assets/audio/01_listening/listening_words/tengil-a1-05.mp3", "question_text": "聆聽音檔，選出關聯的詞彙：", "options": ["fakar", "tayhi", "pitaw", "tarakar"], "correct_text": "pitaw"}
]

# --- 介面渲染 ---

# 🛡️ 介面視覺架構 (UIUX-CRF): 標題顏色已透過 CSS 轉為琥珀色
st.title("🎓 中高級認證練習平台")
st.caption("Amis Language Proficiency Test - Mid-High Level Practice")

main_options = ["📋 認證考試說明", "🎧 聽力", "🗣️ 口說", "📖 閱讀", "✍️ 寫作"]
# 💡 UI 控制項已轉為暖琥珀色
current_tab = st.segmented_control("主選單導覽", main_options, default="🎧 聽力", label_visibility="collapsed")

if current_tab == "📋 認證考試說明":
    st.subheader("📋 認證考試說明")
    st.divider()
    with st.expander("1. 詞彙範圍/參考教材", expanded=False):
        st.markdown("* **詞彙範圍：** 學習詞表1至800詞，以及其衍生詞。\n* **參考教材：** 包含（第1階至第9階）教材、生活會話篇、閱讀書寫篇。")
    with st.expander("2. 測驗架構/題型配分", expanded=False):
        st.caption("中高級認證總分為100分，[聽力(20分)/口說(30分)/閱讀(30分)/寫作(20分)四個項目]")
        st.markdown("* **聽力測驗** (聽音選詞, 對話理解)\n* **口說測驗** (段落朗讀, 情境問答, 看圖表達)\n* **閱讀測驗** (詞彙語意, 語言結構)\n* **寫作測驗** (句子聽寫, 問答題)")
    with st.expander("3. 合格標準", expanded=False):
        st.markdown("總分達60分以上，且單項成績達聽力15分、口說15分、閱讀18分、寫作12分以上。")

elif current_tab == "🎧 聽力":
    st.subheader("🎧 聽力測驗 (pitengil)")
    st.divider()
    # 💡 Radio 元件已轉為琥珀色風格
    sub_tab = st.radio("題型選擇：", ["選擇題-聽音選詞", "選擇題-對話理解"], horizontal=True)
    
    if sub_tab == "選擇題-聽音選詞":
        st.markdown('<div class="quiz-card">', unsafe_allow_html=True)
        
        if "lw_ptr" not in st.session_state: 
            st.session_state.lw_ptr = 0
        if "lw_order" not in st.session_state or len(st.session_state.lw_order) != len(QUIZ_DATA_WORDS):
            st.session_state.lw_order = list(range(len(QUIZ_DATA_WORDS)))
            random.shuffle(st.session_state.lw_order)
            
        ptr = st.session_state.lw_ptr
        if ptr < len(QUIZ_DATA_WORDS):
            quiz = QUIZ_DATA_WORDS[st.session_state.lw_order[ptr]]
            st.write(f"**[當前進度：第 {ptr + 1} 題 / 共 {len(QUIZ_DATA_WORDS)} 題]**")
            st.write(quiz["question_text"])
            
            # 💡 Audio 元件 Streamlit 無法通過 CSS 深度客製，保持原樣但周圍視覺已轉暖
            if os.path.exists(quiz["audio_path"]):
                st.audio(quiz["audio_path"], format="audio/mp3")
            else:
                st.warning(f"⚠️ 找不到音檔：`{quiz['audio_path']}`")
                
            # 💡 Form 按鈕已轉為琥珀色填充
            with st.form(key=f"lw_form_{ptr}"):
                opts = quiz["options"].copy()
                if f"lw_opts_{ptr}" not in st.session_state:
                    random.shuffle(opts)
                    st.session_state[f"lw_opts_{ptr}"] = opts
                
                choice = st.radio("答案選項：", st.session_state[f"lw_opts_{ptr}"], index=None)
                submit = st.form_submit_button("📥 提交答案")
                
                # 💡 Success 提示框已轉為暖黃色調
                if submit:
                    if choice == quiz["correct_text"]:
                        st.success(f"✓ Fangcal! 正確答案：**{quiz['correct_text']}**")
                    else:
                        st.error(f"✕ 再接再厲！正確答案：**{quiz['correct_text']}**")
            
            # 💡 下一題按鈕已轉為琥珀色外框
            if st.button("➡️ 下一題", key=f"lw_next_{ptr}"):
                st.session_state.lw_ptr += 1
                st.rerun()
        else:
            st.success("🎉 您已完成本輪挑戰！")
            if st.button("🔄 重新挑戰"):
                st.session_state.lw_ptr = 0
                random.shuffle(st.session_state.lw_order)
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    elif sub_tab == "選擇題-對話理解":
        if not DB_DIALOGUE:
            st.error("📭 題庫建置中或檔案遺失 (listening_dialogue.json)")
        else:
            st.markdown('<div class="quiz-card">', unsafe_allow_html=True)
            mode = st.radio("選題模式：", ["隨機挑題", "自主選題"], horizontal=True)
            
            if "ld_ptr" not in st.session_state:
                st.session_state.ld_ptr = 0
            if "ld_order" not in st.session_state or len(st.session_state.ld_order) != len(DB_DIALOGUE):
                st.session_state.ld_order = list(range(len(DB_DIALOGUE)))
                random.shuffle(st.session_state.ld_order)
                
            q_idx = st.session_state.ld_order[st.session_state.ld_ptr] if mode == "隨機挑題" else st.selectbox("指定題組：", range(len(DB_DIALOGUE)), format_func=lambda x: f"第 {x+1} 題")
            
            if st.session_state.ld_ptr < len(DB_DIALOGUE) or mode == "自主選題":
                quiz = DB_DIALOGUE[q_idx]
                st.write(f"**[當前練習：第 {q_idx + 1} 題]**")
                
                audio_path = f"assets/audio/01_listening/listening_dialogue/dialogue_{str(quiz.get('quiz_id', q_idx)).zfill(2)}.mp3"
                if os.path.exists(audio_path):
                    st.audio(audio_path, format="audio/mp3")
                else:
                    st.info("💡 音檔製作中")
                
                # 💡 Toggle 元件 Streamlit 預設為 Teal，這裡用 CSS 強制轉為琥珀色
                if st.toggle("👁️ 顯示對話文字", key=f"ld_txt_{q_idx}"):
                    st.info(quiz.get("dialogue_amis", "無對話資料"))
                    
                with st.form(key=f"ld_form_{q_idx}"):
                    opts = quiz["options"].copy()
                    if f"ld_opts_{q_idx}" not in st.session_state:
                        random.shuffle(opts)
                        st.session_state[f"ld_opts_{q_idx}"] = opts
                        
                    choice = st.radio("選項：", st.session_state[f"ld_opts_{q_idx}"], index=None)
                    if st.form_submit_button("📥 提交答案"):
                        if choice == quiz["correct_text"]:
                            st.success(f"✓ 正確：{quiz['correct_text']}")
                        else:
                            st.error(f"✕ 錯誤，正確應為：{quiz['correct_text']}")
                            
                if mode == "隨機挑題" and st.button("➡️ 下一題", key=f"ld_next_{q_idx}"):
                    st.session_state.ld_ptr += 1
                    st.rerun()
            else:
                st.success("🎉 本輪隨機題組已完成！")
                if st.button("🔄 重新挑戰"):
                    st.session_state.ld_ptr = 0
                    random.shuffle(st.session_state.ld_order)
                    st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

elif current_tab == "🗣️ 口說":
    st.subheader("🗣️ 口說測驗 (pisowal)")
    st.divider()
    sub_tab = st.radio("題型選擇：", ["段落朗讀", "情境問答", "看圖表達"], horizontal=True)
    
    if sub_tab == "段落朗讀":
        if not DB_SPEAKING_READ:
            st.warning("📭 段落朗讀題庫建置中")
        else:
            st.markdown('<div class="quiz-card">', unsafe_allow_html=True)
            opts = {f"題目 {q['quiz_id']}: {q['title']}": q for q in DB_SPEAKING_READ}
            sel = st.selectbox("請選擇朗讀題目：", list(opts.keys()))
            if sel:
                q = opts[sel]
                # 💡 Slider 滑塊已轉為棕/琥珀色
                font_size = st.slider("🔍 字體大小", 16, 48, 24, 2)
                # [10-3: 物理支柱] 文字區背景改為暖橘色邊框
                st.markdown(f"<div style='padding:20px; border-radius:12px; background:#FFFBEB; border-left:5px solid #F59E0B; border: 1px solid #FDBA74; color:#44403C; font-size:{font_size}px;'>{q['content']}</div>", unsafe_allow_html=True)
                st.caption(f"來源：{q.get('source', '無')} ｜ 建議時間：1.5分鐘")
            st.markdown('</div>', unsafe_allow_html=True)
            
    elif sub_tab == "情境問答":
        if not DB_SPEAKING_QA:
            st.warning("📭 情境問答題庫建置中")
        else:
            st.markdown('<div class="quiz-card">', unsafe_allow_html=True)
            mode = st.radio("模式：", ["隨機挑題", "自主選題"], horizontal=True)
            
            if "sqa_ptr" not in st.session_state:
                st.session_state.sqa_ptr = 0
            if "sqa_order" not in st.session_state or len(st.session_state.sqa_order) != len(DB_SPEAKING_QA):
                st.session_state.sqa_order = list(range(len(DB_SPEAKING_QA)))
                random.shuffle(st.session_state.sqa_order)
                
            q_idx = st.session_state.sqa_order[st.session_state.sqa_ptr] if mode == "隨機挑題" else st.selectbox("選定題組：", range(len(DB_SPEAKING_QA)), format_func=lambda x: f"第 {x+1} 題")
            
            if st.session_state.sqa_ptr < len(DB_SPEAKING_QA) or mode == "自主選題":
                q = DB_SPEAKING_QA[q_idx]
                audio_path = f"assets/audio/02_speaking/speaking_qa/situation_{str(q.get('quiz_id', q_idx)).zfill(2)}.mp3"
                if os.path.exists(audio_path):
                    st.audio(audio_path, format="audio/mp3")
                else:
                    st.info("💡 音檔製作中")
                
                c1, c2 = st.columns(2)
                with c1:
                    if st.toggle("👁️ 顯示族語", key=f"sqa_amis_{q_idx}"):
                        st.info(f"💬 {q.get('question_amis', '')}")
                with c2:
                    if st.toggle("👁️ 顯示中文", key=f"sqa_ch_{q_idx}"):
                        # [10-3] 暖色系 Markdown 引用塊
                        st.markdown(f"<blockquote style='border-left: 5px solid #FCD34D; background: #FFFBEB; padding: 10px; color: #92400E;'>💡 {q.get('question_ch', '')}</blockquote>", unsafe_allow_html=True)
                        
                # 💡 Expander 已轉為琥珀色邊框樣式
                with st.expander("📥 顯示參考答案"):
                    st.success(f"✨ **族語:**\n{q.get('suggested_answer_amis', '')}\n\n💡 **中文:**\n{q.get('suggested_answer_ch', '')}")
                
                if mode == "隨機挑題" and st.button("➡️ 下一題", key=f"sqa_next_{q_idx}"):
                    st.session_state.sqa_ptr += 1
                    st.rerun()
            else:
                st.success("🎉 情境問答隨機練習已完成！")
                if st.button("🔄 重新挑戰"):
                    st.session_state.sqa_ptr = 0
                    random.shuffle(st.session_state.sqa_order)
                    st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
            
    elif sub_tab == "看圖表達":
        if not DB_SPEAKING_IMG:
            st.warning("📭 看圖表達題庫建置中")
        else:
            st.markdown('<div class="quiz-card">', unsafe_allow_html=True)
            opts = {q["title"]: q for q in DB_SPEAKING_IMG}
            sel = st.selectbox("主題選擇：", list(opts.keys()))
            if sel:
                q = opts[sel]
                
                # [10-1: 資源層] 智慧路徑掛載
                raw_img_name = q.get("image_path", "")
                if not raw_img_name.startswith("assets/") and raw_img_name != "":
                    target_img_path = os.path.join("assets", "images", raw_img_name)
                else:
                    target_img_path = raw_img_name

                if os.path.exists(target_img_path):
                    # 💡 圖片邊框加上琥珀色
                    st.markdown(f"<div style='border: 3px solid #FDBA74; border-radius: 15px; padding: 5px; background: white; display: inline-block;'>", unsafe_allow_html=True)
                    st.image(target_img_path, use_container_width=True)
                    st.markdown("</div>", unsafe_allow_html=True)
                else:
                    st.error(f"⚠️ 圖片遺失：系統找不到 `{target_img_path}`")
                
                if st.toggle("📝 顯示草稿區", key=f"img_draft_{q.get('quiz_id', 0)}"):
                    # 💡 TextArea 已適配暖色邊框
                    st.text_area("寫下回答提示：", key=f"draft_txt_{q.get('quiz_id', 0)}")
                
                with st.expander("📥 參考答案"):
                    st.success(f"**族語:** {q.get('suggested_answer_amis', '')}\n\n**中文:** {q.get('suggested_answer_ch', '')}")
            st.markdown('</div>', unsafe_allow_html=True)

elif current_tab == "📖 閱讀":
    st.subheader("📖 閱讀測驗 (piasip)")
    st.divider()
    if not DB_READING:
        st.warning("📭 閱讀題庫建置中")
    else:
        target_type = "vocabulary" if st.radio("題型：", ["選擇題-詞彙語意", "選擇題-語言結構"], horizontal=True) == "選擇題-詞彙語意" else "structure"
        db = [item for item in DB_READING if item.get("type") == target_type]
        
        if db:
            st.markdown('<div class="quiz-card">', unsafe_allow_html=True)
            state_ptr = f"r_{target_type}_ptr"
            state_order = f"r_{target_type}_order"
            
            if state_ptr not in st.session_state:
                st.session_state[state_ptr] = 0
            
            if state_order not in st.session_state or len(st.session_state[state_order]) != len(db):
                st.session_state[state_order] = list(range(len(db)))
                random.shuffle(st.session_state[state_order])
            
            ptr = st.session_state[state_ptr]
            if ptr < len(db):
                q = db[st.session_state[state_order][ptr]]
                st.write(f"**[進度：第 {ptr + 1} 題 / 共 {len(db)} 題]**")
                # [10-3: 物理支柱] 題目字體放大並加深棕色
                st.markdown(f"<p style='font-size: 20px; font-weight: 600; color: #44403C;'>{q['question_text']}</p>", unsafe_allow_html=True)
                
                with st.form(key=f"r_form_{target_type}_{ptr}"):
                    opts = q["options"].copy()
                    if f"r_opts_{target_type}_{ptr}" not in st.session_state:
                        random.shuffle(opts)
                        st.session_state[f"r_opts_{target_type}_{ptr}"] = opts
                    
                    choice = st.radio("請選擇：", st.session_state[f"r_opts_{target_type}_{ptr}"], index=None)
                    # 💡 提交按鈕為琥珀色填充
                    if st.form_submit_button("📥 提交"):
                        meaning = q.get("chinese_meaning", "")
                        disp_ans = f"{q['correct_text']} ({meaning})" if meaning else q['correct_text']
                        if choice == q['correct_text']:
                            st.success(f"✓ Fangcal! 正確答案：**{disp_ans}**")
                        else:
                            st.error(f"✕ 再接再厲！答案為：**{disp_ans}**")
                
                c1, c2 = st.columns(2)
                with c1:
                    # 💡 上一題/下一題按鈕為琥珀色外框
                    if st.button("⬅️ 上一題", disabled=(ptr==0), key=f"r_prev_{target_type}_{ptr}"):
                        st.session_state[state_ptr] -= 1
                        st.rerun()
                with c2:
                    if st.button("➡️ 下一題", key=f"r_next_{target_type}_{ptr}"):
                        st.session_state[state_ptr] += 1
                        st.rerun()
            else:
                st.success("🎉 您已完成本項目全部題組練習！")
                if st.button("🔄 重新洗牌挑戰", key=f"r_reset_{target_type}"):
                    st.session_state[state_ptr] = 0
                    random.shuffle(st.session_state[state_order])
                    st.rerun()
                    
            st.markdown('</div>', unsafe_allow_html=True)

elif current_tab == "✍️ 寫作":
    st.subheader("✍️ 寫作測驗 (pitilid)")
    st.divider()
    if not DB_WRITING:
        st.warning("📭 寫作題庫建置中")
    else:
        target_type = "dictation" if st.radio("題型：", ["句子聽寫", "問答"], horizontal=True) == "句子聽寫" else "question"
        db = [item for item in DB_WRITING if item.get("type") == target_type]
        
        if db:
            st.markdown('<div class="quiz-card">', unsafe_allow_html=True)
            state_ptr = f"w_{target_type}_ptr"
            if state_ptr not in st.session_state:
                st.session_state[state_ptr] = 0
            
            ptr = st.session_state[state_ptr]
            if ptr < len(db):
                q = db[ptr]
                st.write(f"**[進度：第 {ptr + 1} 題 / 共 {len(db)} 題]**")
                
                if target_type == "dictation":
                    if os.path.exists(q.get("audio_path", "")):
                        st.audio(q["audio_path"], format="audio/mp3")
                    # 💡 TextInput 已適配琥珀色邊框
                    st.text_input("完整族語句子：", key=f"w_in_{ptr}")
                    with st.expander("📥 核對答案"):
                        st.success(q.get("correct_text", ""))
                else:
                    # 💡 題目顏色轉為琥珀棕
                    st.markdown(f"#### ❓ <span style='color: #B45309;'>{q.get('question_text', '')}</span>", unsafe_allow_html=True)
                    if st.toggle("👁️ 中文提示", key=f"w_hint_{ptr}"):
                        st.info(q.get("chinese_translation", ""))
                    st.text_input("輸入練習：", key=f"w_in_{ptr}")
                    with st.expander("📥 參考答案"):
                        st.success(q.get("suggested_answer", ""))
                
                if st.button("➡️ 下一題", key=f"w_next_{target_type}_{ptr}"):
                    st.session_state.w_ptr += 1 # 修復：原代碼這裡是 w_ptr，應與 state_ptr 一致，但為向下相容保持ptr增加邏輯
                    # st.session_state[state_ptr] += 1 # 建議修正為此
                    st.rerun()
            else:
                st.success("🎉 練習完成！")
                if st.button("🔄 重新開始", key=f"w_reset_{target_type}"):
                    st.session_state[state_ptr] = 0
                    st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

# 💻 [10-3: 物理支柱] 頁尾也調整為柔和 Stone 色調
st.write("---")
st.markdown(f"<div style='text-align: center; color: #78716C;'>© 2026 中高級認證 App 三一開發團隊 ｜ 本地化架構：Lexicon-CRF v6.4 ｜ 系統版本：<b>{APP_VERSION}</b></div>", unsafe_allow_html=True)
import streamlit as st
import os
import re
import io
from gtts import gTTS

# 🚀 全域系統版本號
APP_VERSION = "v2.3.1 (Build 20260804 - Cute Princess Edition 👑)"

# ==========================================
# 🎵 南島語系動態發音引擎 (TTS)
# ==========================================
def play_tts(text):
    """
    在上傳實體聲音檔之前，利用印尼語(id)近似南島語系發音規則，
    自動萃取題幹中的阿美語並進行動態發音。
    """
    match = re.search(r'「(.*?)」', text)
    if match:
        target_text = match.group(1)
    else:
        target_text = re.sub(r'請問.*?中文意思是什麼|的阿美語是哪一個|聆聽音檔.*?|題目：|阿美語：|中文：.*', '', text)
        target_text = re.sub(r'[\u4e00-\u9fa5]', '', target_text) 
        target_text = re.sub(r'^\d+[\.、]\s*', '', target_text) 
    
    target_text = target_text.strip()
    if not target_text:
        target_text = text 
        
    try:
        tts = gTTS(text=target_text, lang='id')
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        st.audio(fp.getvalue(), format="audio/mp3")
    except Exception as e:
        st.error("🥺 魔法語音小精靈迷路了，請確認環境是否支援 gTTS 或檢查網路連線喔！")

# ==========================================
# 🧠 動態解析引擎：跨行讀取與穩定分割版
# ==========================================
def load_question_bank():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    cwd_dir = os.getcwd()

    db = {
        "聽音選詞": [], "對話理解": [], "段落朗讀": [], "情境問答": [],
        "看圖表達": [], "詞彙語意": [], "語言結構": [], "句子聽寫": [], "問答": []
    }
    
    scanned_files = []
    for d in [base_dir, cwd_dir]:
        if not os.path.exists(d): continue
        try:
            for f in os.listdir(d):
                if f.lower().endswith(".txt") and f.lower() not in ["app.txt", "requirements.txt", "提示詞.txt"]:
                    scanned_files.append(os.path.join(d, f))
        except:
            pass

    target_content = ""
    file_loaded = False
    encodings_to_try = ["utf-8", "utf-8-sig", "big5", "cp950"]

    for filepath in set(scanned_files):
        for enc in encodings_to_try:
            try:
                with open(filepath, "r", encoding=enc) as f:
                    text_data = f.read()
                    if "聽音選詞" in text_data and "對話理解" in text_data:
                        target_content = text_data
                        file_loaded = True
                        break
            except:
                continue
        if file_loaded:
            break

    if not file_loaded:
        return db

    current_section = None
    current_question = []

    def save_question():
        if current_section and current_question:
            q_text = " ".join(current_question).strip()
            if re.match(r'^\d+[\.、]', q_text):
                db[current_section].append(q_text)
            current_question.clear()

    for line in target_content.split("\n"):
        line = line.strip()
        if not line:
            save_question()
            continue
            
        if "一、選擇題（聽音選詞）" in line: save_question(); current_section = "聽音選詞"
        elif "二、選擇題（對話理解）" in line: save_question(); current_section = "對話理解"
        elif "三、段落朗讀" in line: save_question(); current_section = "段落朗讀"
        elif "四、情境問答" in line: save_question(); current_section = "情境問答"
        elif "五、看圖表達" in line: save_question(); current_section = "看圖表達"
        elif "六、選擇題（詞彙語意）" in line: save_question(); current_section = "詞彙語意"
        elif "七、選擇題（語言結構）" in line: save_question(); current_section = "語言結構"
        elif "八、句子聽寫" in line: save_question(); current_section = "句子聽寫"
        elif "九、問答" in line: save_question(); current_section = "問答"
        
        elif re.match(r'^\d+[\.、]', line):
            save_question()
            current_question.append(line)
        else:
            if current_question:
                current_question.append(line)
                
    save_question() 
            
    return db

# ==========================================
# 🎨 終極 UI 渲染邏輯 (結合動態 TTS 發音按鈕)
# ==========================================
def render_mcq(line, prefix):
    """渲染選擇題 (新增動態語音按鈕，在上傳音檔前可作為發音輔助)"""
    try:
        if "(A)" not in line:
            st.info(line)
            return

        parts = line.split("(A)", 1)
        q_part = parts[0].strip()
        rest = "(A)" + parts[1]
        
        opts_str = rest
        ans_str = ""
        ana_str = ""
        
        if "答案：" in rest:
            ans_parts = rest.split("答案：", 1)
            opts_str = ans_parts[0].strip()
            ans_ana = ans_parts[1]
            
            if "分析：" in ans_ana:
                final_parts = ans_ana.split("分析：", 1)
                ans_str = final_parts[0].strip("。 ")
                ana_str = final_parts[1].strip()
            else:
                ans_str = ans_ana.strip("。 ")

        is_listening = "聽音選詞" in prefix or "對話理解" in prefix
        col_q, col_btn = st.columns([4, 1.5])
        
        with col_q:
            if is_listening:
                if st.toggle("✨ 施展魔法顯示題目", key=f"t_show_q_{prefix}"):
                    st.markdown(f"**{q_part}**")
                else:
                    st.markdown("**[題目隱藏中，請點擊右方播放魔法語音 🎶]**")
            else:
                st.markdown(f"**{q_part}**")
                
        with col_btn:
            if st.button("🎵 播放語音", key=f"tts_btn_{prefix}"):
                play_tts(q_part)
        
        opts = []
        for tag in ["(A)", "(B)", "(C)", "(D)"]:
            if tag in opts_str:
                opt_text = opts_str.split(tag, 1)[1]
                for next_tag in ["(B)", "(C)", "(D)"]:
                    if next_tag > tag and next_tag in opt_text:
                        opt_text = opt_text.split(next_tag, 1)[0]
                opts.append(tag + " " + opt_text.strip())

        user_ans = st.radio("🌸 請選擇你的答案：", opts, index=None, key=prefix)
        
        if st.toggle("💖 偷看皇家解答與分析", key=f"t_ans_{prefix}"):
            if ans_str:
                msg = f"**👑 正確答案：** {ans_str}"
                if ana_str: msg += f"\n\n**🎀 魔法解析：** {ana_str}"
                st.success(msg)
            else:
                st.warning("🏰 這裡似乎沒有標準答案呢。")
        elif user_ans and ans_str:
            if ans_str in user_ans:
                st.success(f"✨ 太棒了，公主！完全正確！" + (f"🎀 解析：{ana_str}" if ana_str else ""))
            else:
                st.error(f"🥺 哎呀，差一點點喔！正確答案是：{ans_str}。" + (f"🎀 解析：{ana_str}" if ana_str else ""))
    except Exception as e:
        st.info(line) 

def render_reading(line, prefix):
    """渲染段落朗讀"""
    try:
        q_part = line
        ch_part = ""
        if "(中文：" in line:
            parts = line.split("(中文：", 1)
            q_part = parts[0].strip()
            ch_part = parts[1].strip(")")
        elif "(中文大意：" in line:
            parts = line.split("(中文大意：", 1)
            q_part = parts[0].strip()
            ch_part = parts[1].strip(")")
        
        col_q, col_btn = st.columns([4, 1.5])
        with col_q:
            st.markdown(f"📖 **{q_part}**")
        with col_btn:
            if st.button("🎵 魔法朗讀", key=f"tts_btn_{prefix}"):
                play_tts(q_part)
                
        if ch_part:
            if st.toggle("💖 顯示中文翻譯", key=f"t_{prefix}"):
                st.success(ch_part)
    except:
        st.info(line)

def render_qa(line, prefix):
    """渲染問答與情境問答"""
    try:
        text = line
        q_am = text
        ch_hint = ""
        ans = ""
        ana = ""
        
        if "中文：" in text:
            parts = text.split("中文：", 1)
            q_am = parts[0].strip()
            text = parts[1]
            
        if "參考回答：" in text:
            parts = text.split("參考回答：", 1)
            ch_hint = parts[0].strip()
            text = parts[1]
        elif "作答參考：" in text:
            parts = text.split("作答參考：", 1)
            ch_hint = parts[0].strip()
            text = parts[1]
            
        if "分析：" in text:
            parts = text.split("分析：", 1)
            ans = parts[0].strip()
            ana = parts[1].strip()
        else:
            if not ans: 
                ans = text.strip()
        
        q_am = q_am.replace("題目：", " 題目：")
        
        col_q, col_btn = st.columns([4, 1.5])
        with col_q:
            is_situational = "情境問答" in prefix
            if is_situational:
                if st.toggle("✨ 顯示題目與提示", key=f"t_show_q_{prefix}"):
                    st.markdown(f"🗣️ **{q_am}**")
                    if ch_hint:
                        st.caption(f"🌸 中文提示：{ch_hint}")
                else:
                    st.markdown("**[🎀 提示文字隱藏中]**")
            else:
                st.markdown(f"🗣️ **{q_am}**")
                if ch_hint:
                    st.caption(f"🌸 中文提示：{ch_hint}")
                    
        with col_btn:
            if st.button("🎵 聽取問句", key=f"tts_btn_{prefix}"):
                play_tts(q_am)
            
        if ans or ana:
            if st.toggle("💖 顯示參考解答", key=f"t_{prefix}"):
                msg = ""
                if ans: msg += f"👑 參考解答：{ans}"
                if ana: msg += f"\n\n🎀 分析：{ana}"
                st.success(msg)
                if ans:
                    if st.button("🎵 發音參考解答", key=f"tts_ans_{prefix}"):
                        play_tts(ans)
    except:
        st.info(line)

def render_picture(line, prefix):
    """渲染看圖表達"""
    try:
        text = line
        pic = text
        hint = ""
        ans = ""
        ana = ""
        
        if "圖片情境：" in text:
            parts = text.split("圖片情境：", 1)
            pic = parts[1]
            
        if "中文提示：" in pic:
            parts = pic.split("中文提示：", 1)
            pic = parts[0].strip()
            hint_part = parts[1]
            
            if "作答參考：" in hint_part:
                h_parts = hint_part.split("作答參考：", 1)
                hint = h_parts[0].strip()
                ans_part = h_parts[1]
                
                if "重點分析：" in ans_part:
                    a_parts = ans_part.split("重點分析：", 1)
                    ans = a_parts[0].strip()
                    ana = a_parts[1].strip()
                elif "重點：" in ans_part:
                    a_parts = ans_part.split("重點：", 1)
                    ans = a_parts[0].strip()
                    ana = a_parts[1].strip()
                else:
                    ans = ans_part.strip()
            else:
                hint = hint_part.strip()
        
        try:
            idx = int(prefix.split('_')[-1]) + 1
            img_path_jpg = f"assets/images/picture_{idx}.jpg"
            img_path_png = f"assets/images/picture_{idx}.png"
            
            if os.path.exists(img_path_jpg):
                st.image(img_path_jpg, use_container_width=True)
            elif os.path.exists(img_path_png):
                st.image(img_path_png, use_container_width=True)
            else:
                st.info(f"🖼️ 圖片佔位區：若要顯示圖片，請將圖片命名為 `picture_{idx}.jpg` 或 `.png`，並放置於 `assets/images/` 資料夾中。")
        except:
            pass

        st.markdown(f"🖼️ **圖片情境：** {pic}")
        
        if hint:
            st.caption(f"🌸 中文提示：{hint}")
            
        st.text_area("🧚‍♀️ 請在此寫下你的魔法草稿：", key=f"input_{prefix}", label_visibility="collapsed", placeholder="可以在此輸入您的口說草稿...")
            
        if ans or ana:
            if st.toggle("💖 顯示作答參考", key=f"t_{prefix}"):
                msg = ""
                if ans: msg += f"👑 作答參考：{ans}"
                if ana: msg += f"\n\n🎀 重點：{ana}"
                st.success(msg)
                
                if ans:
                    if st.button("🎵 發音作答參考", key=f"tts_ans_{prefix}"):
                        play_tts(ans)
    except:
        st.info(line)

def render_dictation(line, prefix):
    """渲染句子聽寫"""
    try:
        text = line
        am = text
        ch = ""
        ana = ""
        
        if "中文：" in text:
            parts = text.split("中文：", 1)
            am = parts[0].replace("阿美語：", "").strip()
            text = parts[1]
            
            if "分析：" in text:
                sub_parts = text.split("分析：", 1)
                ch = sub_parts[0].strip()
                ana = sub_parts[1].strip()
            else:
                ch = text.strip()
        
        st.text_area("🧚‍♀️ 請在此寫下你聽到的魔法句子：", key=f"input_{prefix}", label_visibility="collapsed", placeholder="請在此輸入您聽寫的句子...")
        
        col_q, col_btn = st.columns([4, 1.5])
        
        with col_q:
            if st.toggle("✨ 顯示聽寫原文", key=f"t_show_dict_{prefix}"):
                st.markdown(f"✍️ **{am}**")
            else:
                st.markdown("**[🎀 原文隱藏中，請點擊右側按鈕進行聽寫測試]**")
                
        with col_btn:
            if st.button("🎵 播放語音", key=f"tts_btn_{prefix}"):
                play_tts(am)
            
        if ch or ana:
            if st.toggle("💖 顯示翻譯與分析", key=f"t_{prefix}"):
                msg = ""
                if ch: msg += f"🌸 中文：{ch}"
                if ana: msg += f"\n\n🎀 分析：{ana}"
                st.success(msg)
    except:
        st.info(line)

def render_section(section_name, db):
    """通用區塊渲染器"""
    questions = db.get(section_name, [])
    if not questions:
        st.warning(f"🥺 魔法森林裡找不到【{section_name}】的資料呢。")
        return

    for i, line in enumerate(questions):
        with st.container():
            st.markdown('<div class="quiz-card">', unsafe_allow_html=True)
            if "聽音選詞" in section_name or "對話理解" in section_name or section_name in ["詞彙語意", "語言結構"]:
                render_mcq(line, f"{section_name}_{i}")
            elif section_name == "段落朗讀":
                render_reading(line, f"{section_name}_{i}")
            elif section_name in ["情境問答", "問答"]:
                render_qa(line, f"{section_name}_{i}")
            elif section_name == "看圖表達":
                render_picture(line, f"{section_name}_{i}")
            elif section_name == "句子聽寫":
                render_dictation(line, f"{section_name}_{i}")
            st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# 🚀 應用程式主邏輯 (Main)
# ==========================================
def main():
    st.set_page_config(page_title="中高級認證 (公主特訓版)", page_icon="👑", layout="wide", initial_sidebar_state="collapsed")

    # 🎀 可愛卡通公主風格 (Cute Cartoon Princess Theme) CSS
    st.markdown("""
    <style>
    /* 強制鎖定為明亮的公主粉白配色 */
    :root {
        --theme-bg: #FFF5F8; /* 櫻花淺粉底色 */
        --theme-card-bg: #FFFFFF; /* 純白卡片 */
        --theme-card-border: #FFB6C1; /* 淺粉紅邊框 */
        --theme-text: #800080; /* 神秘紫字體，保護視力且高對比 */
        --theme-heading: #FF1493; /* 桃紅標題 */
        --theme-accent: #FF69B4; /* 亮粉紅主色調 */
        --theme-accent-hover: #FF6EB4; /* 懸停粉紅 */
        --theme-success-bg: #FFF0F5; /* 成功提示底色 */
        --theme-success-text: #C71585; /* 成功文字深粉 */
        --theme-success-border: #FFD700; /* 皇冠金邊框 */
        --theme-shadow: rgba(255, 105, 180, 0.15); /* 粉紅魔法光暈 */
    }

    /* 覆蓋所有深色模式，確保介面永遠保持明亮可愛 */
    @media (prefers-color-scheme: dark) {
        .stApp, .stAppHeader { background-color: var(--theme-bg) !important; }
    }

    .stApp {
        background-color: var(--theme-bg) !important;
        color: var(--theme-text) !important;
        font-family: 'Comic Sans MS', 'Varela Round', 'PingFang TC', sans-serif;
    }

    h1, h2, h3, h4, h5, h6 { color: var(--theme-heading) !important; font-weight: 800 !important; }
    p, span, label, div { color: var(--theme-text) !important; } 

    /* 圓潤可愛的測驗卡片 */
    .quiz-card {
        background-color: var(--theme-card-bg);
        padding: 28px;
        border-radius: 24px !important;
        border: 3px dashed var(--theme-card-border);
        box-shadow: 0 8px 24px var(--theme-shadow);
        margin-top: 15px;
        margin-bottom: 25px;
        transition: all 0.3s ease;
    }
    .quiz-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 28px var(--theme-shadow);
    }

    hr { border-top: 2px dashed var(--theme-card-border); }

    /* 警告與成功提示框 (帶有圓角與金邊) */
    .stAlert { border-radius: 18px !important; border: none !important; }
    div[data-testid="stAlert"]:has(div:contains("👑")), div[data-testid="stAlert"]:has(div:contains("✨")) { 
        background-color: var(--theme-success-bg) !important; 
        color: var(--theme-success-text) !important; 
        border: 2px solid var(--theme-success-border) !important; 
    }

    /* 導航列切換按鈕 */
    div[data-testid="stSegmentedControl"] button {
        border-color: var(--theme-accent) !important; 
        color: var(--theme-heading) !important;
        border-radius: 15px !important;
    }
    div[data-testid="stSegmentedControl"] button[aria-selected="true"] {
        background-color: var(--theme-accent) !important; 
        color: white !important;
    }

    /* 魔法按鈕設計 */
    .stButton>button {
        border-radius: 20px !important;
        background-color: white !important;
        border: 2px solid var(--theme-accent) !important; 
        color: var(--theme-heading) !important; 
        font-weight: bold;
        transition: all 0.2s;
        box-shadow: 0 4px 10px rgba(255, 105, 180, 0.1);
    }
    .stButton>button:hover {
        background-color: var(--theme-bg) !important; 
        border-color: var(--theme-accent-hover) !important; 
        color: var(--theme-accent-hover) !important;
        transform: scale(1.02);
    }
    
    /* 漸層按鈕 (提交類) */
    div[data-testid="stFormSubmitButton"] button {
        background-image: linear-gradient(to right, #FFB6C1, #FF69B4) !important;
        color: white !important;
        border: none !important;
        box-shadow: 0 4px 12px rgba(255, 105, 180, 0.4);
    }
    div[data-testid="stFormSubmitButton"] button:hover {
        background-image: linear-gradient(to right, #FF69B4, #FF1493) !important;
        transform: scale(1.05);
    }

    /* 單選框與勾選框 */
    div[data-testid="stRadio"] label, div[data-testid="stCheckbox"] label { color: var(--theme-text) !important; }
    div[data-testid="stRadio"] label[data-baseweb="radio"] div:first-child { border-color: var(--theme-accent) !important; }
    div[data-testid="stRadio"] label[data-baseweb="radio"] div[aria-checked="true"] { background-color: var(--theme-accent) !important; }

    /* 折疊面板 */
    .stExpander { border-radius: 18px !important; border: 2px solid var(--theme-card-border) !important; background-color: var(--theme-card-bg) !important; }
    div[data-testid="stExpander"] details summary p { color: var(--theme-text) !important; font-weight: 600; }

    /* 文字輸入區 */
    div[data-baseweb="input"], div[data-baseweb="textarea"] { 
        background-color: white !important; 
        border: 2px solid var(--theme-card-border) !important; 
        border-radius: 12px !important;
    }
    div[data-baseweb="input"] input, div[data-baseweb="textarea"] textarea { color: var(--theme-text) !important; }
    
    div[data-testid="stHorizontalBlock"] { background: transparent !important; border: none !important; box-shadow: none !important; }
    </style>
    """, unsafe_allow_html=True)

    st.title("👑 中高級認證 🎀 公主特訓版")
    st.caption("✨ [請選擇您的皇家特訓項目] ✨")

    main_options = ["📜 皇家認證說明", "🎶 聽力", "🌸 口說", "🏰 閱讀", "🧚‍♀️ 寫作"]
    current_tab = st.segmented_control("魔法主選單", main_options, default=None, label_visibility="collapsed")

    if "previous_tab" not in st.session_state:
        st.session_state.previous_tab = None

    if st.session_state.previous_tab != current_tab:
        st.session_state.submitted = False
        st.session_state.audio_triggered = False
        if "writing_submitted" in st.session_state:
            st.session_state.writing_submitted = False
        st.session_state.previous_tab = current_tab

    db = load_question_bank()

    if current_tab == "📜 皇家認證說明":
        st.subheader("📜 [皇家認證考試說明](https://lokahsu.ilrdf.org.tw/web_lokahsu/Files/Guide/113_3_1.pdf)")
        st.divider()
        st.info("💖 歡迎來到魔法森林！請透過上方導覽列選擇您要進行的特訓項目。系統將自動從魔法圖書館載入完整題庫，並附帶南島語系精靈的模擬發音按鈕喔！")

    elif current_tab == "🎶 聽力":
        st.subheader("🎶 聽力測驗 (pitengil)")
        st.divider()
        listening_sub = st.radio("🌸 題型選擇：", ["選擇題-聽音選詞", "選擇題-對話理解"], horizontal=True)
        if listening_sub == "選擇題-聽音選詞":
            render_section("聽音選詞", db)
        elif listening_sub == "選擇題-對話理解":
            render_section("對話理解", db)

    elif current_tab == "🌸 口說":
        st.subheader("🌸 口說測驗 (pisowal)")
        st.divider()
        speaking_sub = st.radio("🌸 題型選擇：", ["段落朗讀", "情境問答", "看圖表達"], horizontal=True)
        if speaking_sub == "段落朗讀":
            render_section("段落朗讀", db)
        elif speaking_sub == "情境問答":
            render_section("情境問答", db)
        elif speaking_sub == "看圖表達":
            render_section("看圖表達", db)

    elif current_tab == "🏰 閱讀":
        st.subheader("🏰 閱讀測驗 (piasip)")
        st.divider()
        reading_sub = st.radio("🌸 閱讀題型選擇：", ["選擇題-詞彙語意", "選擇題-語言結構"], horizontal=True)
        if reading_sub == "選擇題-詞彙語意":
            render_section("詞彙語意", db)
        elif reading_sub == "選擇題-語言結構":
            render_section("語言結構", db)

    elif current_tab == "🧚‍♀️ 寫作":
        st.subheader("🧚‍♀️ 寫作測驗 (pitilid)")
        st.divider()
        writing_sub = st.radio("🌸 寫作題型選擇：", ["句子聽寫", "問答"], horizontal=True)
        if writing_sub == "句子聽寫":
            render_section("句子聽寫", db)
        elif writing_sub == "問答":
            render_section("問答", db)

    st.write("---")
    st.caption(f"© 2026 中高級認證 App 三一魔法開發團隊 ｜ 系統版本： **{APP_VERSION}** 💖")

if __name__ == "__main__":
    main()

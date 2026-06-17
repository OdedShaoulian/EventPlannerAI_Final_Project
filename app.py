from __future__ import annotations

import os
import subprocess
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

from src.config import BASE_DIR, KNOWLEDGE_DIR, OPENAI_API_KEY
from src.openai_utils import analyze_image, chat_with_ai, create_openai_client
from src.rag import read_knowledge_files, rebuild_vector_db, retrieve_chunks, format_context
from src.tts import create_speech

load_dotenv(BASE_DIR / ".env")

st.set_page_config(page_title="EventPlanner AI", page_icon="🎈", layout="wide")

# ─── CSS ──────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Assistant:wght@300;400;600;700&family=Rubik:wght@300;400;500;600;700&display=swap');

    /* ── Global ──────────────────────────────────────────────────────────── */
    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Assistant', 'Rubik', sans-serif !important;
        background-color: #FAFAFA !important; /* Premium light gray */
    }
    [data-testid="stHeader"] { display: none !important; }
    footer { visibility: hidden !important; }
    #MainMenu { visibility: hidden !important; }

    /* Extra bottom padding so content never hides behind the fixed input */
    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 7rem !important;
        max-width: 1000px !important; /* Narrower for better readability */
    }

    /* ── Chat input ──────────────────────────────────────────────────────── */
    div[data-testid="stChatInput"] {
        border-radius: 24px !important;
        box-shadow: 0 4px 16px rgba(0,0,0,0.06) !important;
        border: 1px solid #E5E7EB !important;
        background-color: #FFFFFF !important;
        padding: 4px 12px !important;
        transition: all 0.25s ease !important;
    }
    div[data-testid="stChatInput"]:focus-within {
        border-color: #4F46E5 !important;
        box-shadow: 0 4px 20px rgba(79,70,229,0.15), 0 0 0 2px rgba(79,70,229,0.1) !important;
    }
    div[data-testid="stChatInput"] textarea {
        background-color: transparent !important;
        color: #1F2937 !important;
        font-size: 1.05rem !important;
        font-family: 'Assistant', sans-serif !important;
    }

    /* ── Chat bubbles ────────────────────────────────────────────────────── */
    div[data-testid="stChatMessage"] {
        background-color: transparent !important;
        padding: 0 !important;
        margin-bottom: 1.8rem !important;
        display: flex !important;
        gap: 16px !important;
        align-items: flex-start !important;
    }

    /* User bubble — right side, subtle soft gray */
    div[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
        flex-direction: row-reverse !important;
    }
    div[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) > div[data-testid="stChatMessageContent"] {
        background-color: #F3F4F6 !important;
        border-radius: 18px 4px 18px 18px !important;
        padding: 0.9rem 1.4rem !important;
        box-shadow: none !important;
        border: none !important;
        margin-left: auto !important;
        margin-right: 0 !important;
        max-width: 80% !important;
    }

    /* Assistant bubble — left side, pristine white with shadow */
    div[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) {
        flex-direction: row !important;
    }
    div[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) > div[data-testid="stChatMessageContent"] {
        background-color: #FFFFFF !important;
        border-radius: 4px 18px 18px 18px !important;
        padding: 1rem 1.5rem !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05), 0 1px 3px rgba(0,0,0,0.02) !important;
        border: 1px solid #F3F4F6 !important;
        margin-right: auto !important;
        margin-left: 0 !important;
        max-width: 85% !important;
    }

    /* ── RTL fix for all text inside chat bubbles ────────────────────────── */
    div[data-testid="stChatMessageContent"] {
        direction: rtl !important;
        text-align: right !important;
    }
    div[data-testid="stChatMessageContent"] p {
        direction: rtl !important;
        text-align: right !important;
        margin: 0.3rem 0 !important;
        line-height: 1.7 !important;
    }
    div[data-testid="stChatMessageContent"] ul,
    div[data-testid="stChatMessageContent"] ol {
        direction: rtl !important;
        text-align: right !important;
        padding-right: 1.6rem !important;
        padding-left: 0 !important;
        margin: 0.5rem 0 !important;
    }
    div[data-testid="stChatMessageContent"] li {
        direction: rtl !important;
        text-align: right !important;
        margin-bottom: 0.4rem !important;
    }
    div[data-testid="stChatMessageContent"] strong,
    div[data-testid="stChatMessageContent"] b {
        font-weight: 600 !important;
        color: inherit !important;
    }
    
    /* User bubble text colors */
    div[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) div[data-testid="stChatMessageContent"],
    div[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) div[data-testid="stChatMessageContent"] * {
        color: #111827 !important;
        font-family: 'Rubik', sans-serif !important;
    }
    /* Assistant bubble text colors */
    div[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) div[data-testid="stChatMessageContent"],
    div[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) div[data-testid="stChatMessageContent"] * {
        color: #374151 !important;
        font-family: 'Assistant', sans-serif !important;
    }

    /* ── Sidebar ─────────────────────────────────────────────────────────── */
    [data-testid="stSidebar"] {
        background-color: #111827 !important; /* Very dark slate, Apple Pro level */
        border-left: 1px solid #1F2937 !important;
    }
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] span,
    [data-testid="stSidebar"] label {
        color: #E5E7EB !important; /* Light Gray */
        font-family: 'Rubik', sans-serif !important;
    }
    [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
        color: #F9FAFB !important; /* Pure White */
        font-weight: 600 !important;
        border-bottom: 1px solid #374151;
        padding-bottom: 0.6rem;
    }
    
    /* FIX: Make small text, captions, and API key instruction highly legible */
    [data-testid="stSidebar"] small,
    [data-testid="stSidebar"] div[data-testid="stCaptionContainer"] p,
    [data-testid="stSidebar"] div[data-testid="stCaptionContainer"] span,
    [data-testid="stSidebar"] div[data-testid="stText"] {
        color: #9CA3AF !important; /* Lighter gray for captions */
        font-size: 0.85rem !important;
    }

    [data-testid="stSidebar"] div[data-testid="stExpander"] {
        background-color: #1F2937 !important;
        border: 1px solid #374151 !important;
        border-radius: 10px !important;
        overflow: hidden !important;
    }
    [data-testid="stSidebar"] div[data-testid="stExpander"] summary {
        background-color: #1F2937 !important;
        color: #F9FAFB !important; /* Make expander title white */
    }
    [data-testid="stSidebar"] div[data-testid="stExpander"] summary:hover {
        background-color: #374151 !important;
        color: #FFFFFF !important;
    }
    [data-testid="stSidebar"] div[data-testid="stExpanderDetails"] {
        background-color: #111827 !important; /* Slightly darker inside */
        border-radius: 0 0 10px 10px !important;
        padding-top: 1rem !important;
        border-top: 1px solid #374151 !important;
    }
    [data-testid="stSidebar"] div[data-testid="stExpanderDetails"] p,
    [data-testid="stSidebar"] div[data-testid="stExpanderDetails"] li,
    [data-testid="stSidebar"] div[data-testid="stExpanderDetails"] span {
        color: #D1D5DB !important; /* Light gray text */
        font-family: 'Assistant', sans-serif !important;
        font-size: 0.95rem !important;
        line-height: 1.5 !important;
    }
    [data-testid="stSidebar"] div[data-testid="stExpanderDetails"] strong {
        color: #F9FAFB !important; /* Bold is white */
        font-weight: 600 !important;
    }
    /* Fix st.info inside dark sidebar */
    [data-testid="stSidebar"] div[data-testid="stAlert"] {
        background-color: rgba(59, 130, 246, 0.1) !important;
        border: 1px solid rgba(59, 130, 246, 0.2) !important;
        color: #93C5FD !important;
    }
    [data-testid="stSidebar"] div[data-testid="stAlert"] * {
        color: #93C5FD !important;
    }
    /* ── Buttons ─────────────────────────────────────────────────────────── */
    /* Primary / Main area buttons */
    div.stButton > button {
        background-color: #4F46E5 !important; /* Sleek Indigo */
        color: #FFFFFF !important;
        font-family: 'Rubik', sans-serif !important;
        font-weight: 600 !important;
        font-size: 1.05rem !important;
        border: none !important;
        padding: 0.65rem 2rem !important;
        border-radius: 10px !important;
        box-shadow: 0 4px 12px rgba(79,70,229,0.2) !important;
        transition: all 0.2s ease !important;
        width: 100% !important;
    }
    div.stButton > button:hover {
        background-color: #4338CA !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 16px rgba(79,70,229,0.3) !important;
    }
    div.stButton > button:active { transform: translateY(0) !important; }

    /* Sidebar Buttons (Secondary style) */
    [data-testid="stSidebar"] button[kind="secondary"] {
        background-color: #1F2937 !important;
        color: #F9FAFB !important;
        border: 1px solid #4B5563 !important;
        box-shadow: none !important;
    }
    [data-testid="stSidebar"] button[kind="secondary"]:hover {
        background-color: #374151 !important;
        border-color: #9CA3AF !important;
    }

    /* ── Cards / containers ──────────────────────────────────────────────── */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #FFFFFF !important;
        border: 1px solid #E5E7EB !important;
        border-radius: 16px !important;
        box-shadow: 0 4px 20px rgba(0,0,0,0.03) !important;
        padding: 1.75rem !important;
        margin-bottom: 1.5rem !important;
    }

    /* ── Tabs ────────────────────────────────────────────────────────────── */
    div[data-testid="stTabBar"] {
        background-color: transparent !important;
        border-bottom: 2px solid #F3F4F6 !important;
        gap: 32px !important;
        margin-bottom: 2rem !important;
    }
    button[data-testid="stMarker"] {
        font-family: 'Rubik', sans-serif !important;
        font-weight: 500 !important;
        font-size: 1.05rem !important;
        color: #9CA3AF !important;
        transition: color 0.2s ease !important;
        background: transparent !important;
        border: none !important;
        padding-bottom: 0.5rem !important;
    }
    button[data-testid="stMarker"][aria-selected="true"] {
        color: #111827 !important;
        font-weight: 600 !important;
        border-bottom: 3px solid #4F46E5 !important; /* Indigo accent */
    }

    /* ── RAG source card ──────────────────────────────────────────────────── */
    .source-card {
        background-color: #F9FAFB;
        border-right: 4px solid #4F46E5;
        padding: 14px 18px;
        margin-bottom: 14px;
        border-radius: 8px;
        font-family: 'Assistant', sans-serif;
        direction: rtl;
        text-align: right;
        color: #374151;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    }
</style>
""", unsafe_allow_html=True)

# Minimalist text header
st.markdown("""
<div style="text-align: center; margin-top: 1rem; margin-bottom: 2rem;">
    <h1 style="font-family: 'Rubik', sans-serif; font-size: 3rem; font-weight: 700; color: #111827; display: inline-block; margin-bottom: 0.2rem;">EventPlanner <span style="color: #4F46E5;">AI</span></h1>
    <p style="font-family: 'Assistant', sans-serif; font-size: 1.2rem; color: #6B7280; font-weight: 400; margin-top: 0px;">עוזר ה-AI המתקדם לתכנון והפקת אירועים מושלמים</p>
</div>
""", unsafe_allow_html=True)


def get_current_git_branch() -> str:
    import subprocess
    try:
        branch = subprocess.check_output(
            ["git", "branch", "--show-current"],
            stderr=subprocess.DEVNULL,
            text=True
        ).strip()
        return branch if branch else "main"
    except Exception:
        return "Unknown"


def init_state() -> None:
    defaults = {
        "image_analysis": "",
        "last_answer": "",
        "last_sources": [],
        "chat_history": [],
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


init_state()

# Sidebar Control Panel
with st.sidebar:
    st.markdown("<h2 style='text-align: center; margin-bottom: 1rem;'>✨ פאנל בקרה</h2>", unsafe_allow_html=True)
    
    branch_name = get_current_git_branch()
    st.markdown(
        f"<div style='text-align: center; margin-top: -0.8rem; margin-bottom: 1.2rem; font-size: 0.85rem; color: #9CA3AF; font-family: \"Rubik\", sans-serif;'>"
        f"🌿 ענף פעיל: <code style='color: #4F46E5; background-color: #1F2937; padding: 2px 8px; border-radius: 6px; border: 1px solid #374151; font-weight: 600;'>{branch_name}</code>"
        f"</div>",
        unsafe_allow_html=True
    )
    
    api_key = st.text_input("OPENAI_API_KEY", value=OPENAI_API_KEY, type="password")
    st.caption("🔒 אין להעלות מפתח API ל־GitHub. השתמשו בקובץ `.env` מקומי בלבד.")

    st.divider()
    st.markdown("<h3>⚙️ הגדרות שיחה ולוגיסטיקה</h3>", unsafe_allow_html=True)
    use_rag = st.checkbox("השתמש בבסיס ידע RAG", value=True)
    use_image_context = st.checkbox("שלב את ניתוח התמונה", value=True)
    n_sources = st.slider("מספר מקורות RAG", min_value=2, max_value=6, value=4)

    st.divider()
    st.markdown("<h3>📚 בסיס הידע</h3>", unsafe_allow_html=True)
    knowledge_files = read_knowledge_files(KNOWLEDGE_DIR)
    st.write(f"קבצים נטענים: {len(knowledge_files)}")
    with st.expander("הצג קבצי ידע"):
        if knowledge_files:
            for source, text in knowledge_files:
                st.markdown(f"- **{source}** — {len(text)} תווים")
        else:
            st.info("לא נמצאו קבצי ידע בתיקיית knowledge_base")

    rebuild = st.button("🔄 בנה מחדש ChromaDB", use_container_width=True)

    st.divider()

    # Clear chat button
    msg_count = len(st.session_state.chat_history)
    clear_label = f"🗑️ שיחה חדשה ({msg_count} הודעות)" if msg_count else "🗑️ שיחה חדשה"
    if st.button(clear_label, use_container_width=True, disabled=(msg_count == 0)):
        st.session_state.chat_history = []
        st.session_state.last_answer = ""
        st.session_state.last_sources = []
        st.rerun()

    st.divider()
    with st.expander("💡 הצעות לשאלות בדמו"):
        st.markdown(
            """
            * **שיחה כללית:** "מה כדאי להציע ללקוח שמתכנן חתונה עם 250 אורחים?"
            * **שאלת RAG:** "מה מדיניות המקדמה ומה צריך לבדוק לפני אירוע חוץ?"
            * **שילוב תמונה:** "בהתבסס על התמונה ועל בסיס הידע, איזו חבילה כדאי להציע ומה לבדוק לפני סגירה?"
            """
        )

if not api_key:
    st.info("כדי להתחיל, הזינו API Key בסרגל הצד או בקובץ .env מקומי.")
    st.stop()

os.environ["OPENAI_API_KEY"] = api_key
client = create_openai_client(api_key)

if rebuild:
    try:
        with st.spinner("בונה embeddings ומעדכן את ChromaDB..."):
            count = rebuild_vector_db(client)
        st.success(f"בסיס הידע נבנה בהצלחה עם {count} מקטעים")
    except Exception as exc:
        st.error(f"שגיאה בבניית בסיס הידע: {exc}")

tab_chat, tab_image, tab_audio, tab_about = st.tabs([
    "💬 שיחה + RAG",
    "🖼️ ניתוח תמונה",
    "🔊 Text-to-Speech",
    "📌 הסבר לפרויקט",
])

with tab_chat:
    history = st.session_state.chat_history
    MAX_HISTORY = 10

    # Message counter
    if history:
        st.markdown(
            f"<p style='text-align:right; color:#9CA3AF; font-size:0.8rem; font-family:Rubik,sans-serif; margin-bottom:0.5rem;'>"
            f"💬 {len(history)} הודעות"
            f"{' | ⚡ מוצגות 10 אחרונות' if len(history) > MAX_HISTORY else ''}"
            f"</p>",
            unsafe_allow_html=True,
        )

    # Render history (newest at bottom — ChatGPT style)
    displayed = history[-MAX_HISTORY:] if len(history) > MAX_HISTORY else history
    for chat in displayed:
        with st.chat_message("user"):
            st.markdown(chat["question"])
        with st.chat_message("assistant"):
            st.markdown(chat["answer"])

    # RAG sources expander (below last message)
    if st.session_state.last_sources:
        with st.expander("🔍 מקורות RAG שנשלפו עבור השאלה האחרונה"):
            for i, chunk in enumerate(st.session_state.last_sources, start=1):
                st.markdown('<div class="source-card">', unsafe_allow_html=True)
                st.markdown(f"**מקור {i}: {chunk['source']} | מקטע {chunk['chunk_index']}**")
                st.write(chunk["content"])
                st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# Chat input at the TOP LEVEL (outside tabs) so Streamlit pins it fixed to the
# bottom of the viewport natively — exactly like ChatGPT / Gemini.
# ══════════════════════════════════════════════════════════════════════════════
MAX_HISTORY = 10
user_question = st.chat_input("שאל/י על חבילה, מחיר או לוגיסטיקה של האירוע שלכם...")

if user_question:
    try:
        history = st.session_state.chat_history
        # Step 1 — RAG retrieval
        with st.spinner("🔍 שלב 1/2 — מחפש מידע רלוונטי בבסיס הידע..."):
            chunks = retrieve_chunks(client, user_question, n_results=n_sources) if use_rag else []
            rag_context = format_context(chunks)
            image_context = st.session_state.image_analysis if use_image_context else ""

        # Step 2 — AI generation (pass only last MAX_HISTORY turns)
        trimmed_history = history[-MAX_HISTORY:] if len(history) > MAX_HISTORY else history
        with st.spinner("🤖 שלב 2/2 — מייצר תשובה חכמה..."):
            answer = chat_with_ai(
                client,
                user_message=user_question,
                rag_context=rag_context,
                image_analysis=image_context,
                chat_history=trimmed_history,
            )

        st.session_state.last_answer = answer
        st.session_state.last_sources = chunks
        st.session_state.chat_history.append({"question": user_question, "answer": answer})
        st.rerun()

    except Exception as exc:
        st.error(f"❌ שגיאה: {exc}")

with tab_image:
    with st.container(border=True):
        st.subheader("🖼️ יכולת מולטימודלית — העלאת תמונה וניתוח")
        st.write("העלו תמונה של אולם, כניסה, רחבה, או צילום מסך של מקום האירוע.")
        
        uploaded_image = st.file_uploader(
            "📷 גרור לכאן תמונה של מקום האירוע או לחץ לבחירה",
            type=["png", "jpg", "jpeg", "webp"],
        )
        image_prompt = st.text_area(
            "מה תרצה שה־AI יבדוק בתמונה?",
            value="בדוק האם המקום מתאים לבובות מתנפחות ותן המלצות לוגיסטיות ועסקיות",
            height=90,
        )

        if uploaded_image:
            st.image(uploaded_image, caption="התמונה שהועלתה", use_container_width=True)

        if uploaded_image and st.button("נתח תמונה", type="primary", use_container_width=True):
            try:
                with st.spinner("מנתח תמונה באמצעות OpenAI Vision Input..."):
                    image_bytes = uploaded_image.getvalue()
                    st.session_state.image_analysis = analyze_image(
                        client,
                        image_bytes=image_bytes,
                        mime_type=uploaded_image.type or "image/png",
                        prompt=image_prompt,
                    )
                st.success("ניתוח התמונה הושלם")
            except Exception as exc:
                st.error(f"שגיאה בניתוח התמונה: {exc}")

        if st.session_state.image_analysis:
            st.markdown("### 🔍 תוצאת ניתוח התמונה")
            st.info(st.session_state.image_analysis)
            st.info("עכשיו אפשר לעבור ללשונית שיחה + RAG ולסמן 'שלב את ניתוח התמונה'.")

with tab_audio:
    with st.container(border=True):
        st.subheader("🔊 יכולת OpenAI נוספת — Text-to-Speech")
        st.write("לאחר שמתקבלת תשובת AI בלשונית השיחה, ניתן להפוך אותה לקובץ שמע MP3.")

        if st.session_state.last_answer:
            st.markdown("#### 📝 הטקסט האחרון שיומר לשמע")
            st.text_area("תשובת AI אחרונה", value=st.session_state.last_answer, height=150, disabled=True)
            if st.button("🎙️ צור קובץ שמע MP3", type="primary", use_container_width=True):
                try:
                    with st.spinner("יוצר קובץ MP3 באמצעות OpenAI Text-to-Speech..."):
                        audio_path = create_speech(client, st.session_state.last_answer)
                    st.success(f"קובץ השמע נוצר בהצלחה: {Path(audio_path).name}")
                    st.audio(str(audio_path))
                except Exception as exc:
                    st.error(f"שגיאה ביצירת שמע: {exc}")
        else:
            st.info("קודם שלחו שאלה בלשונית שיחה + RAG, ואז ניתן ליצור שמע מהתשובה.")

with tab_about:
    with st.container(border=True):
        st.subheader("📌 עמידה בדרישות הפרויקט והגשה")
        st.markdown(
            """
            | דרישה | מימוש בפרויקט |
            | :--- | :--- |
            | **Conversational AI** | שיחה טבעית בעברית דרך **OpenAI Responses API** |
            | **Multimodal** | העלאת תמונה וניתוח באמצעות **Vision Input** |
            | **RAG** | שימוש ב-**OpenAI Embeddings API** + **ChromaDB** |
            | **יכולת OpenAI נוספת** | המרת טקסט לשמע (**Text-to-Speech**) ליצירת קבצי MP3 |
            | **ממשק משתמש** | אפליקציית Web מודרנית ומעוצבת מבוססת **Streamlit** |
            | **GitHub** | תיעוד מלא, קוד מקור נקי, קובץ requirements.txt והנחיות הרצה |
            """
        )

        st.markdown("#### 📂 קבצי הפרויקט המרכזיים להגשה")
        st.code(
            """README.md
requirements.txt
app.py
src/
knowledge_base/
sample_inputs/
docs/EventPlannerAI_presentation.pptx
docs/DEMO_SCRIPT.md
scripts/verify_project.py""",
            language="text",
        )

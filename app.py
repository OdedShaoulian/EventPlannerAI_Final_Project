from __future__ import annotations

import os
from pathlib import Path

# pyrefly: ignore [missing-import]
import streamlit as st  
# pyrefly: ignore [missing-import]
from dotenv import load_dotenv

import importlib
import src.config
import src.openai_utils
import src.rag
import src.tts

importlib.reload(src.config)
importlib.reload(src.openai_utils)
importlib.reload(src.rag)
importlib.reload(src.tts)

from src.config import BASE_DIR, KNOWLEDGE_DIR, OPENAI_API_KEY
from src.openai_utils import analyze_image, chat_with_ai, create_openai_client
from src.rag import read_knowledge_files, rebuild_vector_db, retrieve_chunks, format_context
from src.tts import create_speech

load_dotenv(BASE_DIR / ".env")

st.set_page_config(page_title="EventPlanner AI", page_icon="🎈", layout="wide")

# Inject premium, luxury celebratory CSS styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Assistant:wght@300;400;600;700&family=Rubik:wght@300;400;500;700&display=swap');

    /* Global fonts and pearl background styling */
    html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
        font-family: 'Assistant', 'Rubik', sans-serif !important;
        background-color: #FAFAFA !important;
        direction: rtl;
        text-align: right;
    }
    
    /* Remove default Streamlit top margin, header, and footer */
    [data-testid="stHeader"] {
        display: none !important;
    }
    footer {
        visibility: hidden !important;
    }
    #MainMenu {
        visibility: hidden !important;
    }
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 2rem !important;
        max-width: 1200px !important;
    }
    
    /* Sidebar styling: Luxury Midnight Blue and Gold */
    [data-testid="stSidebar"] {
        background-color: #0B132B !important;
        border-left: 2.5px solid #C5A880 !important;
    }
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h1,
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h2,
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h3,
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] span,
    [data-testid="stSidebar"] label {
        color: #FFFFFF !important;
        font-family: 'Rubik', sans-serif !important;
    }
    [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
        color: #C5A880 !important;
        font-weight: 600 !important;
        border-bottom: 1px solid rgba(197, 168, 128, 0.2);
        padding-bottom: 0.5rem;
    }
    [data-testid="stSidebar"] div[data-testid="stExpander"] {
        background-color: #141E3C !important;
        border: 1px solid rgba(197, 168, 128, 0.4) !important;
        border-radius: 8px !important;
    }
    
    /* Styled Action Buttons - Gold/Champagne Gradient */
    div.stButton > button {
        background: linear-gradient(135deg, #C5A880 0%, #A38458 100%) !important;
        color: #0B132B !important;
        font-family: 'Rubik', sans-serif !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
        border: 1px solid #C5A880 !important;
        padding: 0.6rem 2rem !important;
        border-radius: 8px !important;
        box-shadow: 0 4px 15px rgba(197, 168, 128, 0.25) !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        width: 100% !important;
    }
    div.stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(197, 168, 128, 0.45) !important;
        background: linear-gradient(135deg, #D4B993 0%, #B59569 100%) !important;
        color: #0B132B !important;
    }
    div.stButton > button:active {
        transform: translateY(1px) !important;
    }

    /* Sidebar primary button styling (rebuild ChromaDB) */
    div[data-testid="stSidebar"] div.stButton > button {
        background: linear-gradient(135deg, #1C2B54 0%, #101B35 100%) !important;
        color: #C5A880 !important;
        border: 1px solid #C5A880 !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4) !important;
    }
    div[data-testid="stSidebar"] div.stButton > button:hover {
        background: linear-gradient(135deg, #25396D 0%, #19274D 100%) !important;
        color: #FFFFFF !important;
        box-shadow: 0 6px 18px rgba(197, 168, 128, 0.25) !important;
    }
    
    /* Luxury container cards */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #FFFFFF !important;
        border: 1px solid #E5E8EB !important;
        border-radius: 12px !important;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.02) !important;
        padding: 1.5rem !important;
        margin-bottom: 1.5rem !important;
    }

    /* Source list item styled card */
    .source-card {
        background-color: #FAF9F6 !important;
        padding: 1.2rem !important;
        border-radius: 10px !important;
        border: 1px dashed rgba(197, 168, 128, 0.4) !important;
        margin-bottom: 1rem !important;
        direction: rtl;
        text-align: right;
    }

    /* Modern Bubble Chat UI customization */
    div[data-testid="stChatMessage"] {
        background-color: transparent !important;
        padding: 0px !important;
        margin-bottom: 1.5rem !important;
        display: flex !important;
        gap: 12px !important;
        align-items: flex-start !important;
    }
    
    /* User Chat Bubble: Gold/Champagne on the Right */
    div[data-testid="stChatMessage"]:has(svg) {
        flex-direction: row-reverse !important;
    }
    div[data-testid="stChatMessage"]:has(svg) > div[data-testid="stChatMessageContent"] {
        background-color: #C5A880 !important;
        color: #0B132B !important;
        border-radius: 18px 18px 2px 18px !important;
        padding: 0.9rem 1.4rem !important;
        box-shadow: 0 4px 15px rgba(197, 168, 128, 0.2) !important;
        border: none !important;
        margin-left: auto !important;
        margin-right: 0px !important;
    }
    div[data-testid="stChatMessage"]:has(svg) > div[data-testid="stChatMessageContent"] p,
    div[data-testid="stChatMessage"]:has(svg) > div[data-testid="stChatMessageContent"] span,
    div[data-testid="stChatMessage"]:has(svg) > div[data-testid="stChatMessageContent"] li,
    div[data-testid="stChatMessage"]:has(svg) > div[data-testid="stChatMessageContent"] strong {
        color: #0B132B !important;
        font-family: 'Rubik', sans-serif !important;
    }
    
    /* Assistant Chat Bubble: Soft White/Gray on the Left */
    div[data-testid="stChatMessage"]:not(:has(svg)) {
        flex-direction: row !important;
    }
    div[data-testid="stChatMessage"]:not(:has(svg)) > div[data-testid="stChatMessageContent"] {
        background-color: #FFFFFF !important;
        color: #1F2937 !important;
        border-radius: 18px 18px 18px 2px !important;
        padding: 0.9rem 1.4rem !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05) !important;
        border: 1px solid #E5E7EB !important;
        margin-right: auto !important;
        margin-left: 0px !important;
    }
    div[data-testid="stChatMessage"]:not(:has(svg)) > div[data-testid="stChatMessageContent"] p,
    div[data-testid="stChatMessage"]:not(:has(svg)) > div[data-testid="stChatMessageContent"] span,
    div[data-testid="stChatMessage"]:not(:has(svg)) > div[data-testid="stChatMessageContent"] li,
    div[data-testid="stChatMessage"]:not(:has(svg)) > div[data-testid="stChatMessageContent"] strong {
        color: #1F2937 !important;
        font-family: 'Assistant', sans-serif !important;
    }

    /* Modern Chat Input floating modern pill styling */
    div[data-testid="stChatInput"] {
        border-radius: 30px !important;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08) !important;
        border: 1px solid #E5E7EB !important;
        background-color: #FFFFFF !important;
        padding: 4px 8px !important;
    }
    div[data-testid="stChatInput"] textarea {
        background-color: transparent !important;
        color: #1F2937 !important;
        font-size: 1rem !important;
        font-family: 'Assistant', sans-serif !important;
    }

    /* Tabs Styling */
    div[data-testid="stTabBar"] {
        background-color: transparent !important;
        border-bottom: 2px solid #E5E7EB !important;
        gap: 24px !important;
        margin-bottom: 1.5rem !important;
    }
    button[data-testid="stMarker"] {
        font-family: 'Rubik', sans-serif !important;
        font-weight: 600 !important;
        font-size: 1.05rem !important;
        color: #64748B !important;
        transition: all 0.25s ease !important;
        background: transparent !important;
        border: none !important;
    }
    button[data-testid="stMarker"][aria-selected="true"] {
        color: #0B132B !important;
        border-bottom: 3px solid #C5A880 !important;
    }
</style>
""", unsafe_allow_html=True)

# Minimalist text header
st.markdown("""
<div style="text-align: center; margin-top: 0.5rem; margin-bottom: 1.5rem;">
    <h1 style="font-family: 'Rubik', sans-serif; font-size: 2.8rem; font-weight: 700; background: linear-gradient(90deg, #0B132B 0%, #C5A880 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; display: inline-block; margin-bottom: 0.1rem;">EventPlanner AI</h1>
    <p style="font-family: 'Assistant', sans-serif; font-size: 1.15rem; color: #4B5563; font-weight: 400; margin-top: 0px;">עוזר ה-AI היוקרתי לתכנון אירועים והפקות מושלמות ✨</p>
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
        f"<div style='text-align: center; margin-top: -0.8rem; margin-bottom: 1.2rem; font-size: 0.85rem; color: #C5A880; font-family: \"Rubik\", sans-serif;'>"
        f"🌿 ענף פעיל: <code style='color: #FFFFFF; background-color: #141E3C; padding: 2px 6px; border-radius: 4px; border: 1px solid rgba(197, 168, 128, 0.3);'>{branch_name}</code>"
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

    rebuild = st.button("בנה מחדש ChromaDB", use_container_width=True)

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
    # Render all chat history messages using st.chat_message
    for chat in st.session_state.chat_history:
        with st.chat_message("user"):
            st.markdown(chat["question"])
        with st.chat_message("assistant"):
            st.markdown(chat["answer"])

    # If sources exist from the last chat, show them here
    if st.session_state.last_sources:
        with st.expander("🔍 מקורות RAG שנשלפו מ־ChromaDB עבור השאלה האחרונה"):
            for i, chunk in enumerate(st.session_state.last_sources, start=1):
                st.markdown('<div class="source-card">', unsafe_allow_html=True)
                st.markdown(f"**מקור {i}: {chunk['source']} | מקטע {chunk['chunk_index']}**")
                st.write(chunk["content"])
                st.markdown('</div>', unsafe_allow_html=True)

    # Bottom chat input
    user_question = st.chat_input("שאל/י על חבילה, מחיר או לוגיסטיקה של האירוע שלכם...")
    if user_question:
        # Display the user question immediately
        with st.chat_message("user"):
            st.markdown(user_question)
        
        try:
            with st.spinner("מחפש ב־ChromaDB ומייצר תשובה דרך OpenAI Responses API..."):
                chunks = retrieve_chunks(client, user_question, n_results=n_sources) if use_rag else []
                rag_context = format_context(chunks)
                image_context = st.session_state.image_analysis if use_image_context else ""
                answer = chat_with_ai(
                    client,
                    user_message=user_question,
                    rag_context=rag_context,
                    image_analysis=image_context,
                    chat_history=st.session_state.chat_history,
                )
                st.session_state.last_answer = answer
                st.session_state.last_sources = chunks
                st.session_state.chat_history.append({"question": user_question, "answer": answer})
                st.rerun()
        except Exception as exc:
            st.error(f"שגיאה בשליחת הבקשה: {exc}")

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

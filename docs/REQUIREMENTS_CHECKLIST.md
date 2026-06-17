# בדיקת עמידה בדרישות המרצה

| דרישה של המרצה | מימוש בפרויקט | קבצים רלוונטיים | סטטוס |
|---|---|---|---|
| אפליקציה מקורית שמפתרת בעיה אמיתית | EventPlanner AI עוזרת לתכנן אירועים, לבחור חבילות ולבדוק לוגיסטיקה | `README.md`, `app.py` | ✅ |
| Conversational AI | שיחה טבעית בעברית עם עוזר AI | `src/openai_utils.py`, `app.py` | ✅ |
| חובה להשתמש ב־OpenAI Responses API | השיחה וניתוח התמונה ממומשים דרך Responses API | `src/openai_utils.py` | ✅ |
| Multimodal | העלאת תמונה וניתוח באמצעות Vision Input | `app.py`, `src/openai_utils.py` | ✅ |
| RAG | בסיס ידע פרטי + Embeddings + ChromaDB | `knowledge_base/`, `src/rag.py` | ✅ |
| חובה להשתמש ב־OpenAI Embeddings API | יצירת embedding למסמכים ולשאלות | `src/rag.py` | ✅ |
| חובה להשתמש ב־ChromaDB | שמירת וקטורים וחיפוש רלוונטי | `src/rag.py` | ✅ |
| יכולת OpenAI נוספת | Text-to-Speech ליצירת MP3 | `src/tts.py` | ✅ |
| לפחות 3 יכולות OpenAI | Responses, Embeddings, Vision, TTS | `src/` | ✅ |
| ממשק משתמש | Web App באמצעות Streamlit | `app.py` | ✅ |
| GitHub | מוכן להעלאה ללא API Key | `.gitignore`, `.env.example` | ✅ |
| README.md | כולל תיאור, יכולות, APIs, התקנה, env, דמו וחברי צוות | `README.md` | ✅ |
| requirements.txt | מכיל את ספריות Python הדרושות | `requirements.txt` | ✅ |
| קבצי RAG | קיימים קבצי ידע בתיקיית knowledge_base | `knowledge_base/` | ✅ |
| מצגת פרויקט | מצגת מוכנה להצגה של 5–10 דקות | `docs/EventPlannerAI_presentation.pptx` | ✅ |
| דמו חי/מוקלט | תסריט ומדריך הקלטה | `docs/DEMO_SCRIPT.md`, `docs/LIVE_DEMO_RECORDING_GUIDE.md` | ✅ |
| הגנה בזום | קובץ הסבר לשקופיות ולשאלות צפויות | `docs/PRESENTATION_NOTES.md`, `docs/DEFENSE_QA.md` | ✅ |

## הערות חשובות להגשה
- אין להעלות את קובץ `.env` ל־GitHub.
- אין להעלות מפתח API אמיתי.
- לפני ההעלאה מומלץ להריץ: `python scripts/verify_project.py`.
- את הסרטון יש להקליט מקומית אחרי הכנסת API Key אמיתי בקובץ `.env` מקומי בלבד.

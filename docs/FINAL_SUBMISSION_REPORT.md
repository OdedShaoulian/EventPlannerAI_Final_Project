# Final Submission Report - EventPlanner AI

## תקציר
EventPlanner AI היא אפליקציית Web מבוססת Generative AI לתכנון אירועים עם בובות מתנפחות. המערכת מאפשרת ללקוח או לאיש מכירות לשאול שאלות, לקבל המלצה לחבילת אירוע, לנתח תמונה של מקום האירוע, לשלוף מידע מבסיס ידע פנימי, ולהפיק קובץ שמע מתשובת העוזר.

## עמידה בדרישות המרכזיות

### Conversational AI
השיחה ממומשת בעזרת OpenAI Responses API. המשתמש כותב שאלה בעברית ומקבל תשובה מקצועית שמתאימה לעולם האירועים.

### Multimodal
המשתמש מעלה תמונה, למשל תמונת כניסה לאולם או רחבת אירוע. המערכת מנתחת את התמונה באמצעות Vision Input ומחזירה תובנות לוגיסטיות ועסקיות.

### RAG
בסיס הידע נמצא בתיקיית `knowledge_base`. הקבצים עוברים chunking, נשלחים ל־OpenAI Embeddings API, נשמרים ב־ChromaDB, ונשלפים לפי רלוונטיות לשאלת המשתמש.

### OpenAI Additional Capability
היכולת הנוספת היא Text-to-Speech. המערכת יוצרת קובץ MP3 מתשובת העוזר.

### UI
הממשק נבנה ב־Streamlit ומחולק ללשוניות ברורות: שיחה + RAG, ניתוח תמונה, Text-to-Speech והסבר לפרויקט.

## קבצים להגשה
- `app.py`
- `src/`
- `knowledge_base/`
- `sample_inputs/`
- `docs/`
- `README.md`
- `requirements.txt`
- `.env.example`
- `.gitignore`
- `scripts/verify_project.py`

## קבצים שלא להעלות
- `.env`
- `chroma_db/`
- `audio_output/`
- `uploads/`
- `__pycache__/`
- `*.pyc`

## הוראות בדיקה מהירות
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python scripts/verify_project.py
streamlit run app.py
```

## הערה אחרונה
הפרויקט מוכן להעלאה ל־GitHub ולהקלטת דמו. כדי להקליט את הדמו בפועל צריך להריץ את האפליקציה עם OpenAI API Key אישי בקובץ `.env` מקומי בלבד.

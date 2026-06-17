# צ'ק ליסט העלאה ל־GitHub

לפני העלאה ל־GitHub יש לוודא:

- [ ] העליתם את `app.py`
- [ ] העליתם את תיקיית `src`
- [ ] העליתם את תיקיית `knowledge_base`
- [ ] העליתם את תיקיית `docs`
- [ ] העליתם את `README.md`
- [ ] העליתם את `requirements.txt`
- [ ] העליתם את `.env.example`
- [ ] לא העליתם קובץ `.env`
- [ ] לא העליתם מפתח API אמיתי
- [ ] לא העליתם תיקיות `__pycache__`
- [ ] לא העליתם קבצי `*.pyc`
- [ ] לא העליתם תיקיית `chroma_db`
- [ ] לא העליתם תיקיית `audio_output`

## פקודות בדיקה לפני העלאה

אפשר להריץ בתיקיית הפרויקט:

```bash
find . -name "__pycache__" -o -name "*.pyc" -o -name ".env"
```

אם הפקודה מחזירה תוצאות, לא להעלות עדיין. צריך למחוק את הקבצים/תיקיות האלו.

## קבצים שצריכים להיות במאגר

```text
app.py
README.md
requirements.txt
.env.example
.gitignore
src/
knowledge_base/
sample_inputs/
docs/
```

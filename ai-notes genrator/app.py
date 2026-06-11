import os
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
import sqlite3
import pytesseract
from PIL import Image
pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)
from PyPDF2 import PdfReader
from dotenv import load_dotenv
from pydoc import text
from groq import Groq
from flask_dance.contrib.google import make_google_blueprint, google
from flask import jsonify
from flask import (
    Flask, render_template, request, redirect, 
    url_for, flash, session, send_file
)
from typer import prompt
try:
    from flask_sqlalchemy import SQLAlchemy
except ImportError:
    print("ERROR: flask_sqlalchemy is not installed. Run: pip install flask-sqlalchemy")
    raise
from werkzeug.security import generate_password_hash, check_password_hash
from services.pdf_service import extract_pdf_text

# Load environment variables
load_dotenv()

app = Flask(__name__)
google_bp = make_google_blueprint(

    client_id=os.getenv("GOOGLE_CLIENT_ID"),

    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),

    scope=[
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile"
]

)

app.register_blueprint(
    google_bp,
    url_prefix="/login"
)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///notes.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
app.secret_key = os.getenv("SECRET_KEY")
if not os.getenv("GROQ_API_KEY"):
    print("WARNING: GROQ_API_KEY not found")
# ====================== IMPORT MODELS & SERVICES ======================
from database.db import get_connection
from models.user_model import UserModel
from models.note_model import NoteModel
from services.gemini_service import call_ai, chat_with_notes
from services.docx_service import extract_docx_text
from services.gemini_service import (
    generate_summary,
    generate_detailed_notes,
    generate_key_concepts,
    generate_revision_notes,
    generate_flashcards,
    generate_quiz,
    chat_with_notes
)
from io import BytesIO
from models.tutor_model import TutorModel

from flask import send_file
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter
from flask import send_file

# Initialize Groq client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# ====================== ROUTES ======================

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = UserModel.get_user_by_email(email)

        if user and check_password_hash(user["password"], password):
            session["user_id"] = user["id"]
            session["user_name"] = user["name"]
            flash("Login Successful!", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid email or password!", "danger")

    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")

        if UserModel.get_user_by_email(email):
            flash("Email already exists!", "warning")
            return redirect(url_for("register"))

        hashed_password = generate_password_hash(password)
        UserModel.create_user(name, email, hashed_password)

        flash("Registration Successful! Please login.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")

@app.route("/google-login")
def google_login():

    if not google.authorized:

        return redirect(url_for("google.login"))

    resp = google.get("/oauth2/v2/userinfo")

    info = resp.json()

    session["user_id"] = info["email"]

    session["user_name"] = info["name"]

    session["logged_in"] = True

    flash("Google Login Successful!")

    return redirect("/dashboard")

@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        flash("Please login first.", "warning")
        return redirect(url_for("login"))

    conn = get_connection()
    cursor = conn.cursor()

    # Total notes
    cursor.execute("SELECT COUNT(*) FROM notes WHERE user_id = ?", (session["user_id"],))
    total_notes = cursor.fetchone()[0]

    # Recent 3 notes
    cursor.execute("""
        SELECT * FROM notes
        WHERE user_id = ?
        ORDER BY id DESC
        LIMIT 3
    """, (session["user_id"],))
    recent_notes = cursor.fetchall()

    conn.close()

    return render_template(
        "dashboard.html",
        total_notes=total_notes,
        recent_notes=recent_notes,
        user_name=session.get("user_name", "Student")
    )


@app.route("/upload")
def upload():
    return render_template("upload.html")

@app.route("/generate-notes", methods=["POST"])
def generate_notes():

    text = request.form.get("study_text", "").strip()
    language = request.form.get("language", "English")
    title = request.form.get("title", "").strip()
    print("SELECTED LANGUAGE:", language)

    uploaded_file = request.files.get("file")

    # Handle uploaded file
    if uploaded_file and uploaded_file.filename:

        filename = uploaded_file.filename.lower()

        try:

            # PDF
            if filename.endswith(".pdf"):
                text = extract_pdf_text(uploaded_file)

            # DOCX
            elif filename.endswith(".docx"):
                text = extract_docx_text(uploaded_file)

        except Exception as e:

            print("File Error:", e)

            flash(
                "Unable to read uploaded file.",
                "danger"
            )

            return redirect(url_for("upload"))

    # Validate text
    if not text:

        flash(
            "Please enter text or upload a file.",
            "warning"
        )

        return redirect(url_for("upload"))

    if len(text) < 50:

        flash(
            "Please provide at least 50 characters.",
            "warning"
        )

        return redirect(url_for("upload"))

    # Generate AI Notes
    try:

        summary = generate_summary(text, language)

        detailed_notes = generate_detailed_notes(text, language)

        key_concepts = generate_key_concepts(text, language)

        revision_notes = generate_revision_notes(text, language)

    except Exception as e:

        print("AI Error:", e)

        flash(
            "Unable to generate notes.",
            "danger"
        )

        return redirect(url_for("upload"))

    # Save to database
    try:

        NoteModel.create_note(
            user_id=session["user_id"],
            title=title,
            original_content=text,
            summary=summary,
            detailed_notes=detailed_notes,
            key_concepts=key_concepts,
            revision_notes=revision_notes,
            flashcards="",
            quiz_questions=""
        )

    except Exception as e:

        print("Save Error:", e)

    combined_text = f"""
SUMMARY:
{summary}

DETAILED NOTES:
{detailed_notes}

KEY CONCEPTS:
{key_concepts}

REVISION NOTES:
{revision_notes}
"""

    title = request.form.get("title", "").strip()
    if not title:
        title = text[:40] + "..."

    return render_template(
        "view_note.html",
        note={
            "id": 0,
            "title": title,
            "summary": summary,
            "detailed_notes": detailed_notes,
            "key_concepts": key_concepts,
            "revision_notes": revision_notes,
            "combined_text": combined_text,
            "language": language
        }
    )

@app.route("/flashcards", methods=["POST"])
def flashcards():
    text = request.form.get("study_text")
    
    language = request.form.get("language", "English")
    
    print("FLASHCARD TEXT:", text)
    print("FLASHCARD LANGUAGE:", language)


    if not text:
        flash("Please enter text.", "warning")
        return redirect(url_for("upload"))

    try:
       raw = generate_flashcards(text, language)


    except Exception as e:
        print("Flashcard Error:", e)
        flash(
            "Unable to generate flashcards.",
            "danger"
        )
        return redirect(url_for("upload"))

    cards = []
    lines = raw.strip().split("\n")
    question = None
    answer = None

    for line in lines:
        line = line.strip()
        if not line:
            continue
        if line.startswith("Q") and ":" in line:
            question = line.split(":", 1)[1].strip()
        elif line.startswith("A") and ":" in line:
            answer = line.split(":", 1)[1].strip()
            if question and answer:
                cards.append({"question": question, "answer": answer})
                question = None
                answer = None

    if len(cards) == 0:
        flash(
            "No flashcards could be generated.",
            "warning"
        )
        return redirect(url_for("upload"))

    return render_template(
        "flashcards.html",
        cards=cards,
        total=len(cards)
    )


@app.route("/quiz", methods=["POST"])
def quiz():

    text = request.form.get("study_text")

    language = request.form.get("language", "English")

    print("QUIZ TEXT:", text)
    print("QUIZ LANGUAGE:", language)

    if not text:

        flash(
            "Please enter text.",
            "warning"
        )

        return redirect(url_for("upload"))

    try:

        raw = generate_quiz(text, language)

        print(raw)

    except Exception as e:

        print("Quiz Error:", e)

        flash(
            "Unable to generate quiz.",
            "danger"
        )

        return redirect(url_for("upload"))

    questions = []

    lines = [
        line.strip()
        for line in raw.split("\n")
        if line.strip()
    ]

    current = {}

    for line in lines:

        if line.startswith("Q"):

            current = {}

            current["question"] = line.split(":", 1)[1].strip()

        elif line.startswith("A:"):

            current["A"] = line.split(":", 1)[1].strip()

        elif line.startswith("B:"):

            current["B"] = line.split(":", 1)[1].strip()

        elif line.startswith("C:"):

            current["C"] = line.split(":", 1)[1].strip()

        elif line.startswith("D:"):

            current["D"] = line.split(":", 1)[1].strip()

        elif line.startswith("ANS:"):

            current["answer"] = line.split(":", 1)[1].strip()

            if (
                "question" in current and
                "A" in current and
                "B" in current and
                "C" in current and
                "D" in current
            ):

                questions.append({
                    "question": current["question"],
                    "options": {
                        "A": current["A"],
                        "B": current["B"],
                        "C": current["C"],
                        "D": current["D"]
                    },
                    "answer": current["answer"]
                })

    if len(questions) == 0:

        flash(
            "Quiz generation failed.",
            "warning"
        )

        return redirect(url_for("upload"))

    return render_template(
        "quiz.html",
        questions=questions,
        total=len(questions)
    )

@app.route("/quiz-result", methods=["POST"])
def quiz_result():
    import json
    questions = json.loads(request.form.get("questions", "[]"))
    total = len(questions)
    score = 0
    results = []

    for i, q in enumerate(questions):
        user_answer = request.form.get(f"answer_{i}", "")
        correct = q["answer"]
        is_correct = user_answer == correct

        if is_correct:
            score += 1

        results.append({
            "question": q["question"],
            "options": q["options"],
            "correct": correct,
            "user_answer": user_answer,
            "is_correct": is_correct
        })

    percentage = round((score / total) * 100) if total > 0 else 0

    return render_template(
        "quiz_result.html",
        results=results,
        score=score,
        total=total,
        percentage=percentage
    )


@app.route("/my-notes")
def my_notes():
 

    if "user_id" not in session:
        flash("Please login first.", "warning")
        return redirect(url_for("login"))

    search = request.args.get("search", "").strip()

    conn = get_connection()
    cursor = conn.cursor()

    if search:

        cursor.execute("""
            SELECT *
            FROM notes
            WHERE user_id = ?
            AND (
                title LIKE ?
                OR summary LIKE ?
                OR key_concepts LIKE ?
            )
            ORDER BY id DESC
        """, (
            session["user_id"],
            f"%{search}%",
            f"%{search}%",
            f"%{search}%"
        ))

    else:

        cursor.execute("""
            SELECT *
            FROM notes
            WHERE user_id = ?
            ORDER BY id DESC
        """, (session["user_id"],))

    notes = cursor.fetchall()

    conn.close()

    return render_template(
        "my_notes.html",
        notes=notes
    )


@app.route("/view-note/<int:note_id>")
def view_note(note_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM notes WHERE id = ?", (note_id,))
    note = cursor.fetchone()
    conn.close()

    if not note:
        flash("Note not found.", "danger")
        return redirect(url_for("my_notes"))

    return render_template("view_note.html", note=note)


@app.route("/delete-note/<int:note_id>")
def delete_note(note_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM notes WHERE id = ?", (note_id,))
    conn.commit()
    conn.close()

    flash("Note deleted successfully.", "success")
    return redirect(url_for("my_notes"))


@app.route("/save-notes", methods=["POST"])
def save_notes():
    if "user_id" not in session:
        flash("Please login to save notes.", "warning")
        return redirect(url_for("login"))

    title = request.form.get("title") or "Untitled Notes"
    original_content = request.form.get("original_content")
    summary = request.form.get("summary")
    detailed_notes = request.form.get("detailed_notes")
    key_concepts = request.form.get("key_concepts")
    revision_notes = request.form.get("revision_notes")
    subject = request.form.get("subject")

    try:
        NoteModel.create_note(
            user_id=session["user_id"],
            title=title,
            original_content=original_content,
            summary=summary,
            detailed_notes=detailed_notes,
            key_concepts=key_concepts,
            revision_notes=revision_notes,
            flashcards="",
            quiz_questions=""
        )
        flash("Notes saved successfully!", "success")
    except Exception as e:
        print("Save Note Error:", e)
        flash(
            "Unable to save note.",
            "danger"
        )
    return redirect(url_for("my_notes"))


@app.route("/chat", methods=["POST"])
def chat():

    data = request.get_json()

    question = data.get("message", "").strip()

    notes = data.get("notes", "")

    language = data.get("language", "English")

    history = data.get("history", [])

    if not question:

        return jsonify({
            "reply": "Please enter a question."
        })

    try:

        conversation = ""

        for item in history[-5:]:

            conversation += f"""
User: {item.get('user')}

Assistant: {item.get('bot')}
"""

        prompt = f"""
You are an intelligent academic AI tutor.

IMPORTANT:
- Reply ONLY in {language}
- Answer clearly and professionally
- Use bullet points when useful
- Explain step-by-step
- Keep answers student-friendly

STUDY NOTES:
{notes[:2000]}

PREVIOUS CONVERSATION:
{conversation}

STUDENT QUESTION:
{question}
"""

        print("CHAT QUESTION:", question)
        print("CHAT LANGUAGE:", language)

        response = call_ai(prompt)

        print("CHAT RESPONSE:", response)

        return jsonify({
            "reply": response
        })

    except Exception as e:

        print("CHAT ERROR:", e)

        return jsonify({
            "reply": "AI assistant unavailable right now."
        })

@app.route("/interview", methods=["GET", "POST"])
def interview():

    if request.method == "POST":

        topic = request.form.get("topic", "").strip()

        language = request.form.get(
            "language",
            "English"
        )

        if not topic:

            return render_template(
                "interview.html",
                error="Please enter a topic."
            )

        prompt = f"""
Generate professional interview preparation content.

TOPIC:
{topic}

LANGUAGE:
{language}

Generate:

1. 10 HR Interview Questions
2. 10 Technical Questions
3. 5 Advanced Questions
4. Sample answers for each
5. Tips for cracking interview

Format clearly.
"""

        response = call_ai(prompt)

        return render_template(
            "interview.html",
            result=response,
            topic=topic
        )

    return render_template("interview.html")

@app.route("/mock-interview", methods=["GET", "POST"])
def mock_interview():

    if request.method == "POST":

        data = request.get_json()

        topic = data.get("topic", "")

        answer = data.get("answer", "")

        history = data.get("history", [])

        conversation = ""

        for item in history:

            conversation += f"""
Interviewer: {item['question']}

Candidate: {item['answer']}
"""

        prompt = f"""
You are an expert AI interviewer.

JOB ROLE:
{topic}

PREVIOUS INTERVIEW:
{conversation}

LATEST ANSWER:
{answer}

Your tasks:

1. Evaluate the answer
2. Give:
   - Communication Score (/10)
   - Technical Score (/10)
   - Confidence Score (/10)
   - Overall Score (/10)

3. Mention:
   - Strengths
   - Weaknesses
   - Improvements

4. Ask NEXT interview question

FORMAT:

## Feedback
Communication Score: x/10
Technical Score: x/10
Confidence Score: x/10
Overall Score: x/10

Strengths:
- ...

Weaknesses:
- ...

Improvements:
- ...

## Next Question
...
"""

        response = call_ai(prompt)

        return jsonify({
            "reply": response
        })

    return render_template("mock_interview.html")

@app.route("/resume-analyzer", methods=["GET", "POST"])
def resume_analyzer():
    job_role = request.form.get("job_role")
    if request.method == "POST":

        file = request.files.get("resume")

        if not file:

            return render_template(
                "resume_analyzer.html",
                error="Upload resume PDF"
            )

        text = ""

        try:

            pdf = PdfReader(file)

            for page in pdf.pages:

                extracted = page.extract_text()

                if extracted:
                    text += extracted

        except Exception as e:

            print("PDF ERROR:", e)

            return render_template(
                "resume_analyzer.html",
                error="Unable to read PDF"
            )

        prompt = f"""
You are an expert ATS Resume Analyzer.

Analyze this resume for the job role:

JOB ROLE:
{job_role}

RESUME:
{text[:6000]}

Give:

1. ATS Score (/100)
2. Matching Skills
3. Missing Skills
4. Resume Strengths
5. Weaknesses
6. Grammar Improvements
7. Suggested Projects
8. Suggested Certifications
9. Interview Readiness
10. Hiring Probability
11. Final Verdict

Format clearly.
"""

        result = call_ai(prompt)

        return render_template(
            "resume_analyzer.html",
            result=result
        )

    return render_template(
        "resume_analyzer.html"
    )

@app.route("/ats-checker")
def ats_checker():

    if "user_id" not in session:
        return redirect(url_for("login"))

    return render_template("ats_checker.html")

@app.route("/analyze-resume", methods=["POST"])
def analyze_resume():

    if "user_id" not in session:
        return redirect(url_for("login"))

    job_role = request.form.get("job_role")

    resume_text = request.form.get("resume_text")

    if not resume_text:
        return "Resume text missing"

    prompt = f"""
You are an expert ATS Resume Analyzer.

Analyze this resume for the job role:
{job_role}

Resume:
{resume_text}

Give response in this format:

ATS SCORE: xx/100

MISSING SKILLS:
- skill 1
- skill 2

STRONG SKILLS:
- skill 1
- skill 2

IMPROVEMENTS:
- improvement 1
- improvement 2

HIRING CHANCE:
- Low / Medium / High

FINAL SUGGESTION:
- final advice
"""

    result = call_ai(prompt)

    return render_template(
        "ats_result.html",
        result=result,
        job_role=job_role
    )

@app.route("/ai-tutor", methods=["GET", "POST"])
def ai_tutor():
    answer = ""
    question = ""

    if request.method == "POST":
        question = request.form.get("question")
        level = request.form.get("level")
        language = request.form.get("language")

        prompt = f"""


You are an expert AI Tutor.

Explain this topic clearly.

QUESTION:
{question}

LEVEL:
{level}

LANGUAGE:
{language}

Your response should include:

1. Simple explanation
2. Step-by-step breakdown
3. Real-life example
4. Key points
5. Interview tips

Keep explanation easy and engaging.
"""


        try:

            completion = client.chat.completions.create(

                model="llama-3.1-8b-instant",

                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],

                temperature=0.7,
                max_tokens=1024
            )

            answer = completion.choices[0].message.content
            TutorModel.save_chat(
                session["user_id"],
                question,
                answer
            )

            # SAVE IN SESSION
            session["ai_answer"] = answer

        except Exception as e:

            session["ai_answer"] = f"Error: {str(e)}"

            return redirect(url_for("ai_tutor"))

    answer = session.get("ai_answer")
    chat_history = TutorModel.get_user_chats(
session["user_id"]
)

    return render_template(
"tutor.html",
answer=answer,
question=question,
chat_history=chat_history
)

@app.route("/ocr-notes", methods=["GET", "POST"])
def ocr_notes():

    extracted_text = ""
    error = ""
    image_name = ""

    if request.method == "POST":

        image = request.files.get("image")
        if image and image.filename != "":
            try:
                import os
                from PIL import Image
                import pytesseract

                pytesseract.pytesseract.tesseract_cmd = (
                    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
                )

                upload_folder = "static/uploads"

                os.makedirs(upload_folder, exist_ok=True)

                image_path = os.path.join(
                    upload_folder,
                    image.filename
                )

                image.save(image_path)

                image_name = image.filename

                print("IMAGE SAVED:", image_path)

                # OPEN IMAGE
                img = Image.open(image_path)

                # DEBUG
                print("IMAGE SIZE:", img.size)
                print("IMAGE MODE:", img.mode)

                # CONVERT
                img = img.convert("RGB")
                img = img.convert("L")

                # OCR
                extracted_text = pytesseract.image_to_string(img)

                print("OCR RESULT:")
                print(repr(extracted_text))

                if not extracted_text.strip():

                    extracted_text = """
⚠ No text detected.

Try:
• Clear screenshot
• Bigger text
• White background
• PNG image
"""

            except Exception as e:
                error = str(e)

                print("OCR ERROR:", error)
    return render_template(
        "ocr_notes.html",
        extracted_text=extracted_text,
        error=error,
        image_name=image_name
    )

@app.route("/analytics")
def analytics():

    if "user_id" not in session:
        return redirect(url_for("login"))

    user_id = session["user_id"]

    # Get all notes
    notes = NoteModel.get_user_notes(user_id)

    total_notes = len(notes)

    analytics = {
        "total_notes": total_notes,
        "study_time": total_notes * 10,
        "recent_notes": notes[:5]
    }

    return render_template(
        "analytics.html",
        analytics=analytics
    )

@app.route("/roadmap", methods=["GET", "POST"])
def roadmap():

    roadmap_text = ""
    career_goal = ""

    if request.method == "POST":

        career_goal = request.form.get("career_goal")
        level = request.form.get("level")
        duration = request.form.get("duration")

        # FRONTEND

        if career_goal == "Frontend Developer":

            roadmap_text = f"""
🚀 Frontend Developer Roadmap

📌 Level: {level}
📅 Duration: {duration}

STEP 1:
Learn HTML, CSS, JavaScript

STEP 2:
Learn Responsive Design

STEP 3:
Learn React.js

STEP 4:
Build Projects

STEP 5:
Learn Git & GitHub

STEP 6:
Prepare Portfolio

Recommended Skills:
HTML
CSS
JavaScript
React
Bootstrap
Git
"""

        # DATA SCIENCE

        elif career_goal == "Data Scientist":

            roadmap_text = f"""
🚀 Data Scientist Roadmap

📌 Level: {level}
📅 Duration: {duration}

STEP 1:
Learn Python

STEP 2:
Learn NumPy & Pandas

STEP 3:
Learn Data Visualization

STEP 4:
Learn Machine Learning

STEP 5:
Build ML Projects

STEP 6:
Practice Interviews

Recommended Skills:
Python
Pandas
NumPy
Scikit-learn
SQL
Power BI
"""

        # AI ENGINEER

        elif career_goal == "AI Engineer":

            roadmap_text = f"""
🚀 AI Engineer Roadmap

📌 Level: {level}
📅 Duration: {duration}

STEP 1:
Learn Python

STEP 2:
Learn Machine Learning

STEP 3:
Learn Deep Learning

STEP 4:
Learn NLP & LLMs

STEP 5:
Build AI Projects

STEP 6:
Deploy AI Applications

Recommended Skills:
Python
TensorFlow
PyTorch
Transformers
LLMs
LangChain
"""

    return render_template(
        "roadmap.html",
        roadmap=roadmap_text,
        career_goal=career_goal
    )

@app.route("/update-study-time", methods=["POST"])
def update_study_time():

    from flask import request, jsonify

    if "user_id" not in session:
        return jsonify({"success": False})

    minutes = int(request.form.get("minutes"))

    session["study_time"] = session.get("study_time", 0) + minutes

    return jsonify({
        "success": True,
        "total_time": session["study_time"]
    })



@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully.", "info")
    return redirect(url_for("login"))

@app.errorhandler(404)
def page_not_found(error):

    return render_template(
        "404.html"
    ), 404


@app.errorhandler(500)
def server_error(error):

    return render_template(
        "500.html"
    ), 500


@app.route("/download-pdf", methods=["POST"])
def download_pdf():

    title = request.form.get("title", "AI Notes")

    summary = request.form.get("summary", "")
    detailed_notes = request.form.get("detailed_notes", "")
    key_concepts = request.form.get("key_concepts", "")
    revision_notes = request.form.get("revision_notes", "")

    filename = "ai_notes.pdf"

    doc = SimpleDocTemplate(
        filename,
        pagesize=letter
    )

    styles = getSampleStyleSheet()
    story = []

    # Title
    story.append(
        Paragraph(f"<b>{title}</b>", styles['Title'])
    )

    story.append(Spacer(1, 20))

    sections = [
        ("Summary", summary),
        ("Detailed Notes", detailed_notes),
        ("Key Concepts", key_concepts),
        ("Revision Notes", revision_notes)
    ]

    for heading, content in sections:

        story.append(
            Paragraph(f"<b>{heading}</b>", styles['Heading2'])
        )

        story.append(Spacer(1, 10))

        content = content.replace("\n", "<br/>")

        story.append(
            Paragraph(content, styles['BodyText'])
        )

        story.append(Spacer(1, 20))

    doc.build(story)

    return send_file(
        filename,
        as_attachment=True
    )


@app.route("/library")
def library():

    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT id,title,created_at
    FROM notes
    WHERE user_id=?
    ORDER BY id DESC
    """, (session["user_id"],))

    notes = cursor.fetchall()

    conn.close()

    return render_template(
        "library.html",
        notes=notes
    )

@app.route("/favorite/<int:note_id>")
def toggle_favorite(note_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE notes
        SET is_favorite =
        CASE
            WHEN is_favorite = 1 THEN 0
            ELSE 1
        END
        WHERE id = ?
    """, (note_id,))

    conn.commit()
    conn.close()

    return redirect(url_for("library"))

@app.route("/favorites")
def favorites():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM notes
        WHERE user_id = ?
        AND is_favorite = 1
    """, (session["user_id"],))

    notes = cursor.fetchall()

    conn.close()

    return render_template(
        "favorites.html",
        notes=notes
    )

if __name__ == "__main__":

    app.config["JSON_AS_ASCII"] = False

    with app.app_context():
        db.create_all()

   

port = int(os.environ.get("PORT", 5000))

app.run(
    host="0.0.0.0",
    port=port
)

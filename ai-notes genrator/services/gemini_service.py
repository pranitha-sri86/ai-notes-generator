import importlib
import os
from pathlib import Path





def load_dotenv_file():
    env_path = Path(__file__).resolve().parents[1] / ".env"
    if not env_path.exists():
        return
    with env_path.open("r", encoding="utf-8") as env_file:
        for line in env_file:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip().strip('"\''))

load_dotenv_file()

try:
    groq_module = importlib.import_module("groq")
    Groq = groq_module.Groq
except ImportError as exc:
    raise ImportError(
        "The groq package is required. Install it with `pip install groq`."
    ) from exc

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

def call_ai(prompt):

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        temperature=0.3,
        max_tokens=2048,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a multilingual academic tutor. "
                    "Always obey the requested language strictly."
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response.choices[0].message.content



def generate_summary(text, language="English"):

    prompt = f"""
IMPORTANT:

Respond STRICTLY in {language}.

RULES:
- Do NOT use English.
- Do NOT mix languages.
- Translate all explanations into {language}.
- Every heading and bullet point must be in {language}.

Generate detailed study notes for students.

Study Material:
{text}
"""

    return call_ai(prompt)


def generate_detailed_notes(text, language="English"):

    prompt = f"""
IMPORTANT:

Respond STRICTLY in {language} only.

Do NOT use English.

Create comprehensive detailed study notes.

Study Material:
{text}
"""

    return call_ai(prompt)


def generate_key_concepts(text, language="English"):

    prompt = f"""
IMPORTANT:

Respond ONLY in {language}.

Explain all concepts in simple {language}.

Study Material:
{text}
"""

    return call_ai(prompt)


def generate_revision_notes(text, language="English"):

    prompt = f"""
IMPORTANT:

Respond STRICTLY in {language}.

Generate short revision notes and exam points.

Study Material:
{text}
"""

    return call_ai(prompt)
def generate_flashcards(text, language="English"):

    prompt = f"""
IMPORTANT:

Generate ALL flashcards ONLY in {language}.

Return EXACTLY in this format:

Q1: question
A1: answer

Q2: question
A2: answer

Q3: question
A3: answer

Continue until Q15 and A15.

RULES:
- Do NOT add extra explanations.
- Do NOT add markdown.
- Do NOT add headings.
- Keep answers short and clear.

Study Material:
{text}
"""

    return call_ai(prompt)


def generate_quiz(text, language="English"):

    prompt = f"""
IMPORTANT:

Generate ALL quiz questions ONLY in {language}.

Return EXACTLY in this format:

Q1: Question here
A: Option A
B: Option B
C: Option C
D: Option D
ANS: A

Q2: Question here
A: Option A
B: Option B
C: Option C
D: Option D
ANS: B

Continue until Q10.

RULES:
- No markdown
- No explanations
- No extra text
- Only the format above

Study Material:
{text}
"""

    return call_ai(prompt)

def chat_with_notes(notes, question, language="English"):

    notes = notes[:3000]

    prompt = f"""
IMPORTANT:

Answer STRICTLY in {language}.

Notes:
{notes}

Question:
{question}
"""

    return call_ai(prompt)


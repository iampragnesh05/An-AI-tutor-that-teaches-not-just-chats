# AI Learning Tutor 🎓

An end-to-end **AI-powered learning tutor** built with:
- Python
- Streamlit
- LangChain
- ChatGPT (OpenAI API)
- RAG (PDF-based learning)
- Agent-based decision making
- Persistent memory (SQLite)

## Features
- Upload PDFs as learning material
- Automatic syllabus extraction
- Lesson planning and step-by-step teaching
- Conceptual quizzes with feedback
- Adaptive difficulty based on learner mastery
- Persistent progress across sessions

## Tech Stack
- Python 3.14
- Streamlit
- LangChain
- OpenAI API
- SQLite
- BM25 retrieval (rank-bm25)



## Setup
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```
Create .env:
```
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-4o-mini
```
Run:
```
python -m streamlit run app/main.py
```
Status

🚧 Actively evolving — next steps include remediation loops, analytics, and multi-document learning.

---

### 3️⃣ Verify `requirements.txt`
Make sure it matches what you actually use:
```txt
streamlit
python-dotenv
openai
langchain
langchain-openai
rank-bm25
pypdf
```

4️⃣ One clean Git commit sequence
```
git init
git add .# AI Learning Tutor 🎓

An end-to-end **AI-powered learning tutor** built with:
- Python
- Streamlit
- LangChain
- ChatGPT (OpenAI API)
- RAG (PDF-based learning)
- Agent-based decision making
- Persistent memory (SQLite)

## Features
- Upload PDFs as learning material
- Automatic syllabus extraction
- Lesson planning and step-by-step teaching
- Conceptual quizzes with feedback
- Adaptive difficulty based on learner mastery
- Persistent progress across sessions

## Tech Stack
- Python 3.14
- Streamlit
- LangChain
- OpenAI API
- SQLite
- BM25 retrieval (rank-bm25)



## Setup
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```
Create .env:
```
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-4o-mini
```
Run:
```
python -m streamlit run app/main.py
```
Status

🚧 Actively evolving — next steps include remediation loops, analytics, and multi-document learning.

---

### 3️⃣ Verify `requirements.txt`
Make sure it matches what you actually use:
```txt
streamlit
python-dotenv
openai
langchain
langchain-openai
rank-bm25
pypdf
```

4️⃣ One clean Git commit sequence
```
git init
git add .
git commit -m "Initial commit: AI Learning Tutor with RAG, agent, memory, and lesson planning"
```

Then:
```
git branch -M main
git remote add origin https://github.com/iampragnesh05/AI-LLM-Tutorial.git
git push -u origin main
```



```
git commit -m "Initial commit: AI Learning Tutor with RAG, agent, memory, and lesson planning"
```

Then:
```
git branch -M main
git remote add origin https://github.com/iampragnesh05/AI-LLM-Tutorial.git
git push -u origin main
```



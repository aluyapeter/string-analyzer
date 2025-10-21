# String Analyzer Service (FastAPI + Railway)

A RESTful API that analyzes strings and stores their properties.

## 🧩 Features
- Analyzes strings (length, palindrome, unique chars, words, sha256 hash)
- Saves results to DB (PostgreSQL on Railway / SQLite locally)
- Filter and query by properties or natural language
- 5 full endpoints + validation

## ⚙️ Setup (Local)
```bash
git clone <your-repo>
cd string-analyzer
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
uvicorn main:app --reload

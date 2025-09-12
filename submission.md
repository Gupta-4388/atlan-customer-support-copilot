Project: **Customer Support Copilot**  
Author: Boddu Lakshmi Narayana Gupta (AI Engineer Intern)

---

## What I submitted
- **Streamlit app:** `app.py` (bulk dashboard + interactive assistant)  
- **Ingest helper:** `ingest.py` (loads tickets + fetches docs from curated URLs)  
- **Local DB:** `data/chroma_db/` (Chroma persistent storage)  
- **Sample tickets/docs:** `data/`  
- **Requirements:** `requirements.txt`  
- **Documentation:** `README.md`, `submission.md`  

---

## How to run
1. Ensure **Python 3.11+** is installed.  
2. Create a virtual environment and install dependencies:

```bash
python -m venv venv
venv\Scripts\activate   # Windows
pip install -r requirements.txt
````

3. Set up environment variables in `.env` (example in `.env.example`):

```env
OPENAI_API_KEY=your_key_here
OPENAI_CHAT_MODEL=gpt-4o-mini
CHROMA_DB_PATH=./data/chroma_db
```

4. Run ingestion (optional, only if DB is empty):

```bash
python ingest.py
```

5. Launch the Streamlit app:

```bash
streamlit run app.py
```

---

## Notes / Next Steps

* **Future improvement:** Add more SDK docs to improve RAG answer precision.
* **Future improvement:** Tweak classifier heuristics or integrate OpenAI API for better ticket classification.
* **RAG answer note:** Currently, answers are illustrative if relevant SDK docs are not present in `data/docs/`.
* **Chroma DB path:** The app uses `./data/chroma_db/` for local persistence. Ensure this folder exists and is writable.

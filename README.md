# Study Bot

> **RAG Workshop &middot; ATMOS &rsquo;26**  
> **IEEE Student Branch, BITS Pilani Hyderabad Campus**  
> Developed by **Saksham Gupta**

A polished Gradio study-chat interface for the **"Build Your Own StudyBot"** workshop. It runs on top of a Retrieval-Augmented Generation (RAG) backend over textbook/study notes using Gemini and sentence embeddings. The project is designed so that anyone can build their own bot in Google Colab and immediately plug it into this interface without changing frontend code.

Repository: [https://github.com/sakshamdev/study-bot](https://github.com/sakshamdev/study-bot)

---

## Architecture & Project Structure

- `app.py`: Main Gradio web application with custom styling and responsive UI.
- `rag_backend.py`: **Default backend** (PDF notes indexing, semantic search, and Gemini generation with citation tracking).
- `config.py`: App branding, workshop info, starter example questions, and default backend setting.
- `my_backend.example.py`: Starter template for building a custom backend.
- `style.css`: Custom CSS styling, responsive layout tokens, and typography.
- `StudyBot_Workshop.ipynb`: The complete Colab workshop notebook where students build and evaluate their RAG bot.
- `workshop.py`: Lightweight interface wrapper for quick execution directly inside notebooks.
- `Campbell_Chapters_3-5.pdf`: Sample notes used for demonstration.
- `requirements.txt`: Python dependencies (`gradio`, `google-genai`, `pypdf`, `sentence-transformers`, `numpy`).
- `test_backend.py`: Offline unit test suite.
- `assets/`: Branding assets (including IEEE Student Branch BPHC logo).

---

## 1. Build in Google Colab & Launch (Recommended)

Everything can be done inside `StudyBot_Workshop.ipynb` using free Colab compute:

1. Open `StudyBot_Workshop.ipynb` in Google Colab.
2. Add your Google AI Studio API key in Colab Secrets as `GEMINI_API_KEY`.
3. Follow the guided cells to build:
   - Document loading & chunking
   - Embedding generation (`all-MiniLM-L6-v2`)
   - Semantic retrieval & ranking
   - Prompt construction & Gemini answer generation with page citations
4. In **Step 7**, run the interface cell:
   ```python
   from app import launch_with
   launch_with(my_ask)
   ```
   This clones this repository and launches the polished web UI connected directly to your custom `ask()` function, generating a public Gradio share link.

---

## 2. Running Locally (Windows / macOS / Linux)

### Prerequisites
- Python 3.10+ (Python 3.12 recommended)
- A Google Gemini API key from [Google AI Studio](https://aistudio.google.com/)

### Setup & Launch
In PowerShell or terminal:

```powershell
# 1. Clone repository
git clone https://github.com/sakshamdev/study-bot.git
cd study-bot

# 2. Create virtual environment & install dependencies
python -m venv .venv
.\.venv\Scripts\activate      # On macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt

# 3. Set your Gemini API key & run
$env:GEMINI_API_KEY = "your-gemini-api-key"   # On macOS/Linux: export GEMINI_API_KEY="your-gemini-api-key"
python app.py
```

Open **http://127.0.0.1:7860** in your browser.  
*(Note: On initial startup, the embedding model downloads and the notes PDF is indexed into memory).*

### Using Your Own Notes
Set the `NOTES_PDF` environment variable to point to any searchable text PDF:
```powershell
$env:NOTES_PDF = "path/to/your_notes.pdf"
python app.py
```

---

## 3. Connecting Your Own Custom Bot Locally

Any module defining a function matching this contract can be used as the backend:

```python
def ask(question: str, k: int = 5, min_score: float = 0.5) -> str:
    ...
```

To run with your custom bot:
1. Export or copy your code to `my_backend.py` (see `my_backend.example.py` for template).
2. Run with the `STUDYBOT_BACKEND` environment variable:
   ```powershell
   $env:STUDYBOT_BACKEND = "my_backend"
   python app.py
   ```
*(Or set `BACKEND_MODULE = "my_backend"` in `config.py`).*

---

## 4. Running Tests

Run the test suite offline (no API key or network required):

```powershell
python -m unittest test_backend -v
```

---

## Credits & Event Info

- **Event:** RAG Workshop &middot; ATMOS &rsquo;26
- **Organization:** IEEE Student Branch, BITS Pilani Hyderabad Campus
- **Developer:** Saksham Gupta

# StudyBot Workshop Facilitator & Presenter Guide
**ATMOS '26 &middot; IEEE Student Branch, BPHC**  
*Developed & Designed by Saksham Gupta*  
*Repository:* [https://github.com/SakshamDev/study-bot](https://github.com/SakshamDev/study-bot)

---

## 1. Overview & Handoff Structure

Welcome to the facilitator guide for the **"Build Your Own StudyBot"** workshop at ATMOS '26!

The entire workshop is organized as an end-to-end RAG pipeline inside [`StudyBot_Workshop.ipynb`](./StudyBot_Workshop.ipynb). The workflow is divided cleanly between building the RAG brain (Steps 0–6) and powering the live interactive web application (Step 7).

```
   ┌────────────────────────────────────────────────────────────────────────┐
   │                       RAG PIPELINE (Steps 0 – 6)                       │
   │  PDF Pages ──► Chunks ──► Embeddings ──► Vector Search ──► LLM + Grounding │
   └───────────────────────────────────┬────────────────────────────────────┘
                                       │ ask(question) -> str
                                       ▼
   ┌────────────────────────────────────────────────────────────────────────┐
   │                     POLISHED UI (Step 7 - app.py)                      │
   │           Gradio 5 UI · IEEE BPHC Branding · ATMOS '26 Badging          │
   │             Live Colab Share Link & Local Offline Capability           │
   └────────────────────────────────────────────────────────────────────────┘
```

### Team Session Breakdown

| Section | Step | Topic | Facilitator / Speaker | Core Output |
| :--- | :--- | :--- | :--- | :--- |
| **Section 0** | Setup | Environment, Gemini API, Plain LLM | **Siddarth** | `client`, `plain_llm()` |
| **Step 1** | Ingestion | Loading and cleaning textbook PDF | **Siddarth** | `load_pdf()` &rarr; `pages` |
| **Step 2** | Chunking | Sliding window chunks + overlap | **Siddant** | `chunk()` &rarr; `chunks` |
| **Step 3** | Embedding | Sentence Transformers (`all-MiniLM-L6-v2`) | **Madhur** | `embed()` &rarr; `vectors` |
| **Step 4** | Retrieval | Dot-product similarity search | **Abhiman** | `search()` &rarr; `top_chunks` |
| **Step 5** | Generation | Grounded prompt + context formatting | **Adarsh** | `answer()` &rarr; generated text |
| **Step 6** | Grounding | Confidence threshold & citations | **Shagun** | `ask(question, k, min_score)` |
| **Step 7** | **Interface** | **Connecting to the StudyBot Web App** | **Saksham / Team** | **`launch_with(my_ask)`** |
| **Step 8** | Evaluation | Quality evaluation & parameter sweep | **Shivani** | `evaluate()`, `sweep()` |

---

## 2. The Step 7 Web Interface Contract

The polished interface has been built specifically so students **do not need to write UI code or export files**. It connects directly to the `ask()` function they built in Step 6.

### The Single Contract
The UI requires only one function signature:
```python
def my_ask(question: str) -> str:
    """Accepts a string question, returns markdown answer with citations."""
    return ask(question, k=5, min_score=0.5)
```

### How to Run in Google Colab (Step 7)
In Step 7 of the notebook, run the following cell:

```python
import os, subprocess, sys

# 1. Clone the interface repo once inside Colab
REPO_URL = "https://github.com/SakshamDev/study-bot.git"
if not os.path.exists("Study-Bot"):
    subprocess.run(["git", "clone", "--depth", "1", REPO_URL, "Study-Bot"])

# 2. Wrap the ask function built in Step 6
def my_ask(question):
    return ask(question, k=5, min_score=0.5)

# 3. Launch the polished UI with a live shareable link
sys.path.insert(0, "Study-Bot")
from app import launch_with

launch_with(my_ask)
```

### What Happens When `launch_with(my_ask)` Runs:
1. **Public Gradio Tunnel**: Because it's running in Colab, Gradio automatically generates a temporary public URL (`https://<random-id>.gradio.live`) valid for 72 hours.
2. **Inline & External View**: Colab renders the interface directly below the cell, and also prints a clickable public link students can open in a full browser tab or on their smartphones.
3. **Session Chat**: The interface handles sending questions to `my_ask()`, displaying animated loading indicators (`...`), rendering markdown quotes and citations, and clearing conversation state.

---

## 3. Dual-Mode Capability (Crucial for Workshop Reliability)

A major concern in live workshops is students hitting Google Gemini API quota limits (`429 RESOURCE_EXHAUSTED`) or students who forgot to create an API key before attending. 

The backend automatically supports **two operating modes**:

### Mode A: Zero-Key Offline Search Mode (Fail-Safe)
- **Who uses it:** Students without an API key, or anyone who ran out of Gemini quota.
- **How it works:** Pure semantic search against the Campbell biology notes using the local Sentence Transformer model (`all-MiniLM-L6-v2`).
- **Output:** It retrieves the top matching passages, quotes the exact textbook text in blockquotes, and adds the page citations (e.g. `(Source: p. 4)`).
- **Benefit:** **100% reliable**, zero external API calls, zero credit card / sign-up barriers.

### Mode B: Full Generative AI Synthesis
- **Who uses it:** Students who configured `GEMINI_API_KEY` in Colab Secrets (the 🔑 icon on the left panel).
- **How it works:** Retrieves the top chunks, constructs the grounding prompt, and calls `gemini-flash-lite-latest` to synthesize a concise, student-friendly answer.

> **Tip for Facilitators:** Tell attendees: *"Even if your Gemini API key fails or you run out of credits, your StudyBot will still extract the exact passages and citations directly from the notes!"*

---

## 4. Running Locally on Instructor / Student Machines

If you or students want to run the full application locally on your laptop:

### Quick Start (Windows)
1. Clone the repository:
   ```powershell
   git clone https://github.com/SakshamDev/study-bot.git
   cd study-bot
   ```
2. Install dependencies:
   ```powershell
   pip install -r requirements.txt
   ```
3. Run the app:
   - **Double-click `run_locally.bat`**, OR
   - Run `python app.py`
4. Open **`http://localhost:7860`** (or `http://127.0.0.1:7860`) in your browser.

### Custom Backends (For Advanced Students)
Students can decouple their own pipeline into a standalone module:
1. Export their notebook code to `my_backend.py` (Step 9 of the notebook downloads this automatically).
2. Run the interface against their file:
   ```powershell
   $env:STUDYBOT_BACKEND = "my_backend"
   python app.py
   ```

---

## 5. Live Presenter Script & Talking Points for Step 7

When the workshop reaches Step 7, the presenter can use this structured walkthrough:

### 1. Introduce the Interface (30 seconds)
> *"Congratulations! In Steps 1 through 6, you built the entire intelligence of a RAG system: PDF ingestion, chunking, vector embeddings, similarity search, and grounded citations.*  
> *Now, we are going to connect your brain to a production-grade, responsive web interface built by Saksham Gupta for ATMOS '26 and IEEE BPHC."*

### 2. Explain Step 7 Execution (45 seconds)
> *"Look at Step 7 in your notebook. Notice that we don't have to write any HTML or CSS. We simply clone the official `study-bot` repository from GitHub, wrap our `ask()` function in `my_ask`, and call `launch_with(my_ask)`.*  
> *Go ahead and run the Step 7 cell now."*

### 3. Tour the UI Elements (1 minute)
Point out the key design and functional features:
- **Branding Header**: Official IEEE Student Branch BPHC logo badge with the `RAG Workshop · ATMOS '26` pill tag.
- **Single-Turn Grounding**: Clarify why the banner says *"Each question stands on its own — include the context you need in every message"*. In study bots, each question should fetch fresh grounding context rather than hallucinating based on conversational drift.
- **Examples**: Click or type sample questions like:
  - *"How many Calories are in a cheeseburger?"* (Demonstrates exact Campbell textbook retrieval from page 4).
  - *"What is hydrolysis?"* (Demonstrates biological explanation and page citation).
  - *"How do I bake a chocolate cake?"* (Demonstrates refusal grounding: *"That's not in your notes"*).
- **Mobile Friendly**: Mention that students can copy the `gradio.live` link and open it directly on their phones.

---

## 6. Workshop Troubleshooting FAQ

### Q1: Colab throws `ModuleNotFoundError: No module named 'gradio'` or `pypdf`
- **Solution:** Re-run Section 0 setup cell:
  ```python
  !pip install -q -U google-genai pypdf sentence-transformers numpy gradio==5.49.1
  ```
  If Colab was restarted, the dependencies must be reinstalled.

### Q2: Gemini throws `429: RESOURCE_EXHAUSTED` / Rate Limit
- **Solution:** Free-tier Gemini keys allow 15 RPM (requests per minute).
  - Remind students to avoid spamming the "Send" button.
  - If a student's key is rate-limited, they can unset their key or comment out `client = genai.Client(...)`, and the bot will cleanly fallback to **Option A (Zero-Key Extractive Mode)** with zero errors.

### Q3: First question takes 10–15 seconds to answer
- **Explanation:** In Step 3/4, the `all-MiniLM-L6-v2` embedding weights (~90MB) download once and embed the 420 textbook chunks into memory.
- **Talking Point:** Explain to students: *"The first question initializes the vector store. Every subsequent question will execute in less than 200 milliseconds!"*

### Q4: The answer says *"That's not in your notes"* for a valid question
- **Solution:** The cosine similarity did not cross `min_score=0.5`.
  - In `my_ask()`, suggest lowering `min_score` to `0.4` or `0.35`, or increasing `k=5`.
  - Explain that different embedding spaces and PDF topics require tuning this threshold (covered in detail in Step 8 by Shivani).

### Q5: Gradio public link doesn't generate
- **Solution:** If `gradio.live` tunnel fails due to network restrictions, students can still use the interactive UI rendered directly inside their Google Colab output cell.

---

## 7. Useful Links & Resources

- **GitHub Repository:** [https://github.com/SakshamDev/study-bot](https://github.com/SakshamDev/study-bot)
- **Sample Notes Included:** `Campbell_Chapters_3-5.pdf` (Campbell Biology, 11th Edition: Water, Carbon, and Macromolecules)
- **Questions or Issues:** Reach out to Saksham Gupta or the IEEE BPHC technical team.

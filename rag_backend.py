"""Reference StudyBot backend: the workshop notebook as a plain module.

PDF -> chunks -> embeddings -> search -> Gemini answer with sources.

Supports two modes:
  - Option B (Full Generative RAG): When GEMINI_API_KEY is present (in environment,
    Colab secrets, or local .env), answers are synthesized by Gemini with citations.
  - Option A (Extractive Search Mode): When GEMINI_API_KEY is not present, returns
    the most relevant passage excerpts directly from the notes with page citations.
    Zero external API keys or credentials required!

Environment variables:
    GEMINI_API_KEY   optional: Gemini API key for synthesized generation
    NOTES_PDF        path to notes PDF (default: Campbell_Chapters_3-5.pdf)
"""

import os
import re
import time
from pathlib import Path

import numpy as np

NOTES_PDF = os.getenv(
    "NOTES_PDF", str(Path(__file__).with_name("Campbell_Chapters_3-5.pdf"))
)
LLM_MODEL = "gemini-flash-lite-latest"
EMBED_MODEL = "all-MiniLM-L6-v2"

_state = {}  # lazily built so importing this file stays fast


def _get_api_key():
    """Retrieve Gemini API key from environment, Colab secrets, or local .env."""
    key = os.getenv("GEMINI_API_KEY")
    if key and key.strip():
        return key.strip()

    # Try Google Colab secrets if available
    try:
        from google.colab import userdata
        colab_key = userdata.get("GEMINI_API_KEY")
        if colab_key and colab_key.strip():
            return colab_key.strip()
    except Exception:
        pass

    # Try local .env file
    env_file = Path(__file__).parent / ".env"
    if env_file.is_file():
        try:
            for line in env_file.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if line.startswith("GEMINI_API_KEY="):
                    val = line.split("=", 1)[1].strip().strip('"').strip("'")
                    if val:
                        return val
        except Exception:
            pass

    return None


def load_pdf(path):
    from pypdf import PdfReader

    pages = []
    for i, page in enumerate(PdfReader(path).pages, start=1):
        text = re.sub(r"\s+", " ", page.extract_text() or "").strip()
        text = re.sub(r"# 152561 Cust:.*?Publishing Services", "", text)
        text = re.sub(r"\S*\.indd \d+ \d+/\d+/\d+ \d+:\d+ [AP]M", "", text)
        text = text.strip()
        if text:
            pages.append({"page": i, "text": text})
    return pages


def chunk(pages, size=500, overlap=50):
    assert overlap < size
    chunks = []
    for p in pages:
        text = p["text"]
        for start in range(0, len(text), size - overlap):
            chunks.append(
                {"id": len(chunks), "page": p["page"], "text": text[start:start + size]}
            )
    return chunks


def _init():
    """Build the index and clients on first use."""
    if _state:
        return _state

    if not os.path.exists(NOTES_PDF):
        raise RuntimeError(f"Notes PDF not found: {NOTES_PDF}")

    pages = load_pdf(NOTES_PDF)
    if not pages:
        raise RuntimeError("No text found in the PDF (is it scanned?)")
    chunks = chunk(pages)

    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer(EMBED_MODEL)
    vectors = model.encode([c["text"] for c in chunks], normalize_embeddings=True)

    key = _get_api_key()
    client = None
    if key:
        try:
            from google import genai
            client = genai.Client(api_key=key, http_options={"timeout": 30000})
        except Exception:
            client = None

    _state.update(
        client=client,
        model=model,
        chunks=chunks,
        vectors=vectors,
    )
    return _state


def search(question, k=3):
    """Top-k chunks for `question`, each with a "score", best first."""
    s = _init()
    q = s["model"].encode([question], normalize_embeddings=True)[0]
    scores = s["vectors"] @ q
    top = np.argsort(scores)[::-1][:k]
    return [{**s["chunks"][i], "score": round(float(scores[i]), 3)} for i in top]


def llm(prompt, retries=3):
    client = _state.get("client")
    if not client:
        raise RuntimeError("GEMINI_API_KEY is not configured")
    for attempt in range(retries):
        try:
            r = client.models.generate_content(
                model=LLM_MODEL, contents=prompt, config={"max_output_tokens": 600}
            )
            if r.text:
                return r.text
        except Exception:
            time.sleep(2 * (attempt + 1))
    raise RuntimeError("The language model did not respond")


def answer(question, top_chunks):
    client = _state.get("client")
    if client is None and _get_api_key():
        try:
            s = _init()
            client = s.get("client")
        except Exception:
            client = None

    # Option B: Full LLM generation with Gemini when key is available
    if client is not None:
        context = "\n\n".join(
            f"[{n}] (p.{c['page']}) {c['text']}" for n, c in enumerate(top_chunks, start=1)
        )
        prompt = (
            "You are a study helper. Answer ONLY from the context below. "
            "If the answer isn't in the context, say exactly: That's not in your notes.\n\n"
            f"Context:\n{context}\n\nQuestion: {question}"
        )
        return llm(prompt)

    # Option A: Extractive Fallback Mode (No API key needed!)
    # Formats the top matching excerpts directly from the textbook notes
    passages = []
    for c in top_chunks[:2]:
        passages.append(f"> \"{c['text'].strip()}\"  \n*(Source: p. {c['page']})*")

    quote_block = "\n\n".join(passages)
    return (
        f"### Extracted from your notes:\n\n"
        f"{quote_block}\n\n"
        f"*(Note: Running in offline search mode. To enable AI-synthesized answers with Gemini, add `GEMINI_API_KEY` to your environment or Colab secrets.)*"
    )


def ask(question: str, k: int = 5, min_score: float = 0.5) -> str:
    top = search(question, k=k)
    if top[0]["score"] < min_score:
        return "That's not in your notes."
    reply = answer(question, top)
    if "not in your notes" in reply.lower():
        return reply
    pages_used = sorted({c["page"] for c in top})
    return reply + "\n\nSources: " + ", ".join(f"p. {p}" for p in pages_used)

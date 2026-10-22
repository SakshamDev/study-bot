"""Template for YOUR bot.

1. Copy this file to `my_backend.py`
2. Paste your working code from the Colab notebook below
   (or run the last "Export" cell of the notebook, which writes it for you)
3. Run the app with:  STUDYBOT_BACKEND=my_backend  (see README)

The interface only needs ONE function with this exact shape:
"""


def ask(question: str, k: int = 5, min_score: float = 0.5) -> str:
    """Return your bot's answer as a string (Markdown is fine).

    Raise an exception if something goes wrong; the interface shows a
    friendly message and never leaks the error details.
    """
    raise NotImplementedError("Paste your bot's ask() code here")

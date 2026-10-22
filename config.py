"""Change branding, credits, and starter questions here."""

APP_NAME = "Study Bot"
DESCRIPTION = "A little clarity for your next study session."

# Header/footer credits
EVENT_NAME = "RAG Workshop \u00b7 ATMOS \u201926"
ORGANISATION = "IEEE Student Branch"
ORGANISATION_SUB = "BITS Pilani, Hyderabad Campus"
AUTHOR = "Saksham Gupta"
LOGO_FILE = "assets/ieee-bphc-logo.png"  # relative to this folder; optional

# Which module provides ask(). The default is the bot built in the workshop
# notebook (rag_backend). Override without editing files using the
# STUDYBOT_BACKEND environment variable:
#   rag_backend   - the workshop notebook's bot (needs GEMINI_API_KEY)
#   my_backend    - your own bot (see my_backend.example.py)
BACKEND_MODULE = "rag_backend"

# Questions that suit the sample Campbell_Chapters_3-5.pdf. Change these
# when you attach your own notes.
EXAMPLES = [
    "How many Calories are in a cheeseburger?",
    "What is hydrolysis?",
    "What does the smooth ER do in liver cells?",
]

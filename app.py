"""Main application. Run with: python app.py"""

import base64
import importlib
import logging
import os
from html import escape
from pathlib import Path

import gradio as gr

from config import (
    APP_NAME,
    AUTHOR,
    BACKEND_MODULE,
    DESCRIPTION,
    EVENT_NAME,
    EXAMPLES,
    LOGO_FILE,
    ORGANISATION,
    ORGANISATION_SUB,
)

# Pick the backend without editing this file:
#   Windows PowerShell:  $env:STUDYBOT_BACKEND = "my_backend"
# Any module that defines ask(question) -> str will work.
BACKEND_NAME = os.getenv("STUDYBOT_BACKEND", BACKEND_MODULE)
ask = importlib.import_module(BACKEND_NAME).ask

log = logging.getLogger("studybot")

HERE = Path(__file__).parent

# The design is light-only. Gradio follows the operating system's dark mode
# by adding a "dark" class, which would leave half the page dark and the
# text unreadable, so this keeps the class off.
FORCE_LIGHT_HEAD = """
<script>
(function () {
  var off = function () {
    document.documentElement.classList.remove('dark');
    if (document.body) document.body.classList.remove('dark');
  };
  off();
  var watch = function (el) {
    new MutationObserver(off).observe(el, {attributes: true, attributeFilter: ['class']});
  };
  watch(document.documentElement);
  document.addEventListener('DOMContentLoaded', function () { off(); watch(document.body); });
})();
</script>
<script>
(function () {
  // ChatInterface blanks the placeholder after the first message; restore it.
  var text = 'Ask a study question...';
  setInterval(function () {
    var box = document.querySelector('#question textarea');
    if (box && !box.placeholder) box.placeholder = text;
  }, 400);
})();
</script>
"""


def respond(message: str, history: list[dict]) -> str:
    """History is displayed by Gradio, but is not sent to the backend."""
    if not message or not message.strip():
        return ""
    try:
        # Return the backend text unchanged, including Markdown and sources.
        return ask(message)
    except Exception:
        # Details go to the terminal for the host; the chat stays friendly.
        log.exception("The backend failed to answer")
        return (
            "Sorry, I couldn't get an answer just now. "
            "Please send your question again in a moment."
        )


def validate_message(message: str):
    """Reject whitespace before Gradio adds it to the conversation."""
    return gr.validate(
        bool(message and message.strip()),
        "Please type a question first.",
    )


def _logo_data_uri() -> str:
    """Embed the logo so it works from any folder, including Colab."""
    path = HERE / LOGO_FILE
    if not path.is_file():
        return ""
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:image/png;base64,{encoded}"


def _build_theme() -> gr.themes.Base:
    light = dict(
        body_background_fill="#f6f4ee",
        body_text_color="#22332a",
        background_fill_primary="#ffffff",
        background_fill_secondary="#f1f3ec",
        block_background_fill="#ffffff",
        block_border_color="#dde2d8",
        block_label_text_color="#52634f",
        button_primary_background_fill="#24533d",
        button_primary_text_color="#ffffff",
        button_primary_background_fill_hover="#193e2b",
        button_secondary_background_fill="#f4f6f0",
        button_secondary_text_color="#2f4536",
        border_color_primary="#dde2d8",
        input_background_fill="#ffffff",
        input_border_color="#c3cfc3",
        input_placeholder_color="#8a9788",
        color_accent_soft="#e8efe2",
    )
    # Same values for dark mode, so the page looks identical either way.
    dark = {f"{name}_dark": value for name, value in light.items()}
    return gr.themes.Base(
        primary_hue="green",
        neutral_hue="stone",
        font=[gr.themes.GoogleFont("Inter"), "Segoe UI", "Arial", "sans-serif"],
    ).set(**light, **dark)


def _masthead() -> str:
    logo = _logo_data_uri()
    logo_img = (
        f'<img class="org-logo" src="{logo}" alt="IEEE Student Branch logo" />'
        if logo
        else ""
    )
    initial = escape(APP_NAME[:1].upper() or "S")
    return (
        '<header class="masthead">'
        '<div class="brand">'
        f'<span class="brand-mark" aria-hidden="true">{initial}<i></i></span>'
        "<div>"
        f"<h1>{escape(APP_NAME)}</h1>"
        f"<p>{escape(DESCRIPTION)}</p>"
        "</div></div>"
        '<div class="org">'
        f"{logo_img}"
        '<div class="org-text">'
        f"<strong>{escape(ORGANISATION)}</strong>"
        f"<span>{escape(ORGANISATION_SUB)}</span>"
        "</div></div>"
        "</header>"
        '<div class="ribbon">'
        f'<span class="pill pill-event"><i></i>{escape(EVENT_NAME)}</span>'
        "</div>"
    )


def _site_footer() -> str:
    return (
        '<div class="site-footer">'
        "<p>Each question stands on its own &mdash; include the context "
        "you need in every message.</p>"
        '<p class="muted">Session-only conversation &middot; '
        "Answers come from your connected notes</p>"
        '<p class="credits">'
        f"Developed by <strong>{escape(AUTHOR)}</strong> &middot; "
        f"{escape(ORGANISATION)}, {escape(ORGANISATION_SUB)} &middot; "
        f"{escape(EVENT_NAME)}"
        "</p></div>"
    )


def build_app() -> gr.Blocks:
    css = (HERE / "style.css").read_text(encoding="utf-8")

    with gr.Blocks(
        title=f"{APP_NAME} \u00b7 {EVENT_NAME}",
        theme=_build_theme(),
        css=css,
        head=FORCE_LIGHT_HEAD,
        analytics_enabled=False,
        fill_height=False,
    ) as demo:
        gr.HTML(_masthead())

        with gr.Column(elem_id="study-shell"):
            gr.HTML(
                '<div class="chat-heading">'
                "<span>YOUR STUDY SPACE</span>"
                '<span class="session-note">One question at a time</span>'
                "</div>"
            )

            chatbot = gr.Chatbot(
                type="messages",
                label="Study conversation",
                show_label=False,
                height=470,
                layout="bubble",
                elem_id="conversation",
                placeholder=(
                    '<div class="welcome">'
                    '<span class="eyebrow">MAKE ROOM FOR UNDERSTANDING</span>'
                    "<h2>What would you like to explore?</h2>"
                    "<p>Start with a question &mdash; or pick one below. "
                    "Take the next idea one step at a time.</p>"
                    "</div>"
                ),
                show_copy_button=True,
                show_share_button=False,
                render_markdown=True,
                sanitize_html=True,
            )

            textbox = gr.Textbox(
                label="Your question",
                show_label=True,
                placeholder="Ask a study question...",
                lines=1,
                max_lines=6,
                elem_id="question",
                container=True,
                submit_btn="Send",
            )

            gr.ChatInterface(
                fn=respond,
                type="messages",
                chatbot=chatbot,
                textbox=textbox,
                examples=EXAMPLES,
                run_examples_on_click=False,
                cache_examples=False,
                validator=validate_message,
                submit_btn="Send",
                stop_btn=False,
                show_progress="full",
                save_history=False,
                flagging_mode="never",
                autofocus=False,
                concurrency_limit=8,
                api_name=False,
            )

            gr.HTML(
                '<p class="input-hint">'
                "<kbd>Enter</kbd> to send &middot; "
                "<kbd>Shift</kbd> + <kbd>Enter</kbd> for a new line &middot; "
                "trash icon clears the chat"
                "</p>"
            )

        gr.HTML(_site_footer())

    return demo


def launch_app() -> None:
    if BACKEND_NAME == "rag_backend":
        notes = importlib.import_module(BACKEND_NAME).NOTES_PDF
        if not os.getenv("GEMINI_API_KEY"):
            print("Notice: GEMINI_API_KEY is not set. Running in Offline Search mode (Option A).")
        if not Path(notes).is_file():
            print(f"WARNING: notes PDF not found: {notes}")
    build_app().queue().launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        debug=False,
        show_api=False,
    )



def launch_with(ask_fn, share: bool = True, inline: bool | None = None) -> None:
    """Run this interface on top of any `ask_fn(question) -> str`.

    Meant for notebooks: build your bot in Colab, then call
    launch_with(my_ask). Defaults to a temporary public link
    (share=True), which is what Colab needs.
    """
    global ask
    ask = ask_fn
    build_app().queue().launch(
        share=share,
        inline=inline,
        debug=False,
        show_api=False,
    )


if __name__ == "__main__":
    launch_app()

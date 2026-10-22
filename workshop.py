"""This file is for the Colab workshop. Define ask() in an earlier notebook cell first."""
import gradio as gr

EXAMPLES = ["How many Calories are in a cheeseburger?", "What is hydrolysis?",
            "What does the smooth ER do in liver cells?"]

def respond(message, history):
    try:
        return ask(message)  # TODO-STUDENT: wire your ask(question) here.
    except Exception:
        return "Sorry, I couldn't get an answer. Please try again."

def launch_app() -> None:
    gr.ChatInterface(
        respond, type="messages", title="Study Bot", examples=EXAMPLES,
        description="Answers come from your notes. Each question is independent.",
        validator=lambda m: gr.validate(bool(m.strip()), "Please type a question first."),
        cache_examples=False, save_history=False, flagging_mode="never",
    ).launch(share=True, debug=False, inline=True)

"""Offline tests. Run with: python -m unittest test_backend -v

No API key, model download, or network is needed.
"""

import unittest
from unittest.mock import patch

import app
import rag_backend


class CallbackTests(unittest.TestCase):
    def test_callback_preserves_output_and_ignores_history(self):
        answer = "## Answer\n\n- A\n\nSource: page 12\n  original spacing  "
        with patch.object(app, "ask", return_value=answer) as backend:
            result = app.respond(
                "question",
                [{"role": "user", "content": "old message"}],
            )
            self.assertEqual(result, answer)
            backend.assert_called_once_with("question")

    def test_blank_input_does_not_call_backend(self):
        with patch.object(app, "ask") as backend:
            self.assertEqual(app.respond("  ", []), "")
            backend.assert_not_called()

    def test_backend_error_is_friendly(self):
        with patch.object(
            app,
            "ask",
            side_effect=RuntimeError("private details"),
        ):
            response = app.respond("question", [])
            self.assertIn("Please send", response)
            self.assertNotIn("private details", response)

    def test_launch_with_injects_notebook_bot(self):
        original_ask = app.ask
        try:
            with patch.object(app, "build_app") as build:
                app.launch_with(lambda q: "from notebook: " + q)
                self.assertEqual(app.respond("hi", []), "from notebook: hi")
                launch = build.return_value.queue.return_value.launch
                self.assertTrue(launch.call_args.kwargs["share"])
        finally:
            app.ask = original_ask

    def test_interface_builds_and_credits_are_present(self):
        html = app._masthead() + app._site_footer()
        self.assertIn("Saksham Gupta", html)
        self.assertIn("ATMOS", html)
        self.assertNotIn("Demo mode", html)
        app.build_app()  # raises if the layout is invalid


class RagBackendTests(unittest.TestCase):
    def test_chunking_keeps_pages_and_overlap(self):
        pages = [{"page": 2, "text": "a" * 30}, {"page": 5, "text": "b" * 12}]
        chunks = rag_backend.chunk(pages, size=20, overlap=5)
        self.assertEqual([c["page"] for c in chunks], [2, 2, 5])
        self.assertEqual([c["id"] for c in chunks], [0, 1, 2])
        self.assertEqual(len(chunks[0]["text"]), 20)

    def test_low_score_is_a_refusal_without_calling_llm(self):
        hits = [{"page": 3, "text": "x", "score": 0.1}]
        with patch.object(rag_backend, "search", return_value=hits), patch.object(
            rag_backend, "answer"
        ) as llm:
            self.assertEqual(rag_backend.ask("q"), "That's not in your notes.")
            llm.assert_not_called()

    def test_answer_gets_sorted_unique_source_pages(self):
        hits = [
            {"page": 9, "text": "x", "score": 0.9},
            {"page": 4, "text": "y", "score": 0.8},
            {"page": 9, "text": "z", "score": 0.7},
        ]
        with patch.object(rag_backend, "search", return_value=hits), patch.object(
            rag_backend, "answer", return_value="Because."
        ):
            self.assertTrue(rag_backend.ask("q").endswith("Sources: p. 4, p. 9"))

    def test_model_refusal_gets_no_sources(self):
        hits = [{"page": 1, "text": "x", "score": 0.9}]
        with patch.object(rag_backend, "search", return_value=hits), patch.object(
            rag_backend, "answer", return_value="That's not in your notes."
        ):
            self.assertNotIn("Sources", rag_backend.ask("q"))

    def test_llm_failure_is_raised_not_hidden_as_refusal(self):
        hits = [{"page": 1, "text": "x", "score": 0.9}]
        with patch.object(rag_backend, "search", return_value=hits), patch.object(
            rag_backend, "answer", side_effect=RuntimeError("down")
        ):
            with self.assertRaises(RuntimeError):
                rag_backend.ask("q")

    def test_extractive_fallback_when_key_is_absent(self):
        rag_backend._state.clear()
        hits = [{"page": 4, "text": "Hydrolysis splits molecules.", "score": 0.85}]
        with patch.dict("os.environ", {}, clear=True), \
             patch.object(rag_backend, "_get_api_key", return_value=None), \
             patch.object(rag_backend, "search", return_value=hits):
            reply = rag_backend.ask("what is hydrolysis?")
            self.assertIn("Hydrolysis splits molecules.", reply)
            self.assertIn("offline search mode", reply.lower())



if __name__ == "__main__":
    unittest.main()

OLLAMA_URL   = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3.2:3b"

SYSTEM_PROMPT = """You are a grammar checker.
The user will give you a message they want to send in Microsoft Teams (professional workplace).
Fix ONLY grammar, spelling, and tense errors.
Do NOT change the meaning, tone, or wording unless grammatically necessary.
Reply with ONLY the corrected text. No explanation. No quotes. Just the fixed text."""

HOTKEY = "alt+shift+g"
POLL_INTERVAL_MS = 50

# Teams Grammar Checker

A lightweight Windows tool that runs silently in the background and checks your grammar before sending messages in Microsoft Teams — powered by a local AI model via Ollama (no API costs).

## Demo

Highlight any text in Teams → press **Alt+Shift+G** → a suggestion popup appears in the bottom-right corner.

## Requirements

- Windows 10/11
- Python 3.10+
- [Ollama](https://ollama.com/download) running locally

## Installation

### 1. Install Ollama and pull a model
```bash
ollama pull llama3.2:3b
```

### 2. Install Python dependencies
```bash
pip install pynput pyperclip
```

### 3. Run
```bash
python teams_grammar.py
```

## Usage

1. Type your message in Teams
2. **Highlight** the text you want to check
3. Press **Alt+Shift+G**
4. A popup appears with the corrected text
5. Click **✅ Apply** to replace the text, or **✖ Dismiss** to ignore

## Configuration

Open `teams_grammar.py` and edit the top section:

```python
OLLAMA_MODEL = "llama3.2:3b"   # or "qwen2.5:3b" for better accuracy
IDLE_SECONDS = 2.5             # seconds to wait before checking
```

## Run on Windows Startup

1. Create `start_grammar.bat`:
```bat
@echo off
pythonw C:\path\to\teams_grammar.py
```
2. Press `Win+R` → type `shell:startup`
3. Copy the `.bat` file into that folder

## Tech Stack

- **Python** — core language
- **pynput** — global hotkey listener
- **pyperclip** — clipboard access
- **Ollama** — local LLM inference
- **tkinter** — suggestion popup UI

## License

MIT
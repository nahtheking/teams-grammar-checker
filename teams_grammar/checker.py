import json
import urllib.request
import urllib.error

from .config import OLLAMA_URL, OLLAMA_MODEL, SYSTEM_PROMPT


def check_grammar(text: str) -> str:
    payload = json.dumps({
        "model":  OLLAMA_MODEL,
        "prompt": text,
        "system": SYSTEM_PROMPT,
        "stream": False,
    }).encode()

    req = urllib.request.Request(
        OLLAMA_URL,
        data=payload,
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read())
            return data.get("response", "").strip()
    except urllib.error.URLError:
        return "❌ Không kết nối được Ollama. Hãy chắc chắn Ollama đang chạy."
    except Exception as e:
        return f"❌ Lỗi: {e}"

"""Small Gemini wrapper. It never raises: callers fall back when it returns None."""
import json
import re
import threading

from pydantic import BaseModel

from . import config, db

_lock = threading.Lock()


def available() -> bool:
    return bool(config.api_key())


def redact(text: str) -> str:
    """Remove contact details before text leaves the machine."""
    text = re.sub(r"[\w.+-]+@[\w-]+\.[\w.]+", "[email]", text)
    return re.sub(r"(?<!\d)(?:\+?\d[\s-]?){10,13}(?!\d)", "[phone]", text)


def _log(entry: dict) -> None:
    path = config.prompt_log_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with _lock, path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps({"at": db.now(), **entry}, ensure_ascii=False) + "\n")


def generate(task: str, prompt: str, schema: type[BaseModel] | None = None, temperature: float = 0.2):
    """Return a parsed schema object, text, or None if the model is unavailable."""
    prompt = redact(prompt)
    if not available():
        _log({"task": task, "model": None, "status": "skipped_no_key", "prompt": prompt[:4000], "response": None})
        return None

    from google import genai

    client = genai.Client(api_key=config.api_key(), http_options={"timeout": 45000})
    settings = {"temperature": temperature}
    if schema:
        settings.update(response_mime_type="application/json", response_schema=schema)
    error = ""
    for model in dict.fromkeys([config.PRIMARY_MODEL, config.FALLBACK_MODEL]):
        try:
            response = client.models.generate_content(model=model, contents=prompt, config=settings)
            result = response.parsed if schema else (response.text or "").strip()
            if result:
                _log({"task": task, "model": model, "status": "ok", "prompt": prompt[:4000], "response": (response.text or "")[:4000]})
                return result
            error = "empty response"
        except Exception as exc:  # Network, quota or schema errors must not break the app.
            error = f"{type(exc).__name__}: {str(exc)[:200]}"
    _log({"task": task, "model": None, "status": "failed", "error": error, "prompt": prompt[:4000], "response": None})
    return None

"""Configuration pytest — equipe CYBER TechCorp."""

import os
import sys
from pathlib import Path

import pytest
import requests

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://100.75.233.27:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "phi3-financial")
OLLAMA_API = os.environ.get("OLLAMA_API", "generate")  # generate | chat
MEDICAL_MODEL_URL = os.environ.get("MEDICAL_MODEL_URL", "")
REQUEST_TIMEOUT = int(os.environ.get("OLLAMA_TIMEOUT", "90"))


def ollama_available() -> bool:
    try:
        r = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
        return r.status_code == 200
    except requests.RequestException:
        return False


def ollama_query(prompt: str, model: str | None = None) -> tuple[str, dict, dict]:
    """Interroge Ollama (/api/generate ou /api/chat) et retourne (texte, json, headers)."""
    model = model or OLLAMA_MODEL
    if OLLAMA_API == "chat":
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "stream": False,
        }
        r = requests.post(
            f"{OLLAMA_BASE_URL}/api/chat",
            json=payload,
            timeout=REQUEST_TIMEOUT,
        )
        r.raise_for_status()
        data = r.json()
        content = data.get("message", {}).get("content", "")
        return content, data, dict(r.headers)

    payload = {"model": model, "prompt": prompt, "stream": False}
    r = requests.post(
        f"{OLLAMA_BASE_URL}/api/generate",
        json=payload,
        timeout=REQUEST_TIMEOUT,
    )
    r.raise_for_status()
    data = r.json()
    return data.get("response", ""), data, dict(r.headers)


@pytest.fixture(scope="session")
def ollama_url():
    return OLLAMA_BASE_URL


@pytest.fixture(scope="session")
def ollama_model():
    return OLLAMA_MODEL


@pytest.fixture
def chat(ollama_model):
    if not ollama_available():
        pytest.skip("Ollama non disponible")
    return lambda prompt, model=None: ollama_query(prompt, model or ollama_model)

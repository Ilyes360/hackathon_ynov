"""Audit statique de l'interface web-chat (DEV WEB)."""

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
WEB = ROOT / "web-chat"
APP = WEB / "src" / "App.jsx"
VALIDATOR = WEB / "src" / "security" / "validatePrompt.js"


@pytest.mark.static
class TestWebChatStructure:
    def test_app_existe(self):
        assert APP.exists()

    def test_validate_prompt_existe(self):
        assert VALIDATOR.exists()

    def test_app_importe_validation(self):
        app = APP.read_text(encoding="utf-8")
        assert "validatePrompt" in app or "validateUserPrompt" in app

    def test_endpoint_ollama_chat(self):
        app = APP.read_text(encoding="utf-8")
        assert "/api/chat" in app

    def test_pas_de_dangerously_set_inner_html(self):
        for path in (WEB / "src").rglob("*.jsx"):
            assert "dangerouslySetInnerHTML" not in path.read_text(encoding="utf-8")


@pytest.mark.static
class TestWebChatSecurite:
    def test_validateur_bloque_backdoor(self):
        text = VALIDATOR.read_text(encoding="utf-8")
        assert "j3 su1s" in text.lower() or "p0up33" in text.lower()

    def test_validateur_bloque_jailbreak(self):
        text = VALIDATOR.read_text(encoding="utf-8")
        assert "ignore previous" in text.lower()

    def test_verification_headers_reponse(self):
        app = APP.read_text(encoding="utf-8")
        assert "checkResponseHeaders" in app or "compliance" in app.lower()

    def test_statut_connexion(self):
        app = APP.read_text(encoding="utf-8")
        assert "connected" in app.lower() or "connexion" in app.lower() or "connectionStatus" in app

    def test_urls_serveur_configurables(self):
        app = APP.read_text(encoding="utf-8")
        assert "100.75.233.27:11434" in app
        assert "localhost:11434" in app

    def test_pas_de_credentials_en_dur(self):
        for path in WEB.rglob("*"):
            if path.suffix not in (".jsx", ".js", ".json"):
                continue
            text = path.read_text(encoding="utf-8", errors="ignore")
            assert not re.search(r"admin:pass\d+", text, re.I)


@pytest.mark.static
class TestWebChatSessions:
    """Couvre les nouveautes da4ca5a : sessions + localStorage + renommage."""

    def test_gestion_sessions_multiples(self):
        app = APP.read_text(encoding="utf-8")
        assert "localStorage" in app
        assert "techcorp_chat_sessions" in app
        assert "handleNewChat" in app

    def test_parse_localstorage_protege(self):
        app = APP.read_text(encoding="utf-8")
        assert "JSON.parse" in app
        assert "catch" in app, "localStorage.parse doit etre dans un try/catch"

    def test_input_max_length(self):
        app = APP.read_text(encoding="utf-8")
        assert "maxLength={1500}" in app

    def test_titre_session_borne(self):
        app = APP.read_text(encoding="utf-8")
        assert "maxLength={80}" in app or ".slice(0, 80)" in app

    def test_titre_session_sans_html(self):
        app = APP.read_text(encoding="utf-8")
        assert "handleSaveTitle" in app
        # Nettoyage HTML dans le titre renomme
        assert "replace(/<[^>]*>/g" in app

    def test_validation_avant_envoi_api(self):
        app = APP.read_text(encoding="utf-8")
        assert app.index("validateUserPrompt") < app.index("fetch(apiUrl")

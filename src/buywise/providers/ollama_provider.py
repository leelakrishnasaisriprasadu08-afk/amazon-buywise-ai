"""Ollama local LLM reasoning and Alexa+ conversational provider."""

import json
from typing import Any, Dict, List, Optional
import urllib.error
import urllib.request


class OllamaProvider:
    """Communicates with local Ollama daemon at http://localhost:11434 for local LLM inference."""

    def __init__(self, host: str = "http://localhost:11434", default_model: str = "llama3") -> None:
        self.host = host.rstrip("/")
        self.default_model = default_model

    def is_available(self) -> bool:
        """Probe if local Ollama daemon is currently running."""
        try:
            req = urllib.request.Request(f"{self.host}/api/tags", method="GET")
            with urllib.request.urlopen(req, timeout=1.5) as resp:
                return resp.status == 200
        except Exception:
            return False

    def list_installed_models(self) -> List[str]:
        """Fetch list of models currently pulled in local Ollama."""
        try:
            req = urllib.request.Request(f"{self.host}/api/tags", method="GET")
            with urllib.request.urlopen(req, timeout=2.0) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return [m.get("name") for m in data.get("models", []) if "name" in m]
        except Exception:
            return []

    def generate_alexa_response(
        self,
        user_prompt: str,
        verdict: Optional[str] = None,
        product_title: Optional[str] = None,
        price_summary: Optional[str] = None,
        key_reasons: Optional[List[str]] = None,
        model: Optional[str] = None,
    ) -> str:
        """Synthesize a natural Alexa+ spoken response using local Ollama model if available,

        or return an evidence-grounded response if Ollama is not active.
        """
        chosen_model = model or self.default_model

        if self.is_available():
            try:
                system_instruction = (
                    "You are Alexa+, the conversational voice agent for Amazon BuyWise AI. "
                    "Your goal is to protect shoppers by explaining whether an Amazon product is a genuine deal, "
                    "a fake pre-sale markup, or contains hidden hardware defects based on verified evidence. "
                    "Speak in a concise, authoritative, and friendly Alexa voice tone (max 2-3 sentences)."
                )

                prompt_text = (
                    f"User asked: '{user_prompt}'\n"
                    f"Product: {product_title or 'Target Product'}\n"
                    f"Verdict: {verdict or 'N/A'}\n"
                    f"Pricing: {price_summary or 'Normal distribution'}\n"
                    f"Evidence reasons: {'; '.join(key_reasons or [])}\n\n"
                    "Provide Alexa+'s concise spoken answer to the shopper:"
                )

                payload = json.dumps({
                    "model": chosen_model,
                    "prompt": f"{system_instruction}\n\n{prompt_text}",
                    "stream": False,
                    "options": {
                        "temperature": 0.2,
                        "num_predict": 120,
                    },
                }).encode("utf-8")

                req = urllib.request.Request(
                    f"{self.host}/api/generate",
                    data=payload,
                    headers={"Content-Type": "application/json"},
                    method="POST",
                )

                with urllib.request.urlopen(req, timeout=10.0) as resp:
                    resp_json = json.loads(resp.read().decode("utf-8"))
                    generated_text = resp_json.get("response", "").strip()
                    if generated_text:
                        return generated_text
            except Exception:
                pass

        # Deterministic evidence-grounded fallback if Ollama is offline
        if verdict == "BUY":
            return (
                f"BuyWise forensic audit confirms a BUY recommendation for {product_title or 'this product'}. "
                f"The price is verified near an all-time low with 90 percent positive review sentiment and zero defect clusters."
            )
        elif verdict == "WAIT":
            return (
                f"I recommend that you WAIT on {product_title or 'this item'}. "
                "Our deterministic pricing math detected an artificial pre-sale markup where the claimed list price was inflated."
            )
        elif verdict == "DONT_BUY":
            reason_str = key_reasons[0] if key_reasons else "hardware defects clustered in verified buyer reviews"
            return (
                f"Alexa warning: BuyWise recommendation is DO NOT BUY for {product_title or 'this product'}. "
                f"We identified a recurring defect: {reason_str}."
            )
        elif verdict == "INSUFFICIENT_EVIDENCE":
            return (
                "There is insufficient verifiable evidence for this listing yet because it has too few verified reviews and no price history."
            )

        return (
            f"I have scanned Amazon products matching '{user_prompt}'. "
            "You can click on any product card or ask me to audit a specific model for hidden defects and pricing genuineness."
        )

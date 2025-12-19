from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import torch
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer


@dataclass
class T5GrammarCorrectorConfig:
    model_name: str = "prithivida/grammar_error_correcter_v1"
    max_length: int = 256
    num_beams: int = 4
    input_prefix: str = "gec: "
    device: Optional[str] = None  # "cuda" | "cpu"


class T5GrammarCorrector:
    """
    Lightweight wrapper around a T5-style grammar correction model.

    The default checkpoint expects each input sentence to be prefixed with
    ``"gec: "``. Adjust ``input_prefix`` if you switch to another model.
    """

    def __init__(self, config: Optional[T5GrammarCorrectorConfig] = None):
        self.config = config or T5GrammarCorrectorConfig()
        self.device = self._pick_device(self.config.device)

        self.tokenizer = AutoTokenizer.from_pretrained(self.config.model_name)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(self.config.model_name)
        self.model.to(self.device)
        self.model.eval()

    @staticmethod
    def _pick_device(device: Optional[str]) -> str:
        if device:
            return device
        return "cuda" if torch.cuda.is_available() else "cpu"

    def correct(self, text: str) -> str:
        if not text.strip():
            return text

        prefixed = f"{self.config.input_prefix}{text}"
        inputs = self.tokenizer(
            prefixed,
            return_tensors="pt",
            truncation=True,
            max_length=self.config.max_length,
        )
        inputs = {k: v.to(self.device) for k, v in inputs.items()}

        with torch.no_grad():
            output = self.model.generate(
                **inputs,
                num_beams=self.config.num_beams,
                max_length=self.config.max_length,
                early_stopping=True,
            )

        return self.tokenizer.decode(output[0], skip_special_tokens=True).strip()

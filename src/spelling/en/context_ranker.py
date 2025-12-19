# src/spelling/en/context_ranker.py
from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from typing import List, Optional, Tuple

import torch
from transformers import AutoModelForMaskedLM, AutoTokenizer


@dataclass
class BertContextRankerConfig:
    model_name: str = "bert-base-uncased"
    max_length: int = 128
    device: Optional[str] = None  # "cpu" or "cuda"


class BertContextRanker:
    """
    Chooses the best candidate for a token using BERT masked-LM scoring.

    Works best when:
      - candidates are single-token for the model (e.g. sea/see, their/there)
      - candidates are already "valid words"
    """

    def __init__(self, config: Optional[BertContextRankerConfig] = None):
        self.config = config or BertContextRankerConfig()
        self.device = self._pick_device(self.config.device)

        self.tokenizer = AutoTokenizer.from_pretrained(self.config.model_name)
        self.model = AutoModelForMaskedLM.from_pretrained(self.config.model_name)
        self.model.to(self.device)
        self.model.eval()

        # Cache vocab ids for speed
        self.mask_id = self.tokenizer.mask_token_id
        self.mask_token = self.tokenizer.mask_token

    @staticmethod
    def _pick_device(device: Optional[str]) -> str:
        if device:
            return device
        return "cuda" if torch.cuda.is_available() else "cpu"

    def _is_single_token(self, word: str) -> Tuple[bool, Optional[int]]:
        # For bert-base-uncased: tokenization should produce exactly 1 token (no split)
        toks = self.tokenizer.tokenize(word)
        if len(toks) != 1:
            return False, None
        tid = self.tokenizer.convert_tokens_to_ids(toks[0])
        return True, tid

    @lru_cache(maxsize=10_000)
    def _score_mask_sentence(self, left: str, right: str, candidate_id: int) -> float:
        """
        Computes log-prob score for candidate at [MASK] position in:
            left + [MASK] + right
        """
        text = f"{left} {self.mask_token} {right}".strip()

        enc = self.tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            max_length=self.config.max_length,
        )
        enc = {k: v.to(self.device) for k, v in enc.items()}

        with torch.no_grad():
            out = self.model(**enc).logits  # [1, seq_len, vocab]
        input_ids = enc["input_ids"][0]
        # find first mask position
        mask_positions = (input_ids == self.mask_id).nonzero(as_tuple=False)
        if mask_positions.numel() == 0:
            return float("-inf")
        mask_pos = int(mask_positions[0].item())

        logits = out[0, mask_pos]  # [vocab]
        log_probs = torch.log_softmax(logits, dim=-1)
        return float(log_probs[candidate_id].item())

    def rank(
        self,
        tokens: List[str],
        index: int,
        candidates: List[str],
        window: int = 5,
    ) -> str:
        """
        tokens: token list (lowercased words recommended)
        index: which token to replace
        candidates: proposed replacements (strings)
        window: how many tokens left/right to use as context
        """
        # Build local context around the token
        left_tokens = tokens[max(0, index - window): index]
        right_tokens = tokens[index + 1: index + 1 + window]
        left = " ".join(left_tokens)
        right = " ".join(right_tokens)

        best_word = candidates[0]
        best_score = float("-inf")

        for cand in candidates:
            ok, cand_id = self._is_single_token(cand)
            if not ok or cand_id is None:
                # If candidate splits into multiple wordpieces, skip (safe behavior)
                continue
            score = self._score_mask_sentence(left, right, cand_id)
            if score > best_score:
                best_score = score
                best_word = cand

        return best_word

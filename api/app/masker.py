"""
masker.py — the actual PII detection + masking engine.
wraps Presidio Analyzer (finds PII) and Anonymizer (replaces it).
loaded ONCE at app startup — the spaCy model is ~570MB in RAM,
so we never reload it per request.
"""
from typing import Iterable

from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig

from app.entities import DEFAULT_ENTITIES, ENTITY_LABELS


class Masker:
    """holds one Presidio Analyzer + Anonymizer for the life of the process.
    instantiated once in main.py at startup, then mask() is called per request.
    """

    def __init__(self) -> None:
        # Analyzer loads spaCy + all PII recognizers
        # this is the expensive step — ~10-15 sec on cold start
        self.analyzer = AnalyzerEngine()

        # Anonymizer is light — just rule-based replacement
        self.anonymizer = AnonymizerEngine()

    @staticmethod
    def _filter_overlaps(results):
        """drop overlapping spans — keep the higher-scoring one.
        Presidio sometimes finds e.g. URL inside EMAIL_ADDRESS;
        the anonymizer masks only the winner, so we report only the winner too.
        """
        sorted_results = sorted(results, key=lambda r: r.score, reverse=True)
        kept = []
        for r in sorted_results:
            overlaps = any(
                not (r.end <= k.start or r.start >= k.end)
                for k in kept
            )
            if not overlaps:
                kept.append(r)
        return kept

    def mask(
        self,
        text: str,
        entities: Iterable[str] | None = None,
        language: str = "en",
    ) -> dict:
        """detect PII in text, return masked text + list of entities found.

        args:
            text       — the input string to scan
            entities   — which PII types to look for; defaults to DEFAULT_ENTITIES
            language   — only "en" supported in Phase 1

        returns dict with:
            masked_text       — input with PII replaced by <PERSON>, <EMAIL>, etc.
            entities_found    — list of {type, label, start, end, score}
            entities_count    — total spans masked (handy for usage metering)
        """
        # which entity types to look for
        requested = tuple(entities) if entities else DEFAULT_ENTITIES

        # step 1 — Analyzer scans the text, returns list of RecognizerResult
        results = self.analyzer.analyze(
            text=text,
            entities=list(requested),
            language=language,
        )

        # step 2 — build replacement rules
        operators = {
            entity: OperatorConfig("replace", {"new_value": f"<{entity}>"})
            for entity in requested
        }

        # step 3 — Anonymizer applies the replacements
        anonymized = self.anonymizer.anonymize(
            text=text,
            analyzer_results=results,
            operators=operators,
        )

        # filter overlapping spans before reporting — match the masked text
        results = self._filter_overlaps(results)

        # step 4 — shape the response for the API caller
        entities_found = [
            {
                "type":  r.entity_type,
                "label": ENTITY_LABELS.get(r.entity_type, r.entity_type),
                "start": r.start,
                "end":   r.end,
                "score": round(r.score, 3),
            }
            for r in results
        ]

        return {
            "masked_text":    anonymized.text,
            "entities_found": entities_found,
            "entities_count": len(entities_found),
        }

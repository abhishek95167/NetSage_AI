"""
NetSage AI — AI Diagnosis Engine
Abstraction layer that supports multiple AI providers.
Automatically selects between OpenAI API and mock demo provider.
"""

import os
from typing import Dict, Optional
from ai.diagnosis.mock_provider import get_mock_diagnosis
from ai.diagnosis.openai_provider import get_openai_diagnosis


class DiagnosisEngine:
    """
    AI Diagnosis Engine with provider abstraction.
    Supports OpenAI-compatible APIs and a mock demo provider.
    """

    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY", "")
        self.base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    @property
    def is_demo_mode(self) -> bool:
        """Check if running in demo mode (no API key configured)."""
        return not bool(self.api_key)

    async def diagnose(
        self,
        symptom: str,
        topology_notes: str,
        show_outputs: str,
        expected_fault: str = ""
    ) -> Dict:
        """
        Run AI diagnosis on a troubleshooting case.
        Uses OpenAI API if key is available, otherwise uses mock provider.
        """
        if self.is_demo_mode:
            result = await get_mock_diagnosis(
                symptom=symptom,
                topology_notes=topology_notes,
                show_outputs=show_outputs,
                expected_fault=expected_fault
            )
            return result
        else:
            result = await get_openai_diagnosis(
                symptom=symptom,
                topology_notes=topology_notes,
                show_outputs=show_outputs,
                expected_fault=expected_fault,
                api_key=self.api_key,
                base_url=self.base_url,
                model=self.model
            )
            return result


# Singleton instance
_engine: Optional[DiagnosisEngine] = None


def get_engine() -> DiagnosisEngine:
    """Get the singleton diagnosis engine instance."""
    global _engine
    if _engine is None:
        _engine = DiagnosisEngine()
    return _engine

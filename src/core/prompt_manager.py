import logging
from pathlib import Path
from typing import Dict
from core.config import AppConfig

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("PromptManager")

class PromptManager:
    def __init__(self, config: AppConfig):
        self.config = config

    def _get_content_with_fallback(self, directory: Path, context: str, filename: str) -> str:
        """
        Internal engine:
        1. Tries path: directory / context / filename
        2. Tries path: directory / default_context / filename
        3. Raises FileNotFoundError if both fail.
        """
        # 1. Attempt the requested context
        target_path = directory / context / filename
        if target_path.exists():
            return target_path.read_text(encoding="utf-8")

        # 2. Attempt the default context fallback
        fallback_path = directory / self.config.default_context / filename
        if fallback_path.exists():
            logger.warning(
                f"Context '{context}' not found for {filename}. "
                f"Falling back to default context: '{self.config.default_context}'"
            )
            return fallback_path.read_text(encoding="utf-8")

        # 3. Both failed
        raise FileNotFoundError(
            f"Prompt file '{filename}' not found in context '{context}' "
            f"or default context '{self.config.default_context}' (searched in {directory})"
        )

    # --- Summary Related Prompts ---

    def get_summary_agent_prompts(self, context: str) -> Dict[str, str]:
        """Returns system and summarize prompts."""
        return {
            "system_prompt": self._get_content_with_fallback(self.config.summary_dir, context, "summary_system.txt"),
            "summarize_prompt": self._get_content_with_fallback(self.config.summary_dir, context, "summarize.txt")
        }

    def get_read_eval_agent_prompts(self, context: str) -> Dict[str, str]:
        """Returns system and read_eval prompts."""
        return {
            "system_prompt": self._get_content_with_fallback(self.config.summary_dir, context, "read_eval_system.txt"),
            "read_eval_prompt": self._get_content_with_fallback(self.config.summary_dir, context, "read_eval.txt")
        }

    def get_refinement_agent_prompts(self, context: str) -> Dict[str, str]:
        """Returns system and refine prompts."""
        return {
            "system_prompt": self._get_content_with_fallback(self.config.summary_dir, context, "refine_system.txt"),
            "refine_prompt": self._get_content_with_fallback(self.config.summary_dir, context, "refine.txt")
        }

    # --- Translation Related Prompts ---

    def get_translation_draft_prompts(self, context: str) -> Dict[str, str]:
        """Returns system, pre_draft, draft, and refine_draft prompts."""
        return {
            "system_prompt": self._get_content_with_fallback(self.config.translation_dir, context, "draft_system.txt"),
            "pre_draft_prompt": self._get_content_with_fallback(self.config.translation_dir, context, "pre_draft.txt"),
            "draft_prompt": self._get_content_with_fallback(self.config.translation_dir, context, "draft.txt"),
            "refine_draft_prompt": self._get_content_with_fallback(self.config.translation_dir, context, "refine_draft.txt"),
        }

    def get_translation_proofread_prompts(self, context: str) -> Dict[str, str]:
        """Returns system and proofread prompts."""
        return {
            "system_prompt": self._get_content_with_fallback(self.config.translation_dir, context, "proofread_system.txt"),
            "proofread_prompt": self._get_content_with_fallback(self.config.translation_dir, context, "proofread.txt"),
        }

    def get_translation_direct_prompts(self, context: str) -> Dict[str, str]:
        """Returns translate prompt."""
        return {
            "translate_direct_prompt": self._get_content_with_fallback(self.config.translation_dir, context, "direct_translation.txt"),
        }


    # --- Factuality Related Prompts ---

    def get_fact_extractor_prompts(self, context: str) -> Dict[str, str]:
        return {
            "system_prompt": self._get_content_with_fallback(self.config.factuality_dir, context, "key_fact_generation.txt")
        }

    def get_fact_validator_prompts(self, context: str) -> Dict[str, str]:
        return {
            "system_prompt": self._get_content_with_fallback(self.config.factuality_dir, context, "key_fact_validation.txt")
        }

    def get_fact_alignment_prompts(self, context: str) -> Dict[str, str]:
        return {
            "system_prompt": self._get_content_with_fallback(self.config.factuality_dir, context, "key_fact_alignment.txt")
        }

    def get_advocate_prompts(self, context: str) -> Dict[str, str]:
        return {
            "system_prompt": self._get_content_with_fallback(self.config.factuality_dir, context, "advocate.txt")
        }

    def get_skeptic_prompts(self, context: str) -> Dict[str, str]:
        return {
            "system_prompt": self._get_content_with_fallback(self.config.factuality_dir, context, "skeptic.txt")
        }

    def get_adjudicator_prompts(self, context: str) -> Dict[str, str]:
        return {
            "system_prompt": self._get_content_with_fallback(self.config.factuality_dir, context, "adjudicator.txt")
        }

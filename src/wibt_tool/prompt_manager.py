from typing import Dict, Optional
import logging
from importlib import resources
from wibt_tool.config import AppConfig

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("PromptManager")

class PromptManager:
    def __init__(self, config: AppConfig, package_name: str = "wibt_tool"):
        self.config = config
        self.package_name = package_name

    def _get_content_with_fallback(self, sub_package: str, context: str, filename: str) -> str:
        """
        Internal engine using importlib.resources for WASM compatibility.
        1. Tries path: package / sub_package / context / filename
        2. Tries path: package / sub_package / default_context / filename
        3. Raises FileNotFoundError if both fail.
        """
        # 1. Attempt the requested context
        try:
            target_resource = resources.files(self.package_name).joinpath("prompts", sub_package, context, filename)
            if target_resource.exists():
                return target_resource.read_text(encoding="utf-8")
        except Exception:
            pass

        # 2. Attempt the default context fallback
        try:
            fallback_resource = resources.files(self.package_name).joinpath("prompts", sub_package, self.config.default_context, filename)
            if fallback_resource.exists():
                logger.warning(
                    f"Context '{context}' not found for {filename}. "
                    f"Falling back to default context: '{self.config.default_context}'"
                )
                return fallback_resource.read_text(encoding="utf-8")
        except Exception:
            pass

        # 3. Both failed
        raise FileNotFoundError(
            f"Prompt file '{filename}' not found in context '{context}' "
            f"or default context '{self.config.default_context}' (searched in {self.package_name}/{sub_package})"
        )

    # --- Summary Related Prompts ---

    def get_summary_agent_prompts(self, context: str) -> Dict[str, str]:
        """Returns system and summarize prompts."""
        return {
            "system_prompt": self._get_content_with_fallback("summary", context, "summary_system.txt"),
            "summarize_prompt": self._get_content_with_fallback("summary", context, "summarize.txt")
        }

    def get_read_eval_agent_prompts(self, context: str) -> Dict[str, str]:
        """Returns system and read_eval prompts."""
        return {
            "system_prompt": self._get_content_with_fallback("summary", context, "read_eval_system.txt"),
            "read_eval_prompt": self._get_content_with_fallback("summary", context, "read_eval.txt")
        }

    def get_refinement_agent_prompts(self, context: str) -> Dict[str, str]:
        """Returns system and refine prompts."""
        return {
            "system_prompt": self._get_content_with_fallback("summary", context, "refine_system.txt"),
            "refine_prompt": self._get_content_with_fallback("summary", context, "refine.txt")
        }

    # --- Translation Related Prompts ---

    def get_translation_draft_prompts(self, context: str) -> Dict[str, str]:
        """Returns system, pre_draft, draft, and refine_draft prompts."""
        return {
            "system_prompt": self._get_content_with_fallback("translation", context, "draft_system.txt"),
            "pre_draft_prompt": self._get_content_with_fallback("translation", context, "pre_draft.txt"),
            "draft_prompt": self._get_content_with_fallback("translation", context, "draft.txt"),
            "refine_draft_prompt": self._get_content_with_fallback("translation", context, "refine_draft.txt"),
        }

    def get_translation_proofread_prompts(self, context: str) -> Dict[str, str]:
        """Returns system and proofread prompts."""
        return {
            "system_prompt": self._get_content_with_fallback("translation", context, "proofread_system.txt"),
            "proofread_prompt": self._get_content_with_fallback("translation", context, "proofread.txt"),
        }

    def get_translation_direct_prompts(self, context: str) -> Dict[str, str]:
        """Returns translate prompt."""
        return {
            "translate_direct_prompt": self._get_content_with_fallback("translation", context, "direct_translation.txt"),
        }


    # --- Factuality Related Prompts ---

    def get_fact_extractor_prompts(self, context: str) -> Dict[str, str]:
        return {
            "system_prompt": self._get_content_with_fallback("factuality_evaluation", context, "key_fact_generation.txt")
        }

    def get_fact_validator_prompts(self, context: str) -> Dict[str, str]:
        return {
            "system_prompt": self._get_content_with_fallback("factuality_evaluation", context, "key_fact_validation.txt")
        }

    def get_fact_alignment_prompts(self, context: str) -> Dict[str, str]:
        return {
            "system_prompt": self._get_content_with_fallback("factuality_evaluation", context, "key_fact_alignment.txt")
        }

    def get_advocate_prompts(self, context: str) -> Dict[str, str]:
        return {
            "system_prompt": self._get_content_with_fallback("factuality_evaluation", context, "advocate.txt")
        }

    def get_skeptic_prompts(self, context: str) -> Dict[str, str]:
        return {
            "system_prompt": self._get_content_with_fallback("factuality_evaluation", context, "skeptic.txt")
        }

    def get_adjudicator_prompts(self, context: str) -> Dict[str, str]:
        return {
            "system_prompt": self._get_content_with_fallback("factuality_evaluation", context, "adjudicator.txt")
        }

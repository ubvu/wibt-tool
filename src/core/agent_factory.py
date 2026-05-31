from typing import List
from agents import (
    SummaryAgent, 
    ReadEvalAgent, 
    RefinementAgent, 
    TranslationPreDraftAgent,
    TranslationDraftAgent, 
    TranslationRefineDraftAgent,
    TranslationProofreadAgent, 
    TranslationDirectAgent,
    FactExtractorAgent, 
    FactValidatorAgent, 
    FactAlignmentAgent, 
    ArgumentAgent, 
    AdjudicatorAgent
)
from core.config import AppConfig
from core.prompt_manager import PromptManager


class AgentFactory:
    """
    The AgentFactory is responsible for assembling all agents.
    It uses AppConfig for settings, PromptManager for file loading,
    and the llm_endpoint for connectivity.
    """

    def __init__(self, config: AppConfig, prompt_manager: PromptManager, llm_endpoint):
        self.config = config
        self.pm = prompt_manager
        self.llm = llm_endpoint

    def create_summary_agent(self, context: str) -> SummaryAgent:
        prompts = self.pm.get_summary_agent_prompts(context)
        return SummaryAgent(
            llm_endpoint=self.llm,
            model=self.config.summary.name,
            temperature=self.config.summary.temperature,
            history=-1,
            **prompts
        )

    def create_read_eval_agent(self, context: str) -> ReadEvalAgent:
        prompts = self.pm.get_read_eval_agent_prompts(context)
        return ReadEvalAgent(
            llm_endpoint=self.llm,
            model=self.config.read_eval.name,
            temperature=self.config.read_eval.temperature,
            history=-1,
            **prompts
        )

    def create_refinement_agent(self, context: str) -> RefinementAgent:
        prompts = self.pm.get_refinement_agent_prompts(context)
        return RefinementAgent(
            llm_endpoint=self.llm,
            model=self.config.refinement.name,
            temperature=self.config.refinement.temperature,
            **prompts
        )

    def create_translation_pre_draft_agent(self, context: str) -> TranslationPreDraftAgent:
        prompts = self.pm.get_translation_draft_prompts(context)
        return TranslationPreDraftAgent(
            llm_endpoint=self.llm,
            model=self.config.pre_draft.name,
            temperature=self.config.pre_draft.temperature,
            **prompts,
        )

    def create_translation_draft_agent(self, context: str) -> TranslationDraftAgent:
        prompts = self.pm.get_translation_draft_prompts(context)
        return TranslationDraftAgent(
            llm_endpoint=self.llm,
            model=self.config.draft.name,
            temperature=self.config.draft.temperature,
            **prompts,
        )

    def create_translation_refine_draft_agent(self, context: str) -> TranslationRefineDraftAgent:
        prompts = self.pm.get_translation_draft_prompts(context)
        return TranslationRefineDraftAgent(
            llm_endpoint=self.llm,
            model=self.config.refine_draft.name,
            temperature=self.config.refine_draft.temperature,
            **prompts,
        )

    def create_translation_direct_agent(self, context) -> TranslationDirectAgent:
        prompts = self.pm.get_translation_direct_prompts(context)
        return TranslationDirectAgent(
            llm_endpoint=self.llm,
            model=self.config.translation_direct.name,
            temperature=self.config.translation_direct.temperature,
            **prompts
        )

    def create_translation_proofread_agent(self, context: str) -> TranslationProofreadAgent:
        prompts = self.pm.get_translation_proofread_prompts(context)
        return TranslationProofreadAgent(
            llm_endpoint=self.llm,
            model=self.config.proofread.name,
            temperature=self.config.proofread.temperature,
            **prompts
        )

    def create_fact_extractor_agent(self, context: str) -> FactExtractorAgent:
        prompts = self.pm.get_fact_extractor_prompts(context)
        return FactExtractorAgent(
            llm_endpoint=self.llm,
            model=self.config.fact_extractor.name,
            temperature=self.config.fact_extractor.temperature,
            **prompts
        )

    def create_fact_validator_agents(self, context: str) -> List[FactValidatorAgent]:
        """Creates a list of validator agents based on the config settings."""
        agents = []
        prompts = self.pm.get_fact_validator_prompts(context)
        
        for settings in self.config.fact_validators:
            agents.append(FactValidatorAgent(
                llm_endpoint=self.llm,
                model=settings.name,
                temperature=settings.temperature,
                **prompts
            ))
        return agents

    def create_fact_alignment_agent(self, context: str) -> FactAlignmentAgent:
        prompts = self.pm.get_fact_alignment_prompts(context)
        return FactAlignmentAgent(
            llm_endpoint=self.llm,
            model=self.config.fact_alignment.name,
            temperature=self.config.fact_alignment.temperature,
            **prompts
        )

    def create_advocate_agent(self, context: str) -> ArgumentAgent:
        prompts = self.pm.get_advocate_prompts(context)
        return ArgumentAgent(
            llm_endpoint=self.llm,
            model=self.config.advocate.name,
            temperature=self.config.advocate.temperature,
            **prompts
        )

    def create_skeptic_agent(self, context: str) -> ArgumentAgent:
        prompts = self.pm.get_skeptic_prompts(context)
        return ArgumentAgent(
            llm_endpoint=self.llm,
            model=self.config.skeptic.name,
            temperature=self.config.skeptic.temperature,
            **prompts
        )

    def create_adjudicator_agent(self, context: str) -> AdjudicatorAgent:
        prompts = self.pm.get_adjudicator_prompts(context)
        return AdjudicatorAgent(
            llm_endpoint=self.llm,
            model=self.config.adjudicator.name,
            temperature=self.config.adjudicator.temperature,
            **prompts
        )
